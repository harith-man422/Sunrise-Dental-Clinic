/**
 * Sunrise Dental Clinic — Appointments management logic.
 */

/* ── Load appointments ─────────────────────────────────────────── */
async function loadAppointments() {
    const { ok: ok1, data: activeAppts } = await api("/appointments/list/active");
    const { ok: ok2, data: historyAppts } = await api("/appointments/list/history");

    if (ok1) renderActiveAppointments(activeAppts);
    if (ok2) renderAppointmentHistory(historyAppts);
}

/* ── Render active appointments ────────────────────────────────── */
function renderActiveAppointments(appointments) {
    const tbody = document.querySelector("#active-appt-table tbody");
    tbody.innerHTML = "";

    if (appointments.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align:center; padding:1.5rem;">No active appointments</td></tr>';
        return;
    }

    for (const appt of appointments) {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td><strong>${appt.appointment_no}</strong></td>
            <td>${appt.patient_name}</td>
            <td>${appt.appointment_date}</td>
            <td>${appt.appointment_time}</td>
            <td>${appt.dentist_name}</td>
            <td>${appt.treatment_type}</td>
            <td>
                <button class="btn-small btn-primary" onclick="viewAppointmentDetails('${appt.appointment_no}')">👁️ View</button>
            </td>
        `;
        tbody.appendChild(row);
    }
}

/* ── Render appointment history ────────────────────────────────– */
function renderAppointmentHistory(appointments) {
    const tbody = document.querySelector("#history-appt-table tbody");
    tbody.innerHTML = "";

    if (appointments.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align:center; padding:1.5rem;">No appointment history yet</td></tr>';
        return;
    }

    for (const appt of appointments) {
        const billedDate = appt.billed_at ? new Date(appt.billed_at).toLocaleDateString() : "N/A";
        const row = document.createElement("tr");
        row.innerHTML = `
            <td><strong>${appt.appointment_no}</strong></td>
            <td>${appt.patient_name}</td>
            <td>${appt.appointment_date}</td>
            <td>${appt.dentist_name}</td>
            <td>${appt.treatment_type}</td>
            <td>${billedDate}</td>
            <td>
                <button class="btn-small btn-accent" onclick="viewAppointmentDetails('${appt.appointment_no}')">👁️ View</button>
            </td>
        `;
        tbody.appendChild(row);
    }
}

/* ── View appointment details modal ────────────────────────────– */
async function viewAppointmentDetails(appointmentNo) {
    const { ok, data } = await api(`/appointments/${appointmentNo}`);

    if (!ok) {
        alert("Could not load appointment details.");
        return;
    }

    const modal = document.getElementById("appt-details-modal");
    const content = document.getElementById("appt-details-content");

    const billedDate = data.billed_at ? new Date(data.billed_at).toLocaleDateString() : "Not billed";
    const status = data.is_billed ? "✅ Billed" : "⏳ Active";

    content.innerHTML = `
        <div style="margin-bottom:1rem;">
            <p><strong>Appointment No:</strong> ${data.appointment_no}</p>
            <p><strong>Status:</strong> ${status}</p>
            <p><strong>Patient Name:</strong> ${data.patient_name}</p>
            <p><strong>Address:</strong> ${data.address}</p>
            <p><strong>Contact:</strong> ${data.contact_number}</p>
        </div>
        <hr style="margin:1rem 0; border:none; border-top:1px solid #e2e8f0;">
        <div>
            <p><strong>Dentist:</strong> ${data.dentist_name}</p>
            <p><strong>Treatment:</strong> ${data.treatment_type}</p>
            <p><strong>Date:</strong> ${data.appointment_date}</p>
            <p><strong>Time:</strong> ${data.appointment_time}</p>
            ${data.billed_at ? `<p><strong>Billed On:</strong> ${billedDate}</p>` : ""}
        </div>
    `;

    modal.style.display = "flex";
}

function closeApptModal() {
    document.getElementById("appt-details-modal").style.display = "none";
}

/* ── Search appointment ────────────────────────────────────────── */
async function handleSearch(e) {
    e.preventDefault();
    const alertBox = document.getElementById("appt-alert");
    const resultDiv = document.getElementById("search-result");
    alertBox.style.display = "none";
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
        showAlert(alertBox, data.error || "Appointment not found.", "error");
    }
}

function renderSearchResult(appt, container) {
    const rows = [
        ["Appointment No", appt.appointment_no],
        ["Patient Name", appt.patient_name],
        ["Address", appt.address],
        ["Contact Number", appt.contact_number],
        ["Dentist", appt.dentist_name],
        ["Treatment", appt.treatment_type],
        ["Date", appt.appointment_date],
        ["Time", appt.appointment_time],
    ];

    let html = '<table class="detail-table">';
    for (const [label, val] of rows) {
        html += `<tr><th>${label}</th><td>${val}</td></tr>`;
    }
    html += "</table>";

    container.innerHTML = html;
    container.style.display = "block";
}
