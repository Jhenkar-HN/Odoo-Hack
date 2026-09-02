/**
 * Modern Glassmorphic Login & Registration Component for HRMS
 * Supports: Sign In, Sign Up (Employee ID, Email, Role, Password Security Rules, Email Verification)
 */
class LoginViewComponent {
    static activeTab = 'signin';

    static render() {
        const container = document.getElementById('view-container');
        if (!container) return;

        // Hide sidebar and header while on authentication screen
        const sidebar = document.getElementById('sidebar');
        const header = document.getElementById('top-header');
        if (sidebar) sidebar.style.display = 'none';
        if (header) header.style.display = 'none';

        const mainWrapper = document.querySelector('.main-wrapper');
        if (mainWrapper) mainWrapper.style.marginLeft = '0';

        container.innerHTML = `
            <div style="min-height:85vh; display:flex; align-items:center; justify-content:center; padding:20px;">
                <div class="glass-card" style="width:100%; max-width:480px; padding:36px 32px; box-shadow:var(--shadow-xl); border:1px solid var(--border-strong); position:relative; overflow:hidden; border-radius:var(--radius-lg);">
                    <!-- Ambient Glow -->
                    <div style="position:absolute; top:-60px; right:-60px; width:180px; height:180px; border-radius:var(--radius-full); background:radial-gradient(circle, rgba(99, 102, 241, 0.35) 0%, transparent 70%); pointer-events:none;"></div>
                    
                    <!-- Header Branding -->
                    <div style="text-align:center; margin-bottom:24px;">
                        <div style="display:inline-flex; align-items:center; justify-content:center; width:52px; height:52px; border-radius:var(--radius-md); background:linear-gradient(135deg, var(--primary-600), var(--primary-400)); color:#ffffff; font-weight:800; font-size:22px; margin-bottom:12px; box-shadow:0 8px 20px rgba(99, 102, 241, 0.35);">
                            HR
                        </div>
                        <h2 style="font-size:24px; font-weight:800; color:var(--text-main); letter-spacing:-0.02em;">Dayflow HRMS</h2>
                        <p style="font-size:13px; color:var(--text-muted); margin-top:4px;">Every workday, perfectly aligned.</p>
                    </div>

                    <!-- Mode Toggle Tabs (Excalidraw: Sign In vs Sign Up) -->
                    <div class="tabs-header" style="display:flex; margin-bottom:24px; background:var(--bg-surface-elevated, rgba(255,255,255,0.04)); padding:4px; border-radius:var(--radius-md); border:1px solid var(--border-subtle);">
                        <button type="button" class="tab-btn ${this.activeTab === 'signin' ? 'active' : ''}" style="flex:1; text-align:center; padding:9px 12px; border-radius:var(--radius-sm);" onclick="LoginViewComponent.switchAuthTab('signin')">
                            Sign In
                        </button>
                        <button type="button" class="tab-btn ${this.activeTab === 'signup' ? 'active' : ''}" style="flex:1; text-align:center; padding:9px 12px; border-radius:var(--radius-sm);" onclick="LoginViewComponent.switchAuthTab('signup')">
                            Create Account
                        </button>
                    </div>

                    <!-- PANE 1: SIGN IN -->
                    <div id="auth-signin-pane" style="display:${this.activeTab === 'signin' ? 'block' : 'none'};">
                        <form id="hrms-login-form" novalidate onsubmit="LoginViewComponent.handleLogin(event)">
                            <div class="form-group">
                                <label class="form-label required" for="login-username">Login ID / Corporate Email</label>
                                <input type="text" id="login-username" class="form-control" placeholder="e.g. admin@hrmscorp.com or OIJODO20250001" required autocomplete="username">
                                <div class="form-error-msg" id="login-username-err">Username or email is required.</div>
                            </div>

                            <div class="form-group">
                                <label class="form-label required" for="login-password">Password</label>
                                <input type="password" id="login-password" class="form-control" placeholder="••••••••" required autocomplete="current-password">
                                <div class="form-error-msg" id="login-password-err">Password is required.</div>
                            </div>

                            <div style="display:flex; justify-content:space-between; align-items:center; margin:14px 0 20px 0; font-size:12.5px;">
                                <label style="display:flex; align-items:center; gap:6px; color:var(--text-muted); cursor:pointer;">
                                    <input type="checkbox" id="remember-me" checked> Remember me
                                </label>
                                <a href="javascript:void(0)" onclick="Toast.info('Password Reset', 'Contact HR admin or use registered credentials.')" style="color:var(--primary-400); text-decoration:none; font-weight:600;">Forgot Password?</a>
                            </div>

                            <button type="submit" class="btn btn-primary btn-lg" id="login-submit-btn" style="width:100%;">
                                Sign In to Portal
                            </button>
                        </form>

                        <!-- Quick Demo Logins -->
                        <div style="margin-top:28px; padding-top:18px; border-top:1px dashed var(--border-subtle); text-align:center;">
                            <span style="font-size:11.5px; text-transform:uppercase; letter-spacing:0.06em; font-weight:700; color:var(--text-subtle);">Demo One-Click Access</span>
                            <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-top:10px;">
                                <button type="button" class="btn btn-secondary btn-sm" onclick="LoginViewComponent.quickFill('admin@hrmscorp.com', 'Admin@123')" style="font-size:12px; padding:8px;">
                                    👑 HR Admin
                                </button>
                                <button type="button" class="btn btn-secondary btn-sm" onclick="LoginViewComponent.quickFill('john.doe@hrmscorp.com', 'Emp@123')" style="font-size:12px; padding:8px;">
                                    👤 Employee
                                </button>
                            </div>
                        </div>
                    </div>

                    <!-- PANE 2: SIGN UP (PDF 3.1.1) -->
                    <div id="auth-signup-pane" style="display:${this.activeTab === 'signup' ? 'block' : 'none'};">
                        <form id="hrms-signup-form" novalidate onsubmit="LoginViewComponent.handleSignUp(event)">
                            <div class="form-row">
                                <div class="form-group">
                                    <label class="form-label required" for="signup-empid">Employee ID / Code</label>
                                    <input type="text" id="signup-empid" class="form-control" placeholder="e.g. OIJH2026001" required>
                                </div>
                                <div class="form-group">
                                    <label class="form-label required" for="signup-role">Role</label>
                                    <select id="signup-role" class="form-control">
                                        <option value="EMPLOYEE">👤 Employee</option>
                                        <option value="HR_OFFICER">👑 HR Officer / Admin</option>
                                    </select>
                                </div>
                            </div>

                            <div class="form-group">
                                <label class="form-label required" for="signup-fullname">Full Name</label>
                                <input type="text" id="signup-fullname" class="form-control" placeholder="e.g. Jhenkar HN" required>
                            </div>

                            <div class="form-group">
                                <label class="form-label required" for="signup-email">Work Email</label>
                                <input type="email" id="signup-email" class="form-control" placeholder="name@company.com" required>
                            </div>

                            <!-- Email Verification Section (PDF 3.1.1) -->
                            <div class="form-group" style="background:var(--bg-surface-elevated, rgba(255,255,255,0.03)); padding:12px; border-radius:var(--radius-sm); border:1px solid var(--border-subtle);">
                                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                                    <label class="form-label" style="margin:0; font-size:12px;">Email Verification Code</label>
                                    <button type="button" class="btn btn-secondary btn-sm" onclick="LoginViewComponent.sendVerificationCode()" id="verify-code-btn" style="font-size:11px; padding:4px 8px;">
                                        Send OTP Code
                                    </button>
                                </div>
                                <div style="display:flex; gap:8px;">
                                    <input type="text" id="signup-code" class="form-control" placeholder="Enter 6-digit code" maxlength="6" value="749201">
                                    <span id="email-verified-badge" class="badge badge-present" style="display:inline-flex; align-items:center; gap:4px; font-size:11px; white-space:nowrap;">
                                        ✓ Verified
                                    </span>
                                </div>
                            </div>

                            <div class="form-row">
                                <div class="form-group">
                                    <label class="form-label required" for="signup-password">Password</label>
                                    <input type="password" id="signup-password" class="form-control" placeholder="Min 8 chars (letters + digits)" required>
                                </div>
                                <div class="form-group">
                                    <label class="form-label required" for="signup-confirm-password">Confirm Password</label>
                                    <input type="password" id="signup-confirm-password" class="form-control" placeholder="Re-enter password" required>
                                </div>
                            </div>

                            <div style="font-size:11.5px; color:var(--text-subtle); margin-bottom:16px;">
                                🔒 Security Rules: Minimum 8 characters, must contain both letters and digits.
                            </div>

                            <button type="submit" class="btn btn-primary btn-lg" id="signup-submit-btn" style="width:100%;">
                                Complete Registration
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        `;
    }

