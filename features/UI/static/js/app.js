/**
 * Application Core & Routing Controller with Authentication & RBAC
 */
class HRMSApp {
    constructor() {
        this.currentUser = null;
        this.state = {
            currentView: 'dashboard',
            selectedEmployeeId: null,
            viewMode: localStorage.getItem('hrms_view_mode') || 'cards', // 'cards' | 'table'
            searchQuery: '',
            filterDept: 'all',
            filterStatus: 'all',
            filterAttendance: 'all',
            sortBy: 'id',
            sortOrder: 'desc',
            page: 1,
            limit: 24,
            employees: [],
            totalEmployees: 0,
        };

        this.searchDebounceTimer = null;
        this.statusPollingInterval = null;
    }

    init() {
        // Init theme from storage
        const savedTheme = localStorage.getItem('hrms_theme') || 'dark';
        document.documentElement.setAttribute('data-theme', savedTheme);

        // Load authenticated user from localStorage
        try {
            const rawUser = localStorage.getItem('hrms_user');
            if (rawUser) {
                this.currentUser = JSON.parse(rawUser);
                this.currentUser.role = String(this.currentUser.role || 'EMPLOYEE').toUpperCase();
                this.currentUser.token = this.currentUser.access_token || this.currentUser.token || '';
                this.currentUser.display_name = this.currentUser.display_name || this.currentUser.email || this.currentUser.login_id;
                localStorage.setItem('hrms_user', JSON.stringify(this.currentUser));
            }
        } catch (e) {
            this.currentUser = null;
        }

        // Parse initial URL hash or route
        window.addEventListener('hashchange', () => this.handleHashChange());
        this.handleHashChange();

        // Start real-time background status polling (every 20 seconds)
        this.startStatusPolling();
    }

    setSession(user) {
        user = {
            ...user,
            token: user.access_token,
            display_name: user.display_name || user.email || user.login_id,
            role: String(user.role || 'EMPLOYEE').toUpperCase(),
        };
        this.currentUser = user;
        localStorage.setItem('hrms_user', JSON.stringify(user));
        
        // Restore sidebar and header display
        const sidebar = document.getElementById('sidebar');
        const header = document.getElementById('top-header');
        if (sidebar) sidebar.style.display = 'flex';
        if (header) header.style.display = 'flex';
        const mainWrapper = document.querySelector('.main-wrapper');
        if (mainWrapper && window.innerWidth > 1024) mainWrapper.style.marginLeft = 'var(--sidebar-width)';

        if (['ADMIN', 'HR_OFFICER'].includes(String(user.role).toUpperCase())) {
            this.navigate('dashboard');
        } else {
            this.navigate('profile', user.employee_id || 1);
        }
    }

    logout() {
        this.stopStatusPolling();
        this.currentUser = null;
        localStorage.removeItem('hrms_user');
        Toast.info('Signed Out', 'You have been logged out of your session.');
        this.navigate('login');
    }

    handleHashChange() {
        const hash = window.location.hash.replace('#', '') || (this.currentUser ? 'dashboard' : 'login');
        const parts = hash.split('/');
        let view = parts[0] || (this.currentUser ? 'dashboard' : 'login');
        const param = parts[1] || null;

        // Force login view if unauthenticated
        if (!this.currentUser) {
            view = 'login';
        }

        this.renderView(view, param);
    }

    navigate(view, param = null) {
        if (param) {
            window.location.hash = `${view}/${param}`;
        } else {
            window.location.hash = view;
        }
    }

