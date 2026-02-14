<template>
  <div id="app">
    <header class="header">
      <h1>Research Portal</h1>
      <p>Financial Analysis Tools</p>
    </header>

    <div class="container">
      <!-- Tool Selection -->
      <div class="tool-selector">
        <button 
          :class="['tool-btn', { active: selectedTool === 'financials' }]"
          @click="selectedTool = 'financials'"
        >
          Extract Financials
        </button>
        <button 
          :class="['tool-btn', { active: selectedTool === 'earnings' }]"
          @click="selectedTool = 'earnings'"
        >
          Summarize Earnings Call
        </button>
      </div>

      <!-- File Upload Section -->
      <div class="upload-section">
        <div class="upload-box" @dragover.prevent @drop.prevent="handleDrop">
          <input 
            type="file" 
            ref="fileInput"
            accept=".pdf"
            @change="handleFileSelect"
            style="display: none"
          />
          
          <div v-if="!selectedFile" class="upload-placeholder" @click="$refs.fileInput.click()">
            <div class="upload-icon">+</div>
            <p>Click to upload or drag & drop PDF file</p>
            <small>{{ selectedTool === 'financials' ? 'Financial Statements' : 'Earnings Call Transcripts' }}</small>
          </div>

          <div v-else class="file-selected">
            <div class="file-info">
              <span class="file-icon">PDF</span>
              <div>
                <p class="file-name">{{ selectedFile.name }}</p>
                <small>{{ formatFileSize(selectedFile.size) }}</small>
              </div>
            </div>
            <button class="remove-btn" @click="removeFile">×</button>
          </div>
        </div>

        <button 
          class="process-btn"
          :disabled="!selectedFile || processing"
          @click="processFile"
        >
          {{ processing ? 'Processing...' : 'Process Document' }}
        </button>
      </div>

      <!-- Loading State -->
      <div v-if="processing" class="loading">
        <div class="spinner"></div>
        <p>{{ loadingMessage }}</p>
      </div>

      <!-- Error Display -->
      <div v-if="error" class="error-box">
        <h3>Error</h3>
        <p>{{ error }}</p>
        <button @click="error = null">Dismiss</button>
      </div>

      <!-- Results Section -->
      <div v-if="results && !processing" class="results">
        <!-- Financial Extraction Results -->
        <div v-if="selectedTool === 'financials'" class="financial-results">
          <h2>Financial Data Extracted</h2>
          
          <div class="metadata-card">
            <h3>Metadata</h3>
            <div class="metadata-grid">
              <div class="metadata-item">
                <span class="label">Currency:</span>
                <span class="value">{{ results.metadata?.currency || 'N/A' }}</span>
              </div>
              <div class="metadata-item">
                <span class="label">Scale:</span>
                <span class="value">{{ results.metadata?.scale || 'N/A' }}</span>
              </div>
              <div class="metadata-item">
                <span class="label">Periods:</span>
                <span class="value">{{ results.metadata?.periods?.join(', ') || 'N/A' }}</span>
              </div>
              <div class="metadata-item">
                <span class="label">Line Items:</span>
                <span class="value">{{ results.metadata?.line_items_count || 0 }}</span>
              </div>
            </div>
          </div>

          <button class="download-btn" @click="downloadFile">
            Download Excel File
          </button>
        </div>

        <!-- Earnings Call Results -->
        <div v-if="selectedTool === 'earnings'" class="earnings-results">
          <h2>Earnings Call Analysis</h2>

          <div class="summary-grid">
            <div class="summary-card highlight-card">
              <h3>Management Tone</h3>
              <div :class="['tone-badge', results.management_tone]">
                {{ results.management_tone }}
              </div>
            </div>

            <div class="summary-card highlight-card">
              <h3>Confidence Level</h3>
              <div :class="['confidence-badge', results.confidence_level]">
                {{ results.confidence_level }}
              </div>
            </div>
          </div>

          <div class="summary-card">
            <h3>Key Positives</h3>
            <ul class="bullet-list positive">
              <li v-for="(positive, index) in results.key_positives" :key="index">
                {{ positive }}
              </li>
            </ul>
          </div>

          <div class="summary-card">
            <h3>Key Concerns</h3>
            <ul class="bullet-list concerns">
              <li v-for="(concern, index) in results.key_concerns" :key="index">
                {{ concern }}
              </li>
            </ul>
          </div>

          <div class="summary-card">
            <h3>Forward Guidance</h3>
            <div class="guidance-grid">
              <div class="guidance-item">
                <span class="label">Revenue</span>
                <span class="value">{{ results.forward_guidance?.revenue || 'N/A' }}</span>
              </div>
              <div class="guidance-item">
                <span class="label">Margin</span>
                <span class="value">{{ results.forward_guidance?.margin || 'N/A' }}</span>
              </div>
              <div class="guidance-item">
                <span class="label">Capex</span>
                <span class="value">{{ results.forward_guidance?.capex || 'N/A' }}</span>
              </div>
            </div>
          </div>

          <div v-if="results.capacity_utilization" class="summary-card">
            <h3>Capacity Utilization</h3>
            <p class="capacity-text">{{ results.capacity_utilization }}</p>
          </div>

          <div v-if="results.growth_initiatives && results.growth_initiatives.length > 0" class="summary-card">
            <h3>Growth Initiatives</h3>
            <ul class="bullet-list initiatives">
              <li v-for="(initiative, index) in results.growth_initiatives" :key="index">
                {{ initiative }}
              </li>
            </ul>
          </div>
        </div>

        <button class="reset-btn" @click="reset">
          Process Another Document
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'App',
  data() {
    return {
      selectedTool: 'financials',
      selectedFile: null,
      processing: false,
      loadingMessage: '',
      results: null,
      error: null,
      apiBaseUrl: 'http://localhost:8000'
    };
  },
  methods: {
    handleFileSelect(event) {
      const file = event.target.files[0];
      if (file && file.type === 'application/pdf') {
        this.selectedFile = file;
        this.error = null;
      } else {
        this.error = 'Please select a PDF file';
      }
    },
    handleDrop(event) {
      const file = event.dataTransfer.files[0];
      if (file && file.type === 'application/pdf') {
        this.selectedFile = file;
        this.error = null;
      } else {
        this.error = 'Please drop a PDF file';
      }
    },
    removeFile() {
      this.selectedFile = null;
      this.$refs.fileInput.value = '';
    },
    formatFileSize(bytes) {
      if (bytes === 0) return '0 Bytes';
      const k = 1024;
      const sizes = ['Bytes', 'KB', 'MB', 'GB'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    },
    async processFile() {
      if (!this.selectedFile) return;

      this.processing = true;
      this.results = null;
      this.error = null;

      const formData = new FormData();
      formData.append('file', this.selectedFile);

      const endpoint = this.selectedTool === 'financials' 
        ? '/api/extract-financials'
        : '/api/summarize-earnings-call';

      this.loadingMessage = this.selectedTool === 'financials'
        ? 'Extracting financial data... This may take 15-30 seconds'
        : 'Analyzing earnings call... This may take 10-20 seconds';

      try {
        const response = await axios.post(`${this.apiBaseUrl}${endpoint}`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          },
          timeout: 120000
        });

        if (response.data.status === 'success') {
          this.results = response.data;
        } else {
          this.error = response.data.error || 'Processing failed';
        }
      } catch (err) {
        console.error('Error:', err);
        this.error = err.response?.data?.detail || err.message || 'Failed to process document';
      } finally {
        this.processing = false;
      }
    },
    async downloadFile() {
      if (!this.results || !this.results.file_path) return;

      const filename = this.results.file_path.split('/').pop();
      const url = `${this.apiBaseUrl}/api/download/${filename}`;
      
      window.open(url, '_blank');
    },
    reset() {
      this.selectedFile = null;
      this.results = null;
      this.error = null;
      this.$refs.fileInput.value = '';
    }
  }
};
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: #fafafa;
  min-height: 100vh;
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  background: #fff;
  padding: 20px 30px;
  border-bottom: 1px solid #ddd;
}

