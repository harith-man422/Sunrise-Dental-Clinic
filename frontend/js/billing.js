/**
 * Sunrise Dental Clinic — Billing & receipt logic.
 */

async function handleBill(e) {
    e.preventDefault();
    const alertBox   = document.getElementById("bill-alert");
    const receiptDiv = document.getElementById("receipt");
    alertBox.style.display   = "none";
    receiptDiv.style.display = "none";

    const apptNo = document.getElementById("bill-appt-no").value.trim();
    if (!apptNo) {
        showAlert(alertBox, "Please enter an appointment number.", "error");
        return;
    }

    const { ok, data } = await api(`/bill/${encodeURIComponent(apptNo)}`);

    if (ok) {
        renderReceipt(data, receiptDiv);
    } else {
        showAlert(alertBox, data.error || "Could not generate bill.", "error");
    }
}

function renderReceipt(bill, container) {
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
        </div>
    `;
    container.style.display = "block";
}
