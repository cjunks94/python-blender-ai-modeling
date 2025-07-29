/**
 * AI Integration JavaScript Module
 * Handles AI-powered model generation interface and API interactions
 */

class AIModelGenerator {
    constructor() {
        this.modal = document.getElementById('ai-modal');
        this.form = document.getElementById('ai-form');
        this.openBtn = document.getElementById('ai-generate-btn');
        this.closeBtn = document.getElementById('ai-modal-close');
        this.cancelBtn = document.getElementById('ai-cancel-btn');
        
        // Form elements
        this.descriptionField = document.getElementById('ai-description');
        this.styleField = document.getElementById('ai-style');
        this.complexityField = document.getElementById('ai-complexity');
        this.userLevelField = document.getElementById('ai-user-level');
        
        // Status elements
        this.statusDiv = document.getElementById('ai-status');
        this.statusText = document.getElementById('ai-status-text');
        this.infoPanel = document.getElementById('ai-info-panel');
        
        // Info elements
        this.infoStyle = document.getElementById('ai-info-style');
        this.infoReasoning = document.getElementById('ai-info-reasoning');
        this.infoSuggestions = document.getElementById('ai-info-suggestions');
        this.suggestionsList = document.getElementById('ai-suggestions-list');
        this.infoWarnings = document.getElementById('ai-info-warnings');
        this.warningsList = document.getElementById('ai-warnings-list');
        
        this.submitBtn = document.getElementById('ai-submit-btn');
        
        this.isGenerating = false;
        
        this.initializeEventListeners();
        this.checkAIAvailability();
    }
    
