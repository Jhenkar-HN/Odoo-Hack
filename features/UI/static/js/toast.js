/**
 * Toast Notification System
 */
class ToastManager {
    constructor() {
        this.container = document.getElementById('toast-container');
        if (!this.container) {
            this.container = document.createElement('div');
            this.container.id = 'toast-container';
            this.container.className = 'toast-container';
            document.body.appendChild(this.container);
        }
    }

    show(type, title, message, duration = 4500) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;

        const icons = {
            success: `<svg class="toast-icon" viewBox="0 0 24 24" fill="none" stroke="var(--accent-emerald)" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>`,
            error: `<svg class="toast-icon" viewBox="0 0 24 24" fill="none" stroke="var(--accent-rose)" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>`,
            warning: `<svg class="toast-icon" viewBox="0 0 24 24" fill="none" stroke="var(--accent-amber)" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>`,
            info: `<svg class="toast-icon" viewBox="0 0 24 24" fill="none" stroke="var(--primary-400)" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>`
        };

        toast.innerHTML = `
            ${icons[type] || icons.info}
            <div class="toast-content">
                <div class="toast-title">${title}</div>
                <div class="toast-message">${message}</div>
            </div>
            <button class="toast-close" onclick="this.parentElement.remove()">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
            </button>
        `;

        this.container.appendChild(toast);

        if (duration > 0) {
            setTimeout(() => {
                toast.style.opacity = '0';
                toast.style.transform = 'translateX(40px)';
                setTimeout(() => toast.remove(), 300);
            }, duration);
        }
    }

    success(title, message, duration) {
        this.show('success', title, message, duration);
    }

    error(title, message, duration) {
        this.show('error', title, message, duration);
    }

    warning(title, message, duration) {
        this.show('warning', title, message, duration);
    }

    info(title, message, duration) {
        this.show('info', title, message, duration);
    }
}

window.Toast = new ToastManager();
