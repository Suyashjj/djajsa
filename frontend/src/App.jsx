import { useEffect, useState } from "react";
import { getForecast, getHorizonMetrics, getMetrics } from "./api/client";
import Controls from "./components/Controls";
import DailyErrorChart from "./components/DailyErrorChart";
import ForecastChart from "./components/ForecastChart";
import HorizonChart from "./components/HorizonChart";
import MetricsCards from "./components/MetricsCards";
import InsightsPanel from "./components/InsightsPanel";

export default function App() {
  const [date, setDate] = useState("2026-01-10");
  const [cutoff, setCutoff] = useState("09:00");
  const [forecast, setForecast] = useState(null);
  const [dayMetrics, setDayMetrics] = useState(null);
  const [month, setMonth] = useState(null); // { overall, by_day }
  const [horizon, setHorizon] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  // Horizon accuracy does not depend on the controls: load once
  useEffect(() => {
    getHorizonMetrics()
      .then((h) => setHorizon(h.data))
      .catch((e) => setError(e.message));
  }, []);

  useEffect(() => {
    let cancelled = false; // ignore stale responses if inputs change quickly
    setLoading(true);
    setError(null);

    Promise.all([
      getForecast({ date, cutoff }),
      getMetrics({ start: date, end: date, cutoff }),
      getMetrics({ start: "2026-01-01", end: "2026-01-31", cutoff }),
    ])
      .then(([f, day, m]) => {
        if (cancelled) return;
        setForecast(f);
        setDayMetrics(day.overall);
        setMonth(m);
      })
      .catch((e) => !cancelled && setError(e.message))
      .finally(() => !cancelled && setLoading(false));

    return () => { cancelled = true; };
  }, [date, cutoff]);

  return (
    <div className="page">
      <h1>UK Wind Forecast Accuracy</h1>
      <p className="subtitle">
        What the day-ahead desk knew at decision time, and how accurate it turned out to be.
      </p>

      <Controls date={date} cutoff={cutoff} onDateChange={setDate} onCutoffChange={setCutoff} />

      {error && <p className="error">Error: {error}</p>}
      {loading && !error && <p>Loading...</p>}

      {forecast && !error && (
        <>
          <h2>Forecast vs actual, {date}</h2>
          <ForecastChart data={forecast.data} />
          <MetricsCards title={`Accuracy on ${date}`} metrics={dayMetrics} />
          <MetricsCards title="Accuracy across January 2026" metrics={month?.overall} />
          <InsightsPanel overall={month?.overall} byDay={month?.by_day} horizon={horizon} />

          <h2>Day-by-day error (January 2026)</h2>
          <DailyErrorChart data={month?.by_day ?? []} />

          {horizon && (
            <>
              <h2>Accuracy vs forecast horizon</h2>
              <HorizonChart data={horizon} />
            </>
          )}
        </>
      )}
    </div>
  );
}