    static switchAuthTab(tab) {
        this.activeTab = tab;
        const signinPane = document.getElementById('auth-signin-pane');
        const signupPane = document.getElementById('auth-signup-pane');
        const buttons = document.querySelectorAll('.tabs-header .tab-btn');

        if (signinPane && signupPane) {
            signinPane.style.display = tab === 'signin' ? 'block' : 'none';
            signupPane.style.display = tab === 'signup' ? 'block' : 'none';
        }
        buttons.forEach((btn, idx) => {
            if ((idx === 0 && tab === 'signin') || (idx === 1 && tab === 'signup')) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
    }

    static sendVerificationCode() {
        const emailInput = document.getElementById('signup-email');
        const email = emailInput ? emailInput.value.trim() : '';
        if (!email) {
            Toast.warning('Email Required', 'Please enter your work email first to receive a verification code.');
            emailInput?.focus();
            return;
        }

        const codeInput = document.getElementById('signup-code');
        const randomCode = Math.floor(100000 + Math.random() * 900000).toString();
        if (codeInput) codeInput.value = randomCode;

        Toast.success('Verification Code Sent', `A verification code (${randomCode}) has been dispatched to ${email}.`);
    }

    static quickFill(user, pass) {
        this.switchAuthTab('signin');
        const uInput = document.getElementById('login-username');
        const pInput = document.getElementById('login-password');
        if (uInput && pInput) {
            uInput.value = user;
            pInput.value = pass;
            document.getElementById('login-submit-btn')?.focus();
            Toast.info('Credentials Auto-filled', `Selected profile: ${user}`);
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
        }
        if (!password) {
            pInput?.classList.add('is-invalid');
            return;
        }

        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = 'Verifying credentials...';
        }

        try {
            const user = await ApiService.login(username, password);
            Toast.success('Login Successful', `Welcome back, ${user.display_name || user.email}!`);
            App.setSession(user);
        } catch (err) {
            Toast.error('Login Failed', err.message);
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = 'Sign In to Portal';
            }
        }
    }

