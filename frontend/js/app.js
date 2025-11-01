/**
 * EvalSwipe Main Application Controller
 */

class EvalSwipeApp {
    constructor() {
        this.currentSession = null;
        this.currentTraceIndex = 0;
        this.traces = [];
        this.tags = [];
        this.currentTrace = null;
        this.undoStack = [];

        this.init();
    }

    async init() {
        console.log('Initializing EvalSwipe...');

        // Set up event listeners
        this.setupEventListeners();

        // Set up keyboard shortcuts
        this.setupKeyboardHandlers();

        // Load any existing session from localStorage
        this.loadLocalSession();

        console.log('EvalSwipe initialized');
    }

    setupEventListeners() {
        // Welcome screen actions
        document.getElementById('load-demo-btn')?.addEventListener('click', () => this.loadDemoData());
        document.getElementById('import-braintrust-btn')?.addEventListener('click', () => this.showBraintrustModal());
        document.getElementById('upload-json-btn')?.addEventListener('click', () => {
            document.getElementById('upload-json-input').click();
        });
        document.getElementById('upload-json-input')?.addEventListener('change', (e) => this.handleFileUpload(e));

        // Navigation
        document.getElementById('new-session-btn')?.addEventListener('click', () => this.showWelcomeScreen());
        document.getElementById('prev-btn')?.addEventListener('click', () => this.navigateToPrevious());
        document.getElementById('next-btn')?.addEventListener('click', () => this.navigateToNext());

        // Action buttons
        document.getElementById('pass-btn')?.addEventListener('click', () => this.handlePass());
        document.getElementById('fail-btn')?.addEventListener('click', () => this.handleFail());
        document.getElementById('defer-btn')?.addEventListener('click', () => this.handleDefer());

        // Details toggle
        document.getElementById('toggle-details-btn')?.addEventListener('click', () => this.toggleDetails());

        // Modal close buttons
        document.querySelectorAll('.modal-close').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.target.closest('.modal').classList.add('hidden');
            });
        });

        // Open coding modal
        document.getElementById('tag-now-btn')?.addEventListener('click', () => this.handleTagNow());
        document.getElementById('tag-later-btn')?.addEventListener('click', () => this.handleTagLater());
        document.getElementById('open-code-textarea')?.addEventListener('input', (e) => {
            document.getElementById('char-count').textContent = e.target.value.length;
        });

        // Axial coding modal
        document.getElementById('create-tag-btn')?.addEventListener('click', () => this.showTagCreationForm());
        document.getElementById('save-tag-btn')?.addEventListener('click', () => this.handleCreateTag());
        document.getElementById('cancel-tag-btn')?.addEventListener('click', () => this.hideTagCreationForm());
        document.getElementById('apply-tags-btn')?.addEventListener('click', () => this.handleApplyTags());

        // Braintrust modal
        document.getElementById('fetch-traces-btn')?.addEventListener('click', () => this.handleBraintrustImport());

        // Prompt improvement modal
        document.getElementById('prompt-improvement-btn')?.addEventListener('click', () => this.showPromptImprovementModal());
        document.getElementById('generate-suggestions-btn')?.addEventListener('click', () => this.handleGenerateSuggestions());

        // Settings modal
        document.getElementById('settings-btn')?.addEventListener('click', () => this.showSettingsModal());
        document.getElementById('save-settings-btn')?.addEventListener('click', () => this.saveSettings());
        document.getElementById('clear-session-btn')?.addEventListener('click', () => this.clearSession());
        document.getElementById('export-session-btn')?.addEventListener('click', () => this.exportCurrentSession());

        // History view
        document.getElementById('view-history-btn')?.addEventListener('click', () => this.showHistoryView());
        document.getElementById('history-filter')?.addEventListener('change', () => this.filterHistory());
        document.getElementById('history-sort')?.addEventListener('change', () => this.sortHistory());
    }

    setupKeyboardHandlers() {
        document.addEventListener('keydown', (e) => {
            // Ignore if typing in input/textarea
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
                return;
            }

            switch (e.key) {
                case 'ArrowRight':
                case 'p':
                case 'P':
                    e.preventDefault();
                    this.handlePass();
                    break;
                case 'ArrowLeft':
                case 'f':
                case 'F':
                    e.preventDefault();
                    this.handleFail();
                    break;
                case 'ArrowUp':
                case 'd':
                case 'D':
                    e.preventDefault();
                    this.handleDefer();
                    break;
                case ' ':
                    e.preventDefault();
                    this.toggleDetails();
                    break;
                case 'z':
                    if (e.metaKey || e.ctrlKey) {
                        e.preventDefault();
                        this.undo();
                    }
                    break;
            }
        });
    }

    async loadDemoData() {
        try {
            this.showLoading('Loading demo data...');

            const response = await fetch('/static/assets/demo-data.json');
            const data = await response.json();

            await this.startSession('Demo Session', data.traces, { source: 'demo' });

            this.hideLoading();
            this.showToast('Demo data loaded successfully!', 'success');
        } catch (error) {
            this.hideLoading();
            this.showToast(`Failed to load demo data: ${error.message}`, 'error');
        }
    }

    async handleFileUpload(event) {
        const file = event.target.files[0];
        if (!file) return;

        try {
            this.showLoading('Loading traces from file...');

            const text = await file.text();
            const data = JSON.parse(text);

            const traces = data.traces || data;
            if (!Array.isArray(traces)) {
                throw new Error('Invalid file format. Expected array of traces.');
            }

            await this.startSession(`Imported from ${file.name}`, traces, { source: 'upload' });

            this.hideLoading();
            this.showToast('Traces imported successfully!', 'success');
        } catch (error) {
            this.hideLoading();
            this.showToast(`Failed to import file: ${error.message}`, 'error');
        }
    }

    async startSession(name, traces, config = {}) {
        try {
            const response = await apiClient.createSession(name, traces, config);
            this.currentSession = response.session;
            this.traces = response.session.traces;
            this.tags = response.session.axial_tags || [];
            this.currentTraceIndex = 0;

            this.saveLocalSession();
            this.showReviewInterface();
            this.loadTrace(this.currentTraceIndex);
            this.updateProgress();
        } catch (error) {
            throw new Error(`Failed to create session: ${error.message}`);
        }
    }

    loadTrace(index) {
        if (index < 0 || index >= this.traces.length) {
            this.showToast('No more traces to review', 'info');
            return;
        }

        this.currentTraceIndex = index;
        this.currentTrace = this.traces[index];
        this.renderTrace(this.currentTrace);
        this.updateNavigationButtons();
        this.saveLocalSession();
    }

    renderTrace(trace) {
        // Update trace header
        document.getElementById('trace-id').textContent = trace.id;
        document.getElementById('trace-number').textContent = `${this.currentTraceIndex + 1} / ${this.traces.length}`;

        // Update trace content
        document.getElementById('user-input-content').innerHTML = this.formatContent(trace.user_input);
        document.getElementById('agent-output-content').innerHTML = this.formatContent(trace.agent_output);

        // Update details
        document.getElementById('system-prompt-content').textContent = trace.system_prompt || 'No system prompt';

        // Intermediate steps
        const stepsContent = document.getElementById('intermediate-steps-content');
        if (trace.intermediate_steps && trace.intermediate_steps.length > 0) {
            stepsContent.innerHTML = trace.intermediate_steps.map(step => `
                <div class="step-item">
                    <strong>${step.step_type}:</strong>
                    <pre>${this.escapeHtml(step.content)}</pre>
                </div>
            `).join('');
        } else {
            stepsContent.textContent = 'No intermediate steps';
        }

        // Metadata
        document.getElementById('metadata-content').textContent = JSON.stringify(trace.metadata, null, 2);

        // Reset details state
        document.getElementById('trace-details-content').classList.add('hidden');
        document.getElementById('toggle-details-btn').textContent = 'Show Details ▼';

        // Animate card entrance
        const card = document.getElementById('trace-card');
        card.style.animation = 'none';
        setTimeout(() => {
            card.style.animation = 'slideUp 0.3s ease-out';
        }, 10);
    }

    formatContent(text) {
        // Convert markdown-style formatting
        let formatted = this.escapeHtml(text);

        // Bold
        formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

        // Lists
        formatted = formatted.replace(/^\d+\.\s+/gm, '<br>$&');
        formatted = formatted.replace(/^-\s+/gm, '<br>• ');

        // Line breaks
        formatted = formatted.replace(/\n\n/g, '<br><br>');
        formatted = formatted.replace(/\n/g, '<br>');

        return formatted;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    toggleDetails() {
        const content = document.getElementById('trace-details-content');
        const button = document.getElementById('toggle-details-btn');

        if (content.classList.contains('hidden')) {
            content.classList.remove('hidden');
            button.textContent = 'Hide Details ▲';
        } else {
            content.classList.add('hidden');
            button.textContent = 'Show Details ▼';
        }
    }

    async handlePass() {
        if (!this.currentTrace) return;

        this.saveToUndoStack();

        try {
            await apiClient.createAnnotation({
                trace_id: this.currentTrace.id,
                pass_fail: 'pass',
                open_code: null,
                axial_tags: [],
                reviewer_id: 'current_user'
            });

            this.currentTrace.reviewed = true;
            this.currentTrace.pass_fail = 'pass';
            this.updateProgress();

            this.animateSwipe('right');
            setTimeout(() => this.loadNextUnreviewed(), 300);
        } catch (error) {
            this.showToast(`Failed to save annotation: ${error.message}`, 'error');
        }
    }

    handleFail() {
        if (!this.currentTrace) return;
        this.showOpenCodingModal();
    }

    async handleDefer() {
        if (!this.currentTrace) return;

        this.saveToUndoStack();

        try {
            await apiClient.createAnnotation({
                trace_id: this.currentTrace.id,
                pass_fail: 'defer',
                open_code: null,
                axial_tags: [],
                reviewer_id: 'current_user'
            });

            this.currentTrace.reviewed = true;
            this.currentTrace.pass_fail = 'defer';
            this.updateProgress();

            this.animateSwipe('up');
            setTimeout(() => this.loadNextUnreviewed(), 300);
        } catch (error) {
            this.showToast(`Failed to save annotation: ${error.message}`, 'error');
        }
    }

    showOpenCodingModal() {
        document.getElementById('open-coding-modal').classList.remove('hidden');
        document.getElementById('open-code-textarea').value = this.currentTrace.open_code || '';
        document.getElementById('open-code-textarea').focus();
    }

    async handleTagNow() {
        const openCode = document.getElementById('open-code-textarea').value.trim();

        if (!openCode) {
            this.showToast('Please write an open code first', 'warning');
            return;
        }

        if (openCode.length < 20) {
            this.showToast('Open code should be at least 20 characters', 'warning');
            return;
        }

        this.currentTrace.open_code = openCode;

        document.getElementById('open-coding-modal').classList.add('hidden');
        this.showAxialCodingModal();
    }

    async handleTagLater() {
        const openCode = document.getElementById('open-code-textarea').value.trim();

        if (!openCode) {
            this.showToast('Please write an open code first', 'warning');
            return;
        }

        this.saveToUndoStack();

        try {
            await apiClient.createAnnotation({
                trace_id: this.currentTrace.id,
                pass_fail: 'fail',
                open_code: openCode,
                axial_tags: [],
                reviewer_id: 'current_user'
            });

            this.currentTrace.reviewed = true;
            this.currentTrace.pass_fail = 'fail';
            this.currentTrace.open_code = openCode;
            this.updateProgress();

            document.getElementById('open-coding-modal').classList.add('hidden');

            this.animateSwipe('left');
            setTimeout(() => this.loadNextUnreviewed(), 300);
        } catch (error) {
            this.showToast(`Failed to save annotation: ${error.message}`, 'error');
        }
    }

    async showAxialCodingModal() {
        document.getElementById('axial-coding-modal').classList.remove('hidden');
        await this.loadTagsLibrary();
    }

    async loadTagsLibrary() {
        try {
            const response = await apiClient.getTags();
            this.tags = response.tags || [];

            const library = document.getElementById('tag-library');
            library.innerHTML = '';

            if (this.tags.length === 0) {
                library.innerHTML = '<p class="text-center">No tags yet. Create your first tag!</p>';
                return;
            }

            this.tags.forEach(tag => {
                const chip = document.createElement('div');
                chip.className = 'tag-chip';
                if (this.currentTrace.axial_tags && this.currentTrace.axial_tags.includes(tag.id)) {
                    chip.classList.add('selected');
                }
                chip.style.borderColor = tag.color;
                chip.innerHTML = `
                    ${tag.name}
                    <span class="tag-count">(${tag.usage_count})</span>
                `;
                chip.title = tag.description;
                chip.addEventListener('click', () => this.toggleTag(tag.id, chip));
                library.appendChild(chip);
            });
        } catch (error) {
            this.showToast(`Failed to load tags: ${error.message}`, 'error');
        }
    }

    toggleTag(tagId, chipElement) {
        if (!this.currentTrace.axial_tags) {
            this.currentTrace.axial_tags = [];
        }

        const index = this.currentTrace.axial_tags.indexOf(tagId);
        if (index > -1) {
            this.currentTrace.axial_tags.splice(index, 1);
            chipElement.classList.remove('selected');
        } else {
            this.currentTrace.axial_tags.push(tagId);
            chipElement.classList.add('selected');
        }
    }

    showTagCreationForm() {
        document.getElementById('tag-creation-form').classList.remove('hidden');
    }

    hideTagCreationForm() {
        document.getElementById('tag-creation-form').classList.add('hidden');
        document.getElementById('new-tag-name').value = '';
        document.getElementById('new-tag-description').value = '';
        document.getElementById('new-tag-color').value = '#808080';
    }

    async handleCreateTag() {
        const name = document.getElementById('new-tag-name').value.trim();
        const description = document.getElementById('new-tag-description').value.trim();
        const color = document.getElementById('new-tag-color').value;

        if (!name || name.length < 2) {
            this.showToast('Tag name must be at least 2 characters', 'warning');
            return;
        }

        if (!description || description.length < 20) {
            this.showToast('Tag description must be at least 20 characters', 'warning');
            return;
        }

        try {
            const response = await apiClient.createTag({ name, description, color });
            this.tags.push(response.tag);
            this.hideTagCreationForm();
            await this.loadTagsLibrary();
            this.showToast('Tag created successfully!', 'success');
        } catch (error) {
            this.showToast(`Failed to create tag: ${error.message}`, 'error');
        }
    }

    async handleApplyTags() {
        this.saveToUndoStack();

        try {
            await apiClient.createAnnotation({
                trace_id: this.currentTrace.id,
                pass_fail: 'fail',
                open_code: this.currentTrace.open_code,
                axial_tags: this.currentTrace.axial_tags || [],
                reviewer_id: 'current_user'
            });

            this.currentTrace.reviewed = true;
            this.currentTrace.pass_fail = 'fail';
            this.updateProgress();

            document.getElementById('axial-coding-modal').classList.add('hidden');

            this.animateSwipe('left');
            setTimeout(() => this.loadNextUnreviewed(), 300);
        } catch (error) {
            this.showToast(`Failed to save tags: ${error.message}`, 'error');
        }
    }

    showBraintrustModal() {
        document.getElementById('braintrust-modal').classList.remove('hidden');
    }

    async handleBraintrustImport() {
        const apiKey = document.getElementById('bt-api-key').value.trim();
        const projectId = document.getElementById('bt-project-id').value.trim();
        const experimentId = document.getElementById('bt-experiment-id').value.trim();
        const limit = parseInt(document.getElementById('bt-limit').value) || 100;

        if (!projectId || !experimentId) {
            this.showToast('Project ID and Experiment ID are required', 'warning');
            return;
        }

        try {
            this.showLoading('Importing from Braintrust...');

            const response = await apiClient.importFromBraintrust({
                api_key: apiKey || undefined,
                project_id: projectId,
                experiment_id: experimentId,
                filters: { limit }
            });

            document.getElementById('braintrust-modal').classList.add('hidden');

            await this.startSession(
                `Braintrust - ${experimentId}`,
                response.traces,
                { source: 'braintrust' }
            );

            this.hideLoading();
            this.showToast(`Imported ${response.imported_count} traces from Braintrust!`, 'success');
        } catch (error) {
            this.hideLoading();
            this.showToast(`Failed to import from Braintrust: ${error.message}`, 'error');
        }
    }

    showPromptImprovementModal() {
        if (!this.currentSession) {
            this.showToast('Please load a session first', 'warning');
            return;
        }
        document.getElementById('prompt-improvement-modal').classList.remove('hidden');
        this.loadFailureModesForPrompt();
    }

    async loadFailureModesForPrompt() {
        const container = document.getElementById('failure-modes-list');
        container.innerHTML = '';

        if (this.tags.length === 0) {
            container.innerHTML = '<p>No failure modes tagged yet</p>';
            return;
        }

        this.tags.forEach(tag => {
            const chip = document.createElement('div');
            chip.className = 'tag-chip';
            chip.style.borderColor = tag.color;
            chip.innerHTML = `${tag.name} <span class="tag-count">(${tag.usage_count})</span>`;
            chip.title = tag.description;
            chip.dataset.tagId = tag.id;
            chip.addEventListener('click', () => {
                chip.classList.toggle('selected');
            });
            container.appendChild(chip);
        });
    }

    async handleGenerateSuggestions() {
        const currentPrompt = document.getElementById('current-prompt').value.trim();
        const additionalContext = document.getElementById('additional-context').value.trim();
        const numSuggestions = parseInt(document.getElementById('num-suggestions').value) || 3;

        if (!currentPrompt) {
            this.showToast('Please enter a system prompt', 'warning');
            return;
        }

        const selectedTags = Array.from(document.querySelectorAll('#failure-modes-list .tag-chip.selected'))
            .map(chip => chip.dataset.tagId);

        if (selectedTags.length === 0) {
            this.showToast('Please select at least one failure mode', 'warning');
            return;
        }

        try {
            this.showLoading('Generating suggestions with Claude...');

            const response = await apiClient.generatePromptSuggestions({
                current_prompt: currentPrompt,
                target_failure_modes: selectedTags,
                additional_context: additionalContext,
                num_suggestions: numSuggestions
            });

            this.renderPromptSuggestions(response.suggestions);
            this.hideLoading();
        } catch (error) {
            this.hideLoading();
            this.showToast(`Failed to generate suggestions: ${error.message}`, 'error');
        }
    }

    renderPromptSuggestions(suggestions) {
        const container = document.getElementById('suggestions-container');
        container.classList.remove('hidden');
        container.innerHTML = '';

        suggestions.forEach(suggestion => {
            const card = document.createElement('div');
            card.className = 'suggestion-card';
            card.innerHTML = `
                <div class="suggestion-header">
                    <h3>Suggestion ${suggestion.version}</h3>
                    <div class="suggestion-actions">
                        <button class="btn secondary-btn" onclick="navigator.clipboard.writeText(\`${this.escapeHtml(suggestion.improved_prompt)}\`)">
                            Copy
                        </button>
                    </div>
                </div>
                <div class="improved-prompt">${this.escapeHtml(suggestion.improved_prompt)}</div>
                <div class="changes-list">
                    <h4>Changes Made:</h4>
                    <ul>
                        ${suggestion.changes_made.map(change => `<li>${this.escapeHtml(change)}</li>`).join('')}
                    </ul>
                </div>
            `;
            container.appendChild(card);
        });
    }

    navigateToPrevious() {
        if (this.currentTraceIndex > 0) {
            this.loadTrace(this.currentTraceIndex - 1);
        }
    }

    navigateToNext() {
        if (this.currentTraceIndex < this.traces.length - 1) {
            this.loadTrace(this.currentTraceIndex + 1);
        }
    }

    loadNextUnreviewed() {
        const nextIndex = this.traces.findIndex((trace, idx) => idx > this.currentTraceIndex && !trace.reviewed);

        if (nextIndex !== -1) {
            this.loadTrace(nextIndex);
        } else {
            // All traces reviewed
            this.showToast('All traces reviewed! 🎉', 'success');
            this.loadTrace(this.currentTraceIndex + 1);
        }
    }

    updateNavigationButtons() {
        const prevBtn = document.getElementById('prev-btn');
        const nextBtn = document.getElementById('next-btn');

        if (prevBtn) prevBtn.disabled = this.currentTraceIndex === 0;
        if (nextBtn) nextBtn.disabled = this.currentTraceIndex === this.traces.length - 1;
    }

    updateProgress() {
        const reviewed = this.traces.filter(t => t.reviewed).length;
        const passed = this.traces.filter(t => t.pass_fail === 'pass').length;
        const failed = this.traces.filter(t => t.pass_fail === 'fail').length;
        const deferred = this.traces.filter(t => t.pass_fail === 'defer').length;
        const percentage = Math.round((reviewed / this.traces.length) * 100);

        document.getElementById('progress-text').textContent =
            `${reviewed} of ${this.traces.length} traces reviewed (${percentage}%)`;
        document.getElementById('pass-count').textContent = passed;
        document.getElementById('fail-count').textContent = failed;
        document.getElementById('defer-count').textContent = deferred;
        document.getElementById('progress-bar').style.width = `${percentage}%`;
    }

    animateSwipe(direction) {
        const card = document.getElementById('trace-card');
        card.classList.add(`swipe-${direction}`);
        setTimeout(() => {
            card.classList.remove(`swipe-${direction}`);
        }, 300);
    }

    saveToUndoStack() {
        this.undoStack.push({
            traceIndex: this.currentTraceIndex,
            trace: JSON.parse(JSON.stringify(this.currentTrace))
        });
        if (this.undoStack.length > 10) {
            this.undoStack.shift();
        }
    }

    undo() {
        if (this.undoStack.length === 0) {
            this.showToast('Nothing to undo', 'info');
            return;
        }

        const previous = this.undoStack.pop();
        this.traces[previous.traceIndex] = previous.trace;
        this.loadTrace(previous.traceIndex);
        this.updateProgress();
        this.showToast('Action undone', 'info');
    }

    saveLocalSession() {
        if (!this.currentSession) return;

        try {
            const sessionData = {
                session: this.currentSession,
                traces: this.traces,
                tags: this.tags,
                currentTraceIndex: this.currentTraceIndex
            };
            localStorage.setItem('evalswipe_session', JSON.stringify(sessionData));
        } catch (error) {
            console.error('Failed to save session to localStorage:', error);
        }
    }

    loadLocalSession() {
        try {
            const saved = localStorage.getItem('evalswipe_session');
            if (saved) {
                const data = JSON.parse(saved);
                this.currentSession = data.session;
                this.traces = data.traces;
                this.tags = data.tags || [];
                this.currentTraceIndex = data.currentTraceIndex || 0;

                if (this.traces.length > 0) {
                    this.showReviewInterface();
                    this.loadTrace(this.currentTraceIndex);
                    this.updateProgress();
                    this.showToast('Session restored from previous session', 'info');
                }
            }
        } catch (error) {
            console.error('Failed to load session from localStorage:', error);
        }
    }

    showWelcomeScreen() {
        document.getElementById('welcome-screen').classList.remove('hidden');
        document.getElementById('review-interface').classList.add('hidden');
        document.getElementById('progress-tracker').classList.add('hidden');
    }

    showReviewInterface() {
        document.getElementById('welcome-screen').classList.add('hidden');
        document.getElementById('review-interface').classList.remove('hidden');
        document.getElementById('progress-tracker').classList.remove('hidden');
    }

    showLoading(message = 'Loading...') {
        document.getElementById('loading-text').textContent = message;
        document.getElementById('loading-overlay').classList.remove('hidden');
    }

    hideLoading() {
        document.getElementById('loading-overlay').classList.add('hidden');
    }

    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;

        const container = document.getElementById('toast-container');
        container.appendChild(toast);

        setTimeout(() => {
            toast.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    // Settings Modal
    showSettingsModal() {
        // Load current settings
        const settings = this.loadSettings();

        document.getElementById('reviewer-id').value = settings.reviewer_id || '';
        document.getElementById('anthropic-key').value = settings.anthropic_key || '';
        document.getElementById('braintrust-key').value = settings.braintrust_key || '';
        document.getElementById('randomize-traces').checked = settings.randomize_traces || false;
        document.getElementById('auto-save').checked = settings.auto_save !== false;

        document.getElementById('settings-modal').classList.remove('hidden');
    }

    loadSettings() {
        try {
            const saved = localStorage.getItem('evalswipe_settings');
            return saved ? JSON.parse(saved) : {};
        } catch (error) {
            console.error('Failed to load settings:', error);
            return {};
        }
    }

    saveSettings() {
        const settings = {
            reviewer_id: document.getElementById('reviewer-id').value,
            anthropic_key: document.getElementById('anthropic-key').value,
            braintrust_key: document.getElementById('braintrust-key').value,
            randomize_traces: document.getElementById('randomize-traces').checked,
            auto_save: document.getElementById('auto-save').checked
        };

        try {
            localStorage.setItem('evalswipe_settings', JSON.stringify(settings));
            document.getElementById('settings-modal').classList.add('hidden');
            this.showToast('Settings saved successfully', 'success');
        } catch (error) {
            this.showToast('Failed to save settings: ' + error.message, 'error');
        }
    }

    clearSession() {
        if (confirm('Are you sure you want to clear the current session? This cannot be undone.')) {
            localStorage.removeItem('evalswipe_session');
            this.currentSession = null;
            this.traces = [];
            this.tags = [];
            this.currentTraceIndex = 0;
            document.getElementById('settings-modal').classList.add('hidden');
            this.showWelcomeScreen();
            this.showToast('Session cleared', 'info');
        }
    }

    exportCurrentSession() {
        if (!this.currentSession) {
            this.showToast('No session to export', 'warning');
            return;
        }

        const sessionData = {
            session: this.currentSession,
            traces: this.traces,
            tags: this.tags,
            exported_at: new Date().toISOString()
        };

        const blob = new Blob([JSON.stringify(sessionData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `evalswipe_session_${Date.now()}.json`;
        a.click();
        URL.revokeObjectURL(url);

        this.showToast('Session exported successfully', 'success');
    }

    // History View
    showHistoryView() {
        if (!this.currentSession || this.traces.length === 0) {
            this.showToast('No traces to display. Load a session first.', 'warning');
            return;
        }

        this.renderHistoryStats();
        this.renderHistoryList();

        document.getElementById('history-view').classList.remove('hidden');
    }

    renderHistoryStats() {
        const total = this.traces.length;
        const reviewed = this.traces.filter(t => t.reviewed).length;
        const passed = this.traces.filter(t => t.pass_fail === 'pass').length;
        const failed = this.traces.filter(t => t.pass_fail === 'fail').length;
        const deferred = this.traces.filter(t => t.pass_fail === 'defer').length;
        const unreviewed = total - reviewed;

        const statsContainer = document.getElementById('history-stats');
        statsContainer.innerHTML = `
            <div class="stat-card">
                <div class="stat-value">${total}</div>
                <div class="stat-label">Total Traces</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${reviewed}</div>
                <div class="stat-label">Reviewed</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${passed}</div>
                <div class="stat-label">Passed</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${failed}</div>
                <div class="stat-label">Failed</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${deferred}</div>
                <div class="stat-label">Deferred</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${unreviewed}</div>
                <div class="stat-label">Unreviewed</div>
            </div>
        `;
    }

    renderHistoryList() {
        const filter = document.getElementById('history-filter').value;
        const sort = document.getElementById('history-sort').value;

        let filteredTraces = [...this.traces];

        // Apply filter
        if (filter === 'pass') {
            filteredTraces = filteredTraces.filter(t => t.pass_fail === 'pass');
        } else if (filter === 'fail') {
            filteredTraces = filteredTraces.filter(t => t.pass_fail === 'fail');
        } else if (filter === 'defer') {
            filteredTraces = filteredTraces.filter(t => t.pass_fail === 'defer');
        } else if (filter === 'unreviewed') {
            filteredTraces = filteredTraces.filter(t => !t.reviewed);
        }

        // Apply sort
        if (sort === 'recent') {
            filteredTraces.sort((a, b) => {
                if (!a.reviewed_at) return 1;
                if (!b.reviewed_at) return -1;
                return new Date(b.reviewed_at) - new Date(a.reviewed_at);
            });
        } else if (sort === 'status') {
            const statusOrder = { fail: 0, defer: 1, pass: 2, unreviewed: 3 };
            filteredTraces.sort((a, b) => {
                const aStatus = a.pass_fail || 'unreviewed';
                const bStatus = b.pass_fail || 'unreviewed';
                return statusOrder[aStatus] - statusOrder[bStatus];
            });
        }

        const listContainer = document.getElementById('history-list');

        if (filteredTraces.length === 0) {
            listContainer.innerHTML = '<p style="text-align: center; color: var(--color-text-light);">No traces match the selected filter.</p>';
            return;
        }

        listContainer.innerHTML = filteredTraces.map((trace, idx) => {
            const originalIndex = this.traces.indexOf(trace);
            const status = trace.reviewed ? trace.pass_fail : 'unreviewed';
            const statusLabel = status === 'unreviewed' ? 'Not Reviewed' : status.charAt(0).toUpperCase() + status.slice(1);

            // Get tag names
            const tagNames = (trace.axial_tags || []).map(tagId => {
                const tag = this.tags.find(t => t.id === tagId);
                return tag ? tag.name : tagId;
            });

            return `
                <div class="history-item" onclick="window.evalSwipeApp.jumpToTrace(${originalIndex})">
                    <div class="history-item-header">
                        <span class="history-item-id">${trace.id}</span>
                        <span class="history-item-status ${status}">${statusLabel}</span>
                    </div>
                    <div class="history-item-content">
                        <div class="history-item-input">
                            <strong>Input:</strong> ${this.escapeHtml(trace.user_input)}
                        </div>
                        ${trace.open_code ? `
                            <div class="history-item-open-code">
                                <strong>Note:</strong> ${this.escapeHtml(trace.open_code)}
                            </div>
                        ` : ''}
                        ${tagNames.length > 0 ? `
                            <div class="history-item-tags">
                                ${tagNames.map(name => `
                                    <span class="tag-chip">${this.escapeHtml(name)}</span>
                                `).join('')}
                            </div>
                        ` : ''}
                    </div>
                </div>
            `;
        }).join('');
    }

    filterHistory() {
        this.renderHistoryList();
    }

    sortHistory() {
        this.renderHistoryList();
    }

    jumpToTrace(index) {
        document.getElementById('history-view').classList.add('hidden');
        this.loadTrace(index);
        this.showToast(`Jumped to trace ${index + 1}`, 'info');
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.evalSwipeApp = new EvalSwipeApp();
});
