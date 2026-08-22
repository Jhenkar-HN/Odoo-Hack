/**
 * Modern Glassmorphic Login Component for HRMS
 */
class LoginViewComponent {
    static render() {
        const container = document.getElementById('view-container');
        if (!container) return;

        // Hide sidebar and header while on login screen
        const sidebar = document.getElementById('sidebar');
        const header = document.getElementById('top-header');
        if (sidebar) sidebar.style.display = 'none';
        if (header) header.style.display = 'none';

        const mainWrapper = document.querySelector('.main-wrapper');
        if (mainWrapper) mainWrapper.style.marginLeft = '0';

        container.innerHTML = `
            <div style="min-height:85vh; display:flex; align-items:center; justify-content:center; padding:20px;">
                <div class="glass-card" style="width:100%; max-width:460px; padding:40px 36px; box-shadow:var(--shadow-xl); border:1px solid var(--border-strong); position:relative; overflow:hidden;">
                    <!-- Ambient Glow -->
                    <div style="position:absolute; top:-60px; right:-60px; width:160px; height:160px; border-radius:var(--radius-full); background:radial-gradient(circle, rgba(99, 102, 241, 0.35) 0%, transparent 70%); pointer-events:none;"></div>
                    
                    <!-- Header Branding -->
                    <div style="text-align:center; margin-bottom:28px;">
                        <div style="display:inline-flex; align-items:center; justify-content:center; width:52px; height:52px; border-radius:var(--radius-md); background:linear-gradient(135deg, var(--primary-600), var(--primary-400)); color:#ffffff; font-weight:800; font-size:22px; margin-bottom:12px; box-shadow:0 8px 20px rgba(99, 102, 241, 0.35);">
                            HR
                        </div>
                        <h2 style="font-size:24px; font-weight:800; color:var(--text-main); letter-spacing:-0.02em;">Welcome to HRMS</h2>
                        <p style="font-size:13px; color:var(--text-muted); margin-top:4px;">Sign in to access your enterprise workspace</p>
                    </div>

                    <!-- Login Form -->
                    <form id="hrms-login-form" novalidate onsubmit="LoginViewComponent.handleLogin(event)">
                        <div class="form-group">
                            <label class="form-label required" for="login-username">Login ID / Work Email</label>
                            <input type="text" id="login-username" class="form-control" placeholder="e.g. admin@hrms.com or OIAASH20230001" required autocomplete="username">
                            <div class="form-error-msg" id="login-username-err">Username is required.</div>
                        </div>

                        <div class="form-group">
                            <label class="form-label required" for="login-password">Password</label>
                            <input type="password" id="login-password" class="form-control" placeholder="••••••••" required autocomplete="current-password">
                            <div class="form-error-msg" id="login-password-err">Password is required.</div>
                        </div>

                        <div style="display:flex; justify-content:space-between; align-items:center; margin:16px 0 24px 0; font-size:12.5px;">
                            <label style="display:flex; align-items:center; gap:6px; color:var(--text-muted); cursor:pointer;">
                                <input type="checkbox" id="remember-me" checked> Remember me
                            </label>
                            <a href="javascript:void(0)" onclick="Toast.info('Password Reset', 'Please contact your HR administrator to reset your system credentials.')" style="color:var(--primary-400); text-decoration:none; font-weight:600;">Forgot Password?</a>
                        </div>

                        <button type="submit" class="btn btn-primary btn-lg" id="login-submit-btn" style="width:100%;">
                            Sign In to Portal
                        </button>
                    </form>

                    <!-- Quick Demo Logins -->
                    <div style="margin-top:32px; padding-top:20px; border-top:1px dashed var(--border-subtle); text-align:center;">
                        <span style="font-size:11.5px; text-transform:uppercase; letter-spacing:0.06em; font-weight:700; color:var(--text-subtle);">Demo Quick Access</span>
                        <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-top:12px;">
                            <button type="button" class="btn btn-secondary btn-sm" onclick="LoginViewComponent.quickFill('admin@hrmscorp.com', 'Admin@123')" style="font-size:12px; padding:8px;">
                                👑 HR Admin
                            </button>
                            <button type="button" class="btn btn-secondary btn-sm" onclick="LoginViewComponent.quickFill('john.doe@hrmscorp.com', 'Emp@123')" style="font-size:12px; padding:8px;">
                                👤 Employee
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    static quickFill(user, pass) {
        const uInput = document.getElementById('login-username');
        const pInput = document.getElementById('login-password');
        if (uInput && pInput) {
            uInput.value = user;
            pInput.value = pass;
            document.getElementById('login-submit-btn')?.focus();
            Toast.info('Credentials Auto-filled', `Selected demo profile: ${user}`);
        }
    }

    static async handleLogin(event) {
        event.preventDefault();
        const uInput = document.getElementById('login-username');
        const pInput = document.getElementById('login-password');
        const submitBtn = document.getElementById('login-submit-btn');

        const username = uInput ? uInput.value.trim() : '';
        const password = pInput ? pInput.value.trim() : '';

        if (!username) {
            uInput?.classList.add('is-invalid');
            return;
        } else {
            uInput?.classList.remove('is-invalid');
        }

        if (!password) {
            pInput?.classList.add('is-invalid');
            return;
        } else {
            pInput?.classList.remove('is-invalid');
        }

        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = 'Verifying credentials...';
        }

        try {
            const user = await ApiService.login(username, password);
            Toast.success('Login Successful', `Welcome back, ${user.email || user.login_id}!`);
            App.setSession(user);
        } catch (err) {
            Toast.error('Login Failed', err.message);
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = 'Sign In to Portal';
            }
        }
    }
}

window.LoginViewComponent = LoginViewComponent;
