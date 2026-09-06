# ShaktiSafe Brief

**What changed before I leave?** Check weather, modeled air quality, and supported official alerts for the same planned outing. Built around the CHIP-GIS and Shakti 360 preparedness concept.

Python 3.11+ on macOS, Linux, or WSL. No pip packages, local AI model, database, or API key required for the public data endpoints. The default Codespaces configuration uses Python 3.12.

## Run immediately

```bash
python3 -m unittest -v
python3 demo.py
python3 shaktisafe.py run --city Chennai --country IN --location-id 1264527
```

The live command selects the next full UTC hour and a two-hour outing. It saves `output/context.json`, source results, `output/brief.json`, and `output/brief.md`.

Refresh **the same outing**:

```bash
python3 shaktisafe.py refresh --context output/context.json
```

Use `refresh` after the first run: another `run` with the default next-hour setting can select a different outing as the clock advances. For a chosen local time, supply `--start YYYY-MM-DDTHH:MM --hours 2` using a real future date. Ambiguous DST times require a matching UTC offset. Outings must end within four days; individual source availability may be shorter.

Other verified destinations:

```bash
python3 shaktisafe.py run --city Houston --country US --location-id 4699066
python3 shaktisafe.py run --city London --country GB --location-id 2643743
```

For another destination, omit `--location-id`. If several places match, the CLI lists candidate IDs and regions so you can select one explicitly.

## The reusable stages

Each source is independently runnable for Rote recording:

```bash
python3 shaktisafe.py resolve --city Chennai --country IN --location-id 1264527
python3 shaktisafe.py weather --context output/context.json
python3 shaktisafe.py air --context output/context.json
python3 shaktisafe.py alerts --context output/context.json
python3 shaktisafe.py compose --context output/context.json
```

Resolve precedes three independent source steps; compose depends on all three. `run` performs those reads concurrently. A malformed destination fails before source requests; expected source failures produce labeled unavailable results. Never infer successful coverage from the process exit code alone: inspect each source's `status`.

## Honest coverage

| Capability | Coverage |
|---|---|
| Geocoding | Open-Meteo locations worldwide; ambiguity requires selection |
| Weather | Open-Meteo forecast, hourly bins overlapping outing |
| Air quality | CAMS via Open-Meteo; regional/global modeled data, not street-level sensing |
| Official alerts | Currently published NWS alerts for supported US points |
| Other countries' alerts | Explicitly unsupported; never interpreted as all-clear |
| Change history | Same location ID + exact UTC outing + schema version |

Compared weather and air fields are the minimum and maximum over the overlapping hourly bins. This version does not detect every change within an hourly series when its extrema remain unchanged. Alert comparison checks IDs and returned content; an alert disappearing is described as no longer returned, not automatically canceled. NWS can assign a new ID to an update.

## Local effects and privacy

Source requests send destination coordinates to the named public providers. Baselines in `.shaktisafe/state/` store city-level location, outing times, source results and timestamps. `--state-dir` changes this location. Files are locked and atomically replaced; a failed source keeps its last successful baseline. Old data is labeled stale and is not evidence of current conditions. Baselines have no automatic retention deletion; delete the directory to clear history.

Outputs and state should be private to the person running the Play. Use separate `--out` directories for simultaneous outings. Do not commit credentials, personal outputs, Rote account state, or raw private traces. No messages, location tracking, or public posts are sent by this application.

`SHAKTISAFE_USER_AGENT` optionally supplies your app/contact identification for NWS requests. It is not an API credential.

## Demo and tests

`python3 demo.py` creates three **synthetic, explicitly labeled** reports: baseline, changed conditions, and source failure. Fixed dates belong only to this offline example. Tests run without network and cover timezone conversion, DST ambiguity/gaps, wrong offsets, city ambiguity, hourly coverage, malformed data, missing alert coverage, interval filtering, changes, failure recovery, and out-of-order baseline protection.

See `VALIDATION.md` for actual live-check evidence and `ROTE_HANDOFF.md` for recording/publication status. A script repository is not itself a submitted Community Play.

## Sources and attribution

- Weather and geocoding: [Open-Meteo](https://open-meteo.com/), [GeoNames](https://www.geonames.org/).
- Air quality: CAMS ENSEMBLE / CAMS global forecasts through [Open-Meteo](https://open-meteo.com/en/docs/air-quality-api), approximately 11 km Europe / 45 km global.
- Official alerts: [US National Weather Service](https://www.weather.gov/documentation/services-web-api).
- Respect [Open-Meteo usage terms](https://open-meteo.com/en/terms) and data attribution. Public endpoints have use limits; commercial deployment requires reviewing the applicable plan and licenses.

This is environmental preparedness information, not an emergency dispatch system, medical recommendation, crime prediction, or safety guarantee. Follow current local-authority instructions.
