const CUTOFFS = ["06:00", "09:00", "10:00", "12:00"];

export default function Controls({ date, cutoff, onDateChange, onCutoffChange }) {
    return (
        <div className="controls">
            <label>
                Delivery date
                <input
                    type="date"
                    value={date}
                    min="2026-01-01"
                    max="2026-01-31"
                    onChange={(e) => e.target.value && onDateChange(e.target.value)}
                />
            </label>
            <label>
                Decision time (day before, UK)
                <select value={cutoff} onChange={(e) => onCutoffChange(e.target.value)}>
                    {CUTOFFS.map((c) => (
                        <option key={c} value={c}>{c}</option>
                    ))}
                </select>
            </label>
        </div>
    );
}