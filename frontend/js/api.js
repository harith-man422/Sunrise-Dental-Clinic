/**
 * Sunrise Dental Clinic — API wrapper (fetch helper).
 *
 * Every backend call goes through api().  It attaches
 * credentials (cookies) automatically so Flask sessions work.
 */

const API_BASE = window.location.origin.startsWith("http")
    ? `${window.location.origin}/api`
    : "http://localhost:5000/api";

console.log("API_BASE configured as:", API_BASE);

/**
 * Make a JSON request to the backend.
 *
 * @param {string}  endpoint  e.g. "/login"
 * @param {object}  options   {method, body} — body is auto-serialised
 * @returns {Promise<{ok: boolean, status: number, data: object}>}
 */
async function api(endpoint, { method = "GET", body = null } = {}) {
    const opts = {
        method,
        headers: { "Content-Type": "application/json" },
        credentials: "include",          // send session cookie
    };

    if (body) {
        opts.body = JSON.stringify(body);
    }

    try {
        const res  = await fetch(`${API_BASE}${endpoint}`, opts);

        // Check if response is actually JSON
        const contentType = res.headers.get("content-type");
        if (!contentType || !contentType.includes("application/json")) {
            const text = await res.text();
            console.error("Non-JSON response:", text.substring(0, 200));
            return {
                ok: false,
                status: res.status,
                data: { error: `Server returned non-JSON response (status ${res.status})` },
            };
        }

        const data = await res.json();
        return { ok: res.ok, status: res.status, data };
    } catch (err) {
        console.error("API Error:", err, "Endpoint:", `${API_BASE}${endpoint}`);
        return {
            ok: false,
            status: 0,
            data: { error: `Network error — is the backend running? (${err.message})` },
        };
    }
}
