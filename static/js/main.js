// ===== Main JavaScript ===== 

// Utility Functions
const AuthSafe = {
    showAlert: function(message, type = 'info') {
        console.log(`[${type.toUpperCase()}] ${message}`);
    },
    
    hideLoading: function(elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            element.style.display = 'none';
        }
    },
    
    showLoading: function(elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            element.style.display = 'block';
        }
    },
    
    validateEmail: function(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    },
    
    validatePIN: function(pin) {
        return /^\d{4,6}$/.test(pin);
    }
};

// Form Validation
document.addEventListener('DOMContentLoaded', function() {
    // Email validation
    const emailInputs = document.querySelectorAll('input[type="email"]');
    emailInputs.forEach(input => {
        input.addEventListener('blur', function() {
            if (this.value && !AuthSafe.validateEmail(this.value)) {
                this.classList.add('is-invalid');
                this.classList.remove('is-valid');
            } else if (this.value) {
                this.classList.add('is-valid');
                this.classList.remove('is-invalid');
            }
        });
    });
    
    // PIN validation
    const pinInputs = document.querySelectorAll('input[name="pin"], input[name="pin_confirm"]');
    pinInputs.forEach(input => {
        input.addEventListener('input', function() {
            // Only allow digits
            this.value = this.value.replace(/[^\d]/g, '');
            // Limit to 6 digits
            if (this.value.length > 6) {
                this.value = this.value.slice(0, 6);
            }
        });
        
        input.addEventListener('blur', function() {
            if (this.value && !AuthSafe.validatePIN(this.value)) {
                this.classList.add('is-invalid');
                this.classList.remove('is-valid');
            } else if (this.value) {
                this.classList.add('is-valid');
                this.classList.remove('is-invalid');
            }
        });
    });
    
    // Form submission prevention during process
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                setTimeout(() => {
                    submitBtn.disabled = false;
                }, 3000);
            }
        });
    });
});

// Initialize tooltips and popovers
document.addEventListener('DOMContentLoaded', function() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// Dismiss alerts after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            const closeBtn = alert.querySelector('.btn-close');
            if (closeBtn) {
                closeBtn.click();
            }
        }, 5000);
    });
});

// Handle file input preview
const fileInputs = document.querySelectorAll('input[type="file"]');
fileInputs.forEach(input => {
    input.addEventListener('change', function() {
        if (this.files && this.files[0]) {
            const fileName = this.files[0].name;
            const label = this.previousElementSibling || this.labels[0];
            if (label) {
                label.textContent = `File: ${fileName}`;
            }
        }
    });
});

// Prevent multiple submissions
function preventDoubleSubmit(formId) {
    const form = document.getElementById(formId);
    if (form) {
        form.addEventListener('submit', function(e) {
            if (this.dataset.submitted) {
                e.preventDefault();
                return false;
            }
            this.dataset.submitted = 'true';
        });
    }
}

// Log page load
console.log('AuthSafe application loaded successfully');
