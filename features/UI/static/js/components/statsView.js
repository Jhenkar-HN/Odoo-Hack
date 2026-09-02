/**
 * Admin / HR Dashboard & Analytics View Component (PDF 3.2.2)
 * Features:
 * - Real-time KPI metrics & department distribution
 * - Employee switcher dropdown (switch between employees)
 * - Live Attendance Records roster
 * - Pending Leave Approvals widget with one-click review
 */
class StatsViewComponent {
    static async render() {
        const container = document.getElementById('view-container');
        if (!container) return;

        // Skeleton loading state
        container.innerHTML = `
            <div class="stats-grid">
                <div class="stat-card skeleton" style="height: 100px;"></div>
                <div class="stat-card skeleton" style="height: 100px;"></div>
                <div class="stat-card skeleton" style="height: 100px;"></div>
                <div class="stat-card skeleton" style="height: 100px;"></div>
            </div>
            <div class="glass-card skeleton" style="height: 350px; margin-top:20px;"></div>
        `;

        try {
            const [stats, allEmployeesResp, pendingLeaves, todayAttendanceResp] = await Promise.all([
                ApiService.getDashboardStats().catch(() => ({ total_employees: 0, present_today: 0, on_leave_today: 0, absent_today: 0, department_distribution: {} })),
                ApiService.getEmployees({ size: 100 }).catch(() => ({ items: [] })),
                ApiService.getAllLeaves().catch(() => []),
                ApiService.getAllAttendance({ size: 100 }).catch(() => ({ items: [] }))
            ]);

            const allEmps = allEmployeesResp?.items || [];
            const leavesPending = pendingLeaves.filter(l => String(l.status).toUpperCase() === 'PENDING');
            const todayAttendances = todayAttendanceResp?.items || [];

            const deptEntries = Object.entries(stats.department_distribution || {});
            const total = stats.total_employees || 1;

            let deptHtml = '';
            deptEntries.forEach(([dept, count]) => {
                const pct = Math.round((count / total) * 100);
                deptHtml += `
                    <div style="display:flex; flex-direction:column; gap:6px; margin-bottom:14px;">
                        <div style="display:flex; justify-content:space-between; font-size:13px;">
                            <span style="font-weight:600; color:var(--text-main);">${dept}</span>
                            <span style="color:var(--text-muted); font-weight:500;">${count} employees (${pct}%)</span>
                        </div>
                        <div style="height:8px; width:100%; background:var(--bg-surface-elevated); border-radius:var(--radius-full); overflow:hidden;">
                            <div style="height:100%; width:${pct}%; background:linear-gradient(90deg, var(--primary-600), var(--primary-400)); border-radius:var(--radius-full); transition: width 0.6s ease;"></div>
                        </div>
                    </div>
                `;
            });

            // Employee Switcher options
            const employeeOptions = allEmps.map(e => `
                <option value="${e.id}">${e.full_name} (${e.login_id || e.employee_code} - ${e.department})</option>
            `).join('');

            container.innerHTML = `
                <!-- Top Header Bar with Employee Switcher (PDF 3.2.2) -->
                <div class="glass-card" style="margin-bottom:20px; padding:16px 24px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:16px;">
                    <div>
                        <h2 style="font-size:18px; font-weight:800; color:var(--text-main); margin:0;">Admin & HR Control Center</h2>
                        <span style="font-size:12.5px; color:var(--text-muted);">Manage workforce operations, live attendance, and time-off authorizations</span>
                    </div>

                    <!-- Ability to switch between employees (PDF 3.2.2) -->
                    <div style="display:flex; align-items:center; gap:10px;">
                        <label for="admin-emp-switcher" style="font-size:13px; font-weight:600; color:var(--text-main); white-space:nowrap;">
                            👤 Switch Employee:
                        </label>
                        <select id="admin-emp-switcher" class="filter-select" onchange="StatsViewComponent.handleEmployeeSwitch(this.value)" style="min-width:260px; padding:8px 12px; font-size:13px;">
                            <option value="">-- Jump to Employee Profile --</option>
                            ${employeeOptions}
                        </select>
                    </div>
                </div>

                <!-- Top KPI Cards -->
                <div class="stats-grid">
                    <div class="stat-card primary">
                        <div class="stat-icon-wrapper primary">
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
                        </div>
                        <div class="stat-details">
                            <span class="stat-value">${stats.total_employees}</span>
                            <span class="stat-label">Total Headcount</span>
                        </div>
                    </div>

                    <div class="stat-card emerald">
                        <div class="stat-icon-wrapper emerald">
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
                        </div>
                        <div class="stat-details">
                            <span class="stat-value">${stats.present_today}</span>
                            <span class="stat-label">Present in Office</span>
                        </div>
                    </div>

                    <div class="stat-card sky">
                        <div class="stat-icon-wrapper sky">
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.8 19.2L16 11l3.5-3.5C21 6 21.5 4 21 3c-1-.5-3 0-4.5 1.5L13 8 4.8 6.2c-.5-.1-.9.1-1.1.5l-.3.5c-.2.5-.1 1 .3 1.3L9 12l-2 3H4l-1 1 3 2 2 3 1-1v-3l3-2 3.5 5.3c.3.4.8.5 1.3.3l.5-.2c.4-.3.6-.7.5-1.2z"></path></svg>
                        </div>
                        <div class="stat-details">
                            <span class="stat-value">${stats.on_leave_today}</span>
                            <span class="stat-label">On Approved Leave</span>
                        </div>
                    </div>

                    <div class="stat-card amber">
                        <div class="stat-icon-wrapper amber">
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
                        </div>
                        <div class="stat-details">
                            <span class="stat-value">${stats.absent_today}</span>
                            <span class="stat-label">Absent / Unmarked</span>
                        </div>
                    </div>
                </div>

                <!-- Mid Row: Department Distribution & Pending Leave Approvals (PDF 3.2.2) -->
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:20px; margin:24px 0;">
                    
                    <!-- Department Breakdown -->
                    <div class="glass-card" style="padding:24px;">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px; border-bottom:1px solid var(--border-subtle); padding-bottom:12px;">
                            <h3 style="font-size:16px; font-weight:700; color:var(--text-main); margin:0;">Department Distribution</h3>
                            <span class="badge badge-dept">${deptEntries.length} Departments</span>
                        </div>
                        <div>
                            ${deptHtml || '<div class="empty-state-text">No departments recorded.</div>'}
                        </div>
                    </div>

                    <!-- Leave Approvals Widget (PDF 3.2.2) -->
                    <div class="glass-card" style="padding:24px;">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:18px; border-bottom:1px solid var(--border-subtle); padding-bottom:12px;">
                            <div>
                                <h3 style="font-size:16px; font-weight:700; color:var(--text-main); margin:0;">Pending Leave Approvals</h3>
                                <span style="font-size:12px; color:var(--text-muted);">${leavesPending.length} pending authorization</span>
                            </div>
                            <button class="btn btn-secondary btn-sm" onclick="App.navigate('leaves')">View All Leaves</button>
                        </div>

                        ${leavesPending.length === 0 ? `
                            <div style="text-align:center; padding:32px; color:var(--text-muted);">
                                <div style="font-size:28px; margin-bottom:6px;">✨</div>
                                <div style="font-weight:600;">No pending leave requests!</div>
                                <div style="font-size:12px; margin-top:2px;">All employee requests have been processed.</div>
                            </div>
                        ` : `
                            <div style="display:flex; flex-direction:column; gap:12px; max-height:280px; overflow-y:auto;">
                                ${leavesPending.slice(0, 5).map(req => `
                                    <div style="padding:12px; background:var(--bg-surface-elevated); border-radius:var(--radius-sm); border:1px solid var(--border-subtle); display:flex; justify-content:space-between; align-items:center; gap:10px;">
                                        <div style="flex:1;">
                                            <div style="font-weight:700; color:var(--text-main); font-size:13px;">${req.employee_name || 'Employee'}</div>
                                            <div style="font-size:11.5px; color:var(--text-muted);">
                                                ${req.leave_type_name} &bull; ${req.start_date} to ${req.end_date} (<strong>${req.days_count}d</strong>)
                                            </div>
                                            ${req.reason ? `<div style="font-size:11px; color:var(--text-subtle); margin-top:2px; font-style:italic;">"${req.reason}"</div>` : ''}
                                        </div>
                                        <div style="display:flex; gap:6px;">
                                            <button class="btn btn-success btn-sm" onclick="StatsViewComponent.reviewLeaveDirect(${req.id}, 'APPROVED')" style="padding:4px 8px; font-size:11.5px;">
                                                ✓ Approve
                                            </button>
                                            <button class="btn btn-outline-danger btn-sm" onclick="StatsViewComponent.reviewLeaveDirect(${req.id}, 'REJECTED')" style="padding:4px 8px; font-size:11.5px;">
                                                ✗ Reject
                                            </button>
                                        </div>
                                    </div>
                                `).join('')}
                            </div>
                        `}
                    </div>

                </div>

                <!-- Bottom Row: Today's Live Attendance Records (PDF 3.2.2) -->
                <div class="table-container" style="margin-top:24px;">
                    <div style="padding:18px 24px; border-bottom:1px solid var(--border-subtle); display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
                        <div>
                            <h3 style="font-size:16px; font-weight:700; color:var(--text-main); margin:0;">Daily Attendance Records</h3>
                            <span style="font-size:12px; color:var(--text-muted);">Today's employee check-ins, presence statuses, and working hours</span>
                        </div>
                        <div style="display:flex; gap:8px;">
                            <button class="btn btn-secondary btn-sm" onclick="App.navigate('attendance')">
                                📊 Full Attendance Roster
                            </button>
                            <button class="btn btn-primary btn-sm" onclick="App.navigate('employees')">
                                👥 Employee Directory
                            </button>
                        </div>
                    </div>
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Employee</th>
                                <th>Department</th>
                                <th>Check-In Time</th>
                                <th>Check-Out Time</th>
                                <th>Hours Logged</th>
                                <th>Today's Status</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${allEmps.slice(0, 8).map(emp => {
                                const att = todayAttendances.find(a => a.employee_id === emp.id);
                                const status = (emp.attendance_status || (att ? att.status : 'absent')).toLowerCase();
                                const isPresent = status === 'present';
                                const isOnLeave = status === 'on_leave';
                                const badgeClass = isPresent ? 'badge-present' : (isOnLeave ? 'badge-leave' : 'badge-absent');
                                const badgeLabel = isPresent ? '🟢 Present' : (isOnLeave ? '✈️ On Leave' : '🟡 Absent');
                                
                                const checkIn = att?.check_in ? new Date(att.check_in).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : (isPresent ? '09:00 AM' : '—');
                                const checkOut = att?.check_out ? new Date(att.check_out).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '—';
                                const hrs = att?.work_hours ? `${att.work_hours}h` : (isPresent ? '8.0h' : '0.0h');

                                return `
                                    <tr>
                                        <td>
                                            <div style="display:flex; align-items:center; gap:10px; cursor:pointer;" onclick="App.navigate('profile', ${emp.id})">
                                                <img src="${emp.avatar_url || 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150'}" alt="" style="width:32px; height:32px; border-radius:var(--radius-full); object-fit:cover;">
                                                <div>
                                                    <div style="font-weight:700; color:var(--text-main); font-size:13px;">${emp.full_name}</div>
                                                    <div style="font-size:11px; color:var(--primary-400);">${emp.login_id || emp.employee_code}</div>
                                                </div>
                                            </div>
                                        </td>
                                        <td><span class="badge badge-dept">${emp.department}</span></td>
                                        <td style="font-size:12.5px;">${checkIn}</td>
                                        <td style="font-size:12.5px;">${checkOut}</td>
                                        <td style="font-size:12.5px; font-weight:600;">${hrs}</td>
                                        <td><span class="badge ${badgeClass}">${badgeLabel}</span></td>
                                        <td>
                                            <button class="btn btn-secondary btn-sm" onclick="App.navigate('profile', ${emp.id})" style="font-size:11px; padding:4px 8px;">
                                                Profile &rarr;
                                            </button>
                                        </td>
                                    </tr>
                                `;
                            }).join('')}
                        </tbody>
                    </table>
                </div>
            `;
        } catch (err) {
            Toast.error('Dashboard Error', 'Failed to load analytics: ' + err.message);
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-title">Failed to load dashboard</div>
                    <div class="empty-state-text">${err.message}</div>
                    <button class="btn btn-primary" onclick="StatsViewComponent.render()">Retry</button>
                </div>
            `;
        }
    }

    static handleEmployeeSwitch(empId) {
        if (!empId) return;
        App.navigate('profile', empId);
    }

    static async reviewLeaveDirect(reqId, status) {
        let reason = null;
        if (status === 'REJECTED') {
            reason = prompt('Please specify reason for rejection:') || 'Rejected by HR';
        }
        try {
            await ApiService.reviewLeave(reqId, status, reason);
            Toast.success('Leave Updated', `Request has been marked as ${status}.`);
            this.render();
        } catch (err) {
            Toast.error('Review Failed', err.message);
        }
    }
}

window.StatsViewComponent = StatsViewComponent;
