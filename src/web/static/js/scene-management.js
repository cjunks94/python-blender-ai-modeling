/**
 * Scene Management JavaScript Module
 * 
 * This module handles all scene management UI interactions including:
 * - Scene creation and listing
 * - Object management within scenes
 * - Scene preview generation
 * - Multi-mode export functionality
 * - Scene validation
 */

class SceneManager {
    constructor() {
        this.currentScene = null;
        this.selectedObjects = new Set();
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.checkCapabilities();
        this.loadScenesList();
    }

    async checkCapabilities() {
        try {
            const response = await fetch('/api/health');
            const health = await response.json();
            
            // Update UI based on available capabilities
            this.updateCapabilityIndicators(health);
            
            if (!health.scene_management_available) {
                this.showError('Scene management is not available');
                return;
            }
            
            console.log('Scene management capabilities:', {
                scene_management: health.scene_management_available,
                scene_preview: health.scene_preview_available,
                scene_export: health.scene_export_available
            });
            
        } catch (error) {
            console.error('Failed to check capabilities:', error);
            this.showError('Failed to check system capabilities');
        }
    }

    updateCapabilityIndicators(health) {
        // Update status indicators in the UI
        const indicators = {
            'scene-management-status': health.scene_management_available,
            'scene-preview-status': health.scene_preview_available,
            'scene-export-status': health.scene_export_available
        };

        Object.entries(indicators).forEach(([id, available]) => {
            const element = document.getElementById(id);
            if (element) {
                element.className = available ? 'status-available' : 'status-unavailable';
                element.textContent = available ? 'Available' : 'Unavailable';
            }
        });
    }

