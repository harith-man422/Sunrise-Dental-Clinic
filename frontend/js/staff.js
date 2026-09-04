/**
 * Sunrise Dental Clinic — Staff Management logic.
 */

/* ── Load all staff members ────────────────────────────────────── */
async function loadStaffList() {
    const { ok, data } = await api("/staff");

    if (!ok) {
        showAlert(
            document.getElementById("staff-alert"),
            data.error || "Failed to load staff list.",
            "error"
        );
        return;
    }

    renderStaffTable(data);
}

/* ── Render staff table ────────────────────────────────────────── */
function renderStaffTable(staffList) {
    const tbody = document.querySelector("#staff-table tbody");
    tbody.innerHTML = "";

    if (staffList.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;">No staff members found.</td></tr>';
        return;
    }

    for (const staff of staffList) {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${staff.id}</td>
            <td>${staff.username}</td>
            <td>${staff.password}</td>
            <td><span class="badge ${staff.role === 'admin' ? 'badge-admin' : 'badge-staff'}">${staff.role}</span></td>
            <td>${staff.created_at ? new Date(staff.created_at).toLocaleDateString() : "N/A"}</td>
            <td>
                <button class="btn-small btn-accent" onclick="openEditModal(${staff.id}, '${staff.username}', '${staff.password}')">✏️ Edit</button>
                <button class="btn-small btn-danger" onclick="confirmDelete(${staff.id}, '${staff.username}')">🗑️ Delete</button>
            </td>
        `;
        tbody.appendChild(row);
    }
}

/* ── Add new staff ──────────────────────────────────────────────── */
async function handleAddStaff(e) {
    e.preventDefault();
    const alertBox = document.getElementById("staff-alert");
    alertBox.style.display = "none";

    const username = document.getElementById("new-username").value.trim();
    const password = document.getElementById("new-password").value;
    const role = document.getElementById("new-role").value;

    if (!username || !password) {
        showAlert(alertBox, "Username and password are required.", "error");
        return;
    }

    const { ok, data } = await api("/staff", {
        method: "POST",
        body: { username, password, role },
    });

    if (ok) {
        showAlert(alertBox, "Staff member added successfully!", "success");
        document.getElementById("add-staff-form").reset();
        loadStaffList();
    } else {
        showAlert(alertBox, data.error || "Failed to add staff member.", "error");
    }
}

/* ── Edit staff modal ───────────────────────────────────────────── */
function openEditModal(id, username, currentPassword) {
    const modal = document.getElementById("edit-modal");
    document.getElementById("edit-staff-id").value = id;
    document.getElementById("edit-username").value = username;
    document.getElementById("edit-password").value = currentPassword;
    modal.style.display = "flex";
}

function closeEditModal() {
    document.getElementById("edit-modal").style.display = "none";
    document.getElementById("edit-staff-form").reset();
}

async function handleEditStaff(e) {
    e.preventDefault();
    const staffId = document.getElementById("edit-staff-id").value;
    const username = document.getElementById("edit-username").value.trim();
    const password = document.getElementById("edit-password").value;

    const { ok, data } = await api(`/staff/${staffId}`, {
        method: "PUT",
        body: { username, password },
    });

    if (ok) {
        showAlert(
            document.getElementById("staff-alert"),
            "Staff member updated successfully!",
            "success"
        );
        closeEditModal();
        loadStaffList();
    } else {
        showAlert(
            document.getElementById("edit-alert"),
            data.error || "Failed to update staff member.",
            "error"
        );
    }
}

/* ── Delete staff ───────────────────────────────────────────────── */
async function confirmDelete(id, username) {
    if (!confirm(`Are you sure you want to delete staff member "${username}"?`)) {
        return;
    }

    const { ok, data } = await api(`/staff/${id}`, {
        method: "DELETE",
    });

    if (ok) {
        showAlert(
            document.getElementById("staff-alert"),
            "Staff member deleted successfully!",
            "success"
        );
        loadStaffList();
    } else {
        showAlert(
            document.getElementById("staff-alert"),
            data.error || "Failed to delete staff member.",
            "error"
        );
    }
}
