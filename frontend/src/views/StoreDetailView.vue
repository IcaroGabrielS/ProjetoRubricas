<template>
  <div class="store-detail-container">
    <div class="store-detail-content">
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Carregando...</p>
      </div>
      
      <div v-else-if="error" class="error-state">
        <div class="error-icon">!</div>
        <p>{{ error }}</p>
      </div>
      
      <div v-else class="store-content">
        <div class="page-header">
          <h1>{{ store.name }}</h1>
          <div class="header-info">
            <div class="date-info">{{ currentDateTime }}</div>
            <div class="user-info">{{ currentUser }}</div>
          </div>
        </div>
        
        <div class="store-info">
          <div class="info-row">
            <span class="label">Número da Loja:</span>
            <span class="value">{{ store.store_number }}</span>
          </div>
          
          <div class="info-row">
            <span class="label">Inscrição Estadual:</span>
            <span class="value">{{ store.state_registration }}</span>
          </div>
          
          <div class="info-row">
            <span class="label">Endereço:</span>
            <span class="value">{{ store.address }}</span>
          </div>
          
          <div class="info-row">
            <span class="label">Data de Criação:</span>
            <span class="value">{{ formatDate(store.created_at) }}</span>
          </div>
        </div>
        
        <div class="file-section">
          <h2>Arquivos da Loja</h2>
          
          <div v-if="isAdmin" class="file-upload">
            <h3>Upload de Arquivo</h3>
            <form @submit.prevent="uploadFile" class="upload-form">
              <div class="form-group">
                <label for="file" class="file-label">
                  <span class="file-icon">📄</span>
                  <span class="file-text">{{ selectedFile ? selectedFile.name : 'Selecione um arquivo' }}</span>
                  <input 
                    type="file" 
                    id="file" 
                    class="file-input"
                    @change="handleFileChange" 
                    accept=".csv,.xls,.xlsx,.pdf"
                    required
                  >
                </label>
                <small>Formatos aceitos: CSV, Excel, PDF (max: 16MB)</small>
              </div>
              
              <button type="submit" :disabled="fileLoading" class="upload-btn">
                <span v-if="fileLoading" class="loading-indicator small"></span>
                {{ fileLoading ? 'Enviando...' : 'Enviar Arquivo' }}
              </button>
            </form>
            
            <div v-if="fileError" class="error-message">
              <div class="error-icon small">!</div>
              <p>{{ fileError }}</p>
              <button class="close-btn" @click="fileError = null" aria-label="Fechar">×</button>
            </div>
            
            <div v-if="fileSuccess" class="success-message">
              <div class="success-icon small">✓</div>
              <p>{{ fileSuccess }}</p>
            </div>
          </div>
          
          <div class="file-list">
            <h3>Arquivos Disponíveis</h3>
            
            <div v-if="store.files && store.files.length === 0" class="no-files">
              <div class="empty-icon">📂</div>
              <p>Nenhum arquivo disponível para esta loja.</p>
            </div>
            
            <div v-else class="files-table-wrapper">
              <table class="files-table">
                <thead>
                  <tr>
                    <th>Nome do Arquivo</th>
                    <th>Tipo</th>
                    <th>Data de Upload</th>
                    <th>Ação</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="file in store.files" :key="file.id">
                    <td>{{ file.filename }}</td>
                    <td>{{ file.file_type.toUpperCase() }}</td>
                    <td>{{ formatDate(file.uploaded_at) }}</td>
                    <td>
                      <a :href="`/api/files/${file.id}`" target="_blank" class="download-btn">
                        Download
                      </a>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
        
        <div class="actions">
          <router-link to="/stores" class="back-btn">Voltar para Lista</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'StoreDetailView',
  data() {
    return {
      store: {
        id: null,
        name: '',
        state_registration: '',
        store_number: null,
        address: '',
        created_at: null,
        created_by: null,
        files: []
      },
      loading: true,
      error: null,
      isAdmin: false,
      selectedFile: null,
      fileLoading: false,
      fileError: null,
      fileSuccess: null,
      currentDateTime: '2025-03-04 22:32:33',
      currentUser: 'IcaroGabrielS'
    }
  },
  created() {
    this.checkAdmin();
    this.fetchStoreDetails();
  },
  methods: {
    checkAdmin() {
      const userStr = localStorage.getItem('user');
      if (userStr) {
        const user = JSON.parse(userStr);
        this.isAdmin = user.is_admin === true;
      }
    },
    async fetchStoreDetails() {
      try {
        const userStr = localStorage.getItem('user');
        if (!userStr) {
          this.$router.push('/login');
          return;
        }
        
        const user = JSON.parse(userStr);
        const storeId = this.$route.params.id;
        
        const response = await fetch(`/api/stores/${storeId}`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'User-ID': user.id
          }
        });
        
        const data = await response.json();
        
        if (!response.ok) {
          this.error = data.message || 'Erro ao carregar detalhes da loja';
          this.loading = false;
          return;
        }
        
        this.store = data.store;
        this.loading = false;
      } catch (error) {
        this.error = 'Erro ao conectar ao servidor';
        this.loading = false;
        console.error('Error fetching store details:', error);
      }
    },
    formatDate(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      return new Intl.DateTimeFormat('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      }).format(date);
    },
    handleFileChange(event) {
      this.selectedFile = event.target.files[0];
      this.fileError = null;
      this.fileSuccess = null;
    },
    async uploadFile() {
      if (!this.selectedFile) {
        this.fileError = 'Por favor, selecione um arquivo para enviar.';
        return;
      }
      
      this.fileLoading = true;
      this.fileError = null;
      this.fileSuccess = null;
      
      try {
        const userStr = localStorage.getItem('user');
        if (!userStr) {
          this.$router.push('/login');
          return;
        }
        
        const user = JSON.parse(userStr);
        const formData = new FormData();
        formData.append('file', this.selectedFile);
        
        const response = await fetch(`/api/stores/${this.store.id}/files`, {
          method: 'POST',
          headers: {
            'User-ID': user.id
          },
          body: formData
        });
        
        const data = await response.json();
        
        if (!response.ok) {
          this.fileError = data.message || 'Erro ao enviar arquivo';
          this.fileLoading = false;
          return;
        }
        
        this.fileSuccess = 'Arquivo enviado com sucesso!';
        this.fileLoading = false;
        this.selectedFile = null;
        document.getElementById('file').value = '';
        
        // Atualiza a lista de arquivos
        this.fetchStoreDetails();
      } catch (error) {
        this.fileError = 'Erro ao conectar ao servidor';
        this.fileLoading = false;
        console.error('Error uploading file:', error);
      }
    }
  }
}
</script>
  
