/**
 * Sunrise Dental Clinic — Appointment registration & search logic.
 */

/* ── Register appointment ──────────────────────────────────────── */
async function handleRegister(e) {
    e.preventDefault();
    const alertBox = document.getElementById("reg-alert");
    alertBox.style.display = "none";

    const fields = [
        "appointment_no", "patient_name", "address", "contact_number",
        "dentist_name", "treatment_type", "appointment_date", "appointment_time",
    ];
    const body = {};
    for (const f of fields) {
        body[f] = document.getElementById(`reg-${f}`).value.trim();
    }

    const { ok, data } = await api("/appointments", {
        method: "POST",
        body,
    });

    if (ok) {
        showAlert(alertBox, "Appointment registered successfully!", "success");
        e.target.reset();
    } else {
        showAlert(alertBox, data.error || "Registration failed.", "error");
    }
}

/* ── Search appointment ────────────────────────────────────────── */
async function handleSearch(e) {
    e.preventDefault();
    const alertBox  = document.getElementById("search-alert");
    const resultDiv = document.getElementById("search-result");
    alertBox.style.display  = "none";
    resultDiv.style.display = "none";

    const apptNo = document.getElementById("search-appt-no").value.trim();
    if (!apptNo) {
        showAlert(alertBox, "Please enter an appointment number.", "error");
        return;
    }

    const { ok, data } = await api(`/appointments/${encodeURIComponent(apptNo)}`);

    if (ok) {
        renderSearchResult(data, resultDiv);
    } else {
        showAlert(alertBox, data.error || "Not found.", "error");
    }
}

function renderSearchResult(appt, container) {
    const rows = [
        ["Appointment No",  appt.appointment_no],
        ["Patient Name",    appt.patient_name],
        ["Address",         appt.address],
        ["Contact Number",  appt.contact_number],
        ["Dentist",         appt.dentist_name],
        ["Treatment",       appt.treatment_type],
        ["Date",            appt.appointment_date],
        ["Time",            appt.appointment_time],
    ];

    let html = '<table class="detail-table">';
    for (const [label, val] of rows) {
        html += `<tr><th>${label}</th><td>${val}</td></tr>`;
    }
    html += "</table>";

    container.innerHTML     = html;
    container.style.display = "block";
}
