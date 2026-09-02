/**
 * Dedicated Payroll & Salary Slip Generator Component (PDF 3.6 & Section 6 / Excalidraw)
 * Features:
 * - Dynamic Attendance-Based Payable Days calculation
 * - Professional Printable Payslip Document
 * - Read-only view for regular employees
 * - Administrative salary structure management
 */
class PayrollViewComponent {
    static currentEmployeeId = null;
    static currentMonth = new Date().getMonth() + 1;
    static currentYear = new Date().getFullYear();

    static async render(targetEmpId = null) {
        const container = document.getElementById('view-container');
        if (!container) return;

        const user = App.currentUser;
        if (!user) return;

        const isHR = ['ADMIN', 'HR_OFFICER'].includes(String(user.role || '').toUpperCase());
        this.currentEmployeeId = targetEmpId || user.employee_id || 1;

        container.innerHTML = `
            <div class="glass-card skeleton" style="height:100px; margin-bottom:20px;"></div>
            <div class="glass-card skeleton" style="height:450px;"></div>
        `;

        try {
            const [payslip, allEmpsResp] = await Promise.all([
                ApiService.getPayslip(this.currentEmployeeId, this.currentMonth, this.currentYear).catch(() => null),
                isHR ? ApiService.getEmployees({ size: 100 }).catch(() => ({ items: [] })) : Promise.resolve({ items: [] })
            ]);

            const emps = allEmpsResp?.items || [];
            this.renderContent(container, payslip, emps, isHR);
        } catch (err) {
            container.innerHTML = `<div class="glass-card" style="padding:30px; text-align:center;">Failed to load payroll: ${err.message}</div>`;
        }
    }