<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Sarala:wght@400;700&display=swap');

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html, body {
  height: 100%;
  overflow: hidden; /* Previne rolagem em toda a página */
  margin: 0;
  padding: 0;
}

body {
  font-family: 'Sarala', sans-serif;
  background: linear-gradient(135deg, #142C4D, #204578);
  color: #333;
  display: flex;
  align-items: center;
  justify-content: center;
}

.store-detail {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
  animation: fade-in 0.8s ease-out;
}

.loading, .error {
  text-align: center;
  padding: 20px;
}

.error {
  color: #dc3545;
}

.store-content h1 {
  border-bottom: 2px solid #007bff;
  padding-bottom: 10px;
  margin-bottom: 20px;
  color: #142C4D;
  font-size: 2.2rem;
  font-weight: 700;
}

.store-info {
  background-color: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 30px;
}

.info-row {
  margin-bottom: 12px;
  display: flex;
}

.info-row .label {
  font-weight: bold;
  width: 150px;
  color: #495057;
}

.info-row .value {
  flex-grow: 1;
}

.file-section {
  margin-top: 30px;
}

.file-section h2 {
  border-bottom: 1px solid #dee2e6;
  padding-bottom: 10px;
  margin-bottom: 20px;
  color: #142C4D;
  font-size: 1.8rem;
  font-weight: 700;
}

.file-upload {
  background-color: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.file-upload h3 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #142C4D;
  font-size: 1.4rem;
  font-weight: 700;
}

.form-group {
  margin-bottom: 15px;
}

small {
  display: block;
  margin-top: 5px;
  color: #6c757d;
}

.success-message {
  color: #28a745;
  margin-top: 10px;
}

.files-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 15px;
}

.files-table th, .files-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #dee2e6;
}

.files-table th {
  background-color: #f8f9fa;
  font-weight: bold;
  color: #495057;
}

.no-files {
  text-align: center;
  color: #6c757d;
  padding: 20px;
}

.download-btn {
  display: inline-block;
  background-color: #007bff;
  color: white;
  padding: 6px 12px;
  border-radius: 4px;
  text-decoration: none;
  font-size: 14px;
  transition: all 0.3s ease;
}

.download-btn:hover {
  background-color: #0069d9;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 123, 255, 0.3);
}

.back-btn {
  display: inline-block;
  background-color: #6c757d;
  color: white;
  padding: 8px 16px;
  border-radius: 4px;
  text-decoration: none;
  margin-top: 30px;
  transition: all 0.3s ease;
}

.back-btn:hover {
  background-color: #5a6268;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(108, 117, 125, 0.3);
}

.actions {
  margin-top: 30px;
  text-align: center;
}

/* Animações */
@keyframes fade-in {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Responsividade */
@media (max-width: 480px) {
  .store-detail {
    max-width: 90%;
    padding: 2rem 1.5rem;
  }
  
  .store-content h1 {
    font-size: 1.8rem;
  }
  
  .file-section h2 {
    font-size: 1.4rem;
  }
  
  .file-upload h3 {
    font-size: 1.2rem;
  }
}
</style>