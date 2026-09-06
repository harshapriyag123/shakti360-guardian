import copy
from datetime import datetime, timedelta
import tempfile
import unittest
from shaktisafe import UTC, context, source, compose, hourly, resolve, alert_data, FIELDS

CLOCK = datetime(2026, 9, 6, 12, tzinfo=UTC)
LOCATION = {'id': 1264527, 'name': 'Chennai', 'country_code': 'IN',
            'latitude': 13.08784, 'longitude': 80.27847, 'timezone': 'Asia/Kolkata'}


def ctx():
    return context(LOCATION, '2026-09-06T18:30:00+05:30', 2, CLOCK)


def payload(name='weather'):
    return {'hourly': {'time': [1788699600, 1788703200],
                       **{field: [10, 12] for field in FIELDS[name]}},
            'hourly_units': FIELDS[name]}


class BriefTests(unittest.TestCase):
    def test_worldwide_timezone(self):
        self.assertEqual(ctx()['start_utc'], '2026-09-06T13:00:00+00:00')

    def test_dst_gap_and_fold(self):
        loc = LOCATION | {'timezone': 'America/New_York'}
        for date, clock in [('2026-11-01T01:30', datetime(2026, 10, 31, tzinfo=UTC)),
                            ('2026-03-08T02:30', datetime(2026, 3, 7, tzinfo=UTC))]:
            with self.assertRaisesRegex(ValueError, 'Ambiguous or nonexistent'):
                context(loc, date, 2, clock)

    def test_wrong_offset(self):
        with self.assertRaisesRegex(ValueError, 'offset'):
            context(LOCATION, '2026-09-06T18:30:00+00:00', 2, CLOCK)

    def test_past_and_duration_rejected(self):
        for start, hours in [('2026-09-06T12:00', 2), ('next-hour', 0), ('next-hour', 25)]:
            with self.assertRaises(ValueError):
                context(LOCATION, start, hours, CLOCK)

    def test_ambiguous_geocoding(self):
        row = LOCATION | {'admin1': 'Tamil Nadu'}
        with self.assertRaisesRegex(ValueError, 'ambiguous'):
            resolve('Chennai', 'IN', getter=lambda _: {'results': [row, row | {'id': 2}]})
        self.assertEqual(resolve('Chennai', 'IN', 2, lambda _: {'results': [row, row | {'id': 2}]})['id'], 2)

    def test_full_and_partial_hour_sampling(self):
        self.assertEqual(hourly(payload(), ctx(), FIELDS['weather'])['metrics']['temperature_2m']['max'], 12)
        partial = context(LOCATION, '2026-09-06T19:00:00+05:30', 1, CLOCK)
        self.assertEqual(len(hourly(payload(), partial, FIELDS['weather'])['sample_times_utc']), 2)

    def test_missing_null_and_wrong_units(self):
        for modification in ('missing', 'null', 'unit'):
            p = payload()
            if modification == 'missing':
                p['hourly']['time'] = p['hourly']['time'][:1]
            elif modification == 'null':
                p['hourly']['temperature_2m'][0] = None
            else:
                p['hourly_units'] = p['hourly_units'] | {'temperature_2m': '°F'}
            with self.assertRaises(ValueError):
                hourly(p, ctx(), FIELDS['weather'])

    def test_unsupported_does_not_fetch(self):
        r = source('alerts', ctx(), lambda _: self.fail('Unexpected fetch'), CLOCK)
        self.assertEqual(r['status'], 'unsupported')

    def test_malformed_alerts_fail(self):
        with self.assertRaises(ValueError):
            alert_data({}, ctx())

    def test_alert_overlap(self):
        alert = {'id': 'test-1', 'properties': {'id': 'test-1', 'status': 'Actual',
                 'event': 'TEST ONLY', 'onset': '2026-09-06T12:00:00Z', 'expires': '2026-09-06T14:00:00Z'}}
        p = {'type': 'FeatureCollection', 'features': [alert]}
        self.assertEqual(len(alert_data(p, ctx())['alerts']), 1)
        alert['properties']['expires'] = '2026-09-06T13:00:00Z'
        self.assertEqual(alert_data(p, ctx())['alerts'], [])

    def test_baseline_delta_failure_and_separate_outing(self):
        c = ctx()
        results = [source(n, c, lambda _, n=n: payload(n), CLOCK) for n in ('weather', 'air', 'alerts')]
        with tempfile.TemporaryDirectory() as directory:
            first = compose(c, results, directory, CLOCK)
            self.assertIn('Baseline created', first['sources'][0]['changes'][0])
            changed = copy.deepcopy(results)
            changed[0]['data']['metrics']['temperature_2m']['max'] = 16
            second = compose(c, changed, directory, CLOCK)
            self.assertIn('+4', second['sources'][0]['changes'][0])
            failed = copy.deepcopy(changed)
            failed[0] = {k: v for k, v in failed[0].items() if k != 'data'}
            failed[0].update(status='unavailable', reason='Timeout')
            third = compose(c, failed, directory, CLOCK)
            self.assertEqual(third['sources'][0]['last_successful']['data']['metrics']['temperature_2m']['max'], 16)
            recovered = compose(c, changed, directory, CLOCK)
            self.assertIn('No changes', recovered['sources'][0]['changes'][0])
            different = context(LOCATION, '2026-09-06T20:30:00+05:30', 2, CLOCK)
            with self.assertRaisesRegex(ValueError, 'another outing'):
                compose(different, results, directory, CLOCK)

    def test_out_of_order_cannot_overwrite_baseline(self):
        c = ctx()
        current = [source(n, c, lambda _, n=n: payload(n), CLOCK) for n in ('weather', 'air', 'alerts')]
        with tempfile.TemporaryDirectory() as directory:
            compose(c, current, directory, CLOCK)
            old = copy.deepcopy(current)
            old[0]['retrieved_at'] = (CLOCK - timedelta(hours=1)).isoformat()
            with self.assertRaisesRegex(ValueError, 'Older'):
                compose(c, old, directory, CLOCK)


if __name__ == '__main__':
    unittest.main()
