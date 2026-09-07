# ShaktiSafe Brief — What changed before I leave?

**Pitch:** A reusable Rote Play that checks weather, modeled air quality, and supported US official alerts for an outing, then tells you what changed when you check again.

## Problem, people, and repetition

Commuters, parents planning an outing, travelers, and people spending time outdoors repeatedly open separate forecasts, air-quality pages, and alert services before leaving. They must remember earlier readings, match the destination and time window, and decide whether an unavailable source is simply quiet. ShaktiSafe Brief brings those checks into one timestamped Markdown brief and compares the same outing against its last successful source results.

The repeated task is the same even when the destination changes: resolve the place and departure window, fetch three sources, check their completeness, compare earlier observations, and summarize. A refresh reuses the exact saved outing context. A new destination or time window needs a new context; it must not masquerade as a refresh.

## Five stages, one reusable workflow

1. `resolve_outing` resolves a destination or validates saved context, including its timezone and outing window.
2. `read_weather` retrieves and validates weather data.
3. `read_air` retrieves and validates modeled air-quality data.
4. `read_alerts` queries NWS for supported US locations, or explicitly reports unsupported coverage.
5. `compose_brief` compares successful sources with persistent baselines and writes JSON and Markdown reports.

Stages 2–4 run in parallel after stage 1; stage 5 depends on all three. The control flow, validation rules, and comparison logic are deterministic. Live API responses and timestamps are not fixed, so identical requests at different times need not produce identical reports. Ambiguous places require a specific location choice rather than an arbitrary selection.

Rote provides reusable parameters, an inspectable execution plan, dependency ordering, replay, checkpoints, and visible failed or blocked steps. Recorded recovery restored four completed stages and reran only the failed composition stage. Reusing this structure reduces the need for an agent to reason through the same orchestration on every request. Baseline comparison is implemented in the Python workflow, not inferred by a language model.

## Coverage and public benefit

Worldwide destination lookup, timezone handling, weather, and modeled air-quality queries make the workflow relevant beyond one city, subject to provider coverage and availability. Chennai, London, and Houston were exercised. Air quality is modeled—not street-level measurement or a guarantee of personal exposure. Official alerts currently use NWS for supported US locations; non-US official alerts are unsupported. Missing alerts, a failed request, an unsupported region, or an empty response never mean “all clear.”

A common person gets a short, repeatable pre-departure check with explicit uncertainty and change information. The Play is environmental preparedness support, not medical advice, an emergency service, a route-safety assessment, or permission to travel. Follow local authorities and official warning channels. No user study, adoption count, or measured health benefit is claimed.

## Validation and publication evidence

These are historical execution results, not current travel conditions. The September 6 [development validation](../rote/shaktisafe-brief/VALIDATION.md) and [handoff](../rote/shaktisafe-brief/ROTE_HANDOFF.md) describe an earlier, pre-publication state. The September 7 publication verification below supersedes their publication-status statements.

| Evidence | Observed result |
|---|---|
| Existing Python tests | 12 tests passed; timezone/DST, ambiguity, units, missing data, alert intervals, baseline isolation and failure behavior covered. |
| Real staged execution | Houston weather, air and NWS requests succeeded; Chennai and London explicitly reported unsupported official alerts. No newly issued live warning was demonstrated. |
| Same-outing refresh | Saved context reused; comparison completed. No compared-field changes was a valid observed result. |
| Synthetic demonstrations | Baseline, changed readings, and source timeout generated explicitly labeled reports; not live observations. |
| Rote failure/recovery | Missing context blocked dependent stages; a composition failure resumed with four stages restored; network failure retained labeled stale source data. |
| Revised package checks | Lint and validation passed; 15/15 blocked, partial and truncated presentation cases passed. |
| Discovery | Request “Check what changed in weather, air quality, and alerts before I leave” returned `discoverable_by_request=true`. |
| Publication verification, September 7, 2026 | Exact pinned version inspected, downloaded into a clean directory, identity checked, and executed successfully; exact registry-reference execution also completed all five stages. Execution was verified as the publishing account. |

Selected recorded run identifiers: Houston `run_20260907_023017.127_5`; refresh `run_20260907_023403.875_15`; resumed composition `run_20260907_023534.054_25`; degraded network `run_20260907_023543.757_26`; missing context `run_20260907_023619.025_31`; clean downloaded execution `run_20260907_031023.930_0`. These identify author-observed evidence; they are not public CI links.

Published archive SHA-256: `cfbd685844fb447e13a90d240925282e2ec0b6e9b4db7605ff89daa63ebc75cc` (41 entries). Revised verified Play birth: `e013d57d9b9a0b798f3af3faaedef88c977c0b235345228cbca626b248c5e467`. The birth was recaptured for the revised artifact rather than reusing the pre-correction birth.

**Token efficiency:** the birth certificate reported a runtime-generated token-savings estimate of 15,073. This is not an independently measured result or a controlled before/after benchmark. No token-saving percentage, latency improvement, or cost reduction has been independently measured. The demonstrated advantage is reuse of execution structure and completed checkpoints.

## Privacy, runtime effects, and safety

Python 3.11+ is required. The Python process makes HTTPS requests to `geocoding-api.open-meteo.com`, `api.open-meteo.com`, `air-quality-api.open-meteo.com`, and, for supported US alerts, `api.weather.gov`. Destination search text is sent to geocoding; resolved destination coordinates are shared with the applicable weather, air-quality and alert providers. These are external services, not private on-device computation.

The workflow writes outing context, source results, JSON and Markdown output, and persistent baseline files to the selected directories. Location and outing information can remain in those files and execution records. There is no automatic retention deletion: users must manage and remove retained data themselves. Use separate output directories for concurrent invocations and protect baselines from unintended sharing.

The public archive includes required `resources/USAGE.md`, and the description/presentation disclose effects. The generic inspection card may say no services or writes because it does not expose effects inside the Python process; that is not evidence of zero network or filesystem effects.

Execution is subject to Rote's process-execution policy. Authoring guidance restricted personal-handle process execution to the owner, while the publication receipt described broader public execution. Only the publishing account was tested; cross-account execution is unverified. Public discoverability does not guarantee execution permission. Inspect current eligibility and respect any policy restriction; do not bypass it.

Sources: Open-Meteo geocoding, weather and modeled air-quality services; NWS official alert API for supported US locations. Reports retain source status and timestamps. Failed sources can show **STALE** last-successful data, never silently replace it with a current reading. Synthetic examples must remain labeled.

## Links

- [Published Community Play — pinned 0.1.0](https://play.modiqo.ai/harshapriyag123/shaktisafe-brief@0.1.0)
- [GitHub source](https://github.com/harshapriyag123/shakti360-guardian/tree/main/rote/shaktisafe-brief)
- [Demo script](DEMO_SCRIPT.md) · [Judging evidence](JUDGING.md) · [Recording checklist](DEMO_CHECKLIST.md)

This submission documents the published 0.1.0 artifact. It does not update or republish the Play or change the production Shakti360 application.
