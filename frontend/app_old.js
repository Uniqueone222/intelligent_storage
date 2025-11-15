// API Configuration
const API_BASE_URL = 'http://localhost:8000/api';

// State
let selectedFiles = [];

// DOM Elements
const elements = {
    fileInput: null,
    dropzone: null,
    selectedFilesDiv: null,
    uploadFilesBtn: null,
    uploadJsonBtn: null,
    fileComment: null,
    jsonData: null,
    jsonName: null,
    jsonComment: null,
    uploadProgress: null,
    progressBar: null,
    progressText: null,
    uploadResults: null,
    filesList: null,
    dataList: null,
    statsContent: null,
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initializeElements();
    setupEventListeners();
    setupTabs();
    setupUploadTypeSwitcher();
    loadFiles();
});

function initializeElements() {
    elements.fileInput = document.getElementById('fileInput');
    elements.dropzone = document.getElementById('dropzone');
    elements.selectedFilesDiv = document.getElementById('selectedFiles');
    elements.uploadFilesBtn = document.getElementById('uploadFilesBtn');
    elements.uploadJsonBtn = document.getElementById('uploadJsonBtn');
    elements.fileComment = document.getElementById('fileComment');
    elements.jsonData = document.getElementById('jsonData');
    elements.jsonName = document.getElementById('jsonName');
    elements.jsonComment = document.getElementById('jsonComment');
    elements.uploadProgress = document.getElementById('uploadProgress');
    elements.progressBar = document.getElementById('progressBar');
    elements.progressText = document.getElementById('progressText');
    elements.uploadResults = document.getElementById('uploadResults');
    elements.filesList = document.getElementById('filesList');
    elements.dataList = document.getElementById('dataList');
    elements.statsContent = document.getElementById('statsContent');
}

function setupEventListeners() {
    // File input
    elements.fileInput.addEventListener('change', handleFileSelect);

    // Drag and drop
    elements.dropzone.addEventListener('click', () => elements.fileInput.click());
    elements.dropzone.addEventListener('dragover', handleDragOver);
    elements.dropzone.addEventListener('dragleave', handleDragLeave);
    elements.dropzone.addEventListener('drop', handleDrop);

    // Upload buttons
    elements.uploadFilesBtn.addEventListener('click', uploadFiles);
    elements.uploadJsonBtn.addEventListener('click', uploadJson);

    // Refresh buttons
    document.getElementById('refreshFilesBtn')?.addEventListener('click', loadFiles);
    document.getElementById('refreshDataBtn')?.addEventListener('click', loadJsonData);

    // Category filter
    document.getElementById('categoryFilter')?.addEventListener('change', (e) => {
        loadFiles(e.target.value);
    });
}

function setupTabs() {
    const navItems = document.querySelectorAll('.nav-item');
    const tabContents = document.querySelectorAll('.tab-content');

    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const tabName = item.dataset.tab;

            // Update active nav item
            navItems.forEach(nav => nav.classList.remove('active'));
            item.classList.add('active');

            // Show corresponding tab content
            tabContents.forEach(content => {
                content.classList.remove('active');
            });
            document.getElementById(`${tabName}-tab`).classList.add('active');

            // Load data for specific tabs
            if (tabName === 'files') {
                loadFiles();
            } else if (tabName === 'data') {
                loadJsonData();
            } else if (tabName === 'stats') {
                loadStatistics();
            }
        });
    });
}

function setupUploadTypeSwitcher() {
    const uploadTypeBtns = document.querySelectorAll('.upload-type-btn');
    const uploadPanels = document.querySelectorAll('.upload-panel');

    uploadTypeBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const type = btn.dataset.type;

            // Update active button
            uploadTypeBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // Show corresponding panel
            uploadPanels.forEach(panel => {
                panel.classList.remove('active');
            });
            document.getElementById(`${type}-upload-panel`).classList.add('active');
        });
    });
}

// File Upload Functions
function handleFileSelect(e) {
    const files = Array.from(e.target.files);
    addFiles(files);
}

function handleDragOver(e) {
    e.preventDefault();
    elements.dropzone.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    elements.dropzone.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    elements.dropzone.classList.remove('dragover');
    const files = Array.from(e.dataTransfer.files);
    addFiles(files);
}

