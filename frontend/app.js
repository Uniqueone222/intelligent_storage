/**
 * Intelligent Storage - Frontend Application
 * Modern UI with complete RAG functionality
 */

// Configuration
const API_BASE = 'http://localhost:8000/api';

// ============================================
// Utility Functions
// ============================================

function showLoading() {
    document.getElementById('loadingOverlay').style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loadingOverlay').style.display = 'none';
}

function showToast(title, message, type = 'success') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <div class="toast-content">
            <div class="toast-title">${title}</div>
            <div class="toast-message">${message}</div>
        </div>
    `;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideIn 0.3s ease-out reverse';
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}

function scrollToSection(id) {
    document.getElementById(id).scrollIntoView({ behavior: 'smooth' });
}

function closeResults(id) {
    document.getElementById(id).style.display = 'none';
}

// ============================================
// File Upload Handling
// ============================================

// Single File Upload
const singleUploadArea = document.getElementById('singleUploadArea');
const singleFileInput = document.getElementById('singleFileInput');

singleUploadArea.addEventListener('click', () => singleFileInput.click());

singleUploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    singleUploadArea.classList.add('drag-over');
});

singleUploadArea.addEventListener('dragleave', () => {
    singleUploadArea.classList.remove('drag-over');
});

singleUploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    singleUploadArea.classList.remove('drag-over');
    if (e.dataTransfer.files.length) {
        singleFileInput.files = e.dataTransfer.files;
        updateUploadText(singleUploadArea, e.dataTransfer.files[0].name);
    }
});

singleFileInput.addEventListener('change', (e) => {
    if (e.target.files.length) {
        updateUploadText(singleUploadArea, e.target.files[0].name);
    }
});

// Batch File Upload
const batchUploadArea = document.getElementById('batchUploadArea');
const batchFileInput = document.getElementById('batchFileInput');

batchUploadArea.addEventListener('click', () => batchFileInput.click());

batchUploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    batchUploadArea.classList.add('drag-over');
});

batchUploadArea.addEventListener('dragleave', () => {
    batchUploadArea.classList.remove('drag-over');
});

batchUploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    batchUploadArea.classList.remove('drag-over');
    if (e.dataTransfer.files.length) {
        batchFileInput.files = e.dataTransfer.files;
        updateUploadText(batchUploadArea, `${e.dataTransfer.files.length} files selected`);
    }
});

batchFileInput.addEventListener('change', (e) => {
    if (e.target.files.length) {
        updateUploadText(batchUploadArea, `${e.target.files.length} files selected`);
    }
});

function updateUploadText(area, text) {
    const textElement = area.querySelector('.upload-text');
    textElement.textContent = text;
}

// Single File Upload Submit
document.getElementById('singleUploadBtn').addEventListener('click', async () => {
    const fileInput = document.getElementById('singleFileInput');
    const comment = document.getElementById('singleComment').value;

    if (!fileInput.files.length) {
        showToast('Error', 'Please select a file', 'error');
        return;
    }

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    if (comment) formData.append('user_comment', comment);

    try {
        showLoading();
        const response = await fetch(`${API_BASE}/upload/file/`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        hideLoading();

        if (data.success) {
            showToast('Success', data.message, 'success');
            displayUploadResult(data);
            fileInput.value = '';
            document.getElementById('singleComment').value = '';
            updateUploadText(singleUploadArea, 'Drop file here or click to browse');

            // Auto-index the file
            indexDocument(data.file.id);

            // Refresh stats
            loadStats();
        } else {
            showToast('Error', data.error || 'Upload failed', 'error');
        }
    } catch (error) {
        hideLoading();
        showToast('Error', error.message, 'error');
    }
});

// Batch Upload Submit
document.getElementById('batchUploadBtn').addEventListener('click', async () => {
    const fileInput = document.getElementById('batchFileInput');
    const comment = document.getElementById('batchComment').value;

    if (!fileInput.files.length) {
        showToast('Error', 'Please select files', 'error');
        return;
    }

    const formData = new FormData();
    for (let file of fileInput.files) {
        formData.append('files', file);
    }
    if (comment) formData.append('user_comment', comment);

    try {
        showLoading();
        const response = await fetch(`${API_BASE}/upload/batch/`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        hideLoading();

        if (data.success) {
            showToast('Success', `Uploaded ${data.processed} files`, 'success');
            displayBatchResults(data);
            fileInput.value = '';
            document.getElementById('batchComment').value = '';
            updateUploadText(batchUploadArea, 'Drop multiple files here');
            loadStats();
        } else {
            showToast('Error', 'Batch upload failed', 'error');
        }
    } catch (error) {
        hideLoading();
        showToast('Error', error.message, 'error');
    }
});

function displayUploadResult(data) {
    const container = document.getElementById('uploadResults');
    const content = document.getElementById('uploadResultsContent');

    content.innerHTML = `
        <div class="card">
            <div class="result-header">
                <h4 class="result-filename">${data.file.original_name}</h4>
                <span class="result-type">${data.file.detected_type}</span>
            </div>
            <div class="form-group">
                <label class="form-label">File Type</label>
                <p class="result-text">${data.file.mime_type}</p>
            </div>
            <div class="form-group">
                <label class="form-label">AI Category</label>
                <p class="result-text">${data.file.ai_category || 'N/A'}</p>
            </div>
            <div class="form-group">
                <label class="form-label">Storage Location</label>
                <p class="result-text">${data.file.storage_category}/${data.file.storage_subcategory}</p>
            </div>
            ${data.file.ai_tags && data.file.ai_tags.length ? `
                <div class="form-group">
                    <label class="form-label">Tags</label>
                    <div class="tags">
                        ${data.file.ai_tags.map(tag => `<span class="badge badge-secondary">${tag}</span>`).join(' ')}
                    </div>
                </div>
            ` : ''}
        </div>
    `;

    container.style.display = 'block';
}

function displayBatchResults(data) {
    const container = document.getElementById('uploadResults');
    const content = document.getElementById('uploadResultsContent');

    const successResults = data.results.filter(r => r.status === 'success');
    const failedResults = data.results.filter(r => r.status === 'failed');

    content.innerHTML = `
        <div class="grid-2">
            <div class="stat-card">
                <div class="stat-card-icon" style="background: rgba(16, 185, 129, 0.1); color: var(--accent-success);">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                        <path d="M5 13L9 17L19 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </div>
                <div class="stat-card-content">
                    <div class="stat-card-value">${data.processed}</div>
                    <div class="stat-card-label">Successful</div>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-card-icon" style="background: rgba(239, 68, 68, 0.1); color: var(--accent-error);">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                        <path d="M6 18L18 6M6 6L18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                </div>
                <div class="stat-card-content">
                    <div class="stat-card-value">${data.failed}</div>
                    <div class="stat-card-label">Failed</div>
                </div>
            </div>
        </div>
        ${successResults.length ? `
            <div class="mt-2">
                <h4 class="mb-1">Successful Uploads</h4>
                ${successResults.map(r => `
                    <div class="search-result-item">
                        <div class="result-header">
                            <span class="result-filename">${r.file}</span>
                            <span class="result-type">${r.category}</span>
                        </div>
                    </div>
                `).join('')}
            </div>
        ` : ''}
        ${failedResults.length ? `
            <div class="mt-2">
                <h4 class="mb-1">Failed Uploads</h4>
                ${failedResults.map(r => `
                    <div class="search-result-item">
                        <div class="result-header">
                            <span class="result-filename">${r.file}</span>
                        </div>
                        <p class="result-text" style="color: var(--accent-error);">${r.error}</p>
                    </div>
                `).join('')}
            </div>
        ` : ''}
    `;

    container.style.display = 'block';
}

// ============================================
// Semantic Search & RAG
// ============================================

document.getElementById('semanticSearchBtn').addEventListener('click', async () => {
    const query = document.getElementById('searchQuery').value;
    const fileType = document.getElementById('searchFileType').value;
    const limit = parseInt(document.getElementById('searchLimit').value);

    if (!query.trim()) {
        showToast('Error', 'Please enter a search query', 'error');
        return;
    }

    try {
        showLoading();
        const response = await fetch(`${API_BASE}/rag/search/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query,
                file_type: fileType || null,
                limit
            })
        });

        const data = await response.json();
        hideLoading();

        if (data.success) {
            displaySearchResults(data);
            showToast('Success', `Found ${data.results_count} results`, 'success');
        } else {
            showToast('Error', 'Search failed', 'error');
        }
    } catch (error) {
        hideLoading();
        showToast('Error', error.message, 'error');
    }
});

