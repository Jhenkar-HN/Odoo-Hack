/**
 * Leave / Time-Off Application & Review Modal Component
 */
class LeaveModalComponent {
    static async openApplyModal() {
        const modal = document.getElementById('generic-modal-overlay');
        if (!modal) return;

        const user = App.currentUser;
        if (!user) return;

        const today = new Date().toISOString().split('T')[0];

        modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-header">
                    <h3 class="modal-title">Apply for Time Off / Leave</h3>
                    <button class="modal-close" onclick="App.closeModal()">&times;</button>
                </div>
                <div class="modal-body">
                    <!-- Tab Header -->
                    <div class="tabs-header" id="leave-tabs-header" style="margin-bottom:20px;">
                        <button class="tab-btn active" onclick="LeaveModalComponent.switchTab('leave-apply-pane', this)">
                            Request New Leave
                        </button>
                        <button class="tab-btn" onclick="LeaveModalComponent.switchTab('leave-history-pane', this)">
                            My Leave History
                        </button>
                    </div>

                    <!-- PANE 1: Apply Form -->
                    <div class="tab-pane active" id="leave-apply-pane">
                        <form id="leave-apply-form" onsubmit="LeaveModalComponent.submitLeave(event)">
                            <div class="form-row">
                                <div class="form-group">
                                    <label class="form-label required" for="leave_type_id">Leave Type</label>
                                    <select id="leave_type_id" class="form-control" required>
                                        <option value="">Loading leave types...</option>
                                    </select>
                                </div>
                                <div class="form-group">
                                    <label class="form-label required" for="days_count">Number of Days</label>
                                    <input type="number" id="days_count" class="form-control" value="1" min="0.5" step="0.5" readonly style="background:var(--bg-glass-input, rgba(255,255,255,0.05)); cursor:default;">
                                </div>
                            </div>

                            <div class="form-row">
                                <div class="form-group">
                                    <label class="form-label required" for="start_date">Start Date</label>
                                    <input type="date" id="start_date" class="form-control" value="${today}" onchange="LeaveModalComponent.updateDaysCount()" required>
                                </div>
                                <div class="form-group">
                                    <label class="form-label required" for="end_date">End Date</label>
                                    <input type="date" id="end_date" class="form-control" value="${today}" onchange="LeaveModalComponent.updateDaysCount()" required>
                                </div>
                            </div>

                            <div class="form-group">
                                <label class="form-label" for="leave_reason">Reason / Note</label>
                                <textarea id="leave_reason" class="form-control" rows="3" placeholder="Please provide brief reason for leave application..."></textarea>
                            </div>

                            <div style="display:flex; justify-content:flex-end; gap:12px; margin-top:20px;">
                                <button type="button" class="btn btn-secondary" onclick="App.closeModal()">Cancel</button>
                                <button type="submit" class="btn btn-primary" id="leave-submit-btn">
                                    Submit Application
                                </button>
                            </div>
                        </form>
                    </div>

                    <!-- PANE 2: History -->
                    <div class="tab-pane" id="leave-history-pane">
                        <div id="leave-history-content">
                            <div class="glass-card skeleton" style="height:150px;"></div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        modal.classList.add('active');
        await this.populateLeaveTypes();
        this.updateDaysCount();
        await this.loadMyLeaves();
    }

    static async populateLeaveTypes() {
        const select = document.getElementById('leave_type_id');
        if (!select) return;

        try {
            const types = await ApiService.getLeaveTypes();
            if (types && types.length > 0) {
                select.innerHTML = types.map(t => `<option value="${t.id}">${t.name} (${t.default_allocation} days/year)</option>`).join('');
            } else {
                select.innerHTML = `
                    <option value="1">Paid Time Off (PTO)</option>
                    <option value="2">Sick Leave</option>
                    <option value="3">Casual Leave</option>
                    <option value="4">Unpaid Leave</option>
                `;
            }
        } catch (e) {
            select.innerHTML = `
                <option value="1">Paid Time Off (PTO)</option>
                <option value="2">Sick Leave</option>
                <option value="3">Casual Leave</option>
                <option value="4">Unpaid Leave</option>
            `;
        }
    }