    async renderView(view, param = null) {
        // If not logged in, render login
        if (!this.currentUser || view === 'login') {
            this.state.currentView = 'login';
            LoginViewComponent.render();
            return;
        }

        // Permission guard for Employee role
        const isHR = ['ADMIN', 'HR_OFFICER'].includes(String(this.currentUser.role).toUpperCase());
        if (!isHR && (view === 'add-employee' || view === 'edit-employee')) {
            Toast.error('Access Denied', 'Only HR Administrators are authorized to create or edit employee records.');
            this.navigate('employees');
            return;
        }

        // Ensure sidebar and header are visible
        const sidebar = document.getElementById('sidebar');
        const header = document.getElementById('top-header');
        if (sidebar) sidebar.style.display = 'flex';
        if (header) header.style.display = 'flex';
        const mainWrapper = document.querySelector('.main-wrapper');
        if (mainWrapper && window.innerWidth > 1024) mainWrapper.style.marginLeft = 'var(--sidebar-width)';

        this.state.currentView = view;
        this.state.selectedEmployeeId = param;

        // Close mobile sidebar if open
        if (sidebar) sidebar.classList.remove('open');

        // Render Shell Chrome
        SidebarComponent.render(view);

        const titles = {
            'dashboard': isHR ? 'Admin & HR Dashboard' : 'Employee Dashboard',
            'attendance': 'Attendance Management',
            'leaves': isHR ? 'Leave Approvals' : 'Time-Off & Leaves',
            'payroll': 'Payroll & Salary Slips',
            'employees': isHR ? 'Employee Directory' : 'Team Directory',
            'add-employee': 'Onboard Employee',
            'edit-employee': 'Edit Employee Record',
            'profile': 'Employee Profile'
        };
        HeaderComponent.render(titles[view] || 'Dayflow HRMS', view);

        const container = document.getElementById('view-container');
        if (!container) return;

        switch (view) {
            case 'dashboard':
                if (isHR) {
                    await StatsViewComponent.render();
                } else {
                    await EmployeeDashboardComponent.render();
                }
                break;
            case 'attendance':
                await AttendanceViewComponent.render();
                break;
            case 'leaves':
                await LeaveModalComponent.renderPageView();
                break;
            case 'payroll':
                await PayrollViewComponent.render(param);
                break;
            case 'employees':
                await this.renderEmployeeDirectory();
                break;
            case 'add-employee':
                container.innerHTML = EmployeeFormComponent.render();
                EmployeeFormComponent.init();
                break;
            case 'edit-employee':
                await this.renderEditEmployee(param);
                break;
            case 'profile':
                await this.renderProfileView(param || this.currentUser.employee_id || 1);
                break;
            default:
                if (isHR) {
                    await StatsViewComponent.render();
                } else {
                    await EmployeeDashboardComponent.render();
                }
                break;
        }
    }

