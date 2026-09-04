/**
 * Sunrise Dental Clinic — Billing & receipt logic.
 */

/* ── Load registered appointments for billing dropdown ──────────– */
async function loadBillingAppointments() {
    const { ok, data } = await api("/appointments/list/registered");

    if (!ok) {
        document.getElementById("bill-appt-dropdown").innerHTML =
            '<option value="">Error loading appointments</option>';
        return;
    }

    const dropdown = document.getElementById("bill-appt-dropdown");
    dropdown.innerHTML = '<option value="">-- Select an appointment --</option>';

    if (data.length === 0) {
        dropdown.innerHTML = '<option value="">No registered appointments available</option>';
        return;
    }

    for (const appt of data) {
        const status = appt.is_billed ? "(Billed)" : "(Pending)";
        const option = document.createElement("option");
        option.value = appt.appointment_no;
        option.textContent = `${appt.appointment_no} - ${appt.patient_name} - ${appt.appointment_date} ${appt.appointment_time} ${status}`;
        dropdown.appendChild(option);
    }
}

/* ── Update appointment number when dropdown changes ────────────– */
function updateBillAppointmentNo() {
    const selectedValue = document.getElementById("bill-appt-dropdown").value;
    document.getElementById("bill-appt-no").value = selectedValue;
}

/* ── Handle bill generation ────────────────────────────────────– */
async function handleBill(e) {
    e.preventDefault();
    const alertBox   = document.getElementById("bill-alert");
    const receiptDiv = document.getElementById("receipt");
    alertBox.style.display   = "none";
    receiptDiv.style.display = "none";

    const apptNo = document.getElementById("bill-appt-no").value.trim();
    if (!apptNo) {
        showAlert(alertBox, "Please select an appointment from the dropdown.", "error");
        return;
    }

    const { ok, data } = await api(`/bill/${encodeURIComponent(apptNo)}`);

    if (ok) {
        renderReceipt(data, receiptDiv, apptNo);
    } else {
        showAlert(alertBox, data.error || "Could not generate bill.", "error");
    }
}

function renderReceipt(bill, container, apptNo) {
    container.innerHTML = `
        <h3>🦷 Sunrise Dental Clinic</h3>
        <p class="tagline">Your smile, our passion</p>

        <table>
            <tr><th>Patient Name</th><td>${bill.patient_name}</td></tr>
            <tr><th>Appointment No</th><td>${bill.appointment_no}</td></tr>
            <tr><th>Dentist</th><td>${bill.dentist_name}</td></tr>
            <tr><th>Date / Time</th><td>${bill.appointment_date} @ ${bill.appointment_time}</td></tr>
            <tr><th colspan="2" style="padding-top:1rem;border:none;">Cost Breakdown</th></tr>
            <tr><th>Consultation Fee</th><td>LKR ${bill.consultation_fee.toLocaleString()}</td></tr>
            <tr><th>${bill.treatment_type}</th><td>LKR ${bill.treatment_price.toLocaleString()}</td></tr>
            <tr class="total-row"><th>Total</th><td>LKR ${bill.total.toLocaleString()}</td></tr>
        </table>

        <div style="text-align:center; margin-top:1.25rem;">
            <button class="btn btn-primary" onclick="window.print()">🖨️ Print Receipt</button>
            <button class="btn btn-success" onclick="markBilledAndRefresh('${apptNo}')" style="margin-left:.5rem;">✅ Mark as Billed</button>
        </div>
    `;
    container.style.display = "block";
}

async function markBilledAndRefresh(apptNo) {
    const { ok, data } = await api(`/bill/${apptNo}/confirm`, {
        method: "POST",
    });

    if (ok) {
        showAlert(
            document.getElementById("bill-alert"),
            "Appointment marked as billed!",
            "success"
        );
        document.getElementById("receipt").style.display = "none";
        document.getElementById("bill-form").reset();
        document.getElementById("bill-appt-no").value = "";

        // Reload the dropdown
        loadBillingAppointments();

        // Refresh appointments if visible
        if (document.getElementById("section-appointments").classList.contains("active")) {
            loadAppointments();
        }
    } else {
        showAlert(
            document.getElementById("bill-alert"),
            data.error || "Failed to mark as billed.",
            "error"
        );
    }
}


