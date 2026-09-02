/**
 * Employee Table Component for Data-Dense List View
 */
class EmployeeTableComponent {
    static render(employees) {
        const userRole = String(App.currentUser?.role || '').toUpperCase();
        const isHR = ['ADMIN', 'HR_OFFICER'].includes(userRole);

        if (!employees || employees.length === 0) {
            return `
                <div class="empty-state">
                    <div class="empty-state-icon">
                        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle></svg>
                    </div>
                    <div class="empty-state-title">No employees found</div>
                    <div class="empty-state-text">No employee records match the current filter or search criteria.</div>
                    ${isHR ? `<button class="btn btn-primary" onclick="App.navigate('add-employee')">Add First Employee</button>` : ''}
                </div>
            `;
        }

        let rowsHtml = employees.map(emp => {
            const attStatus = (emp.status || emp.attendance_status || 'absent').toLowerCase();
            const attBadge = attStatus === 'present' ? 
                `<span class="badge badge-present"><span class="badge-dot" style="background:#10b981;"></span>Present</span>` : 
                (attStatus === 'on_leave' ? 
                    `<span class="badge badge-leave" style="color:#f97316; border-color:rgba(249,115,22,0.3); background:rgba(249,115,22,0.1);"><span class="badge-dot" style="background:#f97316;"></span>On Leave</span>` : 
                    `<span class="badge badge-absent" style="color:#eab308; border-color:rgba(234,179,8,0.3); background:rgba(234,179,8,0.1);"><span class="badge-dot" style="background:#eab308;"></span>Absent</span>`);

            const avatar = emp.avatar_url || `https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150&auto=format&fit=crop&q=80`;
            const wageStr = isHR || App.currentUser?.employee_id === emp.id ? (emp.monthly_wage ? `₹${Number(emp.monthly_wage).toLocaleString('en-IN')}` : '₹0') : 'Confidential';

            const actionButtons = isHR ? `
                <button class="btn btn-secondary btn-sm" onclick="App.navigate('profile', ${emp.id})" title="View Profile">
                    View
                </button>
                <button class="btn btn-secondary btn-sm" onclick="App.navigate('edit-employee', ${emp.id})" title="Edit Employee">
                    Edit
                </button>
                <button class="btn btn-outline-danger btn-sm" onclick="App.promptDelete(${emp.id}, '${emp.full_name.replace(/'/g, "\\'")}')" title="Deactivate / Delete">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                </button>
            ` : `
                <button class="btn btn-secondary btn-sm" onclick="App.navigate('profile', ${emp.id})" title="View Profile">
                    View Profile
                </button>
            `;

            return `
                <tr onclick="App.navigate('profile', ${emp.id})">
                    <td>
                        <div style="display:flex; align-items:center; gap:12px;">
                            <img src="${avatar}" alt="" style="width:38px; height:38px; border-radius:var(--radius-full); object-fit:cover; border:1px solid var(--border-strong);">
                            <div>
                                <div style="font-weight:700; color:var(--text-main); font-size:14px;">${emp.full_name}</div>
                                <div style="font-size:11.5px; color:var(--primary-400); font-weight:600;">${emp.login_id || emp.emp_code}</div>
                            </div>
                        </div>
                    </td>
                    <td><span class="badge badge-dept">${emp.department}</span></td>
                    <td style="font-weight:500;">${emp.job_position}</td>
                    <td>
                        <div style="font-size:12.5px; color:var(--text-main);">${emp.work_email}</div>
                        <div style="font-size:11.5px; color:var(--text-muted);">${emp.phone}</div>
                    </td>
                    <td style="font-weight:600; color:var(--text-main);">${wageStr}</td>
                    <td>${attBadge}</td>
                    <td onclick="event.stopPropagation()">
                        <div style="display:flex; gap:6px;">
                            ${actionButtons}
                        </div>
                    </td>
                </tr>
            `;
        }).join('');

        return `
            <div class="table-container">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th class="sortable" onclick="App.setSort('name')">Employee</th>
                            <th class="sortable" onclick="App.setSort('department')">Department</th>
                            <th class="sortable" onclick="App.setSort('job_position')">Position</th>
                            <th>Contact</th>
                            <th class="sortable" onclick="App.setSort('monthly_wage')">Monthly Wage</th>
                            <th class="sortable" onclick="App.setSort('attendance_status')">Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${rowsHtml}
                    </tbody>
                </table>
            </div>
        `;
    }
}

window.EmployeeTableComponent = EmployeeTableComponent;
