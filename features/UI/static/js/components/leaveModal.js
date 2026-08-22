/**
 * Leave / Time-Off Application & Review Modal Component
 */
class LeaveModalComponent {
    static async openApplyModal() {
        const modal = document.getElementById('generic-modal-overlay');
        if (!modal) return;

        const user = App.currentUser;
        if (!user) return;

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
                                    <label class="form-label required" for="leave_type">Leave Type</label>
                                    <select id="leave_type" class="form-control" required>
                                        <option value="Paid Time Off">Paid Time Off (Annual Leave)</option>
                                        <option value="Sick Leave">Sick Leave</option>
                                        <option value="Unpaid Leave">Unpaid Leave</option>
                                    </select>
                                </div>
                                <div class="form-group">
                                    <label class="form-label required" for="days_count">Number of Days</label>
                                    <input type="number" id="days_count" class="form-control" value="1" min="0.5" step="0.5" required>
                                </div>
                            </div>

                            <div class="form-row">
                                <div class="form-group">
                                    <label class="form-label required" for="start_date">Start Date</label>
                                    <input type="date" id="start_date" class="form-control" value="${new Date().toISOString().split('T')[0]}" required>
                                </div>
                                <div class="form-group">
                                    <label class="form-label required" for="end_date">End Date</label>
                                    <input type="date" id="end_date" class="form-control" value="${new Date().toISOString().split('T')[0]}" required>
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
        await this.loadMyLeaves();
    }

    static async loadMyLeaves() {
        const historyContainer = document.getElementById('leave-history-content');
        if (!historyContainer) return;

        const user = App.currentUser;
        const empId = user?.employee_id || 1;

        try {
            const leaves = await ApiService.getMyLeaves(empId);
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
                const statusBadge = l.status === 'approved' ? 
                    `<span class="badge badge-present">Approved</span>` : 
                    (l.status === 'rejected' ? 
                        `<span class="badge badge-inactive" style="color:var(--accent-rose); border-color:var(--accent-rose);">Rejected</span>` : 
                        `<span class="badge badge-absent">Pending HR Review</span>`);

                return `
                    <tr>
                        <td><strong>${l.leave_type}</strong></td>
                        <td>${l.start_date} &rarr; ${l.end_date} (${l.days_count} d)</td>
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
        const user = App.currentUser;
        const empId = user?.employee_id || 1;

        const payload = {
            employee_id: empId,
            leave_type: document.getElementById('leave_type')?.value,
            days_count: parseFloat(document.getElementById('days_count')?.value || 1),
            start_date: document.getElementById('start_date')?.value,
            end_date: document.getElementById('end_date')?.value,
            reason: document.getElementById('leave_reason')?.value || ''
        };

        const submitBtn = document.getElementById('leave-submit-btn');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = 'Submitting...';
        }

        try {
            await ApiService.applyLeave(payload);
            Toast.success('Leave Submitted', 'Your leave request has been submitted to HR for approval.');
            this.switchTab('leave-history-pane', document.querySelectorAll('#leave-tabs-header .tab-btn')[1]);
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
                const isPending = l.status === 'pending';
                const statusBadge = l.status === 'approved' ? 
                    `<span class="badge badge-present">Approved</span>` : 
                    (l.status === 'rejected' ? 
                        `<span class="badge badge-inactive" style="color:var(--accent-rose);">Rejected</span>` : 
                        `<span class="badge badge-absent">Pending</span>`);

                const actions = isPending ? `
                    <div style="display:flex; gap:6px;">
                        <button class="btn btn-primary btn-sm" onclick="LeaveModalComponent.reviewLeave(${l.id}, 'approved')">Approve</button>
                        <button class="btn btn-outline-danger btn-sm" onclick="LeaveModalComponent.reviewLeave(${l.id}, 'rejected')">Reject</button>
                    </div>
                ` : `<span style="font-size:12px; color:var(--text-subtle);">Reviewed by ${l.reviewed_by || 'HR'}</span>`;

                return `
                    <tr>
                        <td>
                            <div style="display:flex; align-items:center; gap:10px;">
                                <img src="${l.avatar_url || 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150'}" alt="" style="width:32px; height:32px; border-radius:var(--radius-full); object-fit:cover;">
                                <div>
                                    <div style="font-weight:700; color:var(--text-main); font-size:13.5px;">${l.full_name}</div>
                                    <div style="font-size:11px; color:var(--primary-400);">${l.department}</div>
                                </div>
                            </div>
                        </td>
                        <td><strong>${l.leave_type}</strong></td>
                        <td>${l.start_date} &rarr; ${l.end_date} (${l.days_count} d)</td>
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
            Toast.success('Updated', `Leave request #${leaveId} was ${newStatus}.`);
            await this.loadAllLeavesHR();
        } catch (err) {
            Toast.error('Update Failed', err.message);
        }
    }
}

window.LeaveModalComponent = LeaveModalComponent;
