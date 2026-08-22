/**
 * Sidebar Navigation Component with Role-Based Access Controls
 */
class SidebarComponent {
    static render(activeRoute = 'dashboard') {
        const sidebar = document.getElementById('sidebar');
        if (!sidebar) return;

        const user = App.currentUser;
        if (!user) return;

        const isHR = ['ADMIN', 'HR_OFFICER'].includes(String(user.role || '').toUpperCase());
        const roleLabel = isHR ? '👑 HR Admin' : '👤 Employee';
        const avatar = user.avatar_url || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150';

        let navItems = '';
        if (isHR) {
            navItems = `
                <div class="nav-section-title">HR Administration</div>
                <a class="nav-item ${activeRoute === 'dashboard' ? 'active' : ''}" onclick="App.navigate('dashboard')">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>
                    <span>Dashboard</span>
                </a>
                <a class="nav-item ${activeRoute === 'employees' ? 'active' : ''}" onclick="App.navigate('employees')">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
                    <span>Employee Directory</span>
                </a>
                <a class="nav-item ${activeRoute === 'add-employee' ? 'active' : ''}" onclick="App.navigate('add-employee')">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><line x1="20" y1="8" x2="20" y2="14"></line><line x1="23" y1="11" x2="17" y2="11"></line></svg>
                    <span>Add Employee</span>
                </a>
                <a class="nav-item" onclick="LeaveModalComponent.openHRLeaveManager()">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
                    <span>Leave Approvals</span>
                </a>

                <div class="nav-section-title" style="margin-top: 16px;">System Tools</div>
                <a class="nav-item" onclick="App.openCheckInModal()">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 14 14"></polyline></svg>
                    <span>Mark Attendance</span>
                </a>
                <a class="nav-item" onclick="window.open('/docs', '_blank')">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline></svg>
                    <span>Swagger API Docs</span>
                </a>
            `;
        } else {
            // Employee View
            navItems = `
                <div class="nav-section-title">My Workspace</div>
                <a class="nav-item ${activeRoute === 'profile' ? 'active' : ''}" onclick="App.navigate('profile', ${user.employee_id || 1})">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
                    <span>My Profile</span>
                </a>
                <a class="nav-item ${activeRoute === 'employees' ? 'active' : ''}" onclick="App.navigate('employees')">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle></svg>
                    <span>Team Directory (View)</span>
                </a>
                <a class="nav-item" onclick="LeaveModalComponent.openApplyModal()">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M17.8 19.2L16 11l3.5-3.5C21 6 21.5 4 21 3c-1-.5-3 0-4.5 1.5L13 8 4.8 6.2c-.5-.1-.9.1-1.1.5l-.3.5c-.2.5-.1 1 .3 1.3L9 12l-2 3H4l-1 1 3 2 2 3 1-1v-3l3-2 3.5 5.3c.3.4.8.5 1.3.3l.5-.2c.4-.3.6-.7.5-1.2z"></path></svg>
                    <span>Apply for Leave</span>
                </a>
                <a class="nav-item" onclick="App.openCheckInModal()">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 14 14"></polyline></svg>
                    <span>Mark Daily Attendance</span>
                </a>
            `;
        }

        sidebar.innerHTML = `
            <div class="sidebar-header">
                <div class="brand-logo">HR</div>
                <div class="brand-info">
                    <span class="brand-title">HRMS</span>
                    <span class="brand-sub">Enterprise Portal</span>
                </div>
            </div>

            <div class="sidebar-nav">
                ${navItems}
            </div>

            <div class="sidebar-footer" style="flex-direction:column; align-items:stretch; gap:12px;">
                <div class="user-mini-card">
                    <img src="${avatar}" alt="${user.display_name}" class="user-avatar">
                    <div style="display:flex; flex-direction:column; overflow:hidden; flex:1;">
                        <span style="font-weight:700; font-size:13px; color:var(--text-main); white-space:nowrap; text-overflow:ellipsis; overflow:hidden;">${user.display_name}</span>
                        <span style="font-size:11px; color:var(--primary-400); font-weight:600;">${roleLabel}</span>
                    </div>
                </div>
                <button class="btn btn-secondary btn-sm" onclick="App.logout()" style="width:100%; display:flex; gap:8px; justify-content:center;">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><polyline points="16 17 21 12 16 7"></polyline><line x1="21" y1="12" x2="9" y2="12"></line></svg>
                    Sign Out
                </button>
            </div>
        `;
    }
}

window.SidebarComponent = SidebarComponent;
