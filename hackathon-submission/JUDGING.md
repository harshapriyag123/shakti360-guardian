# Judging evidence

Evidence is author-observed unless specified. Historical runs do not describe current conditions. See [submission provenance and identifiers](SUBMISSION.md#validation-and-publication-evidence).

| Criterion | Supported claim | Evidence | Boundary |
|---|---|---|---|
| Usefulness | Combines outing-specific environmental checks and refresh differences. | Houston, Chennai and London executions produced briefs; same-context refresh compared baselines. | No user-impact study or medical benefit claimed. |
| Repeatability | Saved context preserves the destination and outing window. | Real refresh; baseline isolation unit test. | New outings require new context; live readings can change. |
| Determinism | Fixed five-stage DAG and explicit parsing/comparison rules. | Resolve → three source stages → compose; timezone, unit and interval tests. | Deterministic logic does not imply identical external data. |
| Usability | Markdown reports expose timestamps, changes and source status. | First-run, refresh and labeled synthetic reports. | No formal usability testing; CLI setup and eligibility remain prerequisites. |
| Token efficiency | Workflow and checkpoint reuse reduce repeated orchestration reasoning. | Recorded resume restored four completed stages. | Runtime estimate of 15,073 tokens is not an independently measured saving or percentage. |
| Inspectability | Pinned package can be inspected and its dependency plan reviewed. | Registry inspection, archive identity verification, required `resources/USAGE.md`. | Generic inspection omits Python-internal service/write effects; read the disclosure. |
| Failure recovery | Missing context blocks dependents; failed source data can retain labeled stale values; checkpoints support resume. | Missing-context run, restricted-network run, composition resume, 15/15 presentation cases. | Stale data is not current; synthetic timeout demonstration is labeled separately. |
| Security/privacy | Runtime effects and provider disclosure are explicit. | Required usage resource and public description; source review. | Coordinates leave the device; reports/baselines persist without automatic deletion. Not a security audit or private computation guarantee. |
| Global relevance | Multiple countries, destination timezones and worldwide weather/air queries. | Houston, Chennai, London; timezone/DST tests. | Provider availability varies; modeled air is not street-level; official alerts use NWS for supported US locations only. |

Existing Python suite: 12 tests passed in development and is rerun for this documentation package. Revised published package: lint and validation passed; request discovery returned `discoverable_by_request=true`; clean downloaded and pinned-reference runs completed all five stages as the publishing account. No cross-account execution guarantee is made because process execution remains subject to Rote policy.

No claim of worldwide official alerts, medical advice, independently measured token savings, or active live-warning delivery is made. An empty, unsupported or failed alert result never means “all clear.”
