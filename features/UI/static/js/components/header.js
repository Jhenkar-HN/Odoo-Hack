/**
 * Header Component with Search, Systray Attendance, Theme Toggle, Notification Bell, and User Profile Menu
 */
class HeaderComponent {
    static render(title = "Dashboard", breadcrumb = "Overview") {
        const header = document.getElementById('top-header');
        if (!header) return;

        const user = App.currentUser;
        if (!user) return;

        const isDark = document.documentElement.getAttribute('data-theme') !== 'light';
        const isHR = ['ADMIN', 'HR_OFFICER'].includes(String(user.role || '').toUpperCase());
        const avatar = user.avatar_url || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150';

        header.innerHTML = `
            <div class="header-left">
                <button class="mobile-menu-btn" id="mobile-menu-toggle" aria-label="Toggle Sidebar">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="12" x2="21" y2="12"></line><line x1="3" y1="6" x2="21" y2="6"></line><line x1="3" y1="18" x2="21" y2="18"></line></svg>
                </button>
                <div class="page-breadcrumb">
                    <span>Dayflow HRMS</span>
                    <span>/</span>
                    <span class="breadcrumb-current" id="header-title">${title}</span>
                </div>
            </div>

            <div class="header-right" style="display:flex; align-items:center; gap:12px;">
                <!-- Check-in / Systray Attendance Widget (PDF 3.4) -->
                <div class="systray-attendance" id="systray-attendance-box">
                    <div class="systray-status">
                        <span class="systray-dot" id="systray-dot"></span>
                        <span id="systray-status-text">Checked In</span>
                    </div>
                    <button class="systray-btn check-out" id="systray-toggle-btn" title="Toggle your daily attendance">
                        Check Out
                    </button>
                </div>

                <!-- Notifications Bell (PDF Section 6 Future Enhancements) -->
                <div style="position:relative;" id="notif-bell-container">
                    <button class="icon-btn" id="notif-toggle-btn" title="Notification Alerts" onclick="HeaderComponent.toggleNotifMenu(event)">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path><path d="M13.73 21a2 2 0 0 1-3.46 0"></path></svg>
                        <span class="badge badge-present" style="position:absolute; top:-4px; right:-4px; padding:2px 5px; font-size:10px; border-radius:var(--radius-full);">2</span>
                    </button>
                    <div id="notif-dropdown-menu" class="glass-card" style="display:none; position:absolute; top:45px; right:0; width:280px; padding:12px; z-index:50; box-shadow:var(--shadow-xl); border:1px solid var(--border-strong);">
                        <div style="font-weight:700; font-size:13px; color:var(--text-main); border-bottom:1px solid var(--border-subtle); padding-bottom:8px; margin-bottom:8px; display:flex; justify-content:space-between;">
                            <span>Notifications</span>
                            <span style="font-size:11px; color:var(--primary-400);">Mark all read</span>
                        </div>
                        <div style="display:flex; flex-direction:column; gap:8px; font-size:12px;">
                            <div style="padding:8px; background:var(--bg-surface-elevated); border-radius:var(--radius-sm);">
                                <div style="font-weight:600; color:var(--text-main);">Monthly Payslips Ready</div>
                                <div style="color:var(--text-muted); font-size:11px;">Payslip calculations computed from attendance.</div>
                            </div>
                            <div style="padding:8px; background:var(--bg-surface-elevated); border-radius:var(--radius-sm);">
                                <div style="font-weight:600; color:var(--text-main);">Attendance Tracked</div>
                                <div style="color:var(--text-muted); font-size:11px;">Real-time sync verified with database.</div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Theme Toggle -->
                <button class="icon-btn" id="theme-toggle-btn" title="Toggle Light/Dark Theme">
                    ${isDark ? 
                        `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>` : 
                        `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>`
                    }
                </button>

                <!-- Profile Menu with Avatar Dropdown (Excalidraw lines 57-59) -->
                <div class="user-mini-card" style="cursor: pointer; position:relative;" id="user-header-profile" onclick="HeaderComponent.toggleUserMenu(event)">
                    <img src="${avatar}" alt="${user.display_name}" class="user-avatar" style="width:34px; height:34px; border:2px solid var(--primary-500);">
                    <div id="user-dropdown-menu" class="glass-card" style="display:none; position:absolute; top:45px; right:0; width:200px; padding:10px; z-index:50; box-shadow:var(--shadow-xl); border:1px solid var(--border-strong);">
                        <div style="padding:6px 8px; border-bottom:1px solid var(--border-subtle); margin-bottom:6px;">
                            <div style="font-weight:700; font-size:13px; color:var(--text-main); white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${user.display_name}</div>
                            <div style="font-size:11px; color:var(--primary-400); font-weight:600;">${isHR ? '👑 HR Admin' : '👤 Employee'}</div>
                        </div>
                        <button class="btn btn-secondary btn-sm" onclick="App.navigate('profile', ${user.employee_id || 1})" style="width:100%; justify-content:flex-start; margin-bottom:4px; font-size:12px;">
                            👤 My Profile
                        </button>
                        <button class="btn btn-secondary btn-sm" onclick="App.openPasswordModal()" style="width:100%; justify-content:flex-start; margin-bottom:6px; font-size:12px;">
                            🔑 Change Password
                        </button>
                        <button class="btn btn-outline-danger btn-sm" onclick="App.logout()" style="width:100%; justify-content:flex-start; font-size:12px;">
                            🚪 Log Out
                        </button>
                    </div>
                </div>
            </div>
        `;

        this.attachEvents();
        this.updateSystrayAttendance();
    }

