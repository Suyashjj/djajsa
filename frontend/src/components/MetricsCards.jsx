const num = (v, digits = 0) =>
    v == null ? "–" : v.toLocaleString("en-GB", { maximumFractionDigits: digits });

const signed = (v) => (v == null ? "–" : `${v > 0 ? "+" : ""}${num(v)}`);

export default function MetricsCards({ title, metrics }) {
    const items = [
        { label: "MAE", value: num(metrics?.mae_mw), unit: "MW", hint: "Average miss" },
        { label: "RMSE", value: num(metrics?.rmse_mw), unit: "MW", hint: "Penalises big misses" },
        { label: "Bias", value: signed(metrics?.bias_mw), unit: "MW", hint: "+ = forecast too high" },
        { label: "MAPE", value: num(metrics?.mape_pct, 1), unit: "%", hint: "Miss as % of actual" },
        { label: "P90 error", value: num(metrics?.p90_abs_error_mw), unit: "MW", hint: "9 in 10 hours below" },
    ];

    return (
        <section>
            <h2>{title}</h2>
            <div className="cards">
                {items.map((i) => (
                    <div className="card" key={i.label}>
                        <div className="card-label">{i.label}</div>
                        <div className="card-value">
                            {i.value} <span className="card-unit">{i.unit}</span>
                        </div>
                        <div className="card-hint">{i.hint}</div>
                    </div>
                ))}
            </div>
        </section>
    );
}