    static updateDaysCount() {
        const startInput = document.getElementById('start_date');
        const endInput = document.getElementById('end_date');
        const daysInput = document.getElementById('days_count');

        if (!startInput || !endInput || !daysInput) return;

        const start = new Date(startInput.value);
        const end = new Date(endInput.value);

        if (startInput.value && endInput.value && !isNaN(start.getTime()) && !isNaN(end.getTime())) {
            if (end >= start) {
                const diffTime = Math.abs(end - start);
                const diffDays = Math.round(diffTime / (1000 * 60 * 60 * 24)) + 1;
                daysInput.value = diffDays;
            } else {
                daysInput.value = 1;
            }
        }
    }

    static async loadMyLeaves() {
        const historyContainer = document.getElementById('leave-history-content');
        if (!historyContainer) return;

        try {
            const leaves = await ApiService.getMyLeaves();
            if (!leaves || leaves.length === 0) {
                historyContainer.innerHTML = `
                    <div class="empty-state" style="padding:24px;">
                        <div class="empty-state-title">No leave requests found</div>
                        <div class="empty-state-text">You have not submitted any time-off requests yet.</div>
                    </div>
                `;
                return;
            }

            let rows = leaves.map(l => {
                const statusStr = String(l.status || 'PENDING').toUpperCase();
                const statusBadge = statusStr === 'APPROVED' ? 
                    `<span class="badge badge-present">Approved</span>` : 
                    (statusStr === 'REJECTED' ? 
                        `<span class="badge badge-inactive" style="color:var(--accent-rose); border-color:var(--accent-rose);">Rejected</span>` : 
                        `<span class="badge badge-absent">Pending HR Review</span>`);

                const typeName = l.leave_type_name || l.leave_type?.name || l.leave_type || 'Leave';
                const days = l.number_of_days || l.days_count || 1;

                return `
                    <tr>
                        <td><strong>${typeName}</strong></td>
                        <td>${l.start_date} &rarr; ${l.end_date} (${days} d)</td>
                        <td style="font-size:12.5px; color:var(--text-muted);">${l.reason || 'No note'}</td>
                        <td>${statusBadge}</td>
                    </tr>
                `;
            }).join('');

            historyContainer.innerHTML = `
                <div class="table-container">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Type</th>
                                <th>Dates</th>
                                <th>Reason</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${rows}
                        </tbody>
                    </table>
                </div>
            `;
        } catch (err) {
            historyContainer.innerHTML = `<div class="empty-state-text">Failed to load history: ${err.message}</div>`;
        }
    }

    static switchTab(paneId, btnElement) {
        document.querySelectorAll('#leave-tabs-header .tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.modal-body .tab-pane').forEach(p => p.classList.remove('active'));

        if (btnElement) btnElement.classList.add('active');
        const pane = document.getElementById(paneId);
        if (pane) pane.classList.add('active');

        if (paneId === 'leave-history-pane') {
            this.loadMyLeaves();
        }
    }

    static async submitLeave(event) {
        event.preventDefault();

        const leaveTypeIdVal = document.getElementById('leave_type_id')?.value;
        const startDateVal = document.getElementById('start_date')?.value;
        const endDateVal = document.getElementById('end_date')?.value;
        const reasonVal = document.getElementById('leave_reason')?.value?.trim() || '';

        if (!leaveTypeIdVal) {
            Toast.error('Validation Error', 'Please select a leave type.');
            return;
        }

        if (new Date(endDateVal) < new Date(startDateVal)) {
            Toast.error('Invalid Date Range', 'End Date cannot be earlier than Start Date.');
            return;
        }

        const payload = {
            leave_type_id: parseInt(leaveTypeIdVal, 10),
            start_date: startDateVal,
            end_date: endDateVal,
            reason: reasonVal || null
        };

        const submitBtn = document.getElementById('leave-submit-btn');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = 'Submitting...';
        }