    setupEventListeners() {
        // Scene creation
        const createSceneBtn = document.getElementById('create-scene-btn');
        if (createSceneBtn) {
            createSceneBtn.addEventListener('click', () => this.showCreateSceneModal());
        }

        // Scene selection
        const sceneSelect = document.getElementById('scene-select');
        if (sceneSelect) {
            sceneSelect.addEventListener('change', (e) => this.loadScene(e.target.value));
        }

        // Preview generation
        const generatePreviewBtn = document.getElementById('generate-scene-preview-btn');
        if (generatePreviewBtn) {
            generatePreviewBtn.addEventListener('click', () => this.generateScenePreview());
        }

        // Export buttons
        const exportButtons = {
            'export-complete-btn': 'complete',
            'export-individual-btn': 'individual',
            'export-selective-btn': 'selective'
        };

        Object.entries(exportButtons).forEach(([id, exportType]) => {
            const btn = document.getElementById(id);
            if (btn) {
                btn.addEventListener('click', () => this.showExportModal(exportType));
            }
        });

        // Validation
        const validateSceneBtn = document.getElementById('validate-scene-btn');
        if (validateSceneBtn) {
            validateSceneBtn.addEventListener('click', () => this.validateScene());
        }

        // AI Scene Generation
        const aiSceneBtn = document.getElementById('ai-scene-btn');
        if (aiSceneBtn) {
            aiSceneBtn.addEventListener('click', () => this.showAISceneModal());
        }

        const aiSceneModalClose = document.getElementById('ai-scene-modal-close');
        if (aiSceneModalClose) {
            aiSceneModalClose.addEventListener('click', () => this.hideAISceneModal());
        }

        const aiSceneCancelBtn = document.getElementById('ai-scene-cancel-btn');
        if (aiSceneCancelBtn) {
            aiSceneCancelBtn.addEventListener('click', () => this.hideAISceneModal());
        }

        const aiSceneForm = document.getElementById('ai-scene-form');
        if (aiSceneForm) {
            aiSceneForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.submitAISceneGeneration();
            });
        }

        // Object selection in scene view
        document.addEventListener('change', (e) => {
            if (e.target.classList.contains('object-checkbox')) {
                this.toggleObjectSelection(e.target.value, e.target.checked);
            }
        });
    }

    async loadScenesList() {
        try {
            const response = await fetch('/api/scenes');
            const data = await response.json();

            if (data.success) {
                this.updateScenesDropdown(data.scenes);
            } else {
                this.showError('Failed to load scenes list');
            }
        } catch (error) {
            console.error('Failed to load scenes:', error);
            this.showError('Failed to load scenes list');
        }
    }

    updateScenesDropdown(scenes) {
        const sceneSelect = document.getElementById('scene-select');
        if (!sceneSelect) return;

        // Clear existing options
        sceneSelect.innerHTML = '<option value="">Select a scene...</option>';

        // Add scenes
        scenes.forEach(scene => {
            const option = document.createElement('option');
            option.value = scene.scene_id;
            option.textContent = `${scene.name} (${scene.object_count} objects)`;
            sceneSelect.appendChild(option);
        });
    }

    async createScene(name, description) {
        try {
            const response = await fetch('/api/scenes', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ name, description })
            });

            const data = await response.json();

            if (data.success) {
                this.showSuccess(`Scene "${name}" created successfully!`);
                this.loadScenesList();
                return data.scene.scene_id;
            } else {
                this.showError(data.error || 'Failed to create scene');
                return null;
            }
        } catch (error) {
            console.error('Failed to create scene:', error);
            this.showError('Failed to create scene');
            return null;
        }
    }

    updateExportButtonStates(scene) {
        const exportCompleteBtn = document.getElementById('export-complete-btn');
        const exportIndividualBtn = document.getElementById('export-individual-btn');
        const exportSelectiveBtn = document.getElementById('export-selective-btn');
        const validateBtn = document.getElementById('validate-scene-btn');
        const previewBtn = document.getElementById('generate-scene-preview-btn');

        if (scene && scene.object_count > 0) {
            if (exportCompleteBtn) exportCompleteBtn.disabled = false;
            if (exportIndividualBtn) exportIndividualBtn.disabled = false;
            if (exportSelectiveBtn) exportSelectiveBtn.disabled = false;
            if (validateBtn) validateBtn.disabled = false;
            if (previewBtn) previewBtn.disabled = false;
        } else {
            if (exportCompleteBtn) exportCompleteBtn.disabled = true;
            if (exportIndividualBtn) exportIndividualBtn.disabled = true;
            if (exportSelectiveBtn) exportSelectiveBtn.disabled = true;
            if (validateBtn) validateBtn.disabled = true;
            if (previewBtn) previewBtn.disabled = true;
        }
    }

    async loadScene(sceneId) {
        if (!sceneId) {
            this.currentScene = null;
            this.updateSceneDisplay(null);
            return;
        }

        try {
            const response = await fetch(`/api/scenes/${sceneId}`);
            const data = await response.json();

            if (data.success) {
                this.currentScene = data.scene;
                this.updateSceneDisplay(data.scene);
                this.selectedObjects.clear();
            } else {
                this.showError(data.error || 'Failed to load scene');
            }
        } catch (error) {
            console.error('Failed to load scene:', error);
            this.showError('Failed to load scene');
        }
    }

    updateSceneDisplay(scene) {
        const sceneDisplay = document.getElementById('scene-display');
        if (!sceneDisplay) return;

        // Update export button states
        this.updateExportButtonStates(scene);

        if (!scene) {
            sceneDisplay.innerHTML = '<p class="text-gray-500">No scene selected</p>';
            return;
        }

        const html = `
            <div class="scene-info bg-white p-6 rounded-lg shadow-md">
                <h3 class="text-xl font-bold mb-4">${scene.name}</h3>
                <p class="text-gray-600 mb-4">${scene.description}</p>
                
                <div class="scene-stats grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                    <div class="stat-item">
                        <div class="text-2xl font-bold text-blue-600">${scene.object_count}</div>
                        <div class="text-sm text-gray-500">Objects</div>
                    </div>
                    <div class="stat-item">
                        <div class="text-2xl font-bold text-green-600">${scene.relationships.length}</div>
                        <div class="text-sm text-gray-500">Relationships</div>
                    </div>
                    <div class="stat-item">
                        <div class="text-2xl font-bold text-purple-600">${scene.statistics?.export_ready_objects || 0}</div>
                        <div class="text-sm text-gray-500">Export Ready</div>
                    </div>
                    <div class="stat-item">
                        <div class="text-2xl font-bold text-orange-600">${scene.statistics?.collisions || 0}</div>
                        <div class="text-sm text-gray-500">Collisions</div>
                    </div>
                </div>

                <div class="objects-list">
                    <h4 class="text-lg font-semibold mb-3">Objects</h4>
                    <div class="space-y-2">
                        ${scene.objects.map(obj => `
                            <div class="object-item flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50">
                                <div class="flex items-center space-x-3">
                                    <input type="checkbox" 
                                           class="object-checkbox" 
                                           value="${obj.id}" 
                                           id="obj-${obj.id}">
                                    <label for="obj-${obj.id}" class="flex items-center space-x-3 cursor-pointer">
                                        <div class="object-icon w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
                                            ${this.getObjectIcon(obj.object_type)}
                                        </div>
                                        <div>
                                            <div class="font-medium">${obj.name}</div>
                                            <div class="text-sm text-gray-500">${obj.object_type} | Size: ${obj.size}</div>
                                        </div>
                                    </label>
                                </div>
                                <div class="object-actions flex space-x-2">
                                    <button class="btn-sm btn-outline" onclick="sceneManager.exportIndividualObject('${obj.id}')">
                                        Export
                                    </button>
                                    <button class="btn-sm btn-outline" onclick="sceneManager.previewObject('${obj.id}')">
                                        Preview
                                    </button>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>

                <div class="scene-preview mt-6">
                    <div id="scene-preview-container" class="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
                        <p class="text-gray-500">Generate scene preview to see the complete scene</p>
                        <button id="generate-preview-btn" class="btn btn-primary mt-4" onclick="sceneManager.generateScenePreview()">
                            Generate Preview
                        </button>
                        <p class="text-xs text-gray-400 mt-2">Note: Scene preview is currently in development</p>
                    </div>
                </div>
            </div>
        `;

        sceneDisplay.innerHTML = html;
    }

    getObjectIcon(objectType) {
        const icons = {
            'cube': '⬜',
            'sphere': '⚪',
            'cylinder': '🥫',
            'plane': '▭'
        };
        return icons[objectType] || '📦';
    }

    toggleObjectSelection(objectId, selected) {
        if (selected) {
            this.selectedObjects.add(objectId);
        } else {
            this.selectedObjects.delete(objectId);
        }

        // Update UI to show selection count
        const selectedCount = this.selectedObjects.size;
        const selectionInfo = document.getElementById('selection-info');
        if (selectionInfo) {
            selectionInfo.textContent = selectedCount > 0 
                ? `${selectedCount} objects selected` 
                : 'No objects selected';
        }

        // Enable/disable selective export button
        const selectiveExportBtn = document.getElementById('export-selective-btn');
        if (selectiveExportBtn) {
            selectiveExportBtn.disabled = selectedCount === 0;
        }
    }

    async generateScenePreview() {
        if (!this.currentScene) {
            this.showError('No scene selected');
            return;
        }

        const generateBtn = document.getElementById('generate-preview-btn');
        const originalText = generateBtn?.textContent;
        
        try {
            if (generateBtn) {
                generateBtn.textContent = 'Generating...';
                generateBtn.disabled = true;
            }

            const response = await fetch(`/api/scenes/${this.currentScene.scene_id}/preview`, {
                method: 'POST'
            });

            const data = await response.json();

            if (data.success) {
                this.displayScenePreview(data.preview_url);
                this.showSuccess('Scene preview generated successfully!');
            } else {
                this.showError(data.error || 'Failed to generate scene preview');
            }
        } catch (error) {
            console.error('Failed to generate scene preview:', error);
            this.showError('Failed to generate scene preview');
        } finally {
            if (generateBtn) {
                generateBtn.textContent = originalText;
                generateBtn.disabled = false;
            }
        }
    }

    displayScenePreview(previewUrl) {
        const container = document.getElementById('scene-preview-container');
        if (!container) return;

        container.innerHTML = `
            <div class="scene-preview-image">
                <img src="${previewUrl}" alt="Scene Preview" class="max-w-full h-auto rounded-lg shadow-lg">
                <div class="mt-4 flex justify-center space-x-4">
                    <button class="btn btn-primary" onclick="sceneManager.generateScenePreview()">
                        Regenerate Preview
                    </button>
                    <a href="${previewUrl}" download class="btn btn-outline">
                        Download Preview
                    </a>
                </div>
            </div>
        `;
    }

    showExportModal(exportType) {
        if (!this.currentScene) {
            this.showError('No scene selected');
            return;
        }

        let modalContent = '';
        
        if (exportType === 'individual') {
            modalContent = this.getIndividualExportModalContent();
        } else if (exportType === 'selective') {
            if (this.selectedObjects.size === 0) {
                this.showError('No objects selected for selective export');
                return;
            }
            modalContent = this.getSelectiveExportModalContent();
        } else {
            modalContent = this.getCompleteExportModalContent();
        }

        this.showModal('Export Scene', modalContent);
    }

    getCompleteExportModalContent() {
        return `
            <div class="export-modal-content">
                <p class="mb-4">Export the complete scene with all ${this.currentScene.object_count} objects.</p>
                
                <div class="form-group mb-4">
                    <label class="block text-sm font-medium mb-2">Export Format</label>
                    <select id="export-format" class="form-control">
                        <option value="obj">OBJ (Recommended)</option>
                        <option value="gltf">GLTF (Best for web)</option>
                        <option value="stl">STL (3D Printing)</option>
                    </select>
                </div>

                <div class="form-group mb-4">
                    <label class="block text-sm font-medium mb-2">Custom Filename (optional)</label>
                    <input type="text" id="export-filename" class="form-control" placeholder="my_scene">
                </div>

                <div class="flex justify-end space-x-3">
                    <button class="btn btn-outline" onclick="sceneManager.closeModal()">Cancel</button>
                    <button class="btn btn-primary" onclick="sceneManager.executeExport('complete')">Export Scene</button>
                </div>
            </div>
        `;
    }

    getSelectiveExportModalContent() {
        const selectedObjectNames = Array.from(this.selectedObjects).map(id => {
            const obj = this.currentScene.objects.find(o => o.id === id);
            return obj ? obj.name : id;
        });

        return `
            <div class="export-modal-content">
                <p class="mb-4">Export ${this.selectedObjects.size} selected objects:</p>
                <ul class="list-disc list-inside mb-4 text-sm text-gray-600">
                    ${selectedObjectNames.map(name => `<li>${name}</li>`).join('')}
                </ul>
                
                <div class="form-group mb-4">
                    <label class="block text-sm font-medium mb-2">Export Format</label>
                    <select id="export-format" class="form-control">
                        <option value="obj">OBJ (Recommended)</option>
                        <option value="gltf">GLTF (Best for web)</option>
                        <option value="stl">STL (3D Printing)</option>
                    </select>
                </div>

                <div class="form-group mb-4">
                    <label class="flex items-center">
                        <input type="checkbox" id="combined-file" checked class="mr-2">
                        Export as single combined file
                    </label>
                    <p class="text-sm text-gray-500 mt-1">Uncheck to export each object as separate files</p>
                </div>

                <div class="form-group mb-4">
                    <label class="block text-sm font-medium mb-2">Custom Filename (optional)</label>
                    <input type="text" id="export-filename" class="form-control" placeholder="selected_objects">
                </div>

                <div class="flex justify-end space-x-3">
                    <button class="btn btn-outline" onclick="sceneManager.closeModal()">Cancel</button>
                    <button class="btn btn-primary" onclick="sceneManager.executeExport('selective')">Export Selected</button>
                </div>
            </div>
        `;
    }

    getIndividualExportModalContent() {
        return `
            <div class="export-modal-content">
                <p class="mb-4">Select an object to export individually:</p>
                
                <div class="form-group mb-4">
                    <label class="block text-sm font-medium mb-2">Object</label>
                    <select id="individual-object-select" class="form-control">
                        <option value="">Select an object...</option>
                        ${this.currentScene.objects.map(obj => 
                            `<option value="${obj.id}">${obj.name} (${obj.object_type})</option>`
                        ).join('')}
                    </select>
                </div>

                <div class="form-group mb-4">
                    <label class="block text-sm font-medium mb-2">Export Format</label>
                    <select id="export-format" class="form-control">
                        <option value="obj">OBJ (Recommended)</option>
                        <option value="gltf">GLTF (Best for web)</option>
                        <option value="stl">STL (3D Printing)</option>
                    </select>
                </div>

                <div class="form-group mb-4">
                    <label class="block text-sm font-medium mb-2">Custom Filename (optional)</label>
                    <input type="text" id="export-filename" class="form-control" placeholder="object_name">
                </div>

                <div class="flex justify-end space-x-3">
                    <button class="btn btn-outline" onclick="sceneManager.closeModal()">Cancel</button>
                    <button class="btn btn-primary" onclick="sceneManager.executeExport('individual')">Export Object</button>
                </div>
            </div>
        `;
    }

    async executeExport(exportType) {
        const format = document.getElementById('export-format')?.value || 'obj';
        const filename = document.getElementById('export-filename')?.value || '';

        let exportData = {
            export_type: exportType,
            format: format,
            filename: filename || undefined
        };

        if (exportType === 'individual') {
            const objectId = document.getElementById('individual-object-select')?.value;
            if (!objectId) {
                this.showError('Please select an object to export');
                return;
            }
            exportData.object_id = objectId;
        } else if (exportType === 'selective') {
            exportData.object_ids = Array.from(this.selectedObjects);
            exportData.combined_file = document.getElementById('combined-file')?.checked !== false;
        }

        try {
            this.closeModal();
            this.showLoading('Exporting...');

            const response = await fetch(`/api/scene/${this.currentScene.scene_id}/export`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(exportData)
            });

            const data = await response.json();

            if (response.ok && data.success) {
                this.showExportSuccess(data);
            } else {
                this.showError(data.error || 'Export failed');
            }
        } catch (error) {
            console.error('Export failed:', error);
            this.showError('Export failed');
        } finally {
            this.hideLoading();
        }
    }

    showExportSuccess(exportResult) {
        const fileList = exportResult.download_urls.map((url, index) => {
            const filename = exportResult.filenames[index];
            return `<li><a href="${url}" class="text-blue-600 hover:underline" download>${filename}</a></li>`;
        }).join('');

        const successMessage = `
            <div class="export-success">
                <h3 class="text-lg font-semibold text-green-600 mb-3">Export Successful!</h3>
                <p class="mb-3">Exported ${exportResult.object_count} objects in ${exportResult.format.toUpperCase()} format.</p>
                <p class="text-sm text-gray-600 mb-3">Total file size: ${exportResult.total_size}</p>
                
                <div class="mb-4">
                    <h4 class="font-medium mb-2">Generated Files:</h4>
                    <ul class="list-disc list-inside">${fileList}</ul>
                </div>
                
                <button class="btn btn-primary" onclick="sceneManager.closeModal()">Close</button>
            </div>
        `;

        this.showModal('Export Complete', successMessage);
    }

    async validateScene() {
        if (!this.currentScene) {
            this.showError('No scene selected');
            return;
        }

        try {
            this.showLoading('Validating scene...');

            const response = await fetch(`/api/scenes/${this.currentScene.scene_id}/validate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ auto_fix: false })
            });

            const data = await response.json();

            if (data.success) {
                this.showValidationResults(data.validation);
            } else {
                this.showError(data.error || 'Validation failed');
            }
        } catch (error) {
            console.error('Validation failed:', error);
            this.showError('Validation failed');
        } finally {
            this.hideLoading();
        }
    }

    showValidationResults(validation) {
        const isValid = validation.is_valid;
        const issues = validation.issues;

        let issuesHtml = '';
        if (issues.length > 0) {
            issuesHtml = `
                <div class="validation-issues mt-4">
                    <h4 class="font-medium mb-2">Issues Found:</h4>
                    <div class="space-y-2">
                        ${issues.map(issue => `
                            <div class="issue-item p-3 rounded-lg ${this.getIssueSeverityClass(issue.severity)}">
                                <div class="flex items-start space-x-2">
                                    <span class="issue-severity font-bold">${issue.severity.toUpperCase()}</span>
                                    <div class="flex-1">
                                        <p class="font-medium">${issue.message}</p>
                                        ${issue.suggestion ? `<p class="text-sm mt-1">💡 ${issue.suggestion}</p>` : ''}
                                        ${issue.auto_fixable ? `<p class="text-sm text-blue-600 mt-1">🔧 Auto-fixable</p>` : ''}
                                    </div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }

        const validationHtml = `
            <div class="validation-results">
                <div class="text-center mb-4">
                    <div class="text-4xl mb-2">${isValid ? '✅' : '⚠️'}</div>
                    <h3 class="text-lg font-semibold ${isValid ? 'text-green-600' : 'text-yellow-600'}">
                        Scene ${isValid ? 'Valid' : 'Has Issues'}
                    </h3>
                </div>
                
                <div class="stats-grid grid grid-cols-2 gap-4 mb-4">
                    <div class="stat-item text-center p-3 bg-gray-50 rounded">
                        <div class="text-xl font-bold">${validation.statistics.object_count}</div>
                        <div class="text-sm text-gray-600">Objects</div>
                    </div>
                    <div class="stat-item text-center p-3 bg-gray-50 rounded">
                        <div class="text-xl font-bold">${issues.length}</div>
                        <div class="text-sm text-gray-600">Issues</div>
                    </div>
                </div>

                ${issuesHtml}

                <div class="flex justify-end space-x-3 mt-6">
                    <button class="btn btn-outline" onclick="sceneManager.closeModal()">Close</button>
                    ${!isValid ? `<button class="btn btn-primary" onclick="sceneManager.autoFixScene()">Auto-Fix Issues</button>` : ''}
                </div>
            </div>
        `;

        this.showModal('Scene Validation Results', validationHtml);
    }

    getIssueSeverityClass(severity) {
        const classes = {
            'error': 'bg-red-50 border border-red-200',
            'warning': 'bg-yellow-50 border border-yellow-200',
            'info': 'bg-blue-50 border border-blue-200'
        };
        return classes[severity] || 'bg-gray-50 border border-gray-200';
    }

    // Utility methods for UI management
    showModal(title, content) {
        const modalHtml = `
            <div id="scene-modal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-screen overflow-y-auto">
                    <div class="p-6">
                        <div class="flex justify-between items-center mb-4">
                            <h2 class="text-xl font-bold">${title}</h2>
                            <button onclick="sceneManager.closeModal()" class="text-gray-500 hover:text-gray-700">
                                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                                </svg>
                            </button>
                        </div>
                        <div class="modal-content">${content}</div>
                    </div>
                </div>
            </div>
        `;

        // Remove existing modal
        this.closeModal();

        // Add new modal
        document.body.insertAdjacentHTML('beforeend', modalHtml);
    }

    closeModal() {
        const modal = document.getElementById('scene-modal');
        if (modal) {
            modal.remove();
        }
    }

    showCreateSceneModal() {
        const content = `
            <div class="create-scene-form">
                <div class="form-group mb-4">
                    <label class="block text-sm font-medium mb-2">Scene Name</label>
                    <input type="text" id="scene-name" class="form-control" placeholder="My Awesome Scene" required>
                </div>

                <div class="form-group mb-4">
                    <label class="block text-sm font-medium mb-2">Description</label>
                    <textarea id="scene-description" class="form-control" rows="3" placeholder="Describe your scene..."></textarea>
                </div>

                <div class="flex justify-end space-x-3">
                    <button class="btn btn-outline" onclick="sceneManager.closeModal()">Cancel</button>
                    <button class="btn btn-primary" onclick="sceneManager.submitCreateScene()">Create Scene</button>
                </div>
            </div>
        `;

        this.showModal('Create New Scene', content);
    }

    async submitCreateScene() {
        const name = document.getElementById('scene-name')?.value.trim();
        const description = document.getElementById('scene-description')?.value.trim();

        if (!name) {
            this.showError('Scene name is required');
            return;
        }

        this.closeModal();
        const sceneId = await this.createScene(name, description);
        
        if (sceneId) {
            // Automatically load the new scene
            const sceneSelect = document.getElementById('scene-select');
            if (sceneSelect) {
                sceneSelect.value = sceneId;
                await this.loadScene(sceneId);
            }
        }
    }

    showLoading(message = 'Loading...') {
        const loadingHtml = `
            <div id="loading-overlay" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                <div class="bg-white rounded-lg p-6 flex items-center space-x-3">
                    <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                    <span>${message}</span>
                </div>
            </div>
        `;

        this.hideLoading(); // Remove any existing loading overlay
        document.body.insertAdjacentHTML('beforeend', loadingHtml);
    }

    hideLoading() {
        const loading = document.getElementById('loading-overlay');
        if (loading) {
            loading.remove();
        }
    }

    showError(message) {
        this.showNotification(message, 'error');
    }

    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type} fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 max-w-sm`;
        
        const bgColor = {
            'error': 'bg-red-500 text-white',
            'success': 'bg-green-500 text-white',
            'info': 'bg-blue-500 text-white'
        }[type] || 'bg-gray-500 text-white';
        
        notification.className += ` ${bgColor}`;
        notification.textContent = message;

        document.body.appendChild(notification);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);

        // Remove on click
        notification.addEventListener('click', () => {
            notification.remove();
        });
    }

    // AI Scene Generation Methods
    showAISceneModal() {
        const modal = document.getElementById('ai-scene-modal');
        if (modal) {
            modal.classList.remove('hidden');
            
            // Reset form
            const form = document.getElementById('ai-scene-form');
            if (form) {
                form.reset();
            }
            this.hideAISceneStatus();
            this.hideAIScenePreview();
        }
    }

    hideAISceneModal() {
        const modal = document.getElementById('ai-scene-modal');
        if (modal) {
            modal.classList.add('hidden');
        }
    }

    showAISceneStatus(message = 'Processing...', progress = 0) {
        const statusDiv = document.getElementById('ai-scene-status');
        const statusText = document.getElementById('ai-scene-status-text');
        const progressBar = document.getElementById('ai-scene-progress');
        
        if (statusDiv) statusDiv.classList.remove('hidden');
        if (statusText) statusText.textContent = message;
        if (progressBar) progressBar.style.width = `${progress}%`;
    }

    hideAISceneStatus() {
        const statusDiv = document.getElementById('ai-scene-status');
        if (statusDiv) statusDiv.classList.add('hidden');
    }

    showAIScenePreview(sceneData) {
        const previewDiv = document.getElementById('ai-scene-preview');
        const sceneName = document.getElementById('ai-scene-name');
        const objectsCount = document.getElementById('ai-scene-objects-count');
        const generationStatus = document.getElementById('ai-scene-generation-status');
        const objectsGrid = document.getElementById('ai-scene-objects-grid');
        const previewImage = document.getElementById('ai-scene-preview-img');
        const previewImageDiv = document.getElementById('ai-scene-preview-image');

        if (previewDiv) previewDiv.classList.remove('hidden');
        if (sceneName) sceneName.textContent = sceneData.scene_info?.scene_name || 'AI Generated Scene';
        if (objectsCount) objectsCount.textContent = `${sceneData.generated_objects || sceneData.total_objects || 0} objects`;
        if (generationStatus) generationStatus.textContent = sceneData.status || 'Generated';

        // Show preview image if available
        if (sceneData.preview_url && previewImage && previewImageDiv) {
            previewImage.src = sceneData.preview_url;
            previewImageDiv.classList.remove('hidden');
        }

        // Display objects
        if (objectsGrid && sceneData.objects) {
            objectsGrid.innerHTML = sceneData.objects.map(obj => `
                <div class="flex items-center space-x-2 p-2 bg-white rounded border text-sm">
                    <span class="text-lg">${this.getObjectIcon(obj.object_type)}</span>
                    <div>
                        <div class="font-medium">${obj.name || 'Object'}</div>
                        <div class="text-xs text-gray-500">${obj.object_type}</div>
                        <div class="text-xs ${obj.status === 'generated' ? 'text-green-600' : 'text-red-600'}">
                            ${obj.status || 'planned'}
                        </div>
                    </div>
                </div>
            `).join('');
        }
    }

    hideAIScenePreview() {
        const previewDiv = document.getElementById('ai-scene-preview');
        const previewImageDiv = document.getElementById('ai-scene-preview-image');
        
        if (previewDiv) previewDiv.classList.add('hidden');
        if (previewImageDiv) previewImageDiv.classList.add('hidden');
    }

    async submitAISceneGeneration() {
        const form = document.getElementById('ai-scene-form');
        if (!form) return;

        const formData = new FormData(form);
        const description = formData.get('description')?.trim();
        
        if (!description) {
            this.showError('Please provide a scene description');
            return;
        }

        const generateData = {
            description: description,
            complexity: formData.get('complexity') || 'medium',
            max_objects: parseInt(formData.get('max_objects')) || 5,
            generate_models: formData.get('generate_models') === 'true'
        };

        const submitBtn = document.getElementById('ai-scene-submit-btn');
        const originalText = submitBtn?.textContent;

        try {
            // Disable form
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.textContent = 'Generating...';
            }

            // Show progress
            this.showAISceneStatus('Processing scene description...', 10);

            const response = await fetch('/api/ai/scene', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(generateData)
            });

            const data = await response.json();

            if (response.ok && data.scene_id) {
                // Show completion immediately
                this.showAISceneStatus('Scene generation complete!', 100);
                
                // Show the generated scene data
                this.showAIScenePreview(data);
                
                // Update button text and enable it
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'View Generated Scene';
                    submitBtn.onclick = () => {
                        this.hideAISceneModal();
                        this.loadGeneratedScene(data.scene_id);
                    };
                }

                // Auto-load the scene after a short delay to show it immediately
                setTimeout(() => {
                    this.loadGeneratedScene(data.scene_id);
                }, 3000);

                this.showSuccess(data.message || 'Scene generated successfully!');

                // Hide status after showing preview
                setTimeout(() => this.hideAISceneStatus(), 2000);

            } else {
                this.showError(data.error || 'Scene generation failed');
                this.hideAISceneStatus();
            }

        } catch (error) {
            console.error('AI scene generation failed:', error);
            this.showError('Scene generation failed. Please try again.');
            this.hideAISceneStatus();
        } finally {
            // Re-enable form if not already handled in success case
            if (submitBtn && submitBtn.textContent === 'Generating...') {
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            }
        }
    }

    async loadGeneratedScene(sceneId) {
        // Select the scene in the dropdown
        const sceneSelect = document.getElementById('scene-select');
        if (sceneSelect) {
            // Refresh scenes list first
            await this.loadScenesList();
            
            // Then select the new scene
            sceneSelect.value = sceneId;
            await this.loadScene(sceneId);
        }
    }

    async previewObject(objectId) {
        // Preview individual object functionality
        if (!this.currentScene) {
            this.showError('No scene selected');
            return;
        }

        const object = this.currentScene.objects.find(obj => obj.id === objectId);
        if (!object) {
            this.showError('Object not found');
            return;
        }

        this.showModal('Object Preview', `
            <div class="text-center">
                <h4 class="text-lg font-medium mb-4">${object.name}</h4>
                <p class="text-sm text-gray-600 mb-4">Type: ${object.object_type} | Size: ${object.size}</p>
                <div class="bg-gray-100 rounded-lg p-8">
                    <p class="text-gray-500">Individual object preview coming soon</p>
                </div>
                <button class="btn btn-primary mt-4" onclick="sceneManager.closeModal()">Close</button>
            </div>
        `);
    }

    async exportIndividualObject(objectId) {
        // Export individual object functionality
        if (!this.currentScene) {
            this.showError('No scene selected');
            return;
        }

        const object = this.currentScene.objects.find(obj => obj.id === objectId);
        if (!object) {
            this.showError('Object not found');
            return;
        }

        // Show export modal for individual object
        this.showExportModal('individual');
        
        // Pre-select the object in the dropdown
        setTimeout(() => {
            const objectSelect = document.getElementById('individual-object-select');
            if (objectSelect) {
                objectSelect.value = objectId;
            }
        }, 100);
    }
}

// Initialize scene manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.sceneManager = new SceneManager();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SceneManager;
}