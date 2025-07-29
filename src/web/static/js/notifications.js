/**
 * Notification system for user feedback
 */

class NotificationSystem {
    constructor() {
        this.container = document.getElementById('notifications');
        this.notifications = new Map();
        this.autoCloseDelay = 5000; // 5 seconds
    }
    
    show(message, type = 'info', options = {}) {
        const id = this.generateId();
        const notification = this.createNotification(id, message, type, options);
        
        this.container.appendChild(notification);
        this.notifications.set(id, notification);
        
        // Trigger animation
        requestAnimationFrame(() => {
            notification.classList.remove('translate-x-full', 'opacity-0');
        });
        
        // Auto-close unless disabled
        if (options.autoClose !== false) {
            setTimeout(() => {
                this.hide(id);
            }, options.duration || this.autoCloseDelay);
        }
        
        return id;
    }
    
    hide(id) {
        const notification = this.notifications.get(id);
        if (!notification) return;
        
        // Animate out
        notification.classList.add('translate-x-full', 'opacity-0');
        
        // Remove from DOM after animation
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
            this.notifications.delete(id);
        }, 300);
    }
    
    success(message, options = {}) {
        return this.show(message, 'success', options);
    }
    
    error(message, options = {}) {
        return this.show(message, 'error', { ...options, autoClose: false });
    }
    
    warning(message, options = {}) {
        return this.show(message, 'warning', options);
    }
    
    info(message, options = {}) {
        return this.show(message, 'info', options);
    }
    
    createNotification(id, message, type, options) {
        const notification = document.createElement('div');
        notification.id = `notification-${id}`;
        // Add type-specific styling
        const typeStyles = {
            error: 'bg-red-50 border-red-200',
            success: 'bg-green-50 border-green-200',
            warning: 'bg-yellow-50 border-yellow-200',
            info: 'bg-blue-50 border-blue-200'
        };
        
        notification.className = `
            transform translate-x-full opacity-0 transition-all duration-300 ease-in-out
            max-w-lg w-full ${typeStyles[type] || 'bg-white'} shadow-lg rounded-lg pointer-events-auto 
            ring-1 ring-black ring-opacity-5 border overflow-hidden
        `;
        
        const typeConfig = this.getTypeConfig(type);
        
        notification.innerHTML = `
            <div class="p-4">
                <div class="flex items-start">
                    <div class="flex-shrink-0">
                        ${typeConfig.icon}
                    </div>
                    <div class="ml-3 flex-1 min-w-0 pt-0.5">
                        <p class="text-sm font-medium text-gray-900">
                            ${options.title || typeConfig.title}
                        </p>
                        <p class="mt-1 text-sm text-gray-700 break-words whitespace-pre-wrap">
                            ${this.escapeHtml(message)}
                        </p>
                    </div>
                    <div class="ml-4 flex-shrink-0 flex">
                        <button class="rounded-md inline-flex text-gray-600 hover:text-gray-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 p-1"
                                onclick="notifications.hide('${id}')">
                            <span class="sr-only">Close</span>
                            <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                                <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                            </svg>
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        return notification;
    }
    
    getTypeConfig(type) {
        const configs = {
            success: {
                title: 'Success',
                icon: `<svg class="h-6 w-6 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>`
            },
            error: {
                title: 'Error',
                icon: `<svg class="h-6 w-6 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>`
            },
            warning: {
                title: 'Warning',
                icon: `<svg class="h-6 w-6 text-yellow-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>`
            },
            info: {
                title: 'Info',
                icon: `<svg class="h-6 w-6 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>`
            }
        };
        
        return configs[type] || configs.info;
    }
    
    generateId() {
        return Math.random().toString(36).substr(2, 9);
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    clear() {
        this.notifications.forEach((notification, id) => {
            this.hide(id);
        });
    }
}

// Initialize global notification system
const notifications = new NotificationSystem();

// Export globally
window.notifications = notifications;