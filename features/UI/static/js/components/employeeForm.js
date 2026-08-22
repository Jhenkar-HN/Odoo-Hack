/**
 * Add / Edit Employee Multi-Section Dynamic Form Component
 */
class EmployeeFormComponent {
    static render(employee = null) {
        const isEdit = !!employee;
        const formTitle = isEdit ? `Edit Employee: ${employee.full_name}` : "Onboard New Employee";
        const btnText = isEdit ? "Save Changes" : "Create Employee";

        const skills = isEdit && employee.skills ? employee.skills : [
            { name: "JavaScript", level: "Advanced" },
            { name: "Communication", level: "Expert" }
        ];

        const certs = isEdit && employee.certifications ? employee.certifications : [];

        const wage = employee?.monthly_wage || 50000;
        const cancelAction = isEdit ? `App.navigate('profile', ${employee.id})` : `App.navigate('employees')`;

        return `
            <div class="glass-card" style="padding:32px; max-width:1100px; margin:0 auto;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:24px; border-bottom:1px solid var(--border-subtle); padding-bottom:16px;">
                    <div>
                        <h2 style="font-size:22px; font-weight:800; color:var(--text-main);">${formTitle}</h2>
                        <p style="font-size:13px; color:var(--text-muted); margin-top:4px;">
                            ${isEdit ? `Update profile and compensation details for ${employee.login_id}` : "Fill out the fields below. A unique Login ID (e.g. OIJODO20250001) will be auto-generated."}
                        </p>
                    </div>
                    <button type="button" class="btn btn-secondary" onclick="${cancelAction}">
                        Cancel
                    </button>
                </div>

                <!-- Form Section Tabs Header -->
                <div class="tabs-header" id="form-tabs-header">
                    <button class="tab-btn active" onclick="EmployeeFormComponent.switchTab('form-tab-personal', this)">
                        1. Personal & Company
                    </button>
                    <button class="tab-btn" onclick="EmployeeFormComponent.switchTab('form-tab-private', this)">
                        2. Private & Bank
                    </button>
                    <button class="tab-btn" onclick="EmployeeFormComponent.switchTab('form-tab-salary', this)">
                        3. Salary & Wage
                    </button>
                    <button class="tab-btn" onclick="EmployeeFormComponent.switchTab('form-tab-skills', this)">
                        4. Skills & Certifications
                    </button>
                    <button class="tab-btn" onclick="EmployeeFormComponent.switchTab('form-tab-bio', this)">
                        5. Bio & Resume
                    </button>
                </div>

                <form id="employee-main-form" novalidate onsubmit="EmployeeFormComponent.handleSubmit(event, ${isEdit ? employee.id : 'null'})">
                    <!-- TAB 1: Personal & Company Details -->
                    <div class="tab-pane active" id="form-tab-personal">
                        <div class="form-row">
                            <div class="form-group">
                                <label class="form-label required" for="first_name">First Name</label>
                                <input type="text" id="first_name" name="first_name" class="form-control" required value="${employee?.first_name || ''}" placeholder="e.g. Aarav">
                                <div class="form-error-msg">First name is required.</div>
                            </div>
                            <div class="form-group">
                                <label class="form-label required" for="last_name">Last Name</label>
                                <input type="text" id="last_name" name="last_name" class="form-control" required value="${employee?.last_name || ''}" placeholder="e.g. Sharma">
                                <div class="form-error-msg">Last name is required.</div>
                            </div>
                        </div>

                        <div class="form-row">
                            <div class="form-group">
                                <label class="form-label required" for="work_email">Work Email</label>
                                <input type="email" id="work_email" name="work_email" class="form-control" required value="${employee?.work_email || ''}" placeholder="e.g. aarav.sharma@odooindia.com">
                                <div class="form-hint">Corporate email (duplicate checking enforced).</div>
                                <div class="form-error-msg">Valid corporate email is required.</div>
                            </div>
                            <div class="form-group">
                                <label class="form-label required" for="phone">Phone Number</label>
                                <input type="tel" id="phone" name="phone" class="form-control" required value="${employee?.phone || ''}" placeholder="e.g. +91 98234 56789">
                                <div class="form-hint">7-15 digit contact number.</div>
                                <div class="form-error-msg">Valid phone number is required.</div>
                            </div>
                        </div>

                        <div class="form-row-3">
                            <div class="form-group">
                                <label class="form-label required" for="department">Department</label>
                                <select id="department" name="department" class="form-control" required>
                                    <option value="Engineering" ${employee?.department === 'Engineering' ? 'selected' : ''}>Engineering</option>
                                    <option value="Design" ${employee?.department === 'Design' ? 'selected' : ''}>Design</option>
                                    <option value="Human Resources" ${employee?.department === 'Human Resources' ? 'selected' : ''}>Human Resources</option>
                                    <option value="Finance" ${employee?.department === 'Finance' ? 'selected' : ''}>Finance</option>
                                    <option value="Marketing" ${employee?.department === 'Marketing' ? 'selected' : ''}>Marketing</option>
                                    <option value="Sales" ${employee?.department === 'Sales' ? 'selected' : ''}>Sales</option>
                                    <option value="Operations" ${employee?.department === 'Operations' ? 'selected' : ''}>Operations</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label class="form-label required" for="job_position">Job Position / Title</label>
                                <input type="text" id="job_position" name="job_position" class="form-control" required value="${employee?.job_position || ''}" placeholder="e.g. Senior Software Engineer">
                                <div class="form-error-msg">Job title is required.</div>
                            </div>
                            <div class="form-group">
                                <label class="form-label required" for="date_of_joining">Date of Joining</label>
                                <input type="date" id="date_of_joining" name="date_of_joining" class="form-control" required value="${employee?.date_of_joining || new Date().toISOString().split('T')[0]}">
                                <div class="form-error-msg">Joining date is required.</div>
                            </div>
                        </div>

                        <div class="form-row">
                            <div class="form-group">
                                <label class="form-label" for="manager_name">Manager Name</label>
                                <input type="text" id="manager_name" name="manager_name" class="form-control" value="${employee?.manager_name || ''}" placeholder="e.g. Vikram Malhotra">
                            </div>
                            <div class="form-group">
                                <label class="form-label" for="location">Work Location</label>
                                <input type="text" id="location" name="location" class="form-control" value="${employee?.location || 'Headquarters'}" placeholder="e.g. Mumbai, India">
                            </div>
                        </div>

                        <div class="form-row">
                            <div class="form-group">
                                <label class="form-label" for="work_hours">Work Schedule</label>
                                <input type="text" id="work_hours" name="work_hours" class="form-control" value="${employee?.work_hours || '40 hrs/week (09:00 - 18:00)'}" placeholder="e.g. 40 hrs/week">
                            </div>
                            <div class="form-group">
                                <label class="form-label" for="avatar_url">Profile Avatar URL</label>
                                <input type="url" id="avatar_url" name="avatar_url" class="form-control" value="${employee?.avatar_url || ''}" placeholder="https://...">
                            </div>
                        </div>

                        <div style="display:flex; justify-content:flex-end; margin-top:20px;">
                            <button type="button" class="btn btn-primary" onclick="EmployeeFormComponent.switchTabByIndex(1)">
                                Next: Private & Bank &rarr;
                            </button>
                        </div>
                    </div>

                    <!-- TAB 2: Private & Bank Details -->
                    <div class="tab-pane" id="form-tab-private">
                        <h4 style="font-size:15px; font-weight:700; color:var(--text-main); margin-bottom:16px;">Demographic Information</h4>
                        <div class="form-row-3">
                            <div class="form-group">
                                <label class="form-label" for="date_of_birth">Date of Birth</label>
                                <input type="date" id="date_of_birth" name="date_of_birth" class="form-control" value="${employee?.date_of_birth || ''}">
                            </div>
                            <div class="form-group">
                                <label class="form-label" for="gender">Gender</label>
                                <select id="gender" name="gender" class="form-control">
                                    <option value="Male" ${employee?.gender === 'Male' ? 'selected' : ''}>Male</option>
                                    <option value="Female" ${employee?.gender === 'Female' ? 'selected' : ''}>Female</option>
                                    <option value="Other" ${employee?.gender === 'Other' ? 'selected' : ''}>Other</option>
                                    <option value="Not Specified" ${employee?.gender === 'Not Specified' ? 'selected' : ''}>Not Specified</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label class="form-label" for="marital_status">Marital Status</label>
                                <select id="marital_status" name="marital_status" class="form-control">
                                    <option value="Single" ${employee?.marital_status === 'Single' ? 'selected' : ''}>Single</option>
                                    <option value="Married" ${employee?.marital_status === 'Married' ? 'selected' : ''}>Married</option>
                                    <option value="Divorced" ${employee?.marital_status === 'Divorced' ? 'selected' : ''}>Divorced</option>
                                </select>
                            </div>
                        </div>

                        <div class="form-row">
                            <div class="form-group">
                                <label class="form-label" for="personal_email">Personal Email</label>
                                <input type="email" id="personal_email" name="personal_email" class="form-control" value="${employee?.personal_email || ''}" placeholder="e.g. name@gmail.com">
                            </div>
                            <div class="form-group">
                                <label class="form-label" for="nationality">Nationality</label>
                                <input type="text" id="nationality" name="nationality" class="form-control" value="${employee?.nationality || 'Indian'}">
                            </div>
                        </div>

                        <div class="form-group">
                            <label class="form-label" for="residing_address">Residing Address</label>
                            <textarea id="residing_address" name="residing_address" class="form-control" rows="2" placeholder="Full residential street address, city, pin code">${employee?.residing_address || ''}</textarea>
                        </div>

                        <div class="form-row">
                            <div class="form-group">
                                <label class="form-label" for="pan_number">PAN Number</label>
                                <input type="text" id="pan_number" name="pan_number" class="form-control" value="${employee?.pan_number || ''}" placeholder="e.g. ABCDE1234F" style="text-transform:uppercase;">
                            </div>
                            <div class="form-group">
                                <label class="form-label" for="uan_number">UAN Number</label>
                                <input type="text" id="uan_number" name="uan_number" class="form-control" value="${employee?.uan_number || ''}" placeholder="e.g. 100987654321">
                            </div>
                        </div>

                        <h4 style="font-size:15px; font-weight:700; color:var(--text-main); margin:24px 0 16px 0; border-top:1px solid var(--border-subtle); padding-top:16px;">Bank Account Details</h4>
                        <div class="form-row-3">
                            <div class="form-group">
                                <label class="form-label" for="bank_name">Bank Name</label>
                                <input type="text" id="bank_name" name="bank_name" class="form-control" value="${employee?.bank_name || ''}" placeholder="e.g. HDFC Bank">
                            </div>
                            <div class="form-group">
                                <label class="form-label" for="account_number">Account Number</label>
                                <input type="text" id="account_number" name="account_number" class="form-control" value="${employee?.account_number || ''}" placeholder="e.g. 50100234567890">
                            </div>
                            <div class="form-group">
                                <label class="form-label" for="ifsc_code">IFSC Code</label>
                                <input type="text" id="ifsc_code" name="ifsc_code" class="form-control" value="${employee?.ifsc_code || ''}" placeholder="e.g. HDFC0000128" style="text-transform:uppercase;">
                            </div>
                        </div>

                        <div style="display:flex; justify-content:space-between; margin-top:20px;">
                            <button type="button" class="btn btn-secondary" onclick="EmployeeFormComponent.switchTabByIndex(0)">&larr; Back</button>
                            <button type="button" class="btn btn-primary" onclick="EmployeeFormComponent.switchTabByIndex(2)">Next: Salary & Wage &rarr;</button>
                        </div>
                    </div>

                    <!-- TAB 3: Salary & Wage Structure -->
                    <div class="tab-pane" id="form-tab-salary">
                        <div style="display:grid; grid-template-columns:1fr 1.2fr; gap:24px; align-items:start;">
                            <div>
                                <div class="form-group">
                                    <label class="form-label required" for="monthly_wage">Monthly Defined Wage (₹)</label>
                                    <input type="number" id="monthly_wage" name="monthly_wage" class="form-control" required min="0" step="500" value="${wage}" oninput="EmployeeFormComponent.updateSalaryPreview(this.value)">
                                    <div class="form-hint">Salary breakdown components recalculate automatically in real-time.</div>
                                </div>

                                <div class="form-group">
                                    <label class="form-label" for="status">Employment Status</label>
                                    <select id="status" name="status" class="form-control">
                                        <option value="active" ${employee?.status === 'active' ? 'selected' : ''}>Active</option>
                                        <option value="inactive" ${employee?.status === 'inactive' ? 'selected' : ''}>Inactive / Deactivated</option>
                                    </select>
                                </div>

                                <div class="form-group">
                                    <label class="form-label" for="attendance_status">Initial Attendance Status</label>
                                    <select id="attendance_status" name="attendance_status" class="form-control">
                                        <option value="present" ${employee?.attendance_status === 'present' ? 'selected' : ''}>🟢 Present</option>
                                        <option value="absent" ${employee?.attendance_status === 'absent' ? 'selected' : ''}>🟡 Absent</option>
                                        <option value="on_leave" ${employee?.attendance_status === 'on_leave' ? 'selected' : ''}>✈️ On Leave</option>
                                    </select>
                                </div>
                            </div>

                            <!-- Live Computed Salary Breakdown Card -->
                            <div class="salary-card" id="form-salary-preview-box">
                                <div class="salary-card-header">
                                    <span class="salary-card-title">Live Salary Structure Preview</span>
                                    <span class="badge badge-active" id="preview-yearly-badge">₹${(wage * 12).toLocaleString('en-IN')}/yr</span>
                                </div>
                                <div id="form-salary-preview-rows">
                                    <!-- Injected dynamically -->
                                </div>
                            </div>
                        </div>

                        <div style="display:flex; justify-content:space-between; margin-top:20px;">
                            <button type="button" class="btn btn-secondary" onclick="EmployeeFormComponent.switchTabByIndex(1)">&larr; Back</button>
                            <button type="button" class="btn btn-primary" onclick="EmployeeFormComponent.switchTabByIndex(3)">Next: Skills & Certs &rarr;</button>
                        </div>
                    </div>

                    <!-- TAB 4: Skills & Certifications Dynamic Manager -->
                    <div class="tab-pane" id="form-tab-skills">
                        <!-- Skills Section -->
                        <div style="margin-bottom:28px;">
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
                                <h4 style="font-size:15px; font-weight:700; color:var(--text-main);">Technical & Professional Skills</h4>
                                <button type="button" class="btn btn-secondary btn-sm" onclick="EmployeeFormComponent.addSkillRow()">
                                    + Add Skill
                                </button>
                            </div>
                            <div id="skills-rows-container" style="display:flex; flex-direction:column; gap:10px;">
                                <!-- Rendered dynamically -->
                            </div>
                        </div>

                        <!-- Certifications Section -->
                        <div>
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px; border-top:1px solid var(--border-subtle); padding-top:20px;">
                                <h4 style="font-size:15px; font-weight:700; color:var(--text-main);">Certifications & Credentials</h4>
                                <button type="button" class="btn btn-secondary btn-sm" onclick="EmployeeFormComponent.addCertRow()">
                                    + Add Certification
                                </button>
                            </div>
                            <div id="certs-rows-container" style="display:flex; flex-direction:column; gap:12px;">
                                <!-- Rendered dynamically -->
                            </div>
                        </div>

                        <div style="display:flex; justify-content:space-between; margin-top:24px;">
                            <button type="button" class="btn btn-secondary" onclick="EmployeeFormComponent.switchTabByIndex(2)">&larr; Back</button>
                            <button type="button" class="btn btn-primary" onclick="EmployeeFormComponent.switchTabByIndex(4)">Next: Bio & Resume &rarr;</button>
                        </div>
                    </div>

                    <!-- TAB 5: Bio, Hobbies, Resume -->
                    <div class="tab-pane" id="form-tab-bio">
                        <div class="form-group">
                            <label class="form-label" for="about">About & "What I love about my job"</label>
                            <textarea id="about" name="about" class="form-control" rows="3" placeholder="Share a brief overview of passion, role focus, and background...">${employee?.about || ''}</textarea>
                        </div>

                        <div class="form-group">
                            <label class="form-label" for="interests_hobbies">Interests & Hobbies</label>
                            <input type="text" id="interests_hobbies" name="interests_hobbies" class="form-control" value="${employee?.interests_hobbies || ''}" placeholder="e.g. Trekking, playing guitar, photography, open-source">
                        </div>

                        <div class="form-row">
                            <div class="form-group">
                                <label class="form-label" for="resume_filename">Resume Filename</label>
                                <input type="text" id="resume_filename" name="resume_filename" class="form-control" value="${employee?.resume_filename || ''}" placeholder="e.g. Employee_Resume.pdf">
                            </div>
                            <div class="form-group">
                                <label class="form-label" for="resume_file_input">Upload Resume Document (PDF / DOCX)</label>
                                <input type="file" id="resume_file_input" class="form-control" accept=".pdf,.doc,.docx" onchange="EmployeeFormComponent.handleFileUpload(this)">
                                <input type="hidden" id="resume_url" name="resume_url" value="${employee?.resume_url || ''}">
                            </div>
                        </div>

                        <div style="display:flex; justify-content:space-between; align-items:center; margin-top:32px; border-top:1px solid var(--border-subtle); padding-top:20px;">
                            <button type="button" class="btn btn-secondary" onclick="EmployeeFormComponent.switchTabByIndex(3)">&larr; Back</button>
                            <div style="display:flex; gap:12px; align-items:center;">
                                <button type="button" class="btn btn-secondary" onclick="${cancelAction}">Cancel</button>
                                <button type="submit" class="btn btn-primary btn-lg" id="form-submit-btn">
                                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path><polyline points="17 21 17 13 7 13 7 21"></polyline><polyline points="7 3 7 8 15 8"></polyline></svg>
                                    ${btnText}
                                </button>
                            </div>
                        </div>
                    </div>
                </form>
            </div>
        `;
    }

    static init(employee = null) {
        const form = document.getElementById('employee-main-form');
        if (!form) return;

        FormValidator.attachLiveValidation(form);

        // Populate initial skills
        const initialSkills = employee?.skills || [
            { name: "JavaScript", level: "Expert" },
            { name: "Python", level: "Advanced" }
        ];
        initialSkills.forEach(s => this.addSkillRow(s.name, s.level));

        // Populate initial certs
        const initialCerts = employee?.certifications || [];
        initialCerts.forEach(c => this.addCertRow(c.title, c.issuer, c.issue_date, c.expiry_date, c.credential_id));

        // Update salary preview
        const wage = employee?.monthly_wage || 50000;
        this.updateSalaryPreview(wage);
    }

    static switchTab(paneId, btnElement) {
        document.querySelectorAll('#form-tabs-header .tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));

        if (btnElement) btnElement.classList.add('active');
        const pane = document.getElementById(paneId);
        if (pane) pane.classList.add('active');
    }

    static switchTabByIndex(index) {
        const tabBtns = document.querySelectorAll('#form-tabs-header .tab-btn');
        if (tabBtns[index]) {
            tabBtns[index].click();
        }
    }

    static updateSalaryPreview(monthlyWageVal) {
        const wage = parseFloat(monthlyWageVal) || 0;
        const basic = Math.round(wage * 0.50);
        const hra = Math.round(basic * 0.50);
        const bonus = Math.round(basic * 0.0833);
        const lta = Math.round(basic * 0.08333);
        const tempSum = basic + hra + bonus + lta;
        const stdAllow = wage >= (tempSum + 4167) ? 4167 : Math.max(0, wage - tempSum);
        const fixedAllow = Math.max(0, Math.round(wage - (basic + hra + bonus + lta + stdAllow)));
        const pf = Math.round(basic * 0.12);
        const pt = wage > 15000 ? 200 : 0;
        const net = Math.max(0, wage - (pf + pt));

        const badge = document.getElementById('preview-yearly-badge');
        if (badge) badge.textContent = `₹${(wage * 12).toLocaleString('en-IN')}/yr`;

        const container = document.getElementById('form-salary-preview-rows');
        if (container) {
            container.innerHTML = `
                <div class="salary-row">
                    <span>Basic Salary (50%)</span>
                    <strong>₹${basic.toLocaleString('en-IN')}</strong>
                </div>
                <div class="salary-row">
                    <span>House Rent Allowance (HRA 50% of Basic)</span>
                    <strong>₹${hra.toLocaleString('en-IN')}</strong>
                </div>
                <div class="salary-row">
                    <span>Standard Allowance</span>
                    <strong>₹${stdAllow.toLocaleString('en-IN')}</strong>
                </div>
                <div class="salary-row">
                    <span>Performance Bonus (8.33%)</span>
                    <strong>₹${bonus.toLocaleString('en-IN')}</strong>
                </div>
                <div class="salary-row">
                    <span>Leave Travel Allowance (LTA 8.33%)</span>
                    <strong>₹${lta.toLocaleString('en-IN')}</strong>
                </div>
                <div class="salary-row">
                    <span>Fixed Allowance (Balance)</span>
                    <strong>₹${fixedAllow.toLocaleString('en-IN')}</strong>
                </div>
                <div class="salary-row deduction">
                    <span>Provident Fund (PF 12% Deduction)</span>
                    <span>- ₹${pf.toLocaleString('en-IN')}</span>
                </div>
                <div class="salary-row deduction">
                    <span>Professional Tax (PTax)</span>
                    <span>- ₹${pt.toLocaleString('en-IN')}</span>
                </div>
                <div class="salary-row highlight">
                    <span>Estimated In-Hand Monthly</span>
                    <span>₹${net.toLocaleString('en-IN')}</span>
                </div>
            `;
        }
    }

    static addSkillRow(name = "", level = "Intermediate") {
        const container = document.getElementById('skills-rows-container');
        if (!container) return;

        const row = document.createElement('div');
        row.className = 'skill-input-row';
        row.style = 'display:flex; gap:12px; align-items:center; background:var(--bg-input); padding:8px 12px; border-radius:var(--radius-md); border:1px solid var(--border-subtle);';

        row.innerHTML = `
            <input type="text" class="form-control skill-name-input" placeholder="Skill (e.g. React, Python, Figma)" value="${name}" style="flex:2;">
            <select class="form-control skill-level-select" style="flex:1;">
                <option value="Beginner" ${level === 'Beginner' ? 'selected' : ''}>Beginner</option>
                <option value="Intermediate" ${level === 'Intermediate' ? 'selected' : ''}>Intermediate</option>
                <option value="Advanced" ${level === 'Advanced' ? 'selected' : ''}>Advanced</option>
                <option value="Expert" ${level === 'Expert' ? 'selected' : ''}>Expert</option>
            </select>
            <button type="button" class="btn btn-outline-danger btn-sm" onclick="this.parentElement.remove()" title="Remove skill">
                &times;
            </button>
        `;

        container.appendChild(row);
    }

    static addCertRow(title = "", issuer = "", issue_date = "", expiry_date = "", credential_id = "") {
        const container = document.getElementById('certs-rows-container');
        if (!container) return;

        const row = document.createElement('div');
        row.className = 'cert-input-row';
        row.style = 'display:grid; grid-template-columns:2fr 1.5fr 1fr 1fr 1fr auto; gap:10px; align-items:center; background:var(--bg-input); padding:10px 14px; border-radius:var(--radius-md); border:1px solid var(--border-subtle);';

        row.innerHTML = `
            <input type="text" class="form-control cert-title-input" placeholder="Certification Title (e.g. AWS Solutions Architect)" value="${title}">
            <input type="text" class="form-control cert-issuer-input" placeholder="Issuer (e.g. Amazon, Google)" value="${issuer}">
            <input type="text" class="form-control cert-issue-input" placeholder="Issue (YYYY-MM)" value="${issue_date || ''}">
            <input type="text" class="form-control cert-expiry-input" placeholder="Expiry (YYYY-MM)" value="${expiry_date || ''}">
            <input type="text" class="form-control cert-id-input" placeholder="Cred ID" value="${credential_id || ''}">
            <button type="button" class="btn btn-outline-danger btn-sm" onclick="this.parentElement.remove()" title="Remove cert">
                &times;
            </button>
        `;

        container.appendChild(row);
    }

    static async handleFileUpload(inputElement) {
        if (!inputElement.files || inputElement.files.length === 0) return;
        const file = inputElement.files[0];
        const formData = new FormData();
        formData.append('file', file);

        try {
            Toast.info('Uploading', `Uploading ${file.name}...`);
            const res = await ApiService.uploadFile(formData);
            if (res.success) {
                document.getElementById('resume_url').value = res.url;
                const fnInput = document.getElementById('resume_filename');
                if (fnInput && !fnInput.value) {
                    fnInput.value = res.original_filename;
                }
                Toast.success('Uploaded', 'Resume document uploaded successfully.');
            }
        } catch (err) {
            Toast.error('Upload Failed', err.message);
        }
    }

    static async handleSubmit(event, editId) {
        event.preventDefault();
        const form = document.getElementById('employee-main-form');
        if (!form) return;

        // Perform validation
        const isValid = FormValidator.validateAll(form);
        if (!isValid) {
            Toast.error('Validation Error', 'Please correct the highlighted fields before submitting.');
            return;
        }

        const formData = new FormData(form);
        const payload = Object.fromEntries(formData.entries());

        // Parse numerical fields
        payload.monthly_wage = parseFloat(payload.monthly_wage || 0);

        // Collect skills
        const skillRows = document.querySelectorAll('.skill-input-row');
        const skills = [];
        skillRows.forEach(r => {
            const name = r.querySelector('.skill-name-input')?.value.trim();
            const level = r.querySelector('.skill-level-select')?.value;
            if (name) skills.push({ name, level });
        });
        payload.skills = skills;

        // Collect certifications
        const certRows = document.querySelectorAll('.cert-input-row');
        const certs = [];
        certRows.forEach(r => {
            const title = r.querySelector('.cert-title-input')?.value.trim();
            const issuer = r.querySelector('.cert-issuer-input')?.value.trim();
            const issue_date = r.querySelector('.cert-issue-input')?.value.trim();
            const expiry_date = r.querySelector('.cert-expiry-input')?.value.trim();
            const credential_id = r.querySelector('.cert-id-input')?.value.trim();
            if (title) certs.push({ title, issuer, issue_date, expiry_date, credential_id });
        });
        payload.certifications = certs;

        const submitBtn = document.getElementById('form-submit-btn');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = 'Saving Employee...';
        }

        try {
            if (editId) {
                const res = await ApiService.updateEmployee(editId, payload);
                Toast.success('Employee Updated', `${res.full_name}'s profile was updated successfully.`);
                App.navigate('profile', editId);
            } else {
                const res = await ApiService.createEmployee(payload);
                Toast.success('Employee Onboarded', `${res.full_name} was created with Login ID: ${res.login_id}`);
                App.navigate('profile', res.id);
            }
        } catch (err) {
            Toast.error('Submission Failed', err.message);
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = editId ? 'Save Changes' : 'Create Employee';
            }
        }
    }
}

window.EmployeeFormComponent = EmployeeFormComponent;
