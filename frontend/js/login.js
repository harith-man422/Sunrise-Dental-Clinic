/**
 * Sunrise Dental Clinic — Login page logic.
 */

document.addEventListener("DOMContentLoaded", () => {
    const form     = document.getElementById("login-form");
    const alertBox = document.getElementById("login-alert");

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        alertBox.style.display = "none";

        const username = document.getElementById("username").value.trim();
        const password = document.getElementById("password").value;

        if (!username || !password) {
            showAlert(alertBox, "Please enter both username and password.", "error");
            return;
        }

        const { ok, data } = await api("/login", {
            method: "POST",
            body: { username, password },
        });

        if (ok) {
            // Store a lightweight flag so the dashboard knows we're logged in
            sessionStorage.setItem("staff", JSON.stringify(data.user));
            window.location.href = "dashboard.html";
        } else {
            showAlert(alertBox, data.error || "Login failed.", "error");
        }
    });
});

/* Helper: show an alert div */
function showAlert(el, message, type) {
    el.textContent   = message;
    el.className     = `alert alert-${type}`;
    el.style.display = "block";
}