.header h1 {
  color: #222;
  font-size: 22px;
  margin-bottom: 4px;
  font-weight: 600;
}

.header p {
  color: #666;
  font-size: 13px;
}

.container {
  flex: 1;
  max-width: 900px;
  margin: 30px auto;
  padding: 0 20px;
  width: 100%;
}

.tool-selector {
  display: flex;
  gap: 10px;
  margin-bottom: 25px;
}

.tool-btn {
  flex: 1;
  padding: 12px 20px;
  font-size: 14px;
  border: 1px solid #ddd;
  background: #fff;
  color: #555;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
}

.tool-btn:hover {
  background: #f5f5f5;
  border-color: #ccc;
}

.tool-btn.active {
  background: #2563eb;
  color: #fff;
  border-color: #2563eb;
}

.upload-section {
  background: #fff;
  padding: 20px;
  border-radius: 4px;
  border: 1px solid #ddd;
  margin-bottom: 20px;
}

.upload-box {
  border: 2px dashed #ccc;
  border-radius: 4px;
  padding: 30px;
  text-align: center;
  cursor: pointer;
  margin-bottom: 15px;
  background: #fafafa;
}

.upload-box:hover {
  border-color: #2563eb;
  background: #f0f9ff;
}

.upload-placeholder {
  padding: 20px;
}

