/**
 * Utility functions for the Blender AI Modeling application
 */

// DOM manipulation utilities
const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => document.querySelectorAll(selector);

// API utilities
const API = {
    async request(endpoint, options = {}) {
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };
        
        try {
            console.log('Making API request:', { endpoint, config });
            const response = await fetch(endpoint, config);
            
            console.log('API response received:', {
                status: response.status,
                statusText: response.statusText,
                headers: Object.fromEntries(response.headers.entries())
            });
            
            let data;
            try {
                data = await response.json();
                console.log('API response data:', data);
            } catch (parseError) {
                console.error('Failed to parse JSON response:', parseError);
                throw new Error(`Invalid JSON response from server (${response.status})`);
            }
            
            if (!response.ok) {
                const errorMessage = data.error || data.message || `HTTP ${response.status}: ${response.statusText}`;
                console.error('API request failed with error:', errorMessage);
                throw new Error(errorMessage);
            }
            
            return data;
        } catch (error) {
            console.error('API request failed:', error);
            
            // Handle network errors specifically
            if (error instanceof TypeError && error.message.includes('fetch')) {
                throw new Error('Network error: Unable to connect to server. Make sure the Flask app is running.');
            }
            
            throw error;
        }
    },
    
    async get(endpoint) {
        return this.request(endpoint);
    },
    
    async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }
};

// Form utilities
const FormUtils = {
    serialize(form) {
        const formData = new FormData(form);
        const data = {};
        
        for (let [key, value] of formData.entries()) {
            // Handle radio buttons and checkboxes
            if (form.querySelector(`input[name="${key}"][type="radio"]`)) {
                data[key] = value;
            } else if (form.querySelector(`input[name="${key}"][type="checkbox"]`)) {
                if (!data[key]) data[key] = [];
                data[key].push(value);
            } else {
                // Convert numeric strings to numbers
                const numValue = parseFloat(value);
                data[key] = !isNaN(numValue) && isFinite(numValue) ? numValue : value;
            }
        }
        
        return data;
    },
    
    validate(form, rules = {}) {
        const errors = [];
        const data = this.serialize(form);
        
        for (const [field, ruleSet] of Object.entries(rules)) {
            const value = data[field];
            
            if (ruleSet.required && (!value || value === '')) {
                errors.push(`${field} is required`);
                continue;
            }
            
            if (ruleSet.min && value < ruleSet.min) {
                errors.push(`${field} must be at least ${ruleSet.min}`);
            }
            
            if (ruleSet.max && value > ruleSet.max) {
                errors.push(`${field} must be at most ${ruleSet.max}`);
            }
            
            if (ruleSet.pattern && !ruleSet.pattern.test(value)) {
                errors.push(`${field} format is invalid`);
            }
        }
        
        return {
            isValid: errors.length === 0,
            errors,
            data
        };
    }
};

// UI utilities
const UIUtils = {
    showElement(element) {
        element.classList.remove('hidden');
    },
    
    hideElement(element) {
        element.classList.add('hidden');
    },
    
    toggleElement(element) {
        element.classList.toggle('hidden');
    },
    
    fadeIn(element, duration = 300) {
        element.style.opacity = '0';
        element.style.display = 'block';
        
        const start = performance.now();
        const fade = (timestamp) => {
            const elapsed = timestamp - start;
            const progress = Math.min(elapsed / duration, 1);
            
            element.style.opacity = progress.toString();
            
            if (progress < 1) {
                requestAnimationFrame(fade);
            }
        };
        
        requestAnimationFrame(fade);
    },
    
    fadeOut(element, duration = 300) {
        const start = performance.now();
        const initialOpacity = parseFloat(getComputedStyle(element).opacity) || 1;
        
        const fade = (timestamp) => {
            const elapsed = timestamp - start;
            const progress = Math.min(elapsed / duration, 1);
            
            element.style.opacity = (initialOpacity * (1 - progress)).toString();
            
            if (progress < 1) {
                requestAnimationFrame(fade);
            } else {
                element.style.display = 'none';
            }
        };
        
        requestAnimationFrame(fade);
    }
};

// Debounce utility
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Throttle utility
function throttle(func, limit) {
    let lastFunc;
    let lastRan;
    return function executedFunction(...args) {
        if (!lastRan) {
            func(...args);
            lastRan = Date.now();
        } else {
            clearTimeout(lastFunc);
            lastFunc = setTimeout(() => {
                if ((Date.now() - lastRan) >= limit) {
                    func(...args);
                    lastRan = Date.now();
                }
            }, limit - (Date.now() - lastRan));
        }
    };
}

// Export utilities globally
window.BlenderAI = {
    $,
    $$,
    API,
    FormUtils,
    UIUtils,
    debounce,
    throttle
};