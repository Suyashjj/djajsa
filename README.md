# UK Wind Forecast Accuracy Dashboard

A web app that shows a UK electricity trader **which wind forecast they actually had at decision time**, and **how accurate that forecast turned out to be**.

- **Live app:** https://djajsa-4zxn.vercel.app
- **Live API docs:** https://djajsa.vercel.app/docs
- **Demo video:** _add your unlisted YouTube link here_

> **Note:** the first request after a quiet period can take a few seconds (serverless cold start). Refresh once if the page looks empty.

---

## 1. What problem does this solve?

A UK electricity company buys power **one day ahead** (the "day-ahead market"). Wind is cheap but depends on the weather, so the company relies on **wind forecasts** to decide how much extra power (e.g. gas) to buy.

Forecasts are updated many times. So the real question is:

1. **What was the latest forecast available at the moment of decision?** (not a later one, that would be cheating)
2. **How wrong was it?** (so the trader knows how much safety margin to keep)

This app answers both for **January 2026**.

## 2. Data used

Both datasets come from the free public **Elexon BMRS** API (no API key needed), wind only, UK national level.

| Dataset | What it is | Key fields |
|---|---|---|
| `FUELHH` | **Actual** wind generation, every 30 minutes | `startTime`, `generation` |
| `WINDFOR` | **Forecast** wind generation, hourly | `startTime` (time being forecast), `publishTime` (when the forecast was made), `generation` |

## 3. Key assumptions (please read)

- **Decision time:** to buy power for delivery day **D**, the trader decides on **D-1 at 09:00 UK time**. This is an assumption, so the app lets you change it (06:00, 09:00, 10:00, 12:00).
- **Forecast selection rule:** for each target hour, we use the forecast with the **latest `publishTime` at or before the decision time**. Forecasts published after that are ignored.
- **Resolution mismatch:** forecasts are hourly, actuals are 30-minute. Each hour's actual is the **average of its two half-hours** (incomplete hours are dropped).
- **Error sign:** `error = forecast - actual`. A **positive bias means the forecast was too high**.
- **Time zones:** everything is handled in UTC. UK time equals UTC in January, so no daylight-saving issues.
- **Data window:** forecasts published 30 Dec 2025 to 31 Jan 2026, actuals 1 Jan to 1 Feb 2026.

## 4. What the data showed (January 2026, 09:00 decision time)

| Metric | Value | Meaning |
|---|---|---|
| MAE | 2,142 MW | Average miss per hour |
| RMSE | 2,612 MW | Like MAE but punishes big misses |
| Bias | +1,852 MW | Forecasts were higher than actuals on average |
| MAPE | 22.4 % | Average miss as a % of actual |
| P90 abs error | 4,300 MW | In 9 of 10 hours the miss was below this |

- Forecasts were **too high on 27 of 31 days**. The size of the miss varies a lot from day to day, the worst day being 28 Jan.
- **Fresher forecasts are better:** forecasts made 0-6 hours ahead missed by about 1,771 MW on average, versus about 2,412 MW for those made 60-66 hours ahead.
- The persistent over-forecast is an **observation**, not a proven cause. `WINDFOR` and `FUELHH` may not measure exactly the same thing.

## 5. Tech stack

| Part | Technology |
|---|---|
| Backend | Python 3.12, FastAPI, pandas, requests |
| Frontend | React (Vite), Recharts |
| Tests | pytest |
| Containers | Docker, docker-compose (nginx serves the built frontend) |
| Hosting | Vercel (two projects: backend and frontend) |

## 6. Project structure

```
wind_project/
├── backend/
│   ├── app/
│   │   ├── main.py            # creates the FastAPI app, CORS setup
│   │   ├── routes.py          # API endpoints
│   │   ├── elexon_client.py   # talks to the Elexon API
│   │   ├── processing.py      # loading data + "latest forecast before cutoff" logic
│   │   ├── metrics.py         # MAE, RMSE, bias, MAPE, P90, by day, by horizon
│   │   └── data_store.py      # loads CSVs once and keeps them in memory
│   ├── data/                  # actuals.csv and forecasts.csv (downloaded from Elexon)
│   ├── scripts/
│   │   └── fetch_data.py      # downloads the January data from Elexon
│   ├── tests/                 # pytest tests for the selection logic and metrics
│   ├── index.py               # entrypoint used by Vercel
│   ├── pytest.ini
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .dockerignore
├── frontend/
│   ├── src/
│   │   ├── api/client.js      # all backend calls in one place
│   │   ├── components/        # Controls, MetricsCards, ForecastChart,
│   │   │                      # DailyErrorChart, HorizonChart, InsightsPanel
│   │   ├── App.jsx            # page layout and data loading
│   │   └── index.css
│   ├── package.json
│   ├── Dockerfile
│   └── .dockerignore
├── docker-compose.yml
├── .gitignore
└── README.md
```

## 7. API endpoints

| Endpoint | What it returns |
|---|---|
| `GET /health` | `{"status": "ok"}` |
| `GET /api/forecast?date=2026-01-10&cutoff=09:00` | Hourly forecast the trader would have seen for that day, plus actuals and error |
| `GET /api/metrics?start=2026-01-01&end=2026-01-31&cutoff=09:00` | Overall metrics and per-day metrics |
| `GET /api/metrics/horizon` | Accuracy vs how far ahead the forecast was made |

Interactive docs (Swagger) are at `/docs` on the backend.

---

## 8. Run it locally

You need Python 3.12, Node 22 (or newer) and, for the Docker option, Docker Desktop.

### Option A: run backend and frontend directly

**Backend** (Terminal 1):

```bash
cd backend
python -m venv venv
venv\Scripts\activate            # Windows PowerShell
# source venv/bin/activate       # macOS / Linux
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Check `http://127.0.0.1:8000/docs`.

**Frontend** (Terminal 2):

```bash
cd frontend
npm install
```

Create `frontend/.env` containing:

```
VITE_API_URL=http://127.0.0.1:8000
```

Then:

```bash
npm run dev
```

Open `http://localhost:5173`.

> Always use `python -m uvicorn` and `python -m pip` so the commands run inside your virtual environment.

### Option B: run everything with Docker

```bash
docker compose up --build
```

- App: `http://localhost:3000`
- API docs: `http://localhost:8000/docs`

Stop with `Ctrl+C`, then `docker compose down`.

### Re-download the data (optional)

The CSVs are already included. To fetch them again from Elexon:

```bash
cd backend
python scripts/fetch_data.py
```

### Run the tests

```bash
cd backend
python -m pytest
```

---

## 9. Limitations and ideas for next steps

- Only January 2026 and only UK national wind are covered.
- The 09:00 D-1 decision time is an assumption, not the official market gate closure.
- The consistent over-forecast is described, not explained. A next step would be to compare how `WINDFOR` and `FUELHH` define wind generation.
- Possible additions: a bias-corrected forecast, exporting results as CSV, and more months of data.

## 10. AI tool usage

AI tools were used while building this project: **Claude (Anthropic)** helped with planning, code generation and debugging. _Add any other AI tools you used (for example, an AI coding assistant inside your editor)._ All code was run, tested and reviewed by me before being committed.
