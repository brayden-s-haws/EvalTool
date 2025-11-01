/**
 * API Client for EvalSwipe Backend
 */

const API_BASE = '/api';

class APIClient {
    /**
     * Make a generic API request
     */
    async request(endpoint, options = {}) {
        const url = `${API_BASE}${endpoint}`;

        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
        };

        const config = { ...defaultOptions, ...options };

        try {
            const response = await fetch(url, config);

            if (!response.ok) {
                const error = await response.json().catch(() => ({ detail: 'Request failed' }));
                throw new Error(error.detail || `HTTP ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error(`API Error (${endpoint}):`, error);
            throw error;
        }
    }

    // Trace endpoints
    async getTraces(filters = {}) {
        const params = new URLSearchParams(filters);
        return this.request(`/traces?${params}`);
    }

    async getTrace(traceId) {
        return this.request(`/traces/${traceId}`);
    }

    async importTraces(traces, sessionConfig = {}) {
        return this.request('/traces/import', {
            method: 'POST',
            body: JSON.stringify({ traces, session_config: sessionConfig }),
        });
    }

    // Annotation endpoints
    async createAnnotation(annotation) {
        return this.request('/annotations/', {
            method: 'POST',
            body: JSON.stringify(annotation),
        });
    }

    async updateAnnotation(traceId, annotation) {
        return this.request(`/annotations/${traceId}`, {
            method: 'PUT',
            body: JSON.stringify(annotation),
        });
    }

    // Tag endpoints
    async getTags() {
        return this.request('/tags');
    }

    async createTag(tag) {
        return this.request('/tags', {
            method: 'POST',
            body: JSON.stringify(tag),
        });
    }

    async updateTag(tagId, tag) {
        return this.request(`/tags/${tagId}`, {
            method: 'PUT',
            body: JSON.stringify(tag),
        });
    }

    async deleteTag(tagId, untagTraces = true) {
        return this.request(`/tags/${tagId}?untag_traces=${untagTraces}`, {
            method: 'DELETE',
        });
    }

    async mergeTags(sourceTagId, targetTagId) {
        return this.request('/tags/merge', {
            method: 'POST',
            body: JSON.stringify({ source_tag_id: sourceTagId, target_tag_id: targetTagId }),
        });
    }

    // Session endpoints
    async getSessions() {
        return this.request('/sessions');
    }

    async getSession(sessionId) {
        return this.request(`/sessions/${sessionId}`);
    }

    async createSession(name, traces, config) {
        return this.request('/sessions', {
            method: 'POST',
            body: JSON.stringify({ name, traces, config }),
        });
    }

    async updateSession(sessionId, session) {
        return this.request(`/sessions/${sessionId}`, {
            method: 'PUT',
            body: JSON.stringify(session),
        });
    }

    // Prompt improvement
    async generatePromptSuggestions(request) {
        return this.request('/prompt-improvement/suggest', {
            method: 'POST',
            body: JSON.stringify(request),
        });
    }

    // Braintrust integration
    async importFromBraintrust(request) {
        return this.request('/braintrust/import', {
            method: 'POST',
            body: JSON.stringify(request),
        });
    }

    async exportToBraintrust(request) {
        return this.request('/braintrust/export', {
            method: 'POST',
            body: JSON.stringify(request),
        });
    }

    // Export endpoints
    async exportCSV(sessionId) {
        window.open(`${API_BASE}/export/csv/${sessionId}`, '_blank');
    }

    async exportJSON(sessionId) {
        window.open(`${API_BASE}/export/json/${sessionId}`, '_blank');
    }

    async exportPDF(sessionId) {
        window.open(`${API_BASE}/export/pdf/${sessionId}`, '_blank');
    }
}

// Create singleton instance
const apiClient = new APIClient();