function addFiles(files) {
    selectedFiles = [...selectedFiles, ...files];
    renderSelectedFiles();
    elements.uploadFilesBtn.disabled = selectedFiles.length === 0;
}

function removeFile(index) {
    selectedFiles.splice(index, 1);
    renderSelectedFiles();
    elements.uploadFilesBtn.disabled = selectedFiles.length === 0;
}

function renderSelectedFiles() {
    if (selectedFiles.length === 0) {
        elements.selectedFilesDiv.innerHTML = '';
        return;
    }

    elements.selectedFilesDiv.innerHTML = `
        <h4 style="margin-bottom: 1rem;">Selected Files (${selectedFiles.length})</h4>
        ${selectedFiles.map((file, index) => `
            <div class="file-item">
                <div class="file-info">
                    <span class="file-icon">${getFileIcon(file.name)}</span>
                    <div>
                        <div class="file-name">${file.name}</div>
                        <div class="file-size">${formatFileSize(file.size)}</div>
                    </div>
                </div>
                <button class="file-remove" onclick="removeFile(${index})">×</button>
            </div>
        `).join('')}
    `;
}

function getFileIcon(filename) {
    const ext = filename.split('.').pop().toLowerCase();
    const iconMap = {
        jpg: '🖼️', jpeg: '🖼️', png: '🖼️', gif: '🖼️', svg: '🖼️',
        mp4: '🎥', avi: '🎥', mov: '🎥', mkv: '🎥',
        mp3: '🎵', wav: '🎵', flac: '🎵',
        pdf: '📄', doc: '📝', docx: '📝', txt: '📝',
        zip: '📦', rar: '📦', '7z': '📦',
        exe: '⚙️', dll: '⚙️', sh: '⚙️',
    };
    return iconMap[ext] || '📁';
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

async function uploadFiles() {
    if (selectedFiles.length === 0) return;

    const formData = new FormData();
    const userComment = elements.fileComment.value;

    // Determine if single or batch upload
    if (selectedFiles.length === 1) {
        formData.append('file', selectedFiles[0]);
        if (userComment) formData.append('user_comment', userComment);
        await uploadSingleFile(formData);
    } else {
        selectedFiles.forEach(file => {
            formData.append('files', file);
        });
        if (userComment) formData.append('user_comment', userComment);
        await uploadBatchFiles(formData);
    }
}

async function uploadSingleFile(formData) {
    try {
        showProgress('Uploading file...');

        const response = await fetch(`${API_BASE_URL}/upload/file/`, {
            method: 'POST',
            body: formData,
        });

        const result = await response.json();

        if (response.ok) {
            showResults([{
                file: result.file.original_name,
                status: 'success',
                category: `${result.file.detected_type}/${result.file.storage_subcategory}`,
                message: result.message
            }]);
            showToast('File uploaded successfully!', 'success');
            resetFileUpload();
        } else {
            throw new Error(result.error || 'Upload failed');
        }
    } catch (error) {
        showToast(`Upload failed: ${error.message}`, 'error');
    } finally {
        hideProgress();
    }
}

async function uploadBatchFiles(formData) {
    try {
        showProgress(`Uploading ${selectedFiles.length} files...`);

        const response = await fetch(`${API_BASE_URL}/upload/batch/`, {
            method: 'POST',
            body: formData,
        });

        const result = await response.json();

        if (response.ok) {
            showResults(result.results);
            showToast(`Batch upload completed: ${result.processed}/${result.total} files processed`, 'success');
            resetFileUpload();
        } else {
            throw new Error(result.error || 'Batch upload failed');
        }
    } catch (error) {
        showToast(`Batch upload failed: ${error.message}`, 'error');
    } finally {
        hideProgress();
    }
}

function resetFileUpload() {
    selectedFiles = [];
    elements.fileInput.value = '';
    elements.fileComment.value = '';
    renderSelectedFiles();
    elements.uploadFilesBtn.disabled = true;
}

// JSON Upload Functions
async function uploadJson() {
    const jsonText = elements.jsonData.value.trim();
    const name = elements.jsonName.value.trim();
    const comment = elements.jsonComment.value.trim();
    const dbType = document.querySelector('input[name="dbType"]:checked').value;

    if (!jsonText) {
        showToast('Please enter JSON data', 'error');
        return;
    }

    let jsonData;
    try {
        jsonData = JSON.parse(jsonText);
    } catch (error) {
        showToast('Invalid JSON format', 'error');
        return;
    }

    try {
        showProgress('Analyzing and storing JSON data...');

        const payload = {
            data: jsonData,
        };
        if (name) payload.name = name;
        if (comment) payload.user_comment = comment;
        if (dbType !== 'auto') payload.force_db_type = dbType;

        const response = await fetch(`${API_BASE_URL}/upload/json/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
        });

        const result = await response.json();

        if (response.ok) {
            const aiAnalysis = result.ai_analysis;
            const schema = result.generated_schema;

            showToast(
                `Data stored in ${result.storage.database_type} database (${aiAnalysis.confidence}% confidence)`,
                'success'
            );

            // Prepare schema display
            let schemaDisplay = '';
            if (schema.type === 'SQL') {
                schemaDisplay = `
                    <div class="schema-section">
                        <h4>📊 Generated SQL Schema</h4>
                        <div class="schema-info">
                            <strong>Table Name:</strong> ${schema.table_name}
                        </div>
                        <pre class="sql-code">${schema.create_statement}</pre>
                        <div class="columns-list">
                            <strong>Columns:</strong>
                            <ul>
                                ${Object.entries(schema.columns).map(([col, type]) =>
                                    `<li><code>${col}</code>: ${type}</li>`
                                ).join('')}
                            </ul>
                        </div>
                    </div>
                `;
            } else {
                schemaDisplay = `
                    <div class="schema-section">
                        <h4>📄 Generated MongoDB Schema</h4>
                        <div class="schema-info">
                            <strong>Collection:</strong> ${schema.collection_name}
                        </div>
                        <pre class="mongo-code">${schema.document_structure}</pre>
                    </div>
                `;
            }

            // Show complete results
            elements.uploadResults.innerHTML = `
                <h3>✅ Storage Complete</h3>

                <div class="result-section">
                    <h4>🤖 AI Analysis</h4>
                    <div class="result-item">
                        <div class="result-row">
                            <strong>Decision:</strong>
                            <span class="badge">${result.storage.database_type}</span>
                        </div>
                        <div class="result-row">
                            <strong>Confidence:</strong>
                            <span class="confidence-score">${aiAnalysis.confidence}%</span>
                        </div>
                        <div class="result-row">
                            <strong>Reasoning:</strong>
                            <p class="reasoning-text">${aiAnalysis.reasoning}</p>
                        </div>
                        <div class="result-row">
                            <strong>Records Stored:</strong> ${result.storage.record_count}
                        </div>
                    </div>
                </div>

                ${schemaDisplay}

                <div class="structure-info">
                    <h4>📐 Structure Analysis</h4>
                    <div class="info-grid">
                        <div class="info-item">
                            <span class="info-label">Nesting Depth:</span>
                            <span class="info-value">${result.storage.structure_depth}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Nested Objects:</span>
                            <span class="info-value">${result.storage.has_nested_objects ? 'Yes' : 'No'}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Has Arrays:</span>
                            <span class="info-value">${result.storage.has_arrays ? 'Yes' : 'No'}</span>
                        </div>
                    </div>
                </div>
            `;
            elements.uploadResults.classList.remove('hidden');

            resetJsonUpload();
        } else {
            throw new Error(result.error || 'JSON upload failed');
        }
    } catch (error) {
        showToast(`JSON upload failed: ${error.message}`, 'error');
    } finally {
        hideProgress();
    }
}

function resetJsonUpload() {
    elements.jsonData.value = '';
    elements.jsonName.value = '';
    elements.jsonComment.value = '';
    document.querySelector('input[name="dbType"][value="auto"]').checked = true;
}

// Load Data Functions
async function loadFiles(category = '') {
    try {
        let url = `${API_BASE_URL}/media-files/`;
        if (category) {
            url += `?detected_type=${category}`;
        }

        const response = await fetch(url);
        const files = await response.json();

        if (files.length === 0) {
            elements.filesList.innerHTML = '<div class="loading">No files found</div>';
            return;
        }

        elements.filesList.innerHTML = files.map(file => `
            <div class="file-card">
                <div class="card-header">
                    <span class="card-icon">${getFileIcon(file.original_name)}</span>
                    <div class="card-title" title="${file.original_name}">${file.original_name}</div>
                </div>
                <div class="card-meta">
                    <div><span class="badge">${file.detected_type}</span></div>
                    <div>📁 ${file.storage_category}/${file.storage_subcategory}</div>
                    <div>📏 ${formatFileSize(file.file_size)}</div>
                    <div>📅 ${new Date(file.uploaded_at).toLocaleString()}</div>
                    ${file.ai_description ? `<div>🤖 ${file.ai_description}</div>` : ''}
                </div>
            </div>
        `).join('');
    } catch (error) {
        elements.filesList.innerHTML = '<div class="loading">Error loading files</div>';
        console.error('Error loading files:', error);
    }
}

async function loadJsonData() {
    try {
        const response = await fetch(`${API_BASE_URL}/json-stores/`);
        const datasets = await response.json();

        if (datasets.length === 0) {
            elements.dataList.innerHTML = '<div class="loading">No datasets found</div>';
            return;
        }

        elements.dataList.innerHTML = datasets.map(dataset => `
            <div class="data-card">
                <div class="card-header">
                    <span class="card-icon">📊</span>
                    <div class="card-title" title="${dataset.name}">${dataset.name}</div>
                </div>
                <div class="card-meta">
                    <div><span class="badge">${dataset.database_type}</span></div>
                    <div>🎯 Confidence: ${dataset.confidence_score}%</div>
                    <div>📦 Records: ${dataset.record_count}</div>
                    <div>📐 Depth: ${dataset.structure_depth}</div>
                    <div>📅 ${new Date(dataset.created_at).toLocaleString()}</div>
                    ${dataset.ai_reasoning ? `<div>💡 ${dataset.ai_reasoning}</div>` : ''}
                </div>
            </div>
        `).join('');
    } catch (error) {
        elements.dataList.innerHTML = '<div class="loading">Error loading datasets</div>';
        console.error('Error loading datasets:', error);
    }
}

async function loadStatistics() {
    try {
        const response = await fetch(`${API_BASE_URL}/media-files/statistics/`);
        const stats = await response.json();

        const totalSizeFormatted = formatFileSize(stats.total_size);
        const byTypeHtml = Object.entries(stats.by_type)
            .map(([type, count]) => `
                <div class="stat-card">
                    <div class="stat-value">${count}</div>
                    <div class="stat-label">${type.toUpperCase()}</div>
                </div>
            `).join('');

        elements.statsContent.innerHTML = `
            <div class="stat-card">
                <div class="stat-value">${stats.total_files}</div>
                <div class="stat-label">Total Files</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${totalSizeFormatted}</div>
                <div class="stat-label">Total Size</div>
            </div>
            ${byTypeHtml}
        `;
    } catch (error) {
        elements.statsContent.innerHTML = '<div class="loading">Error loading statistics</div>';
        console.error('Error loading statistics:', error);
    }
}

// UI Helper Functions
function showProgress(message) {
    elements.uploadProgress.classList.remove('hidden');
    elements.progressText.textContent = message;
    elements.progressBar.style.width = '50%';
}

function hideProgress() {
    setTimeout(() => {
        elements.uploadProgress.classList.add('hidden');
        elements.progressBar.style.width = '0%';
    }, 500);
}

function showResults(results) {
    const resultsHtml = results.map(result => `
        <div class="result-item ${result.status === 'failed' ? 'error' : ''}">
            <strong>${result.file}</strong><br>
            Status: ${result.status}<br>
            ${result.category ? `Category: ${result.category}<br>` : ''}
            ${result.message || result.error || ''}
        </div>
    `).join('');

    elements.uploadResults.innerHTML = `<h3>Upload Results</h3>${resultsHtml}`;
    elements.uploadResults.classList.remove('hidden');
}

function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;

    document.getElementById('toastContainer').appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 5000);
}

// Make removeFile globally accessible
window.removeFile = removeFile;
