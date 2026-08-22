/**
 * Client-side validation utilities for HRMS Forms
 */
class FormValidator {
    static validateEmail(email) {
        if (!email) return false;
        const pattern = /^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$/;
        return pattern.test(email.trim());
    }

    static validatePhone(phone) {
        if (!phone) return false;
        const digits = phone.replace(/[\s\-\(\)\+]/g, '');
        return /^\d+$/.test(digits) && digits.length >= 7 && digits.length <= 15;
    }

    static validateRequired(val) {
        if (val === null || val === undefined) return false;
        return String(val).trim().length > 0;
    }

    static validateDate(dateStr) {
        if (!dateStr) return false;
        const d = new Date(dateStr);
        return !isNaN(d.getTime());
    }

    static validateField(inputElement) {
        const value = inputElement.value;
        const fieldName = inputElement.getAttribute('name') || inputElement.id;
        const isRequired = inputElement.hasAttribute('required') || inputElement.classList.contains('required');
        const formGroup = inputElement.closest('.form-group');
        let errorSpan = formGroup ? formGroup.querySelector('.form-error-msg') : null;

        if (!errorSpan && formGroup) {
            errorSpan = document.createElement('div');
            errorSpan.className = 'form-error-msg';
            formGroup.appendChild(errorSpan);
        }

        let errorMessage = '';

        // Required check
        if (isRequired && !this.validateRequired(value)) {
            const label = formGroup ? (formGroup.querySelector('.form-label')?.textContent.replace('*', '').trim()) : fieldName;
            errorMessage = `${label || 'This field'} is required.`;
        }
        // Email check
        else if (inputElement.type === 'email' || fieldName.toLowerCase().includes('email')) {
            if (isRequired || value.trim().length > 0) {
                if (!this.validateEmail(value)) {
                    errorMessage = 'Please enter a valid email address (e.g. name@company.com).';
                }
            }
        }
        // Phone check
        else if (inputElement.type === 'tel' || fieldName.toLowerCase().includes('phone')) {
            if (isRequired || value.trim().length > 0) {
                if (!this.validatePhone(value)) {
                    errorMessage = 'Phone number must be valid (7 to 15 digits).';
                }
            }
        }
        // Date check
        else if (inputElement.type === 'date' || fieldName.toLowerCase().includes('date')) {
            if (isRequired && !this.validateDate(value)) {
                errorMessage = 'Please provide a valid date.';
            }
        }

        // Apply error states
        if (errorMessage) {
            inputElement.classList.add('is-invalid');
            if (errorSpan) {
                errorSpan.textContent = errorMessage;
                errorSpan.style.display = 'flex';
            }
            return false;
        } else {
            inputElement.classList.remove('is-invalid');
            if (errorSpan) {
                errorSpan.style.display = 'none';
            }
            return true;
        }
    }

    static validateAll(formElement) {
        const inputs = formElement.querySelectorAll('input, select, textarea');
        let isValid = true;
        let firstInvalidInput = null;

        inputs.forEach(input => {
            const fieldValid = this.validateField(input);
            if (!fieldValid && isValid) {
                isValid = false;
                firstInvalidInput = input;
            }
        });

        if (firstInvalidInput) {
            firstInvalidInput.focus();
        }

        return isValid;
    }

    static attachLiveValidation(formElement) {
        const inputs = formElement.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('input', () => this.validateField(input));
            input.addEventListener('blur', () => this.validateField(input));
        });
    }
}

window.FormValidator = FormValidator;
