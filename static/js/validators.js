
const Validators = {
    
    // Validar campo vacío
    required: function(value) {
        return value !== null && value !== undefined && value.trim() !== '';
    },
    
    // Validar longitud mínima
    minLength: function(value, length) {
        return value.length >= length;
    },
    
    // Validar longitud máxima
    maxLength: function(value, length) {
        return value.length <= length;
    },
    
    // Validar email
    email: function(value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(value);
    },
    
    // Validar número entero positivo
    positiveInteger: function(value) {
        const num = parseInt(value, 10);
        return !isNaN(num) && num > 0 && num.toString() === value.trim();
    },
    
    // Validar número decimal positivo
    positiveDecimal: function(value) {
        const num = parseFloat(value);
        return !isNaN(num) && num > 0;
    },
    
    // Validar que sea número
    numeric: function(value) {
        return !isNaN(parseFloat(value)) && isFinite(value);
    },
    
    // Validar rango numérico
    range: function(value, min, max) {
        const num = parseFloat(value);
        return !isNaN(num) && num >= min && num <= max;
    },
    
    // Validar patrón
    pattern: function(value, pattern) {
        const regex = new RegExp(pattern);
        return regex.test(value);
    },
    
    // Validar que dos campos coincidan
    match: function(value1, value2) {
        return value1 === value2;
    }
};

// CLASE DE VALIDACIÓN DE FORMULARIOS

class FormValidator {
    constructor(formId) {
        this.form = document.getElementById(formId);
        this.errors = {};
        this.isValid = true;
        
        if (!this.form) {
            console.error('Formulario no encontrado: ' + formId);
            return;
        }
        
        this.initializeValidation();
    }
    
    initializeValidation() {
        // Prevenir envío del formulario al presionar Enter en inputs
        this.form.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && e.target.tagName !== 'TEXTAREA') {
                e.preventDefault();
            }
        });
        
        // Validación en tiempo real
        const inputs = this.form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('blur', () => this.validateField(input));
            input.addEventListener('input', () => this.clearFieldError(input));
        });
    }
    
    validateField(field) {
        const fieldName = field.name;
        const value = field.value.trim();
        const rules = this.getFieldRules(field);
        
        let errorMessage = '';
        
        // Validar requerido
        if (rules.required && !Validators.required(value)) {
            errorMessage = 'Este campo es obligatorio';
        }
        // Validar longitud mínima
        else if (rules.minLength && !Validators.minLength(value, rules.minLength)) {
            errorMessage = `Debe tener al menos ${rules.minLength} caracteres`;
        }
        // Validar longitud máxima
        else if (rules.maxLength && !Validators.maxLength(value, rules.maxLength)) {
            errorMessage = `No puede exceder ${rules.maxLength} caracteres`;
        }
        // Validar email
        else if (rules.email && value && !Validators.email(value)) {
            errorMessage = 'Email inválido';
        }
        // Validar número entero positivo
        else if (rules.positiveInteger && value && !Validators.positiveInteger(value)) {
            errorMessage = 'Debe ser un número entero positivo';
        }
        // Validar número decimal positivo
        else if (rules.positiveDecimal && value && !Validators.positiveDecimal(value)) {
            errorMessage = 'Debe ser un número positivo';
        }
        // Validar rango
        else if (rules.min !== undefined && rules.max !== undefined) {
            if (!Validators.range(value, rules.min, rules.max)) {
                errorMessage = `Debe estar entre ${rules.min} y ${rules.max}`;
            }
        }
        // Validar patrón personalizado
        else if (rules.pattern && value && !Validators.pattern(value, rules.pattern)) {
            errorMessage = rules.patternMessage || 'Formato inválido';
        }
        
        if (errorMessage) {
            this.showFieldError(field, errorMessage);
            this.errors[fieldName] = errorMessage;
            return false;
        } else {
            this.showFieldSuccess(field);
            delete this.errors[fieldName];
            return true;
        }
    }
    
    getFieldRules(field) {
        const rules = {};
        
        // Obtener reglas de atributos HTML5
        if (field.hasAttribute('required')) rules.required = true;
        if (field.hasAttribute('minlength')) rules.minLength = parseInt(field.getAttribute('minlength'));
        if (field.hasAttribute('maxlength')) rules.maxLength = parseInt(field.getAttribute('maxlength'));
        if (field.getAttribute('type') === 'email') rules.email = true;
        if (field.hasAttribute('min')) rules.min = parseFloat(field.getAttribute('min'));
        if (field.hasAttribute('max')) rules.max = parseFloat(field.getAttribute('max'));
        if (field.hasAttribute('pattern')) {
            rules.pattern = field.getAttribute('pattern');
            rules.patternMessage = field.getAttribute('data-pattern-message');
        }
        
        // Obtener reglas de atributos data-*
        if (field.hasAttribute('data-positive-integer')) rules.positiveInteger = true;
        if (field.hasAttribute('data-positive-decimal')) rules.positiveDecimal = true;
        
        return rules;
    }
    
    showFieldError(field, message) {
        field.classList.add('is-invalid');
        field.classList.remove('is-valid');
        
        // Buscar o crear elemento de mensaje de error
        let errorElement = field.parentElement.querySelector('.invalid-feedback');
        if (!errorElement) {
            errorElement = document.createElement('span');
            errorElement.className = 'validation-message invalid-feedback';
            field.parentElement.appendChild(errorElement);
        }
        errorElement.textContent = message;
        errorElement.style.display = 'block';
    }
    
    showFieldSuccess(field) {
        field.classList.add('is-valid');
        field.classList.remove('is-invalid');
        
        const errorElement = field.parentElement.querySelector('.invalid-feedback');
        if (errorElement) {
            errorElement.style.display = 'none';
        }
    }
    
    clearFieldError(field) {
        field.classList.remove('is-invalid', 'is-valid');
        const errorElement = field.parentElement.querySelector('.invalid-feedback');
        if (errorElement) {
            errorElement.style.display = 'none';
        }
    }
    
    validateForm() {
        this.errors = {};
        this.isValid = true;
        
        const inputs = this.form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            if (!this.validateField(input)) {
                this.isValid = false;
            }
        });
        
        return this.isValid;
    }
    
    getErrors() {
        return this.errors;
    }
    
    resetValidation() {
        this.errors = {};
        this.isValid = true;
        
        const inputs = this.form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            this.clearFieldError(input);
        });
    }
}

