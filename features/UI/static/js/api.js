/**
 * Central API Client for Human Resource Management System (HRMS)
 */
const API_BASE = '/api';

class ApiService {
    static getAuthToken() {
        try {
            const user = JSON.parse(localStorage.getItem('hrms_user') || 'null');
            return user?.token || '';
        } catch (e) {
            return '';
        }
    }

    static async request(endpoint, options = {}) {
        const url = `${API_BASE}${endpoint}`;
        const headers = {
            'Accept': 'application/json',
            ...(options.headers || {})
        };

        const token = this.getAuthToken();
        if (token) {
            headers['Authorization'] = token;
        }

        if (options.body && !(options.body instanceof FormData)) {
            headers['Content-Type'] = 'application/json';
            options.body = JSON.stringify(options.body);
        }

        try {
            const response = await fetch(url, {
                ...options,
                headers
            });

            const contentType = response.headers.get('content-type');
            let data = null;
            if (contentType && contentType.includes('application/json')) {
                data = await response.json();
            }

            if (!response.ok) {
                let errorMsg = 'An unexpected error occurred.';
                if (data && data.detail) {
                    if (Array.isArray(data.detail)) {
                        errorMsg = data.detail.map(e => `${e.loc[e.loc.length - 1]}: ${e.msg}`).join(', ');
                    } else {
                        errorMsg = data.detail;
                    }
                } else if (data && data.message) {
                    errorMsg = data.message;
                }
                const error = new Error(errorMsg);
                error.status = response.status;
                error.data = data;
                throw error;
            }

            return data;
        } catch (err) {
            console.error(`API Request failed: ${options.method || 'GET'} ${url}`, err);
            throw err;
        }
    }

    // Authentication Endpoints
    static async login(username, password) {
        return this.request('/auth/login', {
            method: 'POST',
            body: { username, password }
        });
    }

    static async getCurrentUser() {
        return this.request('/auth/me');
    }

    static async logout() {
        return this.request('/auth/logout', {
            method: 'POST'
        });
    }

    // Employee Endpoints
    static async getEmployees(params = {}) {
        const query = new URLSearchParams();
        Object.entries(params).forEach(([key, value]) => {
            if (value !== undefined && value !== null && value !== '' && value !== 'all') {
                query.append(key, value);
            }
        });
        const qs = query.toString() ? `?${query.toString()}` : '';
        return this.request(`/employees${qs}`);
    }

    static async getEmployee(id) {
        return this.request(`/employees/${id}`);
    }

    static async createEmployee(employeeData) {
        return this.request('/employees', {
            method: 'POST',
            body: employeeData
        });
    }

    static async updateEmployee(id, employeeData) {
        return this.request(`/employees/${id}`, {
            method: 'PUT',
            body: employeeData
        });
    }

    static async deleteEmployee(id, hard = false) {
        return this.request(`/employees/${id}?hard=${hard}`, {
            method: 'DELETE'
        });
    }

    static async toggleStatus(id, status) {
        return this.request(`/employees/${id}/status`, {
            method: 'PATCH',
            body: { status }
        });
    }

    static async toggleAttendance(id, attendance_status) {
        return this.request(`/employees/${id}/attendance`, {
            method: 'PATCH',
            body: { attendance_status }
        });
    }

    static async getDepartments() {
        return this.request('/employees/departments');
    }

    // Stats & Analytics
    static async getDashboardStats() {
        return this.request('/stats/dashboard');
    }

    // Time-off & Leaves
    static async applyLeave(payload) {
        return this.request('/timeoff/apply', {
            method: 'POST',
            body: payload
        });
    }

    static async getMyLeaves(employeeId) {
        return this.request(`/timeoff/my-leaves?employee_id=${employeeId}`);
    }

    static async getAllLeaves() {
        return this.request('/timeoff/all');
    }

    static async reviewLeave(leaveId, status, reviewer = "HR Admin") {
        return this.request(`/timeoff/${leaveId}/status`, {
            method: 'PATCH',
            body: { status, reviewer }
        });
    }

    // Duplicate Email Check
    static async checkDuplicateEmail(email, excludeId = null) {
        const params = new URLSearchParams({ email });
        if (excludeId) params.append('exclude_id', excludeId);
        return this.request(`/employees/check-email?${params.toString()}`);
    }

    // Uploads
    static async uploadFile(formData) {
        return this.request('/upload', {
            method: 'POST',
            body: formData
        });
    }
}

window.ApiService = ApiService;
