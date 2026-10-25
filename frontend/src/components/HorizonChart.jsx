import {
    Bar, BarChart, CartesianGrid, Legend,
    ResponsiveContainer, Tooltip, XAxis, YAxis,
} from "recharts";

const MIN_SAMPLES = 200; // hide bins too small to be reliable

export default function HorizonChart({ data }) {
    const rows = data
        .filter((d) => d.n >= MIN_SAMPLES)
        .map((d) => ({ ...d, label: `${d.horizon_from_h}-${d.horizon_to_h}h` }));

    return (
        <div style={{ width: "100%", height: 320 }}>
            <ResponsiveContainer>
                <BarChart data={rows} margin={{ top: 10, right: 20, left: 10, bottom: 10 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="label" label={{ value: "How far ahead the forecast was made", position: "insideBottom", offset: -5 }} />
                    <YAxis unit=" MW" width={90} />
                    <Tooltip formatter={(v) => `${Math.round(v).toLocaleString("en-GB")} MW`} />
                    <Legend verticalAlign="top" />
                    <Bar dataKey="mae_mw" name="MAE" fill="#2563eb" />
                    <Bar dataKey="bias_mw" name="Bias" fill="#f59e0b" />
                </BarChart>
            </ResponsiveContainer>
        </div>
    );
}