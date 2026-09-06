#!/usr/bin/env python3
"""ShaktiSafe Brief: dependency-free, source-linked outing checks (Python 3.11+)."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import tempfile
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

UTC = timezone.utc
FIELDS = {
    'weather': {'temperature_2m': '°C', 'precipitation_probability': '%', 'wind_speed_10m': 'km/h'},
    'air': {'pm2_5': 'μg/m³', 'us_aqi': 'USAQI'},
}
ENDPOINTS = {'weather': 'https://api.open-meteo.com/v1/forecast',
             'air': 'https://air-quality-api.open-meteo.com/v1/air-quality'}


def now():
    return datetime.now(UTC)


def stamp(value):
    return value.astimezone(UTC).isoformat()


def parse(value):
    return datetime.fromisoformat(value.replace('Z', '+00:00'))


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def write(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            json.dump(data, stream, indent=2, ensure_ascii=False, allow_nan=False)
            stream.write('\n')
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def fetch(url):
    headers = {'User-Agent': os.getenv('SHAKTISAFE_USER_AGENT', 'ShaktiSafeBrief/0.1 (hackathon prototype)'),
               'Accept': 'application/json'}
    with urlopen(Request(url, headers=headers), timeout=20) as response:
        value = json.load(response)
    if not isinstance(value, dict) or value.get('error'):
        raise ValueError('Provider returned an invalid response')
    return value


def resolve(city, country, location_id=None, getter=fetch):
    country = country.upper()
    if len(country) != 2 or not country.isalpha() or not city.strip():
        raise ValueError('Provide a city and two-letter country code')
    url = 'https://geocoding-api.open-meteo.com/v1/search?' + urlencode(
        {'name': city, 'count': 100, 'language': 'en', 'format': 'json', 'countryCode': country})
    rows = [r for r in getter(url).get('results', []) if r.get('country_code') == country]
    if location_id is not None:
        rows = [r for r in rows if str(r['id']) == str(location_id)]
    if len(rows) != 1:
        candidates = [{'id': r['id'], 'name': r['name'], 'region': r.get('admin1')} for r in rows]
        raise ValueError('Destination unresolved/ambiguous. Select --location-id from: ' + json.dumps(candidates))
    r = rows[0]
    return {k: r[k] for k in ('id', 'name', 'country_code', 'latitude', 'longitude', 'timezone')} | {'source_url': url}


def context(location, start, hours, clock=None):
    clock = clock or now()
    if not 1 <= hours <= 24:
        raise ValueError('Duration must be 1–24 hours')
    zone = ZoneInfo(location['timezone'])
    if start == 'next-hour':
        dt = clock.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    else:
        dt = parse(start)
        if dt.tzinfo is None:
            candidates = {stamp(dt.replace(tzinfo=zone, fold=f)) for f in (0, 1)
                          if dt.replace(tzinfo=zone, fold=f).astimezone(UTC).astimezone(zone).replace(tzinfo=None) == dt}
            if len(candidates) != 1:
                raise ValueError('Ambiguous or nonexistent local time; provide an ISO timestamp with UTC offset')
            dt = parse(candidates.pop())
        elif dt.utcoffset() != dt.astimezone(zone).utcoffset():
            raise ValueError('Timestamp offset does not match destination timezone')
    dt = dt.astimezone(UTC)
    end = dt + timedelta(hours=hours)
    if dt < clock or end > clock + timedelta(days=4):
        raise ValueError('Choose a future outing ending within four days; individual source coverage may be shorter')
    identity = {'location_id': location['id'], 'start_utc': stamp(dt), 'end_utc': stamp(end), 'schema': 1}
    key = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()[:24]
    return {'schema': 1, 'key': key, 'location': location, 'start_utc': stamp(dt), 'end_utc': stamp(end),
            'start_local': dt.astimezone(zone).isoformat(), 'end_local': end.astimezone(zone).isoformat()}


def hourly(payload, ctx, fields):
    series = payload['hourly']
    times = series['time']
    start, end = parse(ctx['start_utc']).timestamp(), parse(ctx['end_utc']).timestamp()
    # Include every hourly bin overlapping the requested interval, including partial hours.
    first = math.floor(start / 3600) * 3600
    expected = list(range(first, math.ceil(end / 3600) * 3600, 3600))
    indexed = {t: i for i, t in enumerate(times)}
    metrics = {}
    for field, unit in fields.items():
        values = series[field]
        if len(values) != len(times):
            raise ValueError('Provider time/value length mismatch')
        selected = [values[indexed[t]] for t in expected if t in indexed]
        if len(selected) != len(expected) or any(not isinstance(v, (int, float)) or not math.isfinite(v) for v in selected):
            raise ValueError('Incomplete hourly coverage for outing')
        actual_unit = payload['hourly_units'][field]
        if actual_unit != unit:
            raise ValueError(f'Unexpected unit for {field}: {actual_unit}')
        metrics[field] = {'min': min(selected), 'max': max(selected), 'unit': unit}
    return {'metrics': metrics, 'sample_times_utc': [stamp(datetime.fromtimestamp(t, UTC)) for t in expected],
            'sampling_note': 'Hourly bins overlapping the outing; edge bins can extend beyond it.'}


def alert_data(payload, ctx):
    if payload.get('type') != 'FeatureCollection' or not isinstance(payload.get('features'), list):
        raise ValueError('Malformed NWS alert collection')
    start, end = parse(ctx['start_utc']), parse(ctx['end_utc'])
    alerts = []
    for item in payload['features']:
        p = item['properties']
        if p.get('status') != 'Actual':
            continue
        onset = p.get('onset') or p.get('effective')
        expires = p.get('ends') or p.get('expires')
        if not onset or not expires:
            raise ValueError('NWS alert lacks validity interval')
        if parse(onset) < end and parse(expires) > start:
            alerts.append({k: p.get(k) for k in ('id', 'event', 'headline', 'severity', 'instruction', 'description', 'sent', 'expires', 'ends')} |
                          {'onset': onset, 'source_url': item.get('id', p.get('@id'))})
    return {'alerts': sorted(alerts, key=lambda x: str(x['id'])),
            'scope': 'Currently published NWS alerts overlapping this outing; future alerts may not yet be issued.'}


def source(name, ctx, getter=fetch, clock=None):
    clock = clock or now()
    loc = ctx['location']
    result = {'name': name, 'context_key': ctx['key'], 'retrieved_at': stamp(clock), 'status': 'unavailable'}
    if name == 'alerts' and loc['country_code'] != 'US':
        return result | {'status': 'unsupported', 'reason': 'Official alert coverage not implemented for this country', 'source_url': None}
    if name == 'alerts':
        url = 'https://api.weather.gov/alerts/active?' + urlencode({'point': f"{loc['latitude']},{loc['longitude']}"})
    else:
        query = {'latitude': loc['latitude'], 'longitude': loc['longitude'], 'hourly': ','.join(FIELDS[name]),
                 'timezone': 'GMT', 'timeformat': 'unixtime', 'forecast_days': 5}
        url = ENDPOINTS[name] + '?' + urlencode(query)
    result['source_url'] = url
    try:
        payload = getter(url)
        result['data'] = alert_data(payload, ctx) if name == 'alerts' else hourly(payload, ctx, FIELDS[name])
        result['status'] = 'ok'
        result['payload_sha256'] = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
    except (OSError, ValueError, KeyError, TypeError, IndexError) as exc:
        result['reason'] = f'{type(exc).__name__}: {exc}'
    return result


def compare(current, previous):
    if previous is None:
        return ['Baseline created; no previous successful check to compare.']
    changes = []
    if 'metrics' in current:
        for field, metric in current['metrics'].items():
            old = previous.get('metrics', {}).get(field)
            if not old or old['unit'] != metric['unit']:
                changes.append(f'{field}: no compatible baseline')
                continue
            for bound in ('min', 'max'):
                delta = round(metric[bound] - old[bound], 3)
                if delta:
                    changes.append(f"{field} {bound}: {old[bound]} → {metric[bound]} {metric['unit']} ({delta:+g})")
    else:
        before = {a['id']: a for a in previous['alerts']}
        after = {a['id']: a for a in current['alerts']}
        for key in sorted(after.keys() - before.keys()):
            changes.append(f"New official alert: {after[key]['event']}")
        for key in sorted(before.keys() - after.keys()):
            changes.append(f"No longer returned for outing: {before[key]['event']} (not proof of cancellation)")
        for key in sorted(after.keys() & before.keys()):
            if after[key] != before[key]:
                changes.append(f"Updated official alert: {after[key]['event']}")
    return changes or ['No changes in the compared fields.']


@contextmanager
def locked(path):
    # flock is available on the supported macOS/Linux/WSL platforms.
    import fcntl
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a', encoding='utf-8') as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        yield


def compose(ctx, results, state_dir, clock=None):
    clock = clock or now()
    if {r['name'] for r in results} != {'weather', 'air', 'alerts'} or len(results) != 3:
        raise ValueError('Exactly one result per source is required')
    if any(r['context_key'] != ctx['key'] for r in results):
        raise ValueError('Source results belong to another outing')
    state_path = Path(state_dir) / (ctx['key'] + '.json')
    with locked(state_path.with_suffix('.lock')):
        state = read(state_path) if state_path.exists() else {'context': ctx, 'sources': {}}
        output = []
        for original in results:
            r = dict(original)
            previous = state['sources'].get(r['name'])
            if previous and parse(r['retrieved_at']) < parse(previous['retrieved_at']):
                raise ValueError('Older source result cannot replace a newer baseline')
            if r['status'] == 'ok':
                r['changes'] = compare(r['data'], previous['data'] if previous else None)
                r['compared_with'] = previous['retrieved_at'] if previous else None
                state['sources'][r['name']] = original
            else:
                r['changes'] = ['Comparison unavailable: ' + r['reason']]
                if previous:
                    r['last_successful'] = previous
            output.append(r)
        write(state_path, state)
    return {'title': 'ShaktiSafe Brief', 'mode': 'live', 'generated_at': stamp(clock), 'context': ctx, 'sources': output,
            'limitations': ['Environmental preparedness information, not a safety guarantee.',
                            'Air quality is a CAMS model via Open-Meteo (~11 km Europe / ~45 km global), not a street-level sensor.',
                            'Official alert integration currently covers supported US locations only.',
                            'Follow current instructions from local authorities.'],
            'attribution': ['Weather: Open-Meteo', 'Air quality: CAMS ENSEMBLE / CAMS global via Open-Meteo', 'Alerts: US National Weather Service']}


def markdown(report):
    ctx = report['context']
    lines = [f"# {report['title']}", '', f"Mode: **{report['mode']}**", '',
             f"{ctx['location']['name']}, {ctx['location']['country_code']} · {ctx['location']['timezone']}",
             f"Outing: {ctx['start_local']} → {ctx['end_local']}", f"Checked: {report['generated_at']}", '', '## What changed?', '']
    for r in report['sources']:
        lines.extend(f"- **{r['name']}**: {change}" for change in r['changes'])
    for r in report['sources']:
        lines += ['', f"## {r['name'].title()} — {r['status']}", '', f"Retrieved: {r['retrieved_at']}"]
        if r.get('source_url'):
            lines += [f"Source: {r['source_url']}"]
        if r.get('reason'):
            lines += [r['reason']]
        data = r.get('data')
        if r.get('last_successful'):
            previous = r['last_successful']
            lines += ['', f"STALE: last successful data from {previous['retrieved_at']}; current status unknown."]
            data = previous['data']
        if data and 'metrics' in data:
            lines += ['', '| Metric | Minimum | Maximum | Unit |', '|---|---:|---:|---|']
            lines += [f"| {k} | {v['min']} | {v['max']} | {v['unit']} |" for k, v in data['metrics'].items()]
            lines += ['', data['sampling_note']]
        if data and 'alerts' in data:
            lines += ['', data['scope']]
            if not data['alerts']:
                lines += ['No matching alerts in this retrieved response.']
            for a in data['alerts']:
                lines += ['', f"### {a['event']} ({a['severity']})", str(a['headline']),
                          f"Validity: {a['onset']} → {a.get('ends') or a['expires']}",
                          str(a['instruction'] or 'No instructions supplied.'), str(a['source_url'])]
    lines += ['', '## Coverage and attribution', ''] + ['- ' + x for x in report['limitations'] + report['attribution']]
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ('run', 'resolve'):
        p = sub.add_parser(name)
        p.add_argument('--city', required=True)
        p.add_argument('--country', required=True)
        p.add_argument('--location-id', type=int)
        p.add_argument('--start', default='next-hour')
        p.add_argument('--hours', type=int, default=2)
        p.add_argument('--out', default='output')
    for name in ('weather', 'air', 'alerts', 'compose', 'refresh'):
        p = sub.add_parser(name)
        p.add_argument('--context', required=True)
        p.add_argument('--out', default='output')
    sub.choices['compose'].add_argument('--inputs', default='output')
    for name in ('run', 'compose', 'refresh'):
        sub.choices[name].add_argument('--state-dir', default='.shaktisafe/state')
    args = parser.parse_args()
    destination = Path(args.out)
    destination.mkdir(parents=True, exist_ok=True)
    try:
        if args.command in ('run', 'resolve'):
            ctx = context(resolve(args.city, args.country, args.location_id), args.start, args.hours)
            write(destination / 'context.json', ctx)
        else:
            ctx = read(args.context)
        if args.command == 'resolve':
            print(json.dumps(ctx, indent=2))
            return
        if args.command in ('weather', 'air', 'alerts'):
            r = source(args.command, ctx)
            write(destination / (args.command + '.json'), r)
            print(json.dumps(r, indent=2))
            return
        if args.command in ('run', 'refresh'):
            if parse(ctx['end_utc']) <= now():
                raise ValueError('This outing has ended. Resolve a new future outing.')
            with ThreadPoolExecutor(max_workers=3) as pool:
                results = list(pool.map(lambda n: source(n, ctx), ('weather', 'air', 'alerts')))
            for r in results:
                write(destination / (r['name'] + '.json'), r)
        else:
            results = [read(Path(args.inputs) / (n + '.json')) for n in ('weather', 'air', 'alerts')]
        report = compose(ctx, results, args.state_dir)
        write(destination / 'brief.json', report)
        (destination / 'brief.md').write_text(markdown(report), encoding='utf-8')
        print(markdown(report))
    except (ValueError, OSError, KeyError, TypeError) as exc:
        parser.exit(2, f'ShaktiSafe: {exc}\n')


if __name__ == '__main__':
    main()