function displaySearchResults(data) {
    const container = document.getElementById('searchResults');
    const content = document.getElementById('searchResultsContent');
    const count = document.getElementById('searchCount');

    count.textContent = `${data.results_count} results`;

    if (!data.results.length) {
        content.innerHTML = `
            <div class="text-center" style="padding: var(--spacing-2xl);">
                <p class="result-text">No results found. Try a different query or index more documents.</p>
            </div>
        `;
    } else {
        content.innerHTML = data.results.map((result, index) => `
            <div class="search-result-item">
                <div class="result-header">
                    <span class="result-filename">${result.file_name}</span>
                    <span class="result-type">${result.file_type}</span>
                </div>
                <p class="result-text">${result.chunk_text}</p>
                <div style="display: flex; gap: var(--spacing-md); margin-top: var(--spacing-sm);">
                    <span class="badge badge-secondary">Chunk ${result.chunk_index + 1}</span>
                    ${result.media_file_id ? `
                        <button class="btn-text" onclick="indexDocument(${result.media_file_id})">
                            Reindex
                        </button>
                    ` : ''}
                </div>
            </div>
        `).join('');
    }

    container.style.display = 'block';
}

// RAG Query
document.getElementById('ragQueryBtn').addEventListener('click', async () => {
    const question = document.getElementById('ragQuestion').value;
    const fileType = document.getElementById('searchFileType').value;

    if (!question.trim()) {
        showToast('Error', 'Please enter a question', 'error');
        return;
    }

    try {
        showLoading();
        const response = await fetch(`${API_BASE}/rag/query/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                question,
                file_type: fileType || null,
                max_sources: 5
            })
        });

        const data = await response.json();
        hideLoading();

        if (data.success) {
            displayRAGAnswer(data);
            showToast('Success', 'Answer generated', 'success');
        } else {
            showToast('Error', data.error || 'Failed to generate answer', 'error');
        }
    } catch (error) {
        hideLoading();
        showToast('Error', error.message, 'error');
    }
});

function displayRAGAnswer(data) {
    const container = document.getElementById('ragAnswer');
    const content = document.getElementById('ragAnswerContent');
    const sources = document.getElementById('ragSources');

    content.innerHTML = `<p>${data.answer}</p>`;

    if (data.sources && data.sources.length) {
        sources.innerHTML = `
            <h4 class="mb-1">Sources:</h4>
            ${data.sources.map((source, index) => `
                <div class="source-item">
                    ${index + 1}. ${source.file_name} (Chunk ${source.chunk_index + 1})
                </div>
            `).join('')}
        `;
    } else {
        sources.innerHTML = '';
    }

    container.style.display = 'block';
}

// Auto-index document after upload
async function indexDocument(fileId) {
    try {
        const response = await fetch(`${API_BASE}/rag/index/${fileId}/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        const data = await response.json();

        if (data.success) {
            showToast('Indexed', `${data.chunks_created} chunks created`, 'success');
            loadRAGStats();
        }
    } catch (error) {
        console.error('Indexing failed:', error);
    }
}

// ============================================
// JSON Data Upload
// ============================================

document.getElementById('jsonUploadBtn').addEventListener('click', async () => {
    const name = document.getElementById('jsonName').value;
    const jsonText = document.getElementById('jsonData').value;
    const comment = document.getElementById('jsonComment').value;

    if (!jsonText.trim()) {
        showToast('Error', 'Please enter JSON data', 'error');
        return;
    }

    let jsonData;
    try {
        jsonData = JSON.parse(jsonText);
    } catch (e) {
        showToast('Error', 'Invalid JSON format', 'error');
        return;
    }

    try {
        showLoading();
        const response = await fetch(`${API_BASE}/upload/json/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                data: jsonData,
                name: name || undefined,
                user_comment: comment || undefined
            })
        });

        const data = await response.json();
        hideLoading();

        if (data.success) {
            showToast('Success', data.message, 'success');
            displayJSONResults(data);
            document.getElementById('jsonData').value = '';
            document.getElementById('jsonName').value = '';
            document.getElementById('jsonComment').value = '';
        } else {
            showToast('Error', data.error || 'Upload failed', 'error');
        }
    } catch (error) {
        hideLoading();
        showToast('Error', error.message, 'error');
    }
});

function displayJSONResults(data) {
    const container = document.getElementById('jsonResults');
    const content = document.getElementById('jsonResultsContent');

    const schema = data.generated_schema;
    let schemaDisplay = '';

    if (schema.type === 'SQL') {
        schemaDisplay = `
            <div class="card">
                <h4 class="mb-1">📊 SQL Schema</h4>
                <div class="mb-2">
                    <strong>Table:</strong> ${schema.table_name}
                </div>
                <pre class="code-textarea" style="background: var(--bg-primary); padding: var(--spacing-md); border-radius: var(--border-radius-md); overflow-x: auto;">${schema.create_statement}</pre>
                <div class="mt-2">
                    <strong>Columns:</strong>
                    <ul style="margin-left: var(--spacing-lg); margin-top: var(--spacing-sm);">
                        ${Object.entries(schema.columns).map(([col, type]) =>
                            `<li><code>${col}</code>: ${type}</li>`
                        ).join('')}
                    </ul>
                </div>
            </div>
        `;
    } else {
        schemaDisplay = `
            <div class="card">
                <h4 class="mb-1">📄 MongoDB Schema</h4>
                <div class="mb-2">
                    <strong>Collection:</strong> ${schema.collection_name}
                </div>
                <pre class="code-textarea" style="background: var(--bg-primary); padding: var(--spacing-md); border-radius: var(--border-radius-md);">${schema.document_structure}</pre>
            </div>
        `;
    }

    content.innerHTML = `
        <div class="card" style="background: ${data.ai_analysis.database_type === 'SQL' ? 'rgba(99, 102, 241, 0.1)' : 'rgba(139, 92, 246, 0.1)'};">
            <div class="card-header">
                <h3>🤖 AI Decision</h3>
                <span class="badge">${data.ai_analysis.database_type}</span>
            </div>
            <div class="mb-2">
                <strong>Confidence:</strong> ${data.ai_analysis.confidence}%
            </div>
            <div class="mb-2">
                <strong>Reasoning:</strong> ${data.ai_analysis.reasoning}
            </div>
            <div class="grid-3 mt-2">
                <div class="stat-item">
                    <div class="stat-label">Records Stored</div>
                    <div class="stat-value" style="font-size: var(--font-size-xl);">${data.storage.record_count}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Nesting Depth</div>
                    <div class="stat-value" style="font-size: var(--font-size-xl);">${data.storage.structure_depth || 0}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Nested Objects</div>
                    <div class="stat-value" style="font-size: var(--font-size-xl);">${data.storage.has_nested_objects ? 'Yes' : 'No'}</div>
                </div>
            </div>
        </div>
        ${schemaDisplay}
    `;

    container.style.display = 'block';
}

// ============================================
// Statistics & Health Check
// ============================================

async function loadStats() {
    try {
        const [filesResponse, ragResponse] = await Promise.all([
            fetch(`${API_BASE}/media-files/statistics/`),
            fetch(`${API_BASE}/rag/stats/`)
        ]);

        const filesData = await filesResponse.json();
        const ragData = await ragResponse.json();

        // Update hero stats
        document.getElementById('totalFiles').textContent = filesData.total_files || 0;
        document.getElementById('totalChunks').textContent = ragData.total_chunks || 0;
        document.getElementById('indexedFiles').textContent = ragData.indexed_files || 0;

        // Update analytics section
        document.getElementById('analyticsFiles').textContent = filesData.total_files || 0;
        document.getElementById('analyticsChunks').textContent = ragData.total_chunks || 0;
        document.getElementById('analyticsIndexed').textContent = ragData.indexed_files || 0;
    } catch (error) {
        console.error('Failed to load stats:', error);
    }
}

async function loadRAGStats() {
    try {
        const response = await fetch(`${API_BASE}/rag/stats/`);
        const data = await response.json();

        document.getElementById('totalChunks').textContent = data.total_chunks || 0;
        document.getElementById('indexedFiles').textContent = data.indexed_files || 0;
        document.getElementById('analyticsChunks').textContent = data.total_chunks || 0;
        document.getElementById('analyticsIndexed').textContent = data.indexed_files || 0;
    } catch (error) {
        console.error('Failed to load RAG stats:', error);
    }
}

document.getElementById('refreshStatsBtn').addEventListener('click', () => {
    loadStats();
    showToast('Refreshed', 'Statistics updated', 'success');
});

document.getElementById('healthCheckBtn').addEventListener('click', async () => {
    try {
        showLoading();
        const response = await fetch(`${API_BASE}/health/`);
        const data = await response.json();
        hideLoading();

        const services = data.services;
        const allHealthy = Object.values(services).every(v => v === true);

        let message = `
            Django: ${services.django ? '✓' : '✗'}<br>
            PostgreSQL: ${services.postgresql ? '✓' : '✗'}<br>
            MongoDB: ${services.mongodb ? '✓' : '✗'}<br>
            Ollama: ${services.ollama ? '✓' : '✗'}
        `;

        showToast(
            allHealthy ? 'All Systems Healthy' : 'System Issues Detected',
            message,
            allHealthy ? 'success' : 'warning'
        );
    } catch (error) {
        hideLoading();
        showToast('Error', 'Health check failed', 'error');
    }
});

// ============================================
// Initialize
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    loadStats();
    console.log('Intelligent Storage System Initialized');
});
