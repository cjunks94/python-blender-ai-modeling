/**
 * General UI interactions and theme management
 */

class UIController {
    constructor() {
        this.init();
    }
    
    init() {
        this.setupThemeToggle();
        this.setupHelpButton();
        this.setupGetStartedButton();
        this.setupKeyboardShortcuts();
        this.setupCollapsibleSections();
        
        console.log('UI Controller initialized');
    }
    
    setupThemeToggle() {
        const themeToggle = document.getElementById('theme-toggle');
        
        themeToggle.addEventListener('click', () => {
            document.body.classList.toggle('dark');
            
            // Store theme preference
            const isDark = document.body.classList.contains('dark');
            localStorage.setItem('theme', isDark ? 'dark' : 'light');
            
            notifications.info(`Switched to ${isDark ? 'dark' : 'light'} theme`);
        });
        
        // Load saved theme
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme === 'dark') {
            document.body.classList.add('dark');
        }
    }
    
    setupHelpButton() {
        const helpBtn = document.getElementById('help-btn');
        
        helpBtn.addEventListener('click', () => {
            this.showHelpModal();
        });
    }
    
    setupGetStartedButton() {
        const getStartedBtn = document.getElementById('get-started-btn');
        
        getStartedBtn.addEventListener('click', () => {
            // Smooth scroll to form
            const form = document.getElementById('model-form');
            form.scrollIntoView({ 
                behavior: 'smooth',
                block: 'start'
            });
            
            // Focus on first input
            setTimeout(() => {
                const firstInput = form.querySelector('input[type="radio"]:checked');
                if (firstInput) {
                    firstInput.focus();
                }
            }, 500);
        });
    }
    
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + G: Generate model
            if ((e.ctrlKey || e.metaKey) && e.key === 'g') {
                e.preventDefault();
                const generateBtn = document.querySelector('#model-form button[type="submit"]');
                if (generateBtn && !generateBtn.disabled) {
                    generateBtn.click();
                }
            }
            
            // Ctrl/Cmd + E: Export model
            if ((e.ctrlKey || e.metaKey) && e.key === 'e') {
                e.preventDefault();
                const exportBtn = document.getElementById('export-btn');
                if (exportBtn && !exportBtn.disabled) {
                    exportBtn.click();
                }
            }
            
            // Escape: Close modals
            if (e.key === 'Escape') {
                this.closeAllModals();
            }
            
            // F1: Show help
            if (e.key === 'F1') {
                e.preventDefault();
                this.showHelpModal();
            }
        });
    }
    
    showHelpModal() {
        const helpModal = this.createHelpModal();
        document.body.appendChild(helpModal);
        
        BlenderAI.UIUtils.showElement(helpModal);
    }
    
    createHelpModal() {
        const modal = document.createElement('div');
        modal.id = 'help-modal';
        modal.className = 'fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4';
        
        modal.innerHTML = `
            <div class="bg-white rounded-xl max-w-2xl w-full max-h-[80vh] overflow-y-auto">
                <div class="p-6">
                    <div class="flex justify-between items-center mb-6">
                        <h2 class="text-2xl font-bold text-gray-900">Help & Shortcuts</h2>
                        <button class="text-gray-400 hover:text-gray-600" onclick="this.closest('#help-modal').remove()">
                            <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                            </svg>
                        </button>
                    </div>
                    
                    <div class="space-y-6">
                        <section>
                            <h3 class="text-lg font-semibold text-gray-900 mb-3">Getting Started</h3>
                            <ol class="list-decimal list-inside space-y-2 text-gray-600">
                                <li>Select an object type (cube, sphere, cylinder, or plane)</li>
                                <li>Adjust the size and position parameters</li>
                                <li>Click "Generate Model" to create your 3D object</li>
                                <li>Export your model in your preferred format</li>
                            </ol>
                        </section>
                        
                        <section>
                            <h3 class="text-lg font-semibold text-gray-900 mb-3">Keyboard Shortcuts</h3>
                            <div class="grid grid-cols-2 gap-4">
                                <div class="bg-gray-50 p-3 rounded-lg">
                                    <kbd class="bg-gray-200 px-2 py-1 rounded text-sm">Ctrl+G</kbd>
                                    <span class="ml-2 text-sm text-gray-600">Generate Model</span>
                                </div>
                                <div class="bg-gray-50 p-3 rounded-lg">
                                    <kbd class="bg-gray-200 px-2 py-1 rounded text-sm">Ctrl+E</kbd>
                                    <span class="ml-2 text-sm text-gray-600">Export Model</span>
                                </div>
                                <div class="bg-gray-50 p-3 rounded-lg">
                                    <kbd class="bg-gray-200 px-2 py-1 rounded text-sm">F1</kbd>
                                    <span class="ml-2 text-sm text-gray-600">Show Help</span>
                                </div>
                                <div class="bg-gray-50 p-3 rounded-lg">
                                    <kbd class="bg-gray-200 px-2 py-1 rounded text-sm">Esc</kbd>
                                    <span class="ml-2 text-sm text-gray-600">Close Modals</span>
                                </div>
                            </div>
                        </section>
                        
                        <section>
                            <h3 class="text-lg font-semibold text-gray-900 mb-3">Supported Formats</h3>
                            <div class="grid grid-cols-3 gap-4">
                                <div class="text-center p-3 bg-blue-50 rounded-lg">
                                    <strong class="text-blue-600">OBJ</strong>
                                    <p class="text-sm text-gray-600 mt-1">Wavefront OBJ</p>
                                </div>
                                <div class="text-center p-3 bg-green-50 rounded-lg">
                                    <strong class="text-green-600">GLTF</strong>
                                    <p class="text-sm text-gray-600 mt-1">GL Transmission Format</p>
                                </div>
                                <div class="text-center p-3 bg-purple-50 rounded-lg">
                                    <strong class="text-purple-600">STL</strong>
                                    <p class="text-sm text-gray-600 mt-1">Stereolithography</p>
                                </div>
                            </div>
                        </section>
                        
                        <section>
                            <h3 class="text-lg font-semibold text-gray-900 mb-3">Requirements</h3>
                            <ul class="space-y-2 text-gray-600">
                                <li class="flex items-center">
                                    <svg class="h-5 w-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                                        <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                                    </svg>
                                    Blender 3.0+ installed on your system
                                </li>
                                <li class="flex items-center">
                                    <svg class="h-5 w-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                                        <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                                    </svg>
                                    Python 3.8+ with required packages
                                </li>
                                <li class="flex items-center">
                                    <svg class="h-5 w-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                                        <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                                    </svg>
                                    Modern web browser with JavaScript enabled
                                </li>
                            </ul>
                        </section>
                    </div>
                    
                    <div class="mt-6 pt-6 border-t border-gray-200">
                        <button class="w-full bg-blender-orange hover:bg-orange-600 text-white font-semibold py-3 px-6 rounded-lg transition-colors"
                                onclick="this.closest('#help-modal').remove()">
                            Got it!
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        // Close on backdrop click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
        
        return modal;
    }
    
    closeAllModals() {
        const modals = document.querySelectorAll('[id$="-modal"]');
        modals.forEach(modal => {
            if (!modal.classList.contains('hidden')) {
                BlenderAI.UIUtils.hideElement(modal);
                // Remove help modal completely
                if (modal.id === 'help-modal') {
                    setTimeout(() => modal.remove(), 300);
                }
            }
        });
    }
    
    setupCollapsibleSections() {
        const sectionToggles = document.querySelectorAll('.section-toggle');
        console.log('Setting up collapsible sections, found:', sectionToggles.length);
        
        sectionToggles.forEach(toggle => {
            // Remove any existing listeners first
            const newToggle = toggle.cloneNode(true);
            toggle.parentNode.replaceChild(newToggle, toggle);
            
            newToggle.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                
                const section = newToggle.getAttribute('data-section');
                const content = document.getElementById(`${section}-content`);
                const icon = newToggle.querySelector('.toggle-icon');
                
                if (!content) {
                    console.error('Content section not found:', `${section}-content`);
                    return;
                }
                
                console.log('Toggling section:', section);
                
                // Force browser to recalculate styles
                content.style.display = 'block';
                const height = content.scrollHeight;
                content.style.display = '';
                
                // Toggle expanded state
                const isExpanded = content.classList.contains('expanded');
                
                if (isExpanded) {
                    // Collapse
                    newToggle.classList.remove('expanded');
                    icon.classList.remove('expanded');
                    content.style.maxHeight = height + 'px';
                    // Force reflow
                    content.offsetHeight;
                    content.classList.remove('expanded');
                    content.style.maxHeight = '0';
                    console.log('Collapsed section:', section);
                } else {
                    // Expand
                    newToggle.classList.add('expanded');
                    icon.classList.add('expanded');
                    content.classList.add('expanded');
                    content.style.maxHeight = height + 'px';
                    // Remove inline style after transition
                    setTimeout(() => {
                        content.style.maxHeight = '';
                    }, 500);
                    console.log('Expanded section:', section);
                    
                    // Initialize scene management if expanding scene section
                    if (section === 'scene' && window.sceneManager) {
                        setTimeout(() => window.sceneManager.loadScenes(), 100);
                    }
                }
                
                // Save state
                const sectionStates = this.getSectionStates();
                sectionStates[section] = !isExpanded;
                localStorage.setItem('sectionStates', JSON.stringify(sectionStates));
            });
        });
        
        // Don't restore states on initial load - keep everything collapsed
        // Clear any saved states to ensure clean start
        localStorage.removeItem('sectionStates');
    }
    
    getSectionStates() {
        const saved = localStorage.getItem('sectionStates');
        return saved ? JSON.parse(saved) : {};
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new UIController();
});