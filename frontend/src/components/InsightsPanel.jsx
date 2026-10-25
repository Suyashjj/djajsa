const fmt = (v) => Math.round(v).toLocaleString("en-GB");

export default function InsightsPanel({ overall, byDay, horizon }) {
    if (!overall || !byDay?.length) return null;

    const daysOver = byDay.filter((d) => d.bias_mw > 0).length;
    const worst = byDay.reduce((a, b) => (b.mae_mw > a.mae_mw ? b : a));
    const bins = (horizon ?? []).filter((d) => d.n >= 200);
    const first = bins[0];
    const last = bins[bins.length - 1];

    return (
        <section className="insights">
            <h2>Key findings</h2>
            <ul>
                <li>
                    Forecasts were <b>too high on {daysOver} of {byDay.length} days</b> (average{" "}
                    {overall.bias_mw > 0 ? "+" : ""}{fmt(overall.bias_mw)} MW), so expect to need more
                    backup power than the forecast implies.
                </li>
                <li>
                    In 9 out of 10 hours, the miss was below <b>{fmt(overall.p90_abs_error_mw)} MW</b>, a useful
                    buffer when sizing purchases.
                </li>
                <li>
                    Largest errors came on <b>{Number(worst.date.slice(8))} Jan</b> (average miss{" "}
                    {fmt(worst.mae_mw)} MW).
                </li>
                {first && last && (
                    <li>
                        Fresher forecasts are better: forecasts made {first.horizon_from_h}-{first.horizon_to_h} h
                        ahead missed by {fmt(first.mae_mw)} MW on average, versus {fmt(last.mae_mw)} MW for
                        those made {last.horizon_from_h}-{last.horizon_to_h} h ahead.
                    </li>
                )}
            </ul>
        </section>
    );
}