/**
 * Dashboard & Analytics View Component
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
            <div class="glass-card skeleton" style="height: 350px;"></div>
        `;

        try {
            const stats = await ApiService.getDashboardStats();
            
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

            let recentJoinersHtml = '';
            (stats.recent_joiners || []).forEach(emp => {
                const attClass = emp.attendance_status === 'present' ? 'present' : (emp.attendance_status === 'on_leave' ? 'leave' : 'absent');
                const attText = emp.attendance_status === 'present' ? '🟢 Present' : (emp.attendance_status === 'on_leave' ? '✈️ On Leave' : '🟡 Absent');
                
                recentJoinersHtml += `
                    <tr onclick="App.navigate('profile', ${emp.id})">
                        <td>
                            <div style="display:flex; align-items:center; gap:12px;">
                                <img src="${emp.avatar_url || 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150'}" alt="" style="width:36px; height:36px; border-radius:var(--radius-full); object-fit:cover;">
                                <div>
                                    <div style="font-weight:700; color:var(--text-main);">${emp.full_name}</div>
                                    <div style="font-size:11px; color:var(--primary-400);">${emp.login_id}</div>
                                </div>
                            </div>
                        </td>
                        <td><span class="badge badge-dept">${emp.department}</span></td>
                        <td>${emp.job_position}</td>
                        <td><span class="badge badge-${attClass}">${attText}</span></td>
                        <td>${emp.date_of_joining}</td>
                    </tr>
                `;
            });

            container.innerHTML = `
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
                            <span class="stat-label">Absent Today</span>
                        </div>
                    </div>
                </div>

                <!-- Dashboard Content Rows -->
                <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(360px, 1fr)); gap:24px; margin-bottom:24px;">
                    <!-- Department Breakdown -->
                    <div class="glass-card" style="padding:24px;">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px; border-bottom:1px solid var(--border-subtle); padding-bottom:12px;">
                            <h3 style="font-size:16px; font-weight:700; color:var(--text-main);">Department Distribution</h3>
                            <span class="badge badge-active">${stats.departments_count} Active Depts</span>
                        </div>
                        <div>
                            ${deptHtml || '<div class="empty-state-text">No departments recorded.</div>'}
                        </div>
                    </div>

                    <!-- Quick Actions & Attendance Policy -->
                    <div class="glass-card" style="padding:24px; display:flex; flex-direction:column; justify-content:space-between;">
                        <div>
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; border-bottom:1px solid var(--border-subtle); padding-bottom:12px;">
                                <h3 style="font-size:16px; font-weight:700; color:var(--text-main);">HR Quick Actions</h3>
                            </div>
                            <p style="color:var(--text-muted); font-size:13px; margin-bottom:20px; line-height:1.6;">
                                Manage company employee profiles, auto-generate login credentials (e.g. <code>OIJODO20250001</code>), compute salary breakdown components, and track real-time attendance status.
                            </p>
                        </div>
                        <div style="display:flex; flex-direction:column; gap:10px;">
                            <button class="btn btn-primary btn-lg" onclick="App.navigate('add-employee')">
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
                                Onboard New Employee
                            </button>
                            <button class="btn btn-secondary" onclick="App.navigate('employees')">
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle></svg>
                                View Employee Directory
                            </button>
                        </div>
                    </div>
                </div>

                <!-- Recent Joiners Table -->
                <div class="table-container">
                    <div style="padding:18px 24px; border-bottom:1px solid var(--border-subtle); display:flex; justify-content:space-between; align-items:center;">
                        <h3 style="font-size:16px; font-weight:700; color:var(--text-main);">Recently Onboarded Team Members</h3>
                        <button class="btn btn-secondary btn-sm" onclick="App.navigate('employees')">View All</button>
                    </div>
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Employee</th>
                                <th>Department</th>
                                <th>Position</th>
                                <th>Today's Status</th>
                                <th>Joining Date</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${recentJoinersHtml || '<tr><td colspan="5" style="text-align:center; padding:32px; color:var(--text-muted);">No employees found.</td></tr>'}
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
}

window.StatsViewComponent = StatsViewComponent;
