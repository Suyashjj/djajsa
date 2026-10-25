const BASE_URL = import.meta.env.VITE_API_URL;

async function get(path, params = {}) {
    const query = new URLSearchParams(params).toString();
    const res = await fetch(`${BASE_URL}${path}${query ? `?${query}` : ""}`);
    if (!res.ok) throw new Error(`API error ${res.status}`);
    return res.json();
}

export const getMetrics = (params) => get("/api/metrics", params);
export const getForecast = (params) => get("/api/forecast", params);
export const getHorizonMetrics = () => get("/api/metrics/horizon");