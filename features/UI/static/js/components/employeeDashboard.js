/**
 * Employee Dashboard Component (PDF 3.2.1)
 * Features 4 Quick-Access Cards: Profile, Attendance, Leave Requests, Logout
 * Plus Recent Activity, Real-Time Presence Status, and Company Alerts.
 */
class EmployeeDashboardComponent {
    static async render() {
        const container = document.getElementById('view-container');
        if (!container) return;

        const user = App.currentUser;
        if (!user) return;

        // Skeleton loading state
        container.innerHTML = `
            <div class="stats-grid">
                <div class="stat-card skeleton" style="height:140px;"></div>
                <div class="stat-card skeleton" style="height:140px;"></div>
                <div class="stat-card skeleton" style="height:140px;"></div>
                <div class="stat-card skeleton" style="height:140px;"></div>
            </div>
            <div class="glass-card skeleton" style="height:260px; margin-top:20px;"></div>
        `;

        try {
            const empId = user.employee_id || 1;
            
            // Fetch live employee details, today's attendance, and leave summary in parallel
            const [emp, todayAtt, attSummary, leaves, balances] = await Promise.all([
                ApiService.getEmployee(empId).catch(() => ({ id: empId, full_name: user.display_name, department: 'General', job_position: 'Employee' })),
                ApiService.getTodayAttendance().catch(() => null),
                ApiService.getAttendanceSummary().catch(() => ({ total_days_present: 0, total_work_hours: 0 })),
                ApiService.getMyLeaves().catch(() => []),
                ApiService.getMyLeaveBalances().catch(() => []),
            ]);

            const isCheckedIn = !!(todayAtt && todayAtt.check_in && !todayAtt.check_out);
            const checkInTime = todayAtt?.check_in ? new Date(todayAtt.check_in).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'Not yet checked in';
            const workHours = todayAtt?.work_hours ? `${todayAtt.work_hours} hrs` : (isCheckedIn ? 'In Progress' : '0.00 hrs');
            const attStatus = isCheckedIn ? '🟢 Checked In' : (todayAtt?.check_out ? '🏁 Completed' : '🟡 Absent / Pending');

            // Compute leave balance
            let ptoDays = 14;
            let sickDays = 7;
            balances.forEach(b => {
                const name = (b.leave_type_name || '').toLowerCase();
                if (name.includes('paid') || name.includes('pto')) ptoDays = b.remaining_days;
                if (name.includes('sick')) sickDays = b.remaining_days;
            });
            const pendingLeaves = leaves.filter(l => l.status === 'PENDING').length;

            const avatar = emp.profile_picture || emp.avatar_url || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150';
            const todayFormatted = new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });

            container.innerHTML = `
                <!-- Welcome Banner -->
                <div class="glass-card" style="margin-bottom:24px; padding:24px 28px; background:linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(16, 185, 129, 0.08) 100%); border:1px solid var(--border-strong); display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:16px;">
                    <div>
                        <div style="font-size:12px; text-transform:uppercase; letter-spacing:0.06em; font-weight:700; color:var(--primary-400); margin-bottom:4px;">
                            Employee Self-Service Workspace
                        </div>
                        <h1 style="font-size:24px; font-weight:800; color:var(--text-main); margin:0;">
                            Welcome back, ${emp.full_name || user.display_name}! 👋
                        </h1>
                        <p style="font-size:13px; color:var(--text-muted); margin:4px 0 0 0;">
                            ${emp.job_position} &bull; ${emp.department} &bull; ID: <code style="color:var(--primary-300); font-weight:700;">${emp.employee_code || user.login_id}</code>
                        </p>
                    </div>
                    <div style="text-align:right;">
                        <span class="badge badge-dept" style="padding:6px 12px; font-size:12px;">📅 ${todayFormatted}</span>
                    </div>
                </div>

                <!-- 4 Quick-Access Action Cards (PDF 3.2.1) -->
                <div class="stats-grid" style="grid-template-columns:repeat(auto-fit, minmax(240px, 1fr)); gap:18px; margin-bottom:28px;">
                    
                    <!-- CARD 1: My Profile -->
                    <div class="stat-card primary" style="cursor:pointer;" onclick="App.navigate('profile', ${emp.id})">
                        <div style="display:flex; justify-content:space-between; align-items:flex-start; width:100%;">
                            <div class="stat-icon-wrapper primary">
                                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
                            </div>
                            <span class="badge badge-dept" style="font-size:11px;">Card 1</span>
                        </div>
                        <div class="stat-details" style="margin-top:14px;">
                            <span style="font-size:16px; font-weight:700; color:var(--text-main); display:block;">My Profile</span>
                            <span class="stat-label">Personal details, Salary, Documents</span>
                        </div>
                        <div style="margin-top:14px; padding-top:10px; border-top:1px solid var(--border-subtle); display:flex; justify-content:space-between; align-items:center; font-size:12px; color:var(--primary-400); font-weight:600;">
                            <span>View & Edit Profile &rarr;</span>
                        </div>
                    </div>

                    <!-- CARD 2: Attendance Tracking -->
                    <div class="stat-card emerald">
                        <div style="display:flex; justify-content:space-between; align-items:flex-start; width:100%;">
                            <div class="stat-icon-wrapper emerald">
                                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 14 14"></polyline></svg>
                            </div>
                            <span class="badge ${isCheckedIn ? 'badge-present' : 'badge-absent'}" style="font-size:11px;">${attStatus}</span>
                        </div>
                        <div class="stat-details" style="margin-top:14px;">
                            <span style="font-size:16px; font-weight:700; color:var(--text-main); display:block;">Today: ${workHours}</span>
                            <span class="stat-label">Check-In: ${checkInTime}</span>
                        </div>
                        <div style="margin-top:14px; padding-top:10px; border-top:1px solid var(--border-subtle); display:flex; gap:8px;">
                            <button class="btn btn-sm ${isCheckedIn ? 'btn-secondary' : 'btn-primary'}" onclick="EmployeeDashboardComponent.toggleCheckInOut(${isCheckedIn})" style="flex:1; font-size:11.5px; padding:6px 10px;">
                                ${isCheckedIn ? '🏁 Check Out' : '🟢 Check In Now'}
                            </button>
                            <button class="btn btn-secondary btn-sm" onclick="App.navigate('attendance')" style="font-size:11.5px; padding:6px 10px;" title="Full Attendance">
                                📊 Logs
                            </button>
                        </div>
                    </div>

                    <!-- CARD 3: Leave Requests -->
                    <div class="stat-card sky">
                        <div style="display:flex; justify-content:space-between; align-items:flex-start; width:100%;">
                            <div class="stat-icon-wrapper sky">
                                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.8 19.2L16 11l3.5-3.5C21 6 21.5 4 21 3c-1-.5-3 0-4.5 1.5L13 8 4.8 6.2c-.5-.1-.9.1-1.1.5l-.3.5c-.2.5-.1 1 .3 1.3L9 12l-2 3H4l-1 1 3 2 2 3 1-1v-3l3-2 3.5 5.3c.3.4.8.5 1.3.3l.5-.2c.4-.3.6-.7.5-1.2z"></path></svg>
                            </div>
                            ${pendingLeaves > 0 ? `<span class="badge badge-absent" style="font-size:11px;">${pendingLeaves} Pending</span>` : `<span class="badge badge-present" style="font-size:11px;">Available</span>`}
                        </div>
                        <div class="stat-details" style="margin-top:14px;">
                            <span style="font-size:16px; font-weight:700; color:var(--text-main); display:block;">${ptoDays}d PTO / ${sickDays}d Sick</span>
                            <span class="stat-label">Remaining Leave Balances</span>
                        </div>
                        <div style="margin-top:14px; padding-top:10px; border-top:1px solid var(--border-subtle); display:flex; gap:8px;">
                            <button class="btn btn-primary btn-sm" onclick="LeaveModalComponent.openApplyModal()" style="flex:1; font-size:11.5px; padding:6px 10px;">
                                + Apply Leave
                            </button>
                            <button class="btn btn-secondary btn-sm" onclick="App.navigate('leaves')" style="font-size:11.5px; padding:6px 10px;" title="View Leave Requests">
                                📋 History
                            </button>
                        </div>
                    </div>

                    <!-- CARD 4: Account & Logout -->
                    <div class="stat-card amber">
                        <div style="display:flex; justify-content:space-between; align-items:flex-start; width:100%;">
                            <div class="stat-icon-wrapper amber">
                                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
                            </div>
                            <span class="badge badge-dept" style="font-size:11px;">Active Session</span>
                        </div>
                        <div class="stat-details" style="margin-top:14px;">
                            <span style="font-size:16px; font-weight:700; color:var(--text-main); display:block;">Account Security</span>
                            <span class="stat-label">${user.email || user.login_id}</span>
                        </div>
                        <div style="margin-top:14px; padding-top:10px; border-top:1px solid var(--border-subtle); display:flex; gap:8px;">
                            <button class="btn btn-secondary btn-sm" onclick="App.openPasswordModal()" style="flex:1; font-size:11.5px; padding:6px 8px;">
                                🔑 Password
                            </button>
                            <button class="btn btn-outline-danger btn-sm" onclick="App.logout()" style="flex:1; font-size:11.5px; padding:6px 8px;">
                                🚪 Logout
                            </button>
                        </div>
                    </div>

                </div>

                <!-- Recent Activity & Real-Time Alerts Grid -->
                <div style="display:grid; grid-template-columns:2fr 1fr; gap:20px; align-items:start;">
                    
                    <!-- Left: Recent Time-Off Requests -->
                    <div class="glass-card" style="padding:24px;">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:18px;">
                            <div>
                                <h3 style="font-size:16px; font-weight:700; color:var(--text-main); margin:0;">Recent Leave Requests & Activity</h3>
                                <p style="font-size:12.5px; color:var(--text-muted); margin:2px 0 0 0;">Latest status updates on your submitted time-off requests</p>
                            </div>
                            <button class="btn btn-secondary btn-sm" onclick="LeaveModalComponent.openApplyModal()">+ New Request</button>
                        </div>

                        ${leaves.length === 0 ? `
                            <div style="text-align:center; padding:36px; color:var(--text-muted);">
                                <div style="font-size:32px; margin-bottom:8px;">🏖️</div>
                                <div style="font-weight:600;">No leave requests found</div>
                                <div style="font-size:12px; margin-top:4px;">You haven't requested any time-off yet this period.</div>
                            </div>
                        ` : `
                            <div style="overflow-x:auto;">
                                <table class="data-table">
                                    <thead>
                                        <tr>
                                            <th>Type</th>
                                            <th>Date Range</th>
                                            <th>Days</th>
                                            <th>Status</th>
                                            <th>Admin Remarks</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        ${leaves.slice(0, 5).map(l => {
                                            const st = String(l.status).toUpperCase();
                                            const badgeClass = st === 'APPROVED' ? 'badge-present' : (st === 'REJECTED' ? 'badge-absent' : 'badge-leave');
                                            const badgeIcon = st === 'APPROVED' ? '✓' : (st === 'REJECTED' ? '✗' : '⏳');
                                            return `
                                                <tr>
                                                    <td><strong>${l.leave_type_name || 'Leave'}</strong></td>
                                                    <td>${l.start_date} &rarr; ${l.end_date}</td>
                                                    <td><strong>${l.days_count}</strong></td>
                                                    <td><span class="badge ${badgeClass}">${badgeIcon} ${st}</span></td>
                                                    <td style="font-size:12px; color:var(--text-muted);">${l.rejection_reason || l.remarks || '—'}</td>
                                                </tr>
                                            `;
                                        }).join('')}
                                    </tbody>
                                </table>
                            </div>
                        `}
                    </div>

                    <!-- Right: Alerts & Quick Highlights -->
                    <div style="display:flex; flex-direction:column; gap:16px;">
                        
                        <!-- Today's Attendance Pulse -->
                        <div class="glass-card" style="padding:20px;">
                            <h4 style="font-size:14px; font-weight:700; color:var(--text-main); margin-bottom:12px; display:flex; align-items:center; gap:8px;">
                                <span>⚡</span> Quick Systray Action
                            </h4>
                            <div style="font-size:13px; color:var(--text-muted); margin-bottom:14px;">
                                Regular check-in hours ensure accurate automated monthly payslip calculations.
                            </div>
                            <button class="btn btn-primary" style="width:100%; display:flex; justify-content:center; gap:8px;" onclick="EmployeeDashboardComponent.toggleCheckInOut(${isCheckedIn})">
                                ${isCheckedIn ? 'Check Out for Today' : 'Mark Daily Check-In'}
                            </button>
                        </div>

                        <!-- Company Alerts -->
                        <div class="glass-card" style="padding:20px;">
                            <h4 style="font-size:14px; font-weight:700; color:var(--text-main); margin-bottom:12px; display:flex; align-items:center; gap:8px;">
                                <span>🔔</span> Alerts & Announcements
                            </h4>
                            <div style="display:flex; flex-direction:column; gap:10px; font-size:12.5px;">
                                <div style="padding:10px; border-radius:var(--radius-sm); background:var(--bg-surface-elevated); border-left:3px solid var(--primary-500);">
                                    <div style="font-weight:700; color:var(--text-main);">Monthly Payslips Ready</div>
                                    <div style="color:var(--text-muted); margin-top:2px;">Automated salary slips for current cycle are calculated and viewable under the Payroll tab.</div>
                                </div>
                                <div style="padding:10px; border-radius:var(--radius-sm); background:var(--bg-surface-elevated); border-left:3px solid var(--emerald-500, #10b981);">
                                    <div style="font-weight:700; color:var(--text-main);">Attendance Policy Reminder</div>
                                    <div style="color:var(--text-muted); margin-top:2px;">Check-ins after 10:00 AM are tracked as half-day status per corporate policy.</div>
                                </div>
                            </div>
                        </div>

                    </div>

                </div>
            `;
        } catch (err) {
            container.innerHTML = `
                <div class="glass-card" style="padding:30px; text-align:center;">
                    <h3 style="color:var(--text-main);">Failed to load employee dashboard</h3>
                    <p style="color:var(--text-muted); margin-top:8px;">${err.message}</p>
                    <button class="btn btn-primary" onclick="EmployeeDashboardComponent.render()" style="margin-top:16px;">Try Again</button>
                </div>
            `;
        }
    }

    static async toggleCheckInOut(isCheckedIn) {
        try {
            if (isCheckedIn) {
                await ApiService.checkOut();
                Toast.success('Checked Out', 'Your check-out time and hours have been recorded.');
            } else {
                await ApiService.checkIn();
                Toast.success('Checked In', 'Welcome! You are marked as present for today.');
            }
            this.render();
            HeaderComponent.updateSystrayAttendance();
        } catch (err) {
            Toast.error('Action Failed', err.message);
        }
    }
}

window.EmployeeDashboardComponent = EmployeeDashboardComponent;