    initializeEventListeners() {
        // Modal controls
        this.openBtn.addEventListener('click', () => this.openModal());
        this.closeBtn.addEventListener('click', () => this.closeModal());
        this.cancelBtn.addEventListener('click', () => this.closeModal());
        
        // Form submission
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
        
        // Close modal on background click
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.closeModal();
            }
        });
        
        // Real-time form validation
        this.descriptionField.addEventListener('input', () => this.validateForm());
    }
    
    async checkAIAvailability() {
        try {
            const response = await fetch('/api/health');
            const health = await response.json();
            
            if (!health.ai_available) {
                this.openBtn.disabled = true;
                this.openBtn.classList.add('opacity-50', 'cursor-not-allowed');
                this.openBtn.innerHTML = `
                    <svg class="h-5 w-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.864-.833-2.634 0L4.232 15.5c-.77.833.192 2.5 1.732 2.5z"/>
                    </svg>
                    AI Unavailable
                `;
                this.openBtn.title = 'AI integration is not configured or available';
            }
        } catch (error) {
            console.warn('Could not check AI availability:', error);
        }
    }
    
    openModal() {
        if (this.openBtn.disabled) return;
        
        this.modal.classList.remove('hidden');
        this.descriptionField.focus();
        this.resetForm();
    }
    
    closeModal() {
        if (this.isGenerating) {
            if (!confirm('AI generation is in progress. Are you sure you want to cancel?')) {
                return;
            }
        }
        
        this.modal.classList.add('hidden');
        this.resetForm();
        this.isGenerating = false;
    }
    
    resetForm() {
        this.form.reset();
        this.statusDiv.classList.add('hidden');
        this.infoPanel.classList.add('hidden');
        this.submitBtn.disabled = false;
        this.submitBtn.textContent = 'Generate with AI';
        this.validateForm();
    }
    
    validateForm() {
        const description = this.descriptionField.value.trim();
        const isValid = description.length >= 10; // Minimum description length
        
        this.submitBtn.disabled = !isValid || this.isGenerating;
    }
    
    async handleSubmit(event) {
        event.preventDefault();
        
        if (this.isGenerating) return;
        
        const description = this.descriptionField.value.trim();
        if (!description) {
            this.showError('Please enter a description of what you want to create.');
            return;
        }
        
        this.isGenerating = true;
        this.showStatus('Processing your description with AI...');
        
        try {
            const formData = {
                description: description,
                preferred_style: this.styleField.value,
                complexity: this.complexityField.value,
                user_level: this.userLevelField.value
            };
            
            const response = await fetch('/api/ai/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });
            
            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.message || result.error || 'AI generation failed');
            }
            
            // Show AI interpretation info
            this.showAIInfo(result.ai_info);
            
            // Update status
            this.showStatus('AI generation successful! Closing modal...');
            
            // Handle the successful generation (similar to manual generation)
            this.handleGenerationSuccess(result);
            
            // Close modal after a short delay
            setTimeout(() => {
                this.closeModal();
            }, 1500);
            
        } catch (error) {
            console.error('AI generation error:', error);
            this.showError(error.message || 'Failed to generate model with AI');
        } finally {
            this.isGenerating = false;
            this.validateForm();
        }
    }
    
    showStatus(message) {
        this.statusText.textContent = message;
        this.statusDiv.className = 'p-4 rounded-lg border border-blue-200 bg-blue-50';
        this.statusDiv.classList.remove('hidden');
    }
    
    showError(message) {
        this.statusText.textContent = message;
        this.statusDiv.className = 'p-4 rounded-lg border border-red-200 bg-red-50';
        this.statusDiv.classList.remove('hidden');
        
        // Hide error after 5 seconds
        setTimeout(() => {
            this.statusDiv.classList.add('hidden');
        }, 5000);
    }
    
    showAIInfo(aiInfo) {
        // Display AI interpretation details
        this.infoStyle.textContent = aiInfo.prompt_style || 'N/A';
        this.infoReasoning.textContent = aiInfo.reasoning || 'No reasoning provided';
        
        // Show suggestions if any
        if (aiInfo.suggestions && aiInfo.suggestions.length > 0) {
            this.suggestionsList.innerHTML = '';
            aiInfo.suggestions.forEach(suggestion => {
                const li = document.createElement('li');
                li.textContent = suggestion;
                this.suggestionsList.appendChild(li);
            });
            this.infoSuggestions.classList.remove('hidden');
        } else {
            this.infoSuggestions.classList.add('hidden');
        }
        
        // Show warnings if any
        if (aiInfo.warnings && aiInfo.warnings.length > 0) {
            this.warningsList.innerHTML = '';
            aiInfo.warnings.forEach(warning => {
                const li = document.createElement('li');
                li.textContent = warning;
                this.warningsList.appendChild(li);
            });
            this.infoWarnings.classList.remove('hidden');
        } else {
            this.infoWarnings.classList.add('hidden');
        }
        
        this.infoPanel.classList.remove('hidden');
    }
    
    handleGenerationSuccess(result) {
        // Update the main UI with the generated model
        // This integrates with the existing model display system
        
        // Update status panel
        const statusContainer = document.getElementById('status-container');
        if (statusContainer) {
            statusContainer.innerHTML = `
                <div class="flex items-center text-sm text-green-600">
                    <div class="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
                    AI model generated successfully
                </div>
                <div class="flex items-center text-sm text-gray-600">
                    <div class="w-2 h-2 bg-blue-400 rounded-full mr-3"></div>
                    Model ID: ${result.id}
                </div>
                <div class="flex items-center text-sm text-gray-600">
                    <div class="w-2 h-2 bg-purple-400 rounded-full mr-3"></div>
                    Type: ${result.object_type} (AI Generated)
                </div>
            `;
        }
        
        // Show preview if available
        if (result.preview_url) {
            this.showPreview(result.preview_url, result);
        }
        
        // Enable export
        this.enableExport(result);
        
        // Show success message
        this.showNotification(`AI successfully generated a ${result.object_type}!`, 'success');
        
        // Store result for export
        window.lastGeneratedModel = result;
    }
    
    showPreview(previewUrl, modelData) {
        const previewPanel = document.getElementById('preview-panel');
        const previewImage = document.getElementById('preview-image');
        const previewLoading = document.getElementById('preview-loading');
        const previewError = document.getElementById('preview-error');
        const previewInfo = document.getElementById('preview-info');
        const previewDimensions = document.getElementById('preview-dimensions');
        
        if (previewPanel && previewImage) {
            previewPanel.classList.remove('hidden');
            previewLoading.classList.remove('hidden');
            previewImage.classList.add('hidden');
            previewError.classList.add('hidden');
            
            previewImage.onload = function() {
                previewLoading.classList.add('hidden');
                previewImage.classList.remove('hidden');
                if (previewInfo && previewDimensions) {
                    previewDimensions.textContent = `${modelData.object_type} - Size: ${modelData.parameters.size}`;
                    previewInfo.classList.remove('hidden');
                }
            };
            
            previewImage.onerror = function() {
                previewLoading.classList.add('hidden');
                previewError.classList.remove('hidden');
            };
            
            previewImage.src = previewUrl + '?' + Date.now(); // Cache bust
        }
    }
    
    enableExport(modelData) {
        const exportBtn = document.getElementById('export-btn');
        if (exportBtn) {
            exportBtn.disabled = false;
            exportBtn.classList.remove('bg-gray-300', 'text-gray-500', 'cursor-not-allowed');
            exportBtn.classList.add('bg-blue-600', 'hover:bg-blue-700', 'text-white', 'cursor-pointer');
            exportBtn.textContent = 'Export Model';
        }
        
        // Update export instructions
        const exportInstructions = exportBtn.nextElementSibling;
        if (exportInstructions) {
            exportInstructions.textContent = 'Ready to export your AI-generated model';
        }
    }
    
    showNotification(message, type = 'info') {
        // Create a simple notification
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg transition-all duration-300 ${
            type === 'success' ? 'bg-green-500 text-white' : 
            type === 'error' ? 'bg-red-500 text-white' : 
            'bg-blue-500 text-white'
        }`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
            notification.style.opacity = '1';
        }, 100);
        
        // Remove after 4 seconds
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            notification.style.opacity = '0';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 4000);
    }
}

// Initialize AI integration when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.aiModelGenerator = new AIModelGenerator();
});