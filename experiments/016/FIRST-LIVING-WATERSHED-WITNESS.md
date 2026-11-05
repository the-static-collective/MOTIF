# First living-watershed witness — November 5, 2026

**Instrument:** MOTIF-016 Living Watershed. **Outcome:** `HOLD_NO_IMPROVEMENT`.

## Actual public-source read

[Successful CI run, including 10 offline tests and a real USGS/Open-Meteo read](https://github.com/the-static-collective/MOTIF/actions/runs/42030670309). [Machine-produced artifact](https://github.com/the-static-collective/MOTIF/actions/runs/42030670309/artifacts/13416371260). Source report preserved as [actual-watershed-2026-11-05.json](evidence/actual-watershed-2026-11-05.json); parallel older weather source report in [actual-weather-2026-11-05.json](evidence/actual-weather-2026-11-05.json).

- USGS modernized OGC continuous measurements: Blue Earth River `05320000`, Le Sueur River `05320500`, Minnesota River at Mankato `05325000`. River discharge values are reported in **cubic feet/second**.
- Open-Meteo historical **gridded estimated precipitation** at a separate public research coordinate; a model product, **not a physical rain sensor**.
- Time period: 2026-10-16 13:00 UTC through 2026-10-30 00:00 UTC.
- **324** matched complete hourly cases; **178 training**, **64 validation**, **82 held-out test**.
- Four declared candidates: persistence, fitted local trend, fitted cross-gauge changes, and cross-gauge plus gridded rain context.
- Selection made on validation only. All models fit on the earlier training window. No model update was made after seeing test results.

## The actual iron: the validation winner lost on unseen water data

| Retrospective method | Validation MAE (cfs) | Untouched test MAE (cfs) |
|---|---:|---:|
| Persistence of the last completed downstream hour | 37.6562 | **13.1402** |
| Fitted local trend | 21.2352 | 23.0281 |
| Fitted cross-gauge changes (**validation selection**) | **15.0201** | 20.9575 |
| Cross-gauge plus historical gridded rain | 22.7317 | 176.4602 |

**Cross-gauge test error was 7.8173 cfs greater than persistence, 59.491% worse relative to the baseline.** The supposedly more capable method was not more accurate on the later measured data.

There were **zero qualifying rising-flow test hours** under this prototype's event definition. This result therefore provides *no evidence about flood-event or rising-flow forecast skill*. Even a win under benign water conditions would not establish flood-warning performance.

The simple persistence strategy became stronger on the later period; that is a form of *time-regime shift* or changing local predictability, not proof of a single hydrologic cause. Do not infer that Blue Earth / Le Sueur aren't useful predictors in general.

## Self-diagnostic found a better question

The experiment now asks:

> Can a frozen policy beat persistence on a truly independent period containing rising flow events, without selecting on the test data, without relying on after-the-fact rainfall, and with measurements known to have been available by prediction time?

This challenge is harder than creating more route possibilities. The result explicitly calls out:
- possible telemetry/reporting-time leakage,
- correlations among gauges,
- gridded rainfall model dependence,
- hydrological event selection and seasonal shifts,
- absence of original raw provider responses in the current research archive.

**No promotion, external warning, physical action, environmental authority or inference about individual people occurred.**

## Source ledger

USGS readings were collected through the modernized OGC `continuous` API, not WaterServices due for retirement. The machine report includes the SHA-256 fingerprint of each source JSON response.

- Blue Earth: `0f0f0a7073f39b166cec480619fb1288edf7aa1b7622a9bff18bb0982d0c88a8`
- Le Sueur: `5a01ab97cdc15e9871f9e490a0531a88298b00f836f96b0f9f09c04a427c27d1`
- Mankato: `2fdff70a85b4e70d36849903971acb9ab3c1cfb2f87ca816c4d16fad051b83a1`
- Open-Meteo gridded precipitation: `d01380c262430df457a7bfc691fd842e4d78bb2957426a7516657f9ae0cdeab0`

The live run produced the report, but **raw source-response bytes were not preserved**, so these hashes are source references and do not independently establish original sensor authenticity. Git pins establish integrity of the preserved report only.

**Upstream citations:** https://api.waterdata.usgs.gov/docs/ogcapi/migration/ and https://open-meteo.com/en/docs/historical-weather-api ; retain Open-Meteo attribution and honor non-commercial hosted API terms.