    static toggleUserMenu(event) {
        event.stopPropagation();
        const menu = document.getElementById('user-dropdown-menu');
        const notifMenu = document.getElementById('notif-dropdown-menu');
        if (notifMenu) notifMenu.style.display = 'none';
        if (menu) {
            menu.style.display = menu.style.display === 'none' ? 'block' : 'none';
        }
    }

    static toggleNotifMenu(event) {
        event.stopPropagation();
        const userMenu = document.getElementById('user-dropdown-menu');
        const notifMenu = document.getElementById('notif-dropdown-menu');
        if (userMenu) userMenu.style.display = 'none';
        if (notifMenu) {
            notifMenu.style.display = notifMenu.style.display === 'none' ? 'block' : 'none';
        }
    }

    static async updateSystrayAttendance() {
        try {
            const todayAtt = await ApiService.getTodayAttendance().catch(() => null);
            const isCheckedIn = !!(todayAtt && todayAtt.check_in && !todayAtt.check_out);
            const dot = document.getElementById('systray-dot');
            const text = document.getElementById('systray-status-text');
            const btn = document.getElementById('systray-toggle-btn');

            if (dot && text && btn) {
                if (isCheckedIn) {
                    dot.style.background = 'var(--accent-emerald, #10b981)';
                    dot.style.boxShadow = '0 0 8px var(--accent-emerald, #10b981)';
                    text.textContent = 'Checked In';
                    btn.textContent = 'Check Out';
                    btn.className = 'systray-btn check-out';
                } else {
                    dot.style.background = 'var(--accent-amber, #f59e0b)';
                    dot.style.boxShadow = 'none';
                    text.textContent = 'Checked Out';
                    btn.textContent = 'Check In';
                    btn.className = 'systray-btn check-in';
                }
            }
        } catch (e) {}
    }

    static attachEvents() {
        document.addEventListener('click', () => {
            const menu = document.getElementById('user-dropdown-menu');
            const notif = document.getElementById('notif-dropdown-menu');
            if (menu) menu.style.display = 'none';
            if (notif) notif.style.display = 'none';
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
            systrayBtn.onclick = async () => {
                const user = App.currentUser;
                const isCurrentlyCheckedIn = systrayBtn.classList.contains('check-out');
                
                try {
                    if (isCurrentlyCheckedIn) {
                        await ApiService.checkOut();
                        Toast.info('Attendance', 'Checked out at ' + new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));
                    } else {
                        await ApiService.checkIn();
                        Toast.success('Attendance', 'Marked present (Checked In) at ' + new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));
                    }
                    this.updateSystrayAttendance();
                } catch (e) {
                    Toast.error('Attendance Failed', e.message);
                }
            };
        }
    }
}

window.HeaderComponent = HeaderComponent;