        try {
            await ApiService.applyLeave(payload);
            Toast.success('Leave Submitted', 'Your leave request has been submitted to HR for approval.');
            
            // Switch to history tab and refresh
            const historyTabBtn = document.querySelectorAll('#leave-tabs-header .tab-btn')[1];
            this.switchTab('leave-history-pane', historyTabBtn);
        } catch (err) {
            Toast.error('Submission Failed', err.message);
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = 'Submit Application';
            }
        }
    }

    // HR Leave Management View
    static async openHRLeaveManager() {
        const modal = document.getElementById('generic-modal-overlay');
        if (!modal) return;

        modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-header">
                    <h3 class="modal-title">Employee Leave Approvals (HR Portal)</h3>
                    <button class="modal-close" onclick="App.closeModal()">&times;</button>
                </div>
                <div class="modal-body" id="hr-leaves-content">
                    <div class="glass-card skeleton" style="height:200px;"></div>
                </div>
            </div>
        `;

        modal.classList.add('active');
        await this.loadAllLeavesHR();
    }

    static async loadAllLeavesHR() {
        const container = document.getElementById('hr-leaves-content');
        if (!container) return;

        try {
            const leaves = await ApiService.getAllLeaves();
            if (!leaves || leaves.length === 0) {
                container.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-state-title">No pending leave requests</div>
                        <div class="empty-state-text">All employee leave applications are up to date.</div>
                    </div>
                `;
                return;
            }

            let rows = leaves.map(l => {
                const statusStr = String(l.status || 'PENDING').toUpperCase();
                const isPending = statusStr === 'PENDING';
                const statusBadge = statusStr === 'APPROVED' ? 
                    `<span class="badge badge-present">Approved</span>` : 
                    (statusStr === 'REJECTED' ? 
                        `<span class="badge badge-inactive" style="color:var(--accent-rose);">Rejected</span>` : 
                        `<span class="badge badge-absent">Pending</span>`);

                const actions = isPending ? `
                    <div style="display:flex; gap:6px;">
                        <button class="btn btn-primary btn-sm" onclick="LeaveModalComponent.reviewLeave(${l.id}, 'APPROVED')">Approve</button>
                        <button class="btn btn-outline-danger btn-sm" onclick="LeaveModalComponent.reviewLeave(${l.id}, 'REJECTED')">Reject</button>
                    </div>
                ` : `<span style="font-size:12px; color:var(--text-subtle);">Reviewed by ${l.reviewed_by || 'HR'}</span>`;

                const empName = l.employee_name || l.full_name || 'Employee';
                const typeName = l.leave_type_name || l.leave_type?.name || l.leave_type || 'Leave';
                const days = l.number_of_days || l.days_count || 1;

                return `
                    <tr>
                        <td>
                            <div style="display:flex; align-items:center; gap:10px;">
                                <img src="${l.avatar_url || 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150'}" alt="" style="width:32px; height:32px; border-radius:var(--radius-full); object-fit:cover;">
                                <div>
                                    <div style="font-weight:700; color:var(--text-main); font-size:13.5px;">${empName}</div>
                                    <div style="font-size:11px; color:var(--primary-400);">${l.department || 'General'}</div>
                                </div>
                            </div>
                        </td>
                        <td><strong>${typeName}</strong></td>
                        <td>${l.start_date} &rarr; ${l.end_date} (${days} d)</td>
                        <td style="font-size:12px; color:var(--text-muted);">${l.reason || 'None'}</td>
                        <td>${statusBadge}</td>
                        <td>${actions}</td>
                    </tr>
                `;
            }).join('');

            container.innerHTML = `
                <div class="table-container">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Employee</th>
                                <th>Type</th>
                                <th>Duration</th>
                                <th>Reason</th>
                                <th>Status</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${rows}
                        </tbody>
                    </table>
                </div>
            `;
        } catch (err) {
            container.innerHTML = `<div class="empty-state-text">Failed to load leaves: ${err.message}</div>`;
        }
    }

    static async reviewLeave(leaveId, newStatus) {
        try {
            await ApiService.reviewLeave(leaveId, newStatus, App.currentUser?.display_name || 'HR Admin');
            Toast.success('Updated', `Leave request #${leaveId} was marked as ${newStatus}.`);
            if (document.getElementById('view-container')?.dataset?.currentView === 'leaves') {
                this.renderPageView();
            } else {
                await this.loadAllLeavesHR();
            }
        } catch (err) {
            Toast.error('Update Failed', err.message);
        }
    }

    static async renderPageView() {
        const container = document.getElementById('view-container');
        if (!container) return;
        container.dataset.currentView = 'leaves';

        const user = App.currentUser;
        if (!user) return;
        const isHR = ['ADMIN', 'HR_OFFICER'].includes(String(user.role || '').toUpperCase());

        container.innerHTML = `
            <div class="glass-card skeleton" style="height:100px; margin-bottom:20px;"></div>
            <div class="glass-card skeleton" style="height:350px;"></div>
        `;

        try {
            const [types, balances, allLeaves] = await Promise.all([
                ApiService.getLeaveTypes().catch(() => []),
                ApiService.getMyLeaveBalances().catch(() => []),
                isHR ? ApiService.getAllLeaves().catch(() => []) : ApiService.getMyLeaves().catch(() => [])
            ]);

            const pendingCount = allLeaves.filter(l => String(l.status).toUpperCase() === 'PENDING').length;
            const approvedCount = allLeaves.filter(l => String(l.status).toUpperCase() === 'APPROVED').length;

            container.innerHTML = `
                <!-- Top Header & Action -->
                <div class="glass-card" style="margin-bottom:20px; padding:18px 24px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:16px;">
                    <div>
                        <h2 style="font-size:18px; font-weight:800; color:var(--text-main); margin:0;">
                            ${isHR ? 'Time-Off & Leave Authorizations' : 'My Time-Off & Leave Portal'}
                        </h2>
                        <span style="font-size:12.5px; color:var(--text-muted);">
                            ${isHR ? 'Review organization-wide leave applications and balance quotas' : 'Track your paid time off balances and submit new requests'}
                        </span>
                    </div>
                    <button class="btn btn-primary" onclick="LeaveModalComponent.openApplyModal()" style="display:flex; align-items:center; gap:8px;">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
                        Apply for Leave
                    </button>
                </div>

                <!-- Stats / Balances Grid -->
                <div class="stats-grid" style="margin-bottom:24px;">
                    ${isHR ? `
                        <div class="stat-card amber">
                            <div class="stat-icon-wrapper amber">
                                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
                            </div>
                            <div class="stat-details">
                                <span class="stat-value">${pendingCount}</span>
                                <span class="stat-label">Pending Authorizations</span>
                            </div>
                        </div>
                        <div class="stat-card emerald">
                            <div class="stat-icon-wrapper emerald">
                                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg>
                            </div>
                            <div class="stat-details">
                                <span class="stat-value">${approvedCount}</span>
                                <span class="stat-label">Approved Applications</span>
                            </div>
                        </div>
                        <div class="stat-card primary">
                            <div class="stat-icon-wrapper primary">
                                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path></svg>
                            </div>
                            <div class="stat-details">
                                <span class="stat-value">${allLeaves.length}</span>
                                <span class="stat-label">Total Requests Recorded</span>
                            </div>
                        </div>
                    ` : (balances.length > 0 ? balances.map(b => `
                        <div class="stat-card primary">
                            <div class="stat-details">
                                <span class="stat-value">${b.remaining_days} / ${b.allocated_days}</span>
                                <span class="stat-label">${b.leave_type_name || 'Leave'} Days Left</span>
                            </div>
                        </div>
                    `).join('') : `
                        <div class="stat-card emerald">
                            <div class="stat-details">
                                <span class="stat-value">12 / 14</span>
                                <span class="stat-label">Paid Annual Leaves</span>
                            </div>
                        </div>
                        <div class="stat-card sky">
                            <div class="stat-details">
                                <span class="stat-value">7 / 7</span>
                                <span class="stat-label">Sick / Medical Leaves</span>
                            </div>
                        </div>
                        <div class="stat-card amber">
                            <div class="stat-details">
                                <span class="stat-value">3 / 3</span>
                                <span class="stat-label">Casual Floating Leaves</span>
                            </div>
                        </div>
                    `)}
                </div>

                <!-- Table Container -->
                <div class="table-container">
                    <div style="padding:18px 24px; border-bottom:1px solid var(--border-subtle); display:flex; justify-content:space-between; align-items:center;">
                        <h3 style="font-size:16px; font-weight:700; color:var(--text-main); margin:0;">
                            ${isHR ? 'Company-Wide Leave Records' : 'My Leave Request History'}
                        </h3>
                        <span class="badge badge-dept">${allLeaves.length} Applications</span>
                    </div>
                    <table class="data-table">
                        <thead>
                            <tr>
                                ${isHR ? '<th>Employee</th>' : ''}
                                <th>Leave Type</th>
                                <th>Dates &amp; Duration</th>
                                <th>Reason</th>
                                <th>Applied Date</th>
                                <th>Status</th>
                                ${isHR ? '<th>Actions</th>' : ''}
                            </tr>
                        </thead>
                        <tbody>
                            ${allLeaves.length === 0 ? `
                                <tr><td colspan="${isHR ? 7 : 5}" style="text-align:center; padding:32px; color:var(--text-muted);">No leave records found.</td></tr>
                            ` : allLeaves.map(l => {
                                const st = String(l.status || 'PENDING').toUpperCase();
                                const badgeClass = st === 'APPROVED' ? 'badge-present' : (st === 'PENDING' ? 'badge-leave' : 'badge-absent');
                                const badgeLabel = st === 'APPROVED' ? '✓ Approved' : (st === 'PENDING' ? '⏳ Pending' : '✗ Rejected');
                                
                                return `
                                    <tr>
                                        ${isHR ? `
                                            <td>
                                                <div style="font-weight:700; color:var(--text-main); font-size:13px;">${l.employee_name || 'Employee'}</div>
                                                <div style="font-size:11px; color:var(--primary-400);">${l.employee_code || ''}</div>
                                            </td>
                                        ` : ''}
                                        <td><strong>${l.leave_type_name || 'Leave'}</strong></td>
                                        <td>${l.start_date} to ${l.end_date} (<strong>${l.days_count} days</strong>)</td>
                                        <td style="font-size:12px; color:var(--text-muted); max-width:240px;">${l.reason || '—'}</td>
                                        <td style="font-size:12px;">${l.applied_at ? l.applied_at.split('T')[0] : '—'}</td>
                                        <td><span class="badge ${badgeClass}">${badgeLabel}</span></td>
                                        ${isHR ? `
                                            <td>
                                                ${st === 'PENDING' ? `
                                                    <div style="display:flex; gap:6px;">
                                                        <button class="btn btn-success btn-sm" onclick="LeaveModalComponent.reviewLeave(${l.id}, 'APPROVED')" style="padding:4px 8px; font-size:11.5px;">Approve</button>
                                                        <button class="btn btn-outline-danger btn-sm" onclick="LeaveModalComponent.reviewLeave(${l.id}, 'REJECTED')" style="padding:4px 8px; font-size:11.5px;">Reject</button>
                                                    </div>
                                                ` : `<span style="font-size:11.5px; color:var(--text-muted);">Processed</span>`}
                                            </td>
                                        ` : ''}
                                    </tr>
                                `;
                            }).join('')}
                        </tbody>
                    </table>
                </div>
            `;
        } catch (err) {
            container.innerHTML = `<div class="glass-card" style="padding:30px; text-align:center;">Failed to load leaves: ${err.message}</div>`;
        }
    }
}

window.LeaveModalComponent = LeaveModalComponent;

