const API_BASE = '/api/v1';

class ApiService {
    static getAuthToken() {
        try {
            const user = JSON.parse(localStorage.getItem('hrms_user') || 'null');
            return user?.access_token || user?.token || '';
        } catch {
            return '';
        }
    }

    static async request(endpoint, options = {}) {
        const headers = { 'Accept': 'application/json', ...(options.headers || {}) };
        const token = this.getAuthToken();
        if (token) headers.Authorization = `Bearer ${token}`;

        const requestOptions = { ...options, headers };
        if (requestOptions.body && !(requestOptions.body instanceof FormData)) {
            headers['Content-Type'] = 'application/json';
            requestOptions.body = JSON.stringify(requestOptions.body);
        }

        const response = await fetch(`${API_BASE}${endpoint}`, requestOptions);
        const contentType = response.headers.get('content-type') || '';
        const data = contentType.includes('application/json') ? await response.json() : null;

        if (!response.ok) {
            let message = data?.message || 'Request failed.';
            if (data?.details && Array.isArray(data.details)) {
                message = data.details.map(e => `${e.field ? e.field.replace(/^body\s*->\s*/, '') : 'Field'}: ${e.issue || e.msg || 'Invalid'}`).join(', ');
            } else if (data?.detail) {
                message = Array.isArray(data.detail)
                    ? data.detail.map(e => `${e.loc?.at(-1) || 'field'}: ${e.msg}`).join(', ')
                    : data.detail;
            }
            const error = new Error(message);
            error.status = response.status;
            error.data = data;
            if (response.status === 401) localStorage.removeItem('hrms_user');
            throw error;
        }

        // Backend consistently wraps successful responses in ApiResponse.
        return data && Object.prototype.hasOwnProperty.call(data, 'data') ? data.data : data;
    }

    static async login(login_id, password) {
        return this.request('/auth/login', { method: 'POST', body: { login_id, password } });
    }
    static async signUp(payload) {
        return this.request('/auth/signup', { method: 'POST', body: payload });
    }
    static async verifyEmail(email, code) {
        return this.request('/auth/verify-email', { method: 'POST', body: { email, code } });
    }
    static async changePassword(old_password, new_password) {
        return this.request('/auth/change-password', { method: 'POST', body: { old_password, new_password } });
    }
    static async getCurrentUser() { return this.request('/auth/me'); }
    static async logout() { return this.request('/auth/logout', { method: 'POST' }); }

    static async getMyProfile() { return this.request('/profiles/me'); }
    static async updateMyProfile(data) { return this.request('/profiles/me', { method: 'PUT', body: data }); }

    static async getEmployees(params = {}) {
        const query = new URLSearchParams();
        if (params.search) query.set('query', params.search);
        if (params.query) query.set('query', params.query);
        if (params.department && params.department !== 'all') query.set('department', params.department);
        query.set('page', params.page || 1);
        query.set('size', params.size || params.limit || 24);
        return this.request(`/employees?${query}`);
    }
    static async getEmployee(id) { return this.request(`/employees/${id}`); }
    static async createEmployee(data) { return this.request('/employees', { method: 'POST', body: data }); }
    static async updateEmployee(id, data) { return this.request(`/employees/${id}`, { method: 'PUT', body: data }); }
    static async deleteEmployee(id) { return this.request(`/employees/${id}`, { method: 'DELETE' }); }
    static async getDepartments() { return this.request('/employees/departments'); }

    static async getDashboardStats() { return this.request('/stats/dashboard'); }

    static async getAllSalaries() { return this.request('/salaries'); }
    static async getSalary(employeeId) { return this.request(`/salaries/employee/${employeeId}`); }
    static async getSalaryBreakdown(employeeId) { return this.request(`/salaries/employee/${employeeId}/breakdown`); }
    static async getPayslip(employeeId, month = null, year = null) {
        const query = new URLSearchParams();
        if (month) query.set('month', month);
        if (year) query.set('year', year);
        return this.request(`/salaries/employee/${employeeId}/payslip?${query}`);
    }
    static async saveSalary(employeeId, payload) {
        return this.request(`/salaries/employee/${employeeId}`, { method: 'POST', body: payload });
    }

    static async checkIn() { return this.request('/attendance/check-in', { method: 'POST', body: {} }); }
    static async checkOut() { return this.request('/attendance/check-out', { method: 'POST', body: {} }); }
    static async getTodayAttendance() { return this.request('/attendance/today'); }
    static async getMyAttendance(params = {}) {
        const query = new URLSearchParams();
        if (params.page) query.set('page', params.page);
        if (params.size) query.set('size', params.size);
        return this.request(`/attendance/my-history?${query}`);
    }
    static async getAttendanceSummary() { return this.request('/attendance/my-summary'); }
    static async getAllAttendance(params = {}) {
        const query = new URLSearchParams();
        if (params.employee_id) query.set('employee_id', params.employee_id);
        if (params.start_date) query.set('start_date', params.start_date);
        if (params.end_date) query.set('end_date', params.end_date);
        if (params.page) query.set('page', params.page || 1);
        if (params.size) query.set('size', params.size || 50);
        return this.request(`/attendance?${query}`);
    }
    static async getEmployeeAttendance(employeeId, params = {}) {
        const query = new URLSearchParams();
        if (params.start_date) query.set('start_date', params.start_date);
        if (params.end_date) query.set('end_date', params.end_date);
        if (params.page) query.set('page', params.page || 1);
        if (params.size) query.set('size', params.size || 30);
        return this.request(`/attendance/employee/${employeeId}?${query}`);
    }

    static async getLeaveTypes() { return this.request('/time-off/leave-types'); }
    static async getMyLeaveBalances() { return this.request('/time-off/my-balances'); }
    static async applyLeave(payload) { return this.request('/time-off/requests', { method: 'POST', body: payload }); }
    static async getMyLeaves() {
        const result = await this.request('/time-off/my-requests?size=100');
        return result?.items || [];
    }
    static async getAllLeaves() {
        const result = await this.request('/time-off/requests?size=100');
        return result?.items || [];
    }
    static async reviewLeave(id, status, rejection_reason = null) {
        return this.request(`/time-off/requests/${id}/review`, {
            method: 'PUT',
            body: { status: String(status).toUpperCase(), rejection_reason }
        });
    }

    static async toggleAttendance(_id, status) {
        return status === 'present' ? this.checkIn() : this.checkOut();
    }

    static async uploadFile(formData) {
        return this.request('/upload', { method: 'POST', body: formData });
    }

    static async getPrivateInfo(id) { return this.request(`/employees/${id}/private-info`); }
    static async updatePrivateInfo(id, payload) {
        return this.request(`/employees/${id}/private-info`, { method: 'PUT', body: payload });
    }
}

window.ApiService = ApiService;
