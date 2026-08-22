/**
 * Header Component with Search, Systray Attendance, Theme Toggle, and User Profile Menu
 */
class HeaderComponent {
    static render(title = "Dashboard", breadcrumb = "Overview") {
        const header = document.getElementById('top-header');
        if (!header) return;

        const user = App.currentUser;
        if (!user) return;

        const isDark = document.documentElement.getAttribute('data-theme') !== 'light';
        const isHR = user.role === 'hr';
        const avatar = user.avatar_url || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150';

        header.innerHTML = `
            <div class="header-left">
                <button class="mobile-menu-btn" id="mobile-menu-toggle" aria-label="Toggle Sidebar">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="12" x2="21" y2="12"></line><line x1="3" y1="6" x2="21" y2="6"></line><line x1="3" y1="18" x2="21" y2="18"></line></svg>
                </button>
                <div class="page-breadcrumb">
                    <span>HRMS</span>
                    <span>/</span>
                    <span class="breadcrumb-current" id="header-title">${title}</span>
                </div>
            </div>

            <div class="header-right">
                <!-- Check-in / Systray Attendance Widget -->
                <div class="systray-attendance" id="systray-attendance-box">
                    <div class="systray-status">
                        <span class="systray-dot" id="systray-dot"></span>
                        <span id="systray-status-text">Checked In</span>
                    </div>
                    <button class="systray-btn check-out" id="systray-toggle-btn" title="Toggle your daily attendance">
                        Check Out
                    </button>
                </div>

                <!-- Theme Toggle -->
                <button class="icon-btn" id="theme-toggle-btn" title="Toggle Light/Dark Theme">
                    ${isDark ? 
                        `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>` : 
                        `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>`
                    }
                </button>

                <!-- Profile Menu -->
                <div class="user-mini-card" style="cursor: pointer; position:relative;" id="user-header-profile" onclick="HeaderComponent.toggleUserMenu(event)">
                    <img src="${avatar}" alt="${user.display_name}" class="user-avatar" style="width:34px; height:34px;">
                    <div id="user-dropdown-menu" class="glass-card" style="display:none; position:absolute; top:45px; right:0; width:180px; padding:8px; z-index:50; box-shadow:var(--shadow-xl);">
                        <div style="padding:8px 12px; border-bottom:1px solid var(--border-subtle); margin-bottom:4px;">
                            <div style="font-weight:700; font-size:13px; color:var(--text-main);">${user.display_name}</div>
                            <div style="font-size:11px; color:var(--primary-400);">${isHR ? 'HR Admin' : 'Employee'}</div>
                        </div>
                        ${user.employee_id ? `<button class="btn btn-secondary btn-sm" onclick="App.navigate('profile', ${user.employee_id})" style="width:100%; justify-content:flex-start; margin-bottom:4px;">My Profile</button>` : ''}
                        <button class="btn btn-outline-danger btn-sm" onclick="App.logout()" style="width:100%; justify-content:flex-start;">Sign Out</button>
                    </div>
                </div>
            </div>
        `;

        this.attachEvents();
    }

    static toggleUserMenu(event) {
        event.stopPropagation();
        const menu = document.getElementById('user-dropdown-menu');
        if (menu) {
            menu.style.display = menu.style.display === 'none' ? 'block' : 'none';
        }
    }

    static attachEvents() {
        document.addEventListener('click', () => {
            const menu = document.getElementById('user-dropdown-menu');
            if (menu) menu.style.display = 'none';
        });

        const themeBtn = document.getElementById('theme-toggle-btn');
        if (themeBtn) {
            themeBtn.onclick = () => {
                const current = document.documentElement.getAttribute('data-theme') || 'dark';
                const next = current === 'dark' ? 'light' : 'dark';
                document.documentElement.setAttribute('data-theme', next);
                localStorage.setItem('hrms_theme', next);
                this.render(document.getElementById('header-title')?.textContent);
            };
        }

        const mobileToggle = document.getElementById('mobile-menu-toggle');
        if (mobileToggle) {
            mobileToggle.onclick = () => {
                const sidebar = document.getElementById('sidebar');
                if (sidebar) sidebar.classList.toggle('open');
            };
        }

        const systrayBtn = document.getElementById('systray-toggle-btn');
        if (systrayBtn) {
            let isCheckedIn = true;
            systrayBtn.onclick = async () => {
                const user = App.currentUser;
                isCheckedIn = !isCheckedIn;
                const dot = document.getElementById('systray-dot');
                const text = document.getElementById('systray-status-text');
                
                const newStatus = isCheckedIn ? 'present' : 'absent';
                if (user?.employee_id) {
                    try {
                        await ApiService.toggleAttendance(user.employee_id, newStatus);
                    } catch (e) {}
                }

                if (isCheckedIn) {
                    dot.style.background = 'var(--accent-emerald)';
                    dot.style.boxShadow = '0 0 8px var(--accent-emerald)';
                    text.textContent = 'Checked In';
                    systrayBtn.textContent = 'Check Out';
                    systrayBtn.className = 'systray-btn check-out';
                    Toast.success('Attendance', 'You marked your presence (Checked In) at ' + new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));
                } else {
                    dot.style.background = 'var(--accent-amber)';
                    dot.style.boxShadow = 'none';
                    text.textContent = 'Checked Out';
                    systrayBtn.textContent = 'Check In';
                    systrayBtn.className = 'systray-btn check-in';
                    Toast.info('Attendance', 'You checked out at ' + new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));
                }
            };
        }
    }
}

window.HeaderComponent = HeaderComponent;
