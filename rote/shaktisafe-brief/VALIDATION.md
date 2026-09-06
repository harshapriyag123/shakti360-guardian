# Validation evidence

Checked on September 6, 2026. These are development results, not current conditions for travel.

## Automated checks

`python3 -m unittest -v`: 12 tests passed. `python3 -m py_compile shaktisafe.py demo.py`: passed. Offline demo: all three labeled JSON and Markdown reports generated.

## Live API integration

| Destination | Weather | Air quality | Official alerts | Report generated (UTC) |
|---|---|---|---|---|
| Chennai, India | Successful | Successful | Explicitly unsupported | 2026-09-06 12:46:20 |
| London, UK | Successful | Successful | Explicitly unsupported | 2026-09-06 12:45:45 |
| Houston, USA | Successful | Successful | NWS request successful; no matching alerts in response | 2026-09-06 12:45:45 |

Chennai refresh also confirmed comparison against the same outing's existing weather baseline. Live sources did not demonstrate a newly issued alert. Alert interval filtering is tested with synthetic data; live active-warning content still needs a suitable event to verify end to end.

The first live Chennai call exposed Open-Meteo's `USAQI` unit spelling. The parser was corrected and live air checks succeeded afterward. This correction happened during development before a Rote recording; do not describe it as a recorded Rote trace.

No token-saving percentage or adoption count has been measured. Cloud CI is configured but has not yet run on GitHub. No hosted website or published Community Play is claimed by this document.

## Rote integration status

Installed Rote 0.80.0 using the official Playoffs kit (Play release v0.4.94). The Linux container needed GNU tar's `--no-same-owner` option during installer extraction. CLI help for `proc run`, `init`, and `workspace export` was inspected. The actual command `rote init shaktisafe-brief --seq` returned exit 77: `rote requires login`. No authenticated recording, export, lint, or Community publication has occurred. Complete the user's Rote sign-in before continuing; a connected GitHub app does not supply this authentication.