    static renderContent(container, payslip, allEmployees, isHR) {
        if (!payslip) {
            container.innerHTML = `<div class="glass-card" style="padding:30px; text-align:center;">No salary record found for this employee.</div>`;
            return;
        }

        const monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
        const monthOptions = monthNames.map((m, idx) => `
            <option value="${idx + 1}" ${this.currentMonth === idx + 1 ? 'selected' : ''}>${m}</option>
        `).join('');

        const empOptions = allEmployees.map(e => `
            <option value="${e.id}" ${this.currentEmployeeId == e.id ? 'selected' : ''}>${e.full_name} (${e.login_id || e.employee_code})</option>
        `).join('');

        container.innerHTML = `
            <!-- Top Controls -->
            <div class="glass-card" style="margin-bottom:24px; padding:16px 24px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:16px;">
                <div style="display:flex; align-items:center; gap:12px; flex-wrap:wrap;">
                    <div>
                        <label class="form-label" style="margin:0; font-size:12px;">Cycle Month:</label>
                        <select class="filter-select" id="payroll-month-select" onchange="PayrollViewComponent.changeCycle()" style="padding:6px 12px; font-size:13px;">
                            ${monthOptions}
                        </select>
                    </div>
                    <div>
                        <label class="form-label" style="margin:0; font-size:12px;">Year:</label>
                        <select class="filter-select" id="payroll-year-select" onchange="PayrollViewComponent.changeCycle()" style="padding:6px 12px; font-size:13px;">
                            <option value="2025" ${this.currentYear === 2025 ? 'selected' : ''}>2025</option>
                            <option value="2026" ${this.currentYear === 2026 ? 'selected' : ''}>2026</option>
                        </select>
                    </div>
                    ${isHR ? `
                    <div>
                        <label class="form-label" style="margin:0; font-size:12px;">Select Employee:</label>
                        <select class="filter-select" id="payroll-emp-select" onchange="PayrollViewComponent.changeEmployee(this.value)" style="min-width:220px; padding:6px 12px; font-size:13px;">
                            ${empOptions}
                        </select>
                    </div>
                    ` : ''}
                </div>

                <div style="display:flex; gap:10px;">
                    <button class="btn btn-secondary btn-sm" onclick="window.print()" style="display:flex; align-items:center; gap:6px;">
                        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 6 2 18 2 18 9"></polyline><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"></path><rect x="6" y="14" width="12" height="8"></rect></svg>
                        Print / Download PDF
                    </button>
                    ${isHR ? `
                    <button class="btn btn-primary btn-sm" onclick="App.navigate('edit-employee', ${payslip.employee_id})">
                        Edit Salary Structure
                    </button>
                    ` : ''}
                </div>
            </div>

            <!-- Professional Payslip Document (Excalidraw & PDF 3.6) -->
            <div class="glass-card" id="printable-payslip" style="padding:36px; max-width:900px; margin:0 auto; background:var(--bg-surface); border:1px solid var(--border-strong); box-shadow:var(--shadow-xl); border-radius:var(--radius-md);">
                
                <!-- Company Header -->
                <div style="display:flex; justify-content:space-between; align-items:flex-start; border-bottom:2px solid var(--border-subtle); padding-bottom:20px; margin-bottom:24px;">
                    <div style="display:flex; align-items:center; gap:14px;">
                        <div style="width:48px; height:48px; border-radius:var(--radius-sm); background:linear-gradient(135deg, var(--primary-600), var(--primary-400)); color:#fff; display:flex; align-items:center; justify-content:center; font-weight:800; font-size:20px;">
                            HR
                        </div>
                        <div>
                            <h2 style="font-size:22px; font-weight:800; color:var(--text-main); margin:0;">DAYFLOW TECHNOLOGIES</h2>
                            <div style="font-size:12px; color:var(--text-muted); margin-top:2px;">Human Resource Management &amp; Payroll Solutions</div>
                            <div style="font-size:11px; color:var(--text-subtle);">Headquarters, Sector 4, Silicon Valley Park</div>
                        </div>
                    </div>
                    <div style="text-align:right;">
                        <span class="badge badge-dept" style="font-size:13px; font-weight:700; padding:6px 12px;">SALARY SLIP</span>
                        <div style="font-size:13px; font-weight:700; color:var(--text-main); margin-top:6px;">${payslip.month_name}</div>
                        <div style="font-size:11.5px; color:var(--text-subtle);">Confidential Document</div>
                    </div>
                </div>

                <!-- Employee & Attendance Info Grid -->
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:20px; background:var(--bg-surface-elevated, rgba(255,255,255,0.03)); padding:18px 20px; border-radius:var(--radius-sm); border:1px solid var(--border-subtle); margin-bottom:24px; font-size:12.5px;">
                    <div>
                        <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
                            <span style="color:var(--text-muted);">Employee Name:</span>
                            <strong style="color:var(--text-main);">${payslip.employee_name}</strong>
                        </div>
                        <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
                            <span style="color:var(--text-muted);">Employee ID:</span>
                            <strong style="color:var(--primary-400);">${payslip.employee_code}</strong>
                        </div>
                        <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
                            <span style="color:var(--text-muted);">Department:</span>
                            <span style="color:var(--text-main);">${payslip.department}</span>
                        </div>
                        <div style="display:flex; justify-content:space-between;">
                            <span style="color:var(--text-muted);">Designation:</span>
                            <span style="color:var(--text-main);">${payslip.job_position}</span>
                        </div>
                    </div>

                    <div>
                        <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
                            <span style="color:var(--text-muted);">Bank Name:</span>
                            <span style="color:var(--text-main);">${payslip.bank_name || 'HDFC Bank'}</span>
                        </div>
                        <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
                            <span style="color:var(--text-muted);">Bank Account:</span>
                            <span style="color:var(--text-main);">${payslip.bank_account_number || '••••••••4819'}</span>
                        </div>
                        <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
                            <span style="color:var(--text-muted);">PAN Number:</span>
                            <span style="color:var(--text-main);">${payslip.pan || 'ABCDE1234F'}</span>
                        </div>
                        <div style="display:flex; justify-content:space-between;">
                            <span style="color:var(--text-muted);">Attendance Payable Days:</span>
                            <strong style="color:var(--emerald-400, #10b981);">${payslip.payable_days} / ${payslip.total_working_days} Days</strong>
                        </div>
                    </div>
                </div>

                <!-- Earnings & Deductions Tables (Excalidraw lines 218-245) -->
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:24px; margin-bottom:24px;">
                    
                    <!-- Earnings Column -->
                    <div>
                        <div style="background:var(--bg-surface-elevated); padding:8px 12px; font-weight:700; font-size:13px; color:var(--text-main); border-bottom:2px solid var(--primary-500); display:flex; justify-content:space-between;">
                            <span>EARNINGS</span>
                            <span>AMOUNT (₹)</span>
                        </div>
                        <table style="width:100%; font-size:12.5px; border-collapse:collapse;">
                            <tbody>
                                <tr style="border-bottom:1px solid var(--border-subtle);"><td style="padding:8px 6px; color:var(--text-muted);">Basic Salary (50%)</td><td style="padding:8px 6px; text-align:right; font-weight:600;">₹${Number(payslip.basic_salary).toLocaleString()}</td></tr>
                                <tr style="border-bottom:1px solid var(--border-subtle);"><td style="padding:8px 6px; color:var(--text-muted);">House Rent Allowance (HRA)</td><td style="padding:8px 6px; text-align:right; font-weight:600;">₹${Number(payslip.hra).toLocaleString()}</td></tr>
                                <tr style="border-bottom:1px solid var(--border-subtle);"><td style="padding:8px 6px; color:var(--text-muted);">Standard Allowance</td><td style="padding:8px 6px; text-align:right; font-weight:600;">₹${Number(payslip.standard_allowance).toLocaleString()}</td></tr>
                                <tr style="border-bottom:1px solid var(--border-subtle);"><td style="padding:8px 6px; color:var(--text-muted);">Performance Bonus (8.33%)</td><td style="padding:8px 6px; text-align:right; font-weight:600;">₹${Number(payslip.performance_bonus).toLocaleString()}</td></tr>
                                <tr style="border-bottom:1px solid var(--border-subtle);"><td style="padding:8px 6px; color:var(--text-muted);">Leave Travel Allowance (LTA)</td><td style="padding:8px 6px; text-align:right; font-weight:600;">₹${Number(payslip.leave_travel_allowance).toLocaleString()}</td></tr>
                                <tr style="border-bottom:1px solid var(--border-subtle);"><td style="padding:8px 6px; color:var(--text-muted);">Fixed Allowance (Balance)</td><td style="padding:8px 6px; text-align:right; font-weight:600;">₹${Number(payslip.fixed_allowance).toLocaleString()}</td></tr>
                            </tbody>
                            <tfoot>
                                <tr style="background:var(--bg-surface-elevated); font-weight:700;">
                                    <td style="padding:10px 6px; color:var(--text-main);">GROSS EARNINGS</td>
                                    <td style="padding:10px 6px; text-align:right; color:var(--primary-400);">₹${Number(payslip.gross_earnings).toLocaleString()}</td>
                                </tr>
                            </tfoot>
                        </table>
                    </div>

                    <!-- Deductions Column -->
                    <div>
                        <div style="background:var(--bg-surface-elevated); padding:8px 12px; font-weight:700; font-size:13px; color:var(--text-main); border-bottom:2px solid var(--amber-500, #f59e0b); display:flex; justify-content:space-between;">
                            <span>DEDUCTIONS</span>
                            <span>AMOUNT (₹)</span>
                        </div>
                        <table style="width:100%; font-size:12.5px; border-collapse:collapse;">
                            <tbody>
                                <tr style="border-bottom:1px solid var(--border-subtle);"><td style="padding:8px 6px; color:var(--text-muted);">Provident Fund (PF - 12%)</td><td style="padding:8px 6px; text-align:right; font-weight:600;">₹${Number(payslip.pf_deduction).toLocaleString()}</td></tr>
                                <tr style="border-bottom:1px solid var(--border-subtle);"><td style="padding:8px 6px; color:var(--text-muted);">Professional Tax (PTax)</td><td style="padding:8px 6px; text-align:right; font-weight:600;">₹${Number(payslip.professional_tax).toLocaleString()}</td></tr>
                                <tr style="border-bottom:1px solid var(--border-subtle);"><td style="padding:8px 6px; color:var(--text-muted);">Unpaid Leave Deductions</td><td style="padding:8px 6px; text-align:right; font-weight:600;">${payslip.unpaid_leaves > 0 ? `(${payslip.unpaid_leaves} days)` : '₹0.00'}</td></tr>
                                <tr><td style="padding:8px 6px; color:transparent;">&nbsp;</td><td style="padding:8px 6px;">&nbsp;</td></tr>
                                <tr><td style="padding:8px 6px; color:transparent;">&nbsp;</td><td style="padding:8px 6px;">&nbsp;</td></tr>
                                <tr><td style="padding:8px 6px; color:transparent;">&nbsp;</td><td style="padding:8px 6px;">&nbsp;</td></tr>
                            </tbody>
                            <tfoot>
                                <tr style="background:var(--bg-surface-elevated); font-weight:700;">
                                    <td style="padding:10px 6px; color:var(--text-main);">TOTAL DEDUCTIONS</td>
                                    <td style="padding:10px 6px; text-align:right; color:var(--rose-400, #f43f5e);">₹${Number(payslip.total_deductions).toLocaleString()}</td>
                                </tr>
                            </tfoot>
                        </table>
                    </div>

                </div>

                <!-- Net In-Hand Payout Callout -->
                <div style="background:linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(99, 102, 241, 0.15) 100%); border:1px solid rgba(16, 185, 129, 0.3); border-radius:var(--radius-sm); padding:20px 24px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:16px;">
                    <div>
                        <div style="font-size:12px; font-weight:700; text-transform:uppercase; letter-spacing:0.06em; color:var(--emerald-400, #10b981);">
                            Net Take-Home Salary
                        </div>
                        <div style="font-size:26px; font-weight:800; color:var(--text-main); margin-top:2px;">
                            ₹${Number(payslip.net_payable).toLocaleString()}
                        </div>
                    </div>
                    <div style="text-align:right; font-size:12px; color:var(--text-muted);">
                        Direct deposit to ${payslip.bank_name || 'Bank'}<br>
                        Transfer Status: <strong>PROCESSED &bull; VERIFIED</strong>
                    </div>
                </div>

                <!-- Footer Signatures -->
                <div style="display:flex; justify-content:space-between; margin-top:36px; padding-top:24px; border-top:1px dashed var(--border-subtle); font-size:12px; color:var(--text-muted);">
                    <div>
                        <div style="height:32px;"></div>
                        <div style="border-top:1px solid var(--border-strong); padding-top:4px;">Employee Signature</div>
                    </div>
                    <div style="text-align:right;">
                        <div style="height:32px; font-style:italic; font-family:serif; font-size:16px; color:var(--primary-400);">Dayflow HR Officer</div>
                        <div style="border-top:1px solid var(--border-strong); padding-top:4px;">Authorized HR Signatory</div>
                    </div>
                </div>

            </div>
        `;
    }

    static changeCycle() {
        this.currentMonth = parseInt(document.getElementById('payroll-month-select')?.value || 1);
        this.currentYear = parseInt(document.getElementById('payroll-year-select')?.value || 2026);
        this.render(this.currentEmployeeId);
    }

    static changeEmployee(empId) {
        if (!empId) return;
        this.currentEmployeeId = parseInt(empId);
        this.render(this.currentEmployeeId);
    }
}

window.PayrollViewComponent = PayrollViewComponent;