    async renderEmployeeDirectory() {
        const container = document.getElementById('view-container');
        if (!container) return;

        const isHR = ['ADMIN', 'HR_OFFICER'].includes(String(this.currentUser?.role || '').toUpperCase());

        let depts = ["Engineering", "Design", "Human Resources", "Finance", "Marketing", "Sales", "Operations"];
        try {
            depts = await ApiService.getDepartments();
        } catch (e) {}

        const deptOptions = depts.map(d => `<option value="${d}" ${this.state.filterDept === d ? 'selected' : ''}>${d}</option>`).join('');

        container.innerHTML = `
            <div class="control-bar">
                <div class="search-input-wrapper">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
                    <input type="text" id="global-search-input" class="search-input" placeholder="Search by name, role, email, phone, skills, ID..." value="${this.state.searchQuery}">
                </div>

                <div class="filter-group">
                    <select class="filter-select" id="dept-filter-select" onchange="App.handleDeptFilter(this.value)">
                        <option value="all">All Departments</option>
                        ${deptOptions}
                    </select>

                    <select class="filter-select" id="status-filter-select" onchange="App.handleStatusFilter(this.value)">
                        <option value="all" ${this.state.filterStatus === 'all' ? 'selected' : ''}>All Statuses</option>
                        <option value="active" ${this.state.filterStatus === 'active' ? 'selected' : ''}>Active</option>
                        <option value="inactive" ${this.state.filterStatus === 'inactive' ? 'selected' : ''}>Inactive</option>
                    </select>

                    <select class="filter-select" id="attendance-filter-select" onchange="App.handleAttendanceFilter(this.value)">
                        <option value="all" ${this.state.filterAttendance === 'all' ? 'selected' : ''}>All Attendance</option>
                        <option value="present" ${this.state.filterAttendance === 'present' ? 'selected' : ''}>🟢 Present</option>
                        <option value="absent" ${this.state.filterAttendance === 'absent' ? 'selected' : ''}>🟡 Absent</option>
                        <option value="on_leave" ${this.state.filterAttendance === 'on_leave' ? 'selected' : ''}>✈️ On Leave</option>
                    </select>

                    <div class="view-toggle">
                        <button class="view-toggle-btn ${this.state.viewMode === 'cards' ? 'active' : ''}" onclick="App.setViewMode('cards')" title="Grid Cards View">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>
                        </button>
                        <button class="view-toggle-btn ${this.state.viewMode === 'table' ? 'active' : ''}" onclick="App.setViewMode('table')" title="Dense Table View">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="8" y1="6" x2="21" y2="6"></line><line x1="8" y1="12" x2="21" y2="12"></line><line x1="8" y1="18" x2="21" y2="18"></line><line x1="3" y1="6" x2="3.01" y2="6"></line><line x1="3" y1="12" x2="3.01" y2="12"></line><line x1="3" y1="18" x2="3.01" y2="18"></line></svg>
                        </button>
                    </div>

                    ${isHR ? `
                    <button class="btn btn-primary btn-sm" onclick="App.navigate('add-employee')">
                        + Add Employee
                    </button>
                    ` : ''}
                </div>
            </div>

            <!-- List Container -->
            <div id="employees-content-area" style="margin-top:20px;">
                <div class="employee-grid">
                    <div class="glass-card skeleton" style="height:220px;"></div>
                    <div class="glass-card skeleton" style="height:220px;"></div>
                    <div class="glass-card skeleton" style="height:220px;"></div>
                </div>
            </div>
        `;

        // Search Input event with debounce
        const searchInput = document.getElementById('global-search-input');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                clearTimeout(this.searchDebounceTimer);
                this.searchDebounceTimer = setTimeout(() => {
                    this.state.searchQuery = e.target.value;
                    this.fetchAndRenderEmployees();
                }, 300);
            });
        }

        await this.fetchAndRenderEmployees();
    }

    async fetchAndRenderEmployees() {
        const area = document.getElementById('employees-content-area');
        if (!area) return;

        try {
            const res = await ApiService.getEmployees({
                search: this.state.searchQuery,
                department: this.state.filterDept,
                status: this.state.filterStatus,
                attendance_status: this.state.filterAttendance,
                sort_by: this.state.sortBy,
                sort_order: this.state.sortOrder,
                page: this.state.page,
                limit: this.state.limit
            });

            this.state.employees = res.items || [];
            this.state.totalEmployees = res.total || 0;

            if (this.state.employees.length === 0) {
                const isHR = ['ADMIN', 'HR_OFFICER'].includes(String(this.currentUser?.role || '').toUpperCase());
                area.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-state-icon">
                            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
                        </div>
                        <div class="empty-state-title">No employees matched your criteria</div>
                        <div class="empty-state-text">Try modifying your search keywords or clearing active filters.</div>
                        ${isHR ? `<button class="btn btn-primary" onclick="App.navigate('add-employee')">Add Employee</button>` : ''}
                    </div>
                `;
                return;
            }

            if (this.state.viewMode === 'cards') {
                const cardsHtml = this.state.employees.map(emp => EmployeeCardComponent.render(emp)).join('');
                area.innerHTML = `<div class="employee-grid">${cardsHtml}</div>`;
            } else {
                area.innerHTML = EmployeeTableComponent.render(this.state.employees);
            }
        } catch (err) {
            Toast.error('Load Failed', err.message);
            area.innerHTML = `<div class="empty-state"><div class="empty-state-title">Error loading employees</div><div class="empty-state-text">${err.message}</div></div>`;
        }
    }

    startStatusPolling() {
        this.stopStatusPolling();
        // Polling interval between 15-30s (20s)
        this.statusPollingInterval = setInterval(() => {
            if (this.currentUser && this.state.currentView === 'employees') {
                this.refreshEmployeeStatusesSilent();
            } else if (this.currentUser && this.state.currentView === 'dashboard') {
                if (typeof StatsViewComponent !== 'undefined' && StatsViewComponent.render) {
                    // Refresh dashboard stats silently if available
                }
            }
        }, 20000);
    }

    stopStatusPolling() {
        if (this.statusPollingInterval) {
            clearInterval(this.statusPollingInterval);
            this.statusPollingInterval = null;
        }
    }

    async refreshEmployeeStatusesSilent() {
        if (!this.currentUser) return;
        try {
            const res = await ApiService.getEmployees({
                search: this.state.searchQuery,
                department: this.state.filterDept,
                status: this.state.filterStatus,
                attendance_status: this.state.filterAttendance,
                sort_by: this.state.sortBy,
                sort_order: this.state.sortOrder,
                page: this.state.page,
                limit: this.state.limit
            });

            this.state.employees = res.items || [];
            this.state.totalEmployees = res.total || 0;

            // Live in-place DOM update without full page reload or scroll disruption
            this.state.employees.forEach(emp => {
                const attStatus = (emp.status || emp.attendance_status || 'absent').toLowerCase();
                const isPresent = attStatus === 'present';
                const isOnLeave = attStatus === 'on_leave';

                const badgeHtml = isPresent ? 
                    `<span class="badge badge-present"><span class="badge-dot" style="background:#10b981;"></span>Present</span>` : 
                    (isOnLeave ? 
                        `<span class="badge badge-leave" style="color:#f97316; border-color:rgba(249,115,22,0.3); background:rgba(249,115,22,0.1);"><span class="badge-dot" style="background:#f97316;"></span>On Leave</span>` : 
                        `<span class="badge badge-absent" style="color:#eab308; border-color:rgba(234,179,8,0.3); background:rgba(234,179,8,0.1);"><span class="badge-dot" style="background:#eab308;"></span>Absent</span>`);

                const card = document.getElementById(`emp-card-${emp.id}`);
                if (card) {
                    const dot = card.querySelector('.card-attendance-dot');
                    if (dot) {
                        dot.className = `card-attendance-dot ${attStatus}`;
                        dot.title = `Status: ${attStatus}`;
                    }
                    const indicator = card.querySelector('.card-status-indicator');
                    if (indicator) {
                        indicator.innerHTML = badgeHtml;
                    }
                }
            });
        } catch (e) {
            // Background polling error is non-blocking
        }
    }

    setViewMode(mode) {
        this.state.viewMode = mode;
        localStorage.setItem('hrms_view_mode', mode);
        this.renderEmployeeDirectory();
    }

    handleDeptFilter(val) {
        this.state.filterDept = val;
        this.fetchAndRenderEmployees();
    }

    handleStatusFilter(val) {
        this.state.filterStatus = val;
        this.fetchAndRenderEmployees();
    }

    handleAttendanceFilter(val) {
        this.state.filterAttendance = val;
        this.fetchAndRenderEmployees();
    }

    setSort(col) {
        if (this.state.sortBy === col) {
            this.state.sortOrder = this.state.sortOrder === 'asc' ? 'desc' : 'asc';
        } else {
            this.state.sortBy = col;
            this.state.sortOrder = 'asc';
        }
        this.fetchAndRenderEmployees();
    }

    async renderProfileView(empId) {
        const container = document.getElementById('view-container');
        if (!container) return;

        container.innerHTML = `<div class="glass-card skeleton" style="height:450px;"></div>`;

        try {
            const emp = await ApiService.getEmployee(empId);
            container.innerHTML = EmployeeProfileComponent.render(emp);
        } catch (err) {
            Toast.error('Profile Error', err.message);
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-title">Employee Not Found</div>
                    <div class="empty-state-text">${err.message}</div>
                    <button class="btn btn-primary" onclick="App.navigate('employees')">Return to Directory</button>
                </div>
            `;
        }
    }

    async renderEditEmployee(empId) {
        const container = document.getElementById('view-container');
        if (!container) return;

        if (this.currentUser?.role !== 'hr') {
            Toast.error('Access Denied', 'Only HR can edit employee profiles.');
            this.navigate('employees');
            return;
        }

        container.innerHTML = `<div class="glass-card skeleton" style="height:450px;"></div>`;

        try {
            const emp = await ApiService.getEmployee(empId);
            container.innerHTML = EmployeeFormComponent.render(emp);
            EmployeeFormComponent.init(emp);
        } catch (err) {
            Toast.error('Edit Error', err.message);
            App.navigate('employees');
        }
    }

    promptDelete(empId, empName) {
        if (this.currentUser?.role !== 'hr') {
            Toast.error('Access Denied', 'Only HR can delete or deactivate employees.');
            return;
        }

        const modal = document.getElementById('generic-modal-overlay');
        if (!modal) return;

        modal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-header">
                    <h3 class="modal-title">Deactivate / Delete Employee</h3>
                    <button class="modal-close" onclick="App.closeModal()">&times;</button>
                </div>
                <div class="modal-body">
                    <p style="font-size:14px; color:var(--text-main); margin-bottom:12px;">
                        Are you sure you want to deactivate or delete <strong>${empName}</strong>?
                    </p>
                    <p style="font-size:12.5px; color:var(--text-muted); line-height:1.5;">
                        <strong>Deactivation (Soft Delete)</strong> retains salary records and activity logs while marking the employee inactive.<br>
                        <strong>Permanent Delete (Hard Delete)</strong> removes the employee and all connected logs from the SQLite database.
                    </p>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" onclick="App.closeModal()">Cancel</button>
                    <button class="btn btn-secondary" onclick="App.confirmDelete(${empId}, false)">Deactivate (Soft)</button>
                    <button class="btn btn-danger" onclick="App.confirmDelete(${empId}, true)">Permanent Delete</button>
                </div>
            </div>
        `;

        modal.classList.add('active');
    }

    async confirmDelete(empId, hard) {
        try {
            await ApiService.deleteEmployee(empId, hard);
            Toast.success('Success', `Employee record ${hard ? 'permanently deleted' : 'deactivated'}.`);
            this.closeModal();
            this.navigate('employees');
        } catch (err) {
            Toast.error('Delete Failed', err.message);
        }
    }

    openCheckInModal() {
        const modal = document.getElementById('generic-modal-overlay');
        if (!modal) return;

        const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        const dateStr = new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });

        modal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-header">
                    <h3 class="modal-title">Daily Attendance Systray</h3>
                    <button class="modal-close" onclick="App.closeModal()">&times;</button>
                </div>
                <div class="modal-body" style="text-align:center;">
                    <div style="font-size:32px; font-weight:800; color:var(--text-main); margin-bottom:4px;">${timeStr}</div>
                    <div style="font-size:13px; color:var(--text-muted); margin-bottom:24px;">${dateStr}</div>

                    <p style="font-size:13.5px; color:var(--text-main); margin-bottom:20px;">
                        Record your presence for payroll computation and verified payable working days.
                    </p>

                    <div style="display:flex; justify-content:center; gap:16px; flex-wrap:wrap;">
                        <button class="btn btn-primary btn-lg" onclick="App.markAttendanceSelf('present')">
                            🟢 Check In (Present)
                        </button>
                        <button class="btn btn-secondary btn-lg" onclick="App.closeModal(); LeaveModalComponent.openApplyModal();">
                            ✈️ Apply Time-Off / Leave
                        </button>
                    </div>
                </div>
            </div>
        `;

        modal.classList.add('active');
    }

    async markAttendanceSelf(status) {
        this.closeModal();
        const user = this.currentUser;
        if (user?.employee_id) {
            try {
                await ApiService.toggleAttendance(user.employee_id, status);
            } catch (e) {}
        }

        if (status === 'present') {
            Toast.success('Attendance', 'Successfully checked in for today!');
        } else {
            Toast.info('Time Off', 'Leave request recorded in system.');
        }

        // Real-time status update without full page reload
        this.refreshEmployeeStatusesSilent();

        if (this.state.currentView === 'dashboard') {
            StatsViewComponent.render();
        } else if (this.state.currentView === 'profile') {
            this.renderProfileView(user?.employee_id || 1);
        } else if (this.state.currentView === 'employees') {
            this.fetchAndRenderEmployees();
        }
    }

    openPasswordModal() {
        const modal = document.getElementById('generic-modal-overlay');
        if (!modal) return;

        modal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-header">
                    <h3 class="modal-title">Change Account Password</h3>
                    <button class="modal-close" onclick="App.closeModal()">&times;</button>
                </div>
                <div class="modal-body">
                    <form id="change-password-form" onsubmit="App.handlePasswordChange(event)">
                        <div class="form-group">
                            <label class="form-label required" for="old-pwd">Current Password</label>
                            <input type="password" id="old-pwd" class="form-control" required placeholder="Enter current password">
                        </div>
                        <div class="form-group">
                            <label class="form-label required" for="new-pwd">New Password</label>
                            <input type="password" id="new-pwd" class="form-control" minlength="8" required placeholder="Min. 8 characters (letters & digits)">
                        </div>
                        <div class="form-group">
                            <label class="form-label required" for="confirm-new-pwd">Confirm New Password</label>
                            <input type="password" id="confirm-new-pwd" class="form-control" minlength="8" required placeholder="Confirm new password">
                        </div>
                        <div style="display:flex; justify-content:flex-end; gap:10px; margin-top:20px;">
                            <button type="button" class="btn btn-secondary" onclick="App.closeModal()">Cancel</button>
                            <button type="submit" class="btn btn-primary" id="change-pwd-btn">Update Password</button>
                        </div>
                    </form>
                </div>
            </div>
        `;
        modal.classList.add('active');
    }

    async handlePasswordChange(event) {
        event.preventDefault();
        const oldPassword = document.getElementById('old-pwd')?.value;
        const newPassword = document.getElementById('new-pwd')?.value;
        const confirmPassword = document.getElementById('confirm-new-pwd')?.value;

        if (newPassword !== confirmPassword) {
            Toast.error('Validation Error', 'New passwords do not match.');
            return;
        }

        const btn = document.getElementById('change-pwd-btn');
        if (btn) {
            btn.disabled = true;
            btn.innerText = 'Updating...';
        }

        try {
            await ApiService.changePassword(oldPassword, newPassword);
            Toast.success('Password Changed', 'Your password has been updated securely.');
            this.closeModal();
        } catch (err) {
            Toast.error('Change Failed', err.message);
            if (btn) {
                btn.disabled = false;
                btn.innerText = 'Update Password';
            }
        }
    }

    closeModal() {
        const modal = document.getElementById('generic-modal-overlay');
        if (modal) modal.classList.remove('active');
    }
}


window.App = new HRMSApp();
window.addEventListener('DOMContentLoaded', () => window.App.init());
