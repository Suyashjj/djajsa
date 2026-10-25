import {
    CartesianGrid, Legend, Line, LineChart,
    ResponsiveContainer, Tooltip, XAxis, YAxis,
} from "recharts";

export default function ForecastChart({ data }) {
    // startTime is UTC, which equals UK time in January
    const rows = data.map((d) => ({ ...d, time: d.startTime.slice(11, 16) }));

    return (
        <div style={{ width: "100%", height: 360 }}>
            <ResponsiveContainer>
                <LineChart data={rows} margin={{ top: 10, right: 20, left: 10, bottom: 10 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="time" />
                    <YAxis unit=" MW" width={90} />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="forecast_mw" name="Forecast (known at decision time)"
                        stroke="#2563eb" strokeWidth={2} dot={false} />
                    <Line type="monotone" dataKey="actual_mw" name="Actual"
                        stroke="#16a34a" strokeWidth={2} dot={false} />
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
}