.upload-icon {
  font-size: 40px;
  margin-bottom: 10px;
  color: #999;
  font-weight: 300;
}

.upload-placeholder p {
  font-size: 14px;
  color: #333;
  margin-bottom: 4px;
  font-weight: 500;
}

.upload-placeholder small {
  color: #666;
  font-size: 12px;
}

.file-selected {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background: #f0f9ff;
  border-radius: 4px;
  border: 1px solid #bfdbfe;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.file-icon {
  font-size: 11px;
  font-weight: 600;
  color: #2563eb;
  background: #dbeafe;
  padding: 6px 10px;
  border-radius: 3px;
}

.file-name {
  font-weight: 600;
  color: #222;
  margin-bottom: 3px;
  font-size: 13px;
}

.file-info small {
  color: #666;
  font-size: 12px;
}

.remove-btn {
  background: #dc2626;
  color: #fff;
  border: none;
  width: 28px;
  height: 28px;
  border-radius: 3px;
  cursor: pointer;
  font-size: 18px;
  line-height: 1;
}

.remove-btn:hover {
  background: #b91c1c;
}

.process-btn {
  width: 100%;
  padding: 12px;
  font-size: 14px;
  background: #2563eb;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
}

.process-btn:hover:not(:disabled) {
  background: #1d4ed8;
}

.process-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.loading {
  background: #fff;
  padding: 40px;
  border-radius: 4px;
  text-align: center;
  border: 1px solid #ddd;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #eee;
  border-top: 3px solid #2563eb;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 15px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading p {
  color: #666;
  font-size: 14px;
}

.error-box {
  background: #fef2f2;
  border: 1px solid #fecaca;
  padding: 15px;
  border-radius: 4px;
  margin-bottom: 20px;
}

.error-box h3 {
  color: #991b1b;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 600;
}

.error-box p {
  color: #7f1d1d;
  margin-bottom: 10px;
  font-size: 13px;
}

.error-box button {
  background: #dc2626;
  color: #fff;
  border: none;
  padding: 6px 14px;
  border-radius: 3px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
}

.error-box button:hover {
  background: #b91c1c;
}

.results {
  background: #fff;
  padding: 25px;
  border-radius: 4px;
  border: 1px solid #ddd;
}

.results h2 {
  color: #222;
  margin-bottom: 20px;
  font-size: 20px;
  font-weight: 600;
}

.metadata-card, .summary-card {
  background: #fafafa;
  padding: 18px;
  border-radius: 4px;
  margin-bottom: 15px;
  border: 1px solid #e5e5e5;
}

.metadata-card h3, .summary-card h3 {
  color: #222;
  margin-bottom: 12px;
  font-size: 13px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.metadata-grid, .guidance-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.metadata-item, .guidance-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.label {
  font-size: 12px;
  color: #666;
  font-weight: 500;
}

.value {
  font-size: 14px;
  color: #222;
  font-weight: 600;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 15px;
  margin-bottom: 15px;
}

.highlight-card {
  background: #fff;
  border: 1px solid #ddd;
}

.tone-badge, .confidence-badge {
  display: inline-block;
  padding: 6px 12px;
  border-radius: 3px;
  font-size: 13px;
  font-weight: 600;
  margin-top: 5px;
}

.tone-badge.Positive, .tone-badge.Optimistic {
  background: #dcfce7;
  color: #166534;
}

.tone-badge.Negative, .tone-badge.Cautious {
  background: #fee2e2;
  color: #991b1b;
}

.tone-badge.Neutral {
  background: #f3f4f6;
  color: #374151;
}

.confidence-badge.High {
  background: #dcfce7;
  color: #166534;
}

.confidence-badge.Medium {
  background: #fef3c7;
  color: #92400e;
}

.confidence-badge.Low {
  background: #fee2e2;
  color: #991b1b;
}

.bullet-list {
  list-style: none;
  padding: 0;
}

.bullet-list li {
  padding: 8px 0 8px 16px;
  position: relative;
  font-size: 13px;
  color: #333;
  line-height: 1.5;
}

.bullet-list li:before {
  content: "•";
  position: absolute;
  left: 0;
  color: #666;
  font-weight: bold;
}

.capacity-text {
  font-size: 13px;
  color: #333;
  line-height: 1.6;
}

.download-btn, .reset-btn {
  width: 100%;
  padding: 12px;
  font-size: 14px;
  background: #2563eb;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
  margin-top: 10px;
}

.download-btn:hover, .reset-btn:hover {
  background: #1d4ed8;
}

.reset-btn {
  background: #6b7280;
}

.reset-btn:hover {
  background: #4b5563;
}
</style>