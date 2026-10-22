# Data provenance

## 1. Live observations: CPCB via data.gov.in (`/live/*`)

| Field | Value |
|---|---|
| Publisher | Central Pollution Control Board (CPCB), Ministry of Environment, Forest and Climate Change |
| Platform | Open Government Data Platform India, data.gov.in |
| Dataset | Real time Air Quality Index from various locations |
| Resource ID | `3b01bcb8-0b14-4abf-b6f2-c1bfd384ba69` |
| Licence | Government Open Data Licence - India (GODL) |
| Refresh | Hourly, from CPCB's CAAQMS station network |
| Grain | One row per station per pollutant: 24-hour min / max / avg, last update time (IST) |

**AQI method.** `app/services/cpcb_aqi.py` implements the CPCB National Air Quality Index
breakpoint tables (CUPS/82/2014-15) with linear interpolation and the CPCB aggregation rule
(overall AQI = maximum sub-index, reported only with at least 3 pollutants including PM10 or PM2.5).

**Value interpretation.** The feed's per-pollutant values are treated as CPCB pollutant index
values by default (`CPCB_FEED_VALUES=sub_index`), so station AQI is the maximum of them. Set
`CPCB_FEED_VALUES=concentration` to treat them as concentrations and convert through the
breakpoints instead. Check the data.gov.in resource page for the current data dictionary.

**Assumption.** CPCB defines no upper concentration for the "Severe" band. For interpolation in
the 401-500 range the engine uses nominal upper bounds (PM2.5 380, PM10 600, NO2 500, O3 1000,
CO 50 mg/m3, SO2 2100, NH3 2400, Pb 4.0) and caps the result at 500.

Live readings are provisional, real-time data as published by CPCB and are not QA/QC-validated.

## 2. Synthetic development dataset (`/data/*`, ML training)

The included 320,000-record development dataset is synthetic. It must not be represented as
official CPCB/PRANA/OpenAQ observations. It is used for the forecasting and ML demonstration
modules only. Production ingestion must retain source provenance and licensing information.
