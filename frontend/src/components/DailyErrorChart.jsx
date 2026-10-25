import {
    Bar, CartesianGrid, ComposedChart, Legend, Line,
    ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from "recharts";

export default function DailyErrorChart({ data }) {
    const rows = data.map((d) => ({ ...d, day: d.date.slice(8) })); // "2026-01-10" -> "10"

    return (
        <div style={{ width: "100%", height: 320 }}>
            <ResponsiveContainer>
                <ComposedChart data={rows} margin={{ top: 10, right: 20, left: 10, bottom: 10 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="day" label={{ value: "Day of January", position: "insideBottom", offset: -5 }} />
                    <YAxis unit=" MW" width={90} />
                    <Tooltip formatter={(v) => `${Math.round(v).toLocaleString("en-GB")} MW`} />
                    <Legend verticalAlign="top" />
                    <ReferenceLine y={0} stroke="#64748b" />
                    <Bar dataKey="bias_mw" name="Bias (+ = forecast too high)" fill="#f59e0b" />
                    <Line type="monotone" dataKey="mae_mw" name="MAE" stroke="#2563eb" strokeWidth={2} dot={false} />
                </ComposedChart>
            </ResponsiveContainer>
        </div>
    );
}