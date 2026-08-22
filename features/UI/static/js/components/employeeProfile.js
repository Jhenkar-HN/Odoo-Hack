/**
 * Detailed Employee Profile Component with 5 Rich Tabs & Salary Computation Breakdown
 */
class EmployeeProfileComponent {
    static render(emp) {
        const isHR = App.currentUser?.role === 'hr';
        const isOwnProfile = App.currentUser?.employee_id === emp.id;

        const salary = emp.salary_breakdown || {};
        const avatar = emp.avatar_url || 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150&auto=format&fit=crop&q=80';
        
        const attStatus = emp.attendance_status || 'present';
        const attBadge = attStatus === 'present' ? 
            `<span class="badge badge-present"><span class="badge-dot"></span>Present</span>` : 
            (attStatus === 'on_leave' ? 
                `<span class="badge badge-leave"><span class="badge-dot"></span>On Leave</span>` : 
                `<span class="badge badge-absent"><span class="badge-dot"></span>Absent</span>`);

        const actionButtons = isHR ? `
            <div class="filter-group">
                <select class="filter-select" onchange="EmployeeProfileComponent.handleAttendanceChange(${emp.id}, this.value)" style="padding:7px 12px; font-size:12.5px;">
                    <option value="present" ${attStatus === 'present' ? 'selected' : ''}>🟢 Status: Present</option>
                    <option value="absent" ${attStatus === 'absent' ? 'selected' : ''}>🟡 Status: Absent</option>
                    <option value="on_leave" ${attStatus === 'on_leave' ? 'selected' : ''}>✈️ Status: On Leave</option>
                </select>
            </div>
            <button class="btn btn-secondary" onclick="App.navigate('edit-employee', ${emp.id})">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
                Edit Profile
            </button>
            <button class="btn btn-outline-danger" onclick="App.promptDelete(${emp.id}, '${emp.full_name.replace(/'/g, "\\'")}')">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                Deactivate
            </button>
        ` : (isOwnProfile ? `
            <div class="filter-group">
                <select class="filter-select" onchange="EmployeeProfileComponent.handleAttendanceChange(${emp.id}, this.value)" style="padding:7px 12px; font-size:12.5px;">
                    <option value="present" ${attStatus === 'present' ? 'selected' : ''}>🟢 Status: Present</option>
                    <option value="absent" ${attStatus === 'absent' ? 'selected' : ''}>🟡 Status: Absent</option>
                    <option value="on_leave" ${attStatus === 'on_leave' ? 'selected' : ''}>✈️ Status: On Leave</option>
                </select>
            </div>
            <button class="btn btn-primary" onclick="LeaveModalComponent.openApplyModal()">
                Apply for Leave
            </button>
        ` : ``);

        return `
            <!-- Hero Header -->
            <div class="profile-hero">
                <div class="profile-cover"></div>
                <div class="profile-hero-content">
                    <div class="profile-avatar-block">
                        <img src="${avatar}" alt="${emp.full_name}" class="profile-avatar">
                        <div class="profile-main-meta">
                            <div class="profile-name">
                                <span>${emp.full_name}</span>
                                <span class="profile-code-badge">${emp.login_id || emp.emp_code}</span>
                                ${attBadge}
                            </div>
                            <div class="profile-role">${emp.job_position} &bull; <span style="color:var(--primary-400);">${emp.department}</span></div>
                            <div style="font-size:12.5px; color:var(--text-muted); margin-top:4px;">
                                📍 ${emp.location || 'Headquarters'} &bull; 📅 Joined ${emp.date_of_joining} &bull; 🕒 ${emp.work_hours || 'Full-time'}
                            </div>
                        </div>
                    </div>

                    <div class="profile-actions">
                        ${actionButtons}
                    </div>
                </div>
            </div>

            <!-- Profile Tabs Container -->
            <div class="profile-content-card">
                <div class="tabs-header" id="profile-tabs-header">
                    <button class="tab-btn active" onclick="EmployeeProfileComponent.switchTab('tab-personal', this)">
                        Overview & Personal
                    </button>
                    <button class="tab-btn" onclick="EmployeeProfileComponent.switchTab('tab-skills', this)">
                        Skills & Certifications (${(emp.skills || []).length + (emp.certifications || []).length})
                    </button>
                    <button class="tab-btn" onclick="EmployeeProfileComponent.switchTab('tab-private', this)">
                        Private & Bank Info
                    </button>
                    <button class="tab-btn" onclick="EmployeeProfileComponent.switchTab('tab-salary', this)">
                        Salary Information & Benefits
                    </button>
                    <button class="tab-btn" onclick="EmployeeProfileComponent.switchTab('tab-docs', this)">
                        Documents & Resume
                    </button>
                </div>

                <!-- TAB 1: Overview & Personal -->
                <div class="tab-pane active" id="tab-personal">
                    <div class="info-grid">
                        <div class="info-item">
                            <span class="info-label">Full Name</span>
                            <span class="info-value">${emp.full_name}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">System Login ID</span>
                            <span class="info-value" style="color:var(--primary-400);">${emp.login_id || emp.emp_code}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Work Email</span>
                            <span class="info-value"><a href="mailto:${emp.work_email}" style="color:inherit; text-decoration:none;">${emp.work_email}</a></span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Contact Phone</span>
                            <span class="info-value">${emp.phone}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Department</span>
                            <span class="info-value"><span class="badge badge-dept">${emp.department}</span></span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Reporting Manager</span>
                            <span class="info-value">${emp.manager_name || 'None Assigned'}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Date of Joining</span>
                            <span class="info-value">${emp.date_of_joining}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Working Hours Schedule</span>
                            <span class="info-value">${emp.work_hours || '40 hrs/week'}</span>
                        </div>
                    </div>

                    <div style="margin-top:28px; padding-top:20px; border-top:1px solid var(--border-subtle);">
                        <h4 style="font-size:14px; font-weight:700; color:var(--text-main); margin-bottom:8px;">What I Love About My Job / Bio</h4>
                        <p style="font-size:13.5px; color:var(--text-muted); line-height:1.6;">
                            ${emp.about || 'No personal bio added yet.'}
                        </p>
                    </div>

                    <div style="margin-top:20px; padding-top:16px; border-top:1px solid var(--border-subtle);">
                        <h4 style="font-size:14px; font-weight:700; color:var(--text-main); margin-bottom:8px;">Interests & Hobbies</h4>
                        <p style="font-size:13.5px; color:var(--text-muted);">
                            ${emp.interests_hobbies || 'Not specified.'}
                        </p>
                    </div>
                </div>

                <!-- TAB 2: Skills & Certifications -->
                <div class="tab-pane" id="tab-skills">
                    <div style="margin-bottom:28px;">
                        <h4 style="font-size:15px; font-weight:700; color:var(--text-main); margin-bottom:16px;">Core Competencies & Skills</h4>
                        <div class="skills-container">
                            ${(emp.skills && emp.skills.length > 0) ? emp.skills.map(s => {
                                const lvl = (s.level || 'Intermediate').toLowerCase();
                                return `
                                    <div class="skill-chip">
                                        <span class="skill-chip-name">${s.name}</span>
                                        <span class="skill-level-badge ${lvl}">${s.level}</span>
                                    </div>
                                `;
                            }).join('') : '<div class="empty-state-text">No skills registered for this employee.</div>'}
                        </div>
                    </div>

                    <div style="padding-top:20px; border-top:1px solid var(--border-subtle);">
                        <h4 style="font-size:15px; font-weight:700; color:var(--text-main); margin-bottom:16px;">Professional Certifications</h4>
                        <div class="cert-grid">
                            ${(emp.certifications && emp.certifications.length > 0) ? emp.certifications.map(c => `
                                <div class="cert-card">
                                    <div class="cert-title">${c.title}</div>
                                    <div class="cert-issuer">${c.issuer || 'Issuing Authority'}</div>
                                    <div class="cert-meta">
                                        <span>Issued: ${c.issue_date || 'N/A'}</span>
                                        <span>&bull;</span>
                                        <span>Expires: ${c.expiry_date || 'No Expiry'}</span>
                                    </div>
                                    ${c.credential_id ? `<div style="font-size:11.5px; color:var(--text-subtle);">ID: ${c.credential_id}</div>` : ''}
                                </div>
                            `).join('') : '<div class="empty-state-text">No certifications listed.</div>'}
                        </div>
                    </div>
                </div>

                <!-- TAB 3: Private & Bank Info -->
                <div class="tab-pane" id="tab-private">
                    <h4 style="font-size:15px; font-weight:700; color:var(--text-main); margin-bottom:16px;">Private Demographic Information</h4>
                    <div class="info-grid" style="margin-bottom:28px;">
                        <div class="info-item">
                            <span class="info-label">Date of Birth</span>
                            <span class="info-value">${emp.date_of_birth || 'Not Specified'}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Gender</span>
                            <span class="info-value">${emp.gender || 'Not Specified'}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Marital Status</span>
                            <span class="info-value">${emp.marital_status || 'Single'}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Nationality</span>
                            <span class="info-value">${emp.nationality || 'Indian'}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Personal Email</span>
                            <span class="info-value">${emp.personal_email || 'Not Provided'}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Permanent PAN Number</span>
                            <span class="info-value" style="text-transform:uppercase;">${emp.pan_number || 'Pending'}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Provident Fund (UAN)</span>
                            <span class="info-value">${emp.uan_number || 'Pending'}</span>
                        </div>
                    </div>

                    <div class="info-item" style="margin-bottom:28px;">
                        <span class="info-label">Residing Residential Address</span>
                        <span class="info-value" style="font-weight:500;">${emp.residing_address || 'No residential address recorded.'}</span>
                    </div>

                    <h4 style="font-size:15px; font-weight:700; color:var(--text-main); margin-bottom:16px; padding-top:20px; border-top:1px solid var(--border-subtle);">Bank & Direct Deposit Information</h4>
                    <div class="info-grid">
                        <div class="info-item">
                            <span class="info-label">Bank Institution Name</span>
                            <span class="info-value">${emp.bank_name || 'Pending Onboarding'}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Bank Account Number</span>
                            <span class="info-value">${emp.account_number ? `•••• •••• ${emp.account_number.slice(-4)}` : 'Pending'}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">IFSC Routing Code</span>
                            <span class="info-value" style="text-transform:uppercase;">${emp.ifsc_code || 'Pending'}</span>
                        </div>
                    </div>
                </div>

                <!-- TAB 4: Salary & Benefits -->
                <div class="tab-pane" id="tab-salary">
                    ${(isHR || isOwnProfile) ? `
                    <div class="salary-sheet">
                        <!-- Defined Compensation Card -->
                        <div class="salary-card">
                            <div class="salary-card-header">
                                <span class="salary-card-title">Base Compensation</span>
                                <span class="badge badge-active">Fixed Wage</span>
                            </div>
                            <div class="salary-row">
                                <span>Monthly Defined Gross Wage</span>
                                <strong>₹${Number(salary.monthly_wage || 0).toLocaleString('en-IN')}</strong>
                            </div>
                            <div class="salary-row">
                                <span>Annual Cost to Company (CTC)</span>
                                <strong>₹${Number(salary.yearly_wage || 0).toLocaleString('en-IN')}</strong>
                            </div>
                            <div class="salary-row">
                                <span>Pay Schedule</span>
                                <span>Monthly (Last Working Day)</span>
                            </div>
                            <div class="salary-row highlight">
                                <span>Net In-Hand Monthly Take-home</span>
                                <span>₹${Number(salary.net_monthly || 0).toLocaleString('en-IN')}</span>
                            </div>
                        </div>

                        <!-- Earnings Breakdown -->
                        <div class="salary-card">
                            <div class="salary-card-header">
                                <span class="salary-card-title">Salary Earnings Structure</span>
                                <span style="font-size:12px; color:var(--text-muted);">Auto-Computed</span>
                            </div>
                            <div class="salary-row">
                                <span>Basic Salary (50% of Wage)</span>
                                <strong>₹${Number(salary.basic_salary || 0).toLocaleString('en-IN')}</strong>
                            </div>
                            <div class="salary-row">
                                <span>House Rent Allowance (50% of Basic)</span>
                                <strong>₹${Number(salary.hra || 0).toLocaleString('en-IN')}</strong>
                            </div>
                            <div class="salary-row">
                                <span>Standard Allowance</span>
                                <strong>₹${Number(salary.standard_allowance || 0).toLocaleString('en-IN')}</strong>
                            </div>
                            <div class="salary-row">
                                <span>Performance Bonus (8.33%)</span>
                                <strong>₹${Number(salary.performance_bonus || 0).toLocaleString('en-IN')}</strong>
                            </div>
                            <div class="salary-row">
                                <span>Leave Travel Allowance (LTA 8.33%)</span>
                                <strong>₹${Number(salary.lta || 0).toLocaleString('en-IN')}</strong>
                            </div>
                            <div class="salary-row">
                                <span>Fixed Allowance (Portion balance)</span>
                                <strong>₹${Number(salary.fixed_allowance || 0).toLocaleString('en-IN')}</strong>
                            </div>
                        </div>

                        <!-- Deductions Breakdown -->
                        <div class="salary-card">
                            <div class="salary-card-header">
                                <span class="salary-card-title">Statutory Deductions</span>
                                <span class="badge badge-inactive">Taxes & PF</span>
                            </div>
                            <div class="salary-row deduction">
                                <span>Provident Fund (PF - 12% of Basic)</span>
                                <span>- ₹${Number(salary.pf_deduction || 0).toLocaleString('en-IN')}</span>
                            </div>
                            <div class="salary-row deduction">
                                <span>Professional Tax (PTax)</span>
                                <span>- ₹${Number(salary.professional_tax || 0).toLocaleString('en-IN')}</span>
                            </div>
                            <div class="salary-row" style="margin-top:12px; border-top:1px solid var(--border-subtle); padding-top:12px;">
                                <span>Total Monthly Deductions</span>
                                <strong style="color:var(--accent-rose);">- ₹${Number(salary.total_deductions || 0).toLocaleString('en-IN')}</strong>
                            </div>
                            <div class="salary-row highlight">
                                <span>Annual Net Earnings</span>
                                <span>₹${Number(salary.net_yearly || 0).toLocaleString('en-IN')}</span>
                            </div>
                        </div>
                    </div>
                    ` : `
                    <div class="empty-state" style="padding:40px 20px;">
                        <div class="empty-state-icon">
                            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>
                        </div>
                        <div class="empty-state-title">Compensation Information Restricted</div>
                        <div class="empty-state-text">Salary breakdown structures are confidential and visible only to HR Administrators.</div>
                    </div>
                    `}
                </div>

                <!-- TAB 5: Documents & Resume -->
                <div class="tab-pane" id="tab-docs">
                    <div style="display:flex; flex-direction:column; gap:16px;">
                        <div class="doc-box">
                            <div class="doc-info">
                                <div class="doc-icon">
                                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
                                </div>
                                <div>
                                    <div class="doc-name">${emp.resume_filename || `${emp.first_name}_${emp.last_name}_Resume.pdf`}</div>
                                    <div class="doc-sub">Curriculum Vitae & Verified Experience Record</div>
                                </div>
                            </div>
                            <div style="display:flex; gap:10px;">
                                ${emp.resume_url ? 
                                    `<a href="${emp.resume_url}" target="_blank" class="btn btn-secondary btn-sm">Download Resume</a>` : 
                                    `<button class="btn btn-secondary btn-sm" onclick="App.navigate('edit-employee', ${emp.id})">Upload Document</button>`
                                }
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    static switchTab(paneId, btnElement) {
        document.querySelectorAll('#profile-tabs-header .tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.profile-content-card .tab-pane').forEach(p => p.classList.remove('active'));

        if (btnElement) btnElement.classList.add('active');
        const pane = document.getElementById(paneId);
        if (pane) pane.classList.add('active');
    }

    static async handleAttendanceChange(empId, newStatus) {
        try {
            const res = await ApiService.toggleAttendance(empId, newStatus);
            Toast.success('Attendance Updated', `${res.full_name}'s status changed to ${newStatus}.`);
            App.navigate('profile', empId);
        } catch (err) {
            Toast.error('Update Failed', err.message);
        }
    }
}

window.EmployeeProfileComponent = EmployeeProfileComponent;
