/**
 * Model creation form controller
 */

class ModelFormController {
    constructor() {
        this.form = document.getElementById('model-form');
        this.progressModal = document.getElementById('progress-modal');
        this.progressBar = document.getElementById('progress-bar');
        this.exportBtn = document.getElementById('export-btn');
        this.currentModel = null;
        
        this.init();
    }
    
    init() {
        this.setupFormSubmission();
        this.setupSliderUpdates();
        this.setupObjectTypeSelection();
        this.setupAIGeneration();
        
        notifications.info('Model creation form initialized');
    }
    
    setupFormSubmission() {
        this.form.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.generateModel();
        });
    }
    
    setupSliderUpdates() {
        // Size slider
        const sizeSlider = document.getElementById('size');
        const sizeValue = document.getElementById('size-value');
        
        sizeSlider.addEventListener('input', () => {
            sizeValue.textContent = parseFloat(sizeSlider.value).toFixed(1);
        });
        
        // Position X slider
        const posXSlider = document.getElementById('pos_x');
        const posXValue = document.getElementById('pos-x-value');
        
        posXSlider.addEventListener('input', () => {
            posXValue.textContent = parseFloat(posXSlider.value).toFixed(1);
        });
    }
    
    setupObjectTypeSelection() {
        const objectTypeInputs = document.querySelectorAll('input[name=\"object_type\"]');
        
        objectTypeInputs.forEach(input => {
            input.addEventListener('change', () => {
                // Add visual feedback for selection
                this.updateStatusMessage(`Selected object type: ${input.value}`);
            });
        });
    }
    
    setupAIGeneration() {
        const aiBtn = document.getElementById('ai-generate-btn');
        
        aiBtn.addEventListener('click', () => {
            notifications.info('AI generation feature coming soon!', {
                title: 'Future Feature'
            });
        });
    }
    
    async generateModel() {
        try {
            // Validate form
            const validation = this.validateForm();
            if (!validation.isValid) {
                notifications.error(validation.errors.join(', '));
                return;
            }
            
            // Show progress modal
            this.showProgressModal();
            this.updateStatusMessage('Generating model...');
            
            // Simulate progress
            await this.simulateProgress();
            
            // Make API call
            const response = await BlenderAI.API.post('/api/generate', validation.data);
            
            // Handle successful generation
            this.currentModel = response;
            this.updateStatusMessage(`Model generated successfully: ${response.object_type}`);
            notifications.success('Model generated successfully!');
            
            // Enable export button
            this.enableExport();
            
        } catch (error) {
            console.error('Model generation failed:', error);
            
            // Provide more detailed error information
            let errorMessage = 'Unknown error occurred';
            if (error.message) {
                errorMessage = error.message;
            } else if (typeof error === 'string') {
                errorMessage = error;
            } else if (error.error) {
                errorMessage = error.error;
            }
            
            console.log('Error details:', {
                message: error.message,
                stack: error.stack,
                fullError: error
            });
            
            notifications.error(`Generation failed: ${errorMessage}`, {
                title: 'Model Generation Error'
            });
            this.updateStatusMessage(`Error: ${errorMessage}`);
        } finally {
            this.hideProgressModal();
        }
    }
    
    validateForm() {
        return BlenderAI.FormUtils.validate(this.form, {
            object_type: { required: true },
            size: { required: true, min: 0.1, max: 10 },
            pos_x: { required: true, min: -10, max: 10 }
        });
    }
    
    showProgressModal() {
        BlenderAI.UIUtils.showElement(this.progressModal);
        this.progressBar.style.width = '0%';
    }
    
    hideProgressModal() {
        BlenderAI.UIUtils.hideElement(this.progressModal);
    }
    
    async simulateProgress() {
        const steps = [
            { progress: 20, message: 'Initializing Blender...' },
            { progress: 40, message: 'Generating geometry...' },
            { progress: 60, message: 'Applying transformations...' },
            { progress: 80, message: 'Finalizing model...' },
            { progress: 100, message: 'Complete!' }
        ];
        
        for (const step of steps) {
            await new Promise(resolve => setTimeout(resolve, 500));
            this.progressBar.style.width = `${step.progress}%`;
        }
    }
    
    enableExport() {
        this.exportBtn.disabled = false;
        this.exportBtn.classList.remove('bg-gray-300', 'text-gray-500', 'cursor-not-allowed');
        this.exportBtn.classList.add('bg-blue-600', 'hover:bg-blue-700', 'text-white', 'cursor-pointer');
        this.exportBtn.textContent = 'Export Model';
        
        // Add export functionality
        this.exportBtn.onclick = () => this.exportModel();
    }
    
    async exportModel() {
        if (!this.currentModel) {
            notifications.error('No model to export');
            return;
        }
        
        try {
            const format = document.getElementById('export-format').value;
            notifications.info(`Exporting model as ${format.toUpperCase()}...`);
            
            const exportResponse = await BlenderAI.API.post('/api/export', {
                model_id: this.currentModel.id,
                format: format,
                model_params: {
                    object_type: this.currentModel.object_type,
                    size: this.currentModel.parameters.size,
                    pos_x: this.currentModel.parameters.pos_x
                }
            });
            
            // Create download link
            const link = document.createElement('a');
            link.href = exportResponse.download_url;
            link.download = exportResponse.filename;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            notifications.success('Model exported successfully!');
            
        } catch (error) {
            notifications.error(`Export failed: ${error.message}`);
        }
    }
    
    updateStatusMessage(message) {
        const statusContainer = document.getElementById('status-container');
        const timestamp = new Date().toLocaleTimeString();
        
        const statusItem = document.createElement('div');
        statusItem.className = 'flex items-center text-sm text-gray-600';
        statusItem.innerHTML = `
            <div class="w-2 h-2 bg-blue-400 rounded-full mr-3"></div>
            <span class="text-gray-500 mr-2">${timestamp}</span>
            ${message}
        `;
        
        statusContainer.appendChild(statusItem);
        
        // Keep only last 5 status messages
        while (statusContainer.children.length > 5) {
            statusContainer.removeChild(statusContainer.firstChild);
        }
        
        // Scroll to bottom
        statusContainer.scrollTop = statusContainer.scrollHeight;
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new ModelFormController();
});