# Digital Twin MVP – Test Scenario Pack

This document captures fault-injection scripts, acceptance checks, and
observations for the FastAPI-only MVP. Each scenario uses only the bundled
services (`/`, `/twin/*`, `/chat/ask`) and the sample Excel dataset.

---

## 1. Baseline Availability

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | Start backend (`uv run --project backend backend`). | Service boots, logs indicate IDSL + simulator load. |
| 2 | Open `http://localhost:8000/`. | Dashboard renders with KPIs, telemetry table, chat welcome. |
| 3 | Hit `/health`. | JSON `{"status": "ok"}`. |

Acceptance: UI shows assets, alerts, predictive items populated from sample
workbook.

---

## 2. Cooling Flow Drop Fault

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | On dashboard, trigger “Coolant Flow Drop”. | Toast in chat bubble acknowledges trigger. |
| 2 | Observe telemetry rows. | `FLOW_COOLANT` deviates (status `warning`). |
| 3 | Check alerts panel. | New alert referencing flow drop appears. |
| 4 | Review predictive list. | Entry recommending coolant investigation with ETA ~6 hrs. |
| 5 | Ask chat “How do I mitigate the coolant issue?”. | Reply includes SOP extract & action plan. |

Acceptance: telemetry + predictive + chat align with triggered fault.

---

## 3. Reactor Temperature Spike

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | Trigger “Reactor Temperature Spike”. | Chat bubble acknowledges. |
| 2 | Watch telemetry row `TEMP_REACTOR`. | Value climbs; severity flips to `critical`. |
| 3 | Alerts panel | Highlighted alert referencing temperature spike. |
| 4 | Predictive tab | Suggestion enumerating immediate cool-down steps. |
| 5 | Chat query “Give me SOP steps for VFD faults.” | Response surfaces VFD SOP excerpt. |

Acceptance: Chat references SOP Sample and recommends approvals.

---

## 4. Compliance Acknowledgement Loop

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | Ask chat “Summarise compliance obligations for electric faults.” | Response lists approval workflow (maintenance supervisor + compliance officer). |
| 2 | Ask chat “Is there downtime planned for M001?” | Response references production schedule from sample data. |
| 3 | Capture recommended actions. | Output lists immediate and long-term plan segments. |

Acceptance: Chat integrates ERP/MES data for schedule/resourcing context.

---

## 5. Regression Checks

| Command | Purpose |
| --- | --- |
| `uv run --project backend pytest` | Loader, simulator, chat, and dashboard tests pass. |
| `uv run --project backend python -m backend.main` | Manual smoke; stop via Ctrl+C. |

Residual risk: FastAPI hooks use deprecated `on_event`; consider lifespan refactor in
subsequent iteration.|