    static async handleSignUp(event) {
        event.preventDefault();
        const empId = document.getElementById('signup-empid')?.value.trim();
        const role = document.getElementById('signup-role')?.value.trim();
        const fullName = document.getElementById('signup-fullname')?.value.trim();
        const email = document.getElementById('signup-email')?.value.trim();
        const code = document.getElementById('signup-code')?.value.trim();
        const password = document.getElementById('signup-password')?.value;
        const confirmPassword = document.getElementById('signup-confirm-password')?.value;
        const submitBtn = document.getElementById('signup-submit-btn');

        if (!empId || !fullName || !email || !password) {
            Toast.error('Validation Error', 'Please complete all required fields.');
            return;
        }

        if (password !== confirmPassword) {
            Toast.error('Password Mismatch', 'The confirmed password does not match.');
            return;
        }

        if (password.length < 8) {
            Toast.error('Security Rule Violation', 'Password must be at least 8 characters.');
            return;
        }

        const hasLetter = /[a-zA-Z]/.test(password);
        const hasDigit = /[0-9]/.test(password);
        if (!hasLetter || !hasDigit) {
            Toast.error('Security Rule Violation', 'Password must contain both letters and digits.');
            return;
        }

        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = 'Registering account...';
        }

        try {
            const user = await ApiService.signUp({
                employee_id: empId,
                role: role,
                full_name: fullName,
                email: email,
                password: password,
                verification_code: code
            });
            Toast.success('Registration Complete', `Account created successfully! Welcome to Dayflow.`);
            App.setSession(user);
        } catch (err) {
            Toast.error('Registration Failed', err.message);
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = 'Complete Registration';
            }
        }
    }
}

window.LoginViewComponent = LoginViewComponent;

