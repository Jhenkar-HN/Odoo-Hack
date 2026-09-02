/**
 * Employee Card Component for Grid View
 */
class EmployeeCardComponent {
    static render(emp) {
        const attStatus = (emp.status || emp.attendance_status || 'absent').toLowerCase();
        const isPresent = attStatus === 'present';
        const isOnLeave = attStatus === 'on_leave';
        const isAbsent = attStatus === 'absent';

        const attBadge = isPresent ? 
            `<span class="badge badge-present"><span class="badge-dot" style="background:#10b981;"></span>Present</span>` : 
            (isOnLeave ? 
                `<span class="badge badge-leave" style="color:#f97316; border-color:rgba(249,115,22,0.3); background:rgba(249,115,22,0.1);"><span class="badge-dot" style="background:#f97316;"></span>On Leave</span>` : 
                `<span class="badge badge-absent" style="color:#eab308; border-color:rgba(234,179,8,0.3); background:rgba(234,179,8,0.1);"><span class="badge-dot" style="background:#eab308;"></span>Absent</span>`);

        const avatar = emp.avatar_url || `https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150&auto=format&fit=crop&q=80`;

        const skills = (emp.skills || []).slice(0, 3);
        const remainingSkills = (emp.skills || []).length - 3;
        
        let skillsHtml = skills.map(s => `<span class="card-skill-tag">${s.name}</span>`).join('');
        if (remainingSkills > 0) {
            skillsHtml += `<span class="card-skill-tag">+${remainingSkills} more</span>`;
        }

        return `
            <div class="employee-card" onclick="App.navigate('profile', ${emp.id})" id="emp-card-${emp.id}">
                <div class="card-status-indicator">
                    ${attBadge}
                </div>

                <div class="card-header">
                    <div class="card-avatar-wrapper">
                        <img src="${avatar}" alt="${emp.full_name}" class="card-avatar">
                        <span class="card-attendance-dot ${attStatus}" title="Status: ${attStatus}"></span>
                    </div>
                    <div class="card-info">
                        <div class="card-code">${emp.login_id || emp.emp_code}</div>
                        <h4 class="card-name" title="${emp.full_name}">${emp.full_name}</h4>
                        <div class="card-role">${emp.job_position}</div>
                    </div>
                </div>

                <div class="card-body">
                    <div class="card-meta-item">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path><polyline points="22,6 12,13 2,6"></polyline></svg>
                        <span style="overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">${emp.work_email}</span>
                    </div>
                    <div class="card-meta-item">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>
                        <span>${emp.phone}</span>
                    </div>

                    ${skills.length > 0 ? `
                        <div class="card-skills-preview">
                            ${skillsHtml}
                        </div>
                    ` : ''}
                </div>

                <div class="card-footer">
                    <span class="badge badge-dept">${emp.department}</span>
                    <span class="card-date">Joined ${emp.date_of_joining}</span>
                </div>
            </div>
        `;
    }
}

window.EmployeeCardComponent = EmployeeCardComponent;