// VALIDACIÓN DE LOGIN

function initLoginValidation() {
    const validator = new FormValidator('login-form');
    
    const form = document.getElementById('login-form');
    if (!form) return;
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (!validator.validateForm()) {
            showAlert('Por favor, corrija los errores en el formulario', 'error');
            return false;
        }
        
        // Deshabilitar botón de envío
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.classList.add('loading');
        }
        
        // Enviar formulario
        form.submit();
    });
}
// VALIDACIÓN DE PUNTO DE VENTA

function validateCartItem(productoId, cantidad, stock) {
    const errors = [];
    
    if (!productoId || productoId <= 0) {
        errors.push('ID de producto inválido');
    }
    
    if (!Validators.positiveInteger(cantidad.toString())) {
        errors.push('La cantidad debe ser un número entero positivo');
    }
    
    if (parseInt(cantidad) > parseInt(stock)) {
        errors.push('La cantidad solicitada excede el stock disponible');
    }
    
    if (parseInt(cantidad) <= 0) {
        errors.push('La cantidad debe ser mayor a cero');
    }
    
    return errors;
}

function validateSaleData(items) {
    const errors = [];
    
    if (!Array.isArray(items) || items.length === 0) {
        errors.push('El carrito está vacío');
        return errors;
    }
    
    items.forEach((item, index) => {
        if (!item.producto_id) {
            errors.push(`Item ${index + 1}: ID de producto faltante`);
        }
        
        if (!item.cantidad || item.cantidad <= 0) {
            errors.push(`Item ${index + 1}: Cantidad inválida`);
        }
        
        if (!item.precio_unitario || item.precio_unitario <= 0) {
            errors.push(`Item ${index + 1}: Precio inválido`);
        }
    });
    
    return errors;
}

// UTILIDADES DE MENSAJES

function showAlert(message, type = 'info') {
    const alertContainer = document.getElementById('alert-container');
    if (!alertContainer) {
        console.error('Contenedor de alertas no encontrado');
        return;
    }
    
    const alert = document.createElement('div');
    alert.className = `form-alert form-alert-${type}`;
    alert.textContent = message;
    
    alertContainer.innerHTML = '';
    alertContainer.appendChild(alert);
    
    // Auto-cerrar después de 5 segundos
    setTimeout(() => {
        alert.style.transition = 'opacity 0.3s';
        alert.style.opacity = '0';
        setTimeout(() => alert.remove(), 300);
    }, 5000);
}

function clearAlerts() {
    const alertContainer = document.getElementById('alert-container');
    if (alertContainer) {
        alertContainer.innerHTML = '';
    }
}

// PREVENCIÓN DE DOBLE ENVÍO

function preventDoubleSubmit(formId) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    let isSubmitting = false;
    
    form.addEventListener('submit', function(e) {
        if (isSubmitting) {
            e.preventDefault();
            return false;
        }
        
        isSubmitting = true;
        
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.classList.add('loading');
        }
        
        // Reset después de 5 segundos por si hay error
        setTimeout(() => {
            isSubmitting = false;
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.classList.remove('loading');
            }
        }, 5000);
    });
}

// EXPORTAR FUNCIONES

if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        Validators,
        FormValidator,
        initLoginValidation,
        validateCartItem,
        validateSaleData,
        showAlert,
        clearAlerts,
        preventDoubleSubmit
    };
}