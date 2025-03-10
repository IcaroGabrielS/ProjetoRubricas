<template>
  <div class="store-layout">
    <div class="store-container">
      <div class="store-content">
        <div class="page-header">
          <h1>{{ company.name }}</h1>
          <p class="subtitle">Detalhes e arquivos da empresa</p>
        </div>
        
        <div v-if="error" class="error-alert">
          <span>{{ error }}</span>
          <button class="close-btn" @click="error = ''" aria-label="Fechar">&times;</button>
        </div>

        <div v-if="loading" class="loading-container">
          <div class="loading-spinner"></div>
          <p>Carregando informações da empresa...</p>
        </div>

        <div v-else>
          <!-- Informações da Empresa -->
          <div class="section-card">
            <h2>Informações Gerais</h2>
            <div class="company-details">
              <div class="detail-row">
                <div class="detail-label">Nome:</div>
                <div class="detail-value">{{ company.name }}</div>
              </div>
              <div class="detail-row">
                <div class="detail-label">CNPJ:</div>
                <div class="detail-value">{{ company.cnpj }}</div>
              </div>
              <div class="detail-row">
                <div class="detail-label">Criado em:</div>
                <div class="detail-value">{{ formatDate(company.created_at) }}</div>
              </div>
              <div class="detail-row">
                <div class="detail-label">Grupo:</div>
                <div class="detail-value">
                  <a @click="goToGroupDetail(company.group_id)" class="group-link">
                    {{ groupName }}
                  </a>
                </div>
              </div>
            </div>
          </div>

          <!-- Lista de Arquivos -->
          <div class="section-card">
            <div class="section-header">
              <h2>Arquivos</h2>
              <button v-if="isAdmin" class="upload-btn" @click="showUploadForm = !showUploadForm">
                {{ showUploadForm ? 'Cancelar' : 'Enviar Arquivo' }}
              </button>
            </div>

            <!-- Formulário de Upload -->
            <div v-if="showUploadForm && isAdmin" class="upload-form">
              <form @submit.prevent="uploadFile">
                <div class="form-group">
                  <label for="file">Selecionar Arquivo:</label>
                  <input 
                    type="file" 
                    id="file" 
                    ref="fileInput"
                    @change="handleFileChange" 
                    required
                  >
                  <div class="file-types">Formatos permitidos: .csv, .xls, .xlsx, .pdf</div>
                </div>
                <button type="submit" class="action-button" :disabled="uploading">
                  {{ uploading ? 'Enviando...' : 'Enviar Arquivo' }}
                </button>
              </form>
            </div>

            <div v-if="!files || files.length === 0" class="empty-state">
              <p>Nenhum arquivo foi adicionado a esta empresa.</p>
            </div>

            <div v-else class="files-list">
              <div v-for="file in files" :key="file.id" class="file-item">
                <div class="file-info">
                  <div :class="['file-icon', getFileIconClass(file.file_type)]">
                    {{ file.file_type.toUpperCase() }}
                  </div>
                  <div class="file-details">
                    <div class="file-name">{{ file.filename }}</div>
                    <div class="file-date">Enviado em {{ formatDate(file.uploaded_at) }}</div>
                  </div>
                </div>
                <div class="file-actions">
                  <button class="download-btn" @click="downloadFile(file.id)">Download</button>
                </div>
              </div>
            </div>
          </div>

          <div class="company-actions">
            <button class="secondary-button" @click="goBack">Voltar para o Grupo</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CompanyDetailView',
  data() {
    return {
      companyId: null,
      company: {},
      files: [],
      loading: true,
      error: '',
      isAdmin: false,
      showUploadForm: false,
      groupName: '',
      selectedFile: null,
      uploading: false
    }
  },
  created() {
    this.checkAccess();
    this.companyId = parseInt(this.$route.params.id);
    if (isNaN(this.companyId)) {
      this.error = 'ID de empresa inválido';
      this.loading = false;
      return;
    }
    this.fetchCompanyData();
  },
  methods: {
    checkAccess() {
      const userStr = localStorage.getItem('user');
      if (!userStr) {
        this.$router.push('/login');
        return;
      }
      
      const user = JSON.parse(userStr);
      this.isAdmin = user.is_admin === true;
    },
    async fetchCompanyData() {
      try {
        this.loading = true;
        const userStr = localStorage.getItem('user');
        if (!userStr) {
          this.$router.push('/login');
          return;
        }
        
        const user = JSON.parse(userStr);
        
        // Buscar dados da empresa
        console.log('Fetching company data for ID:', this.companyId);
        const response = await fetch(`/api/companies/${this.companyId}`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'User-ID': user.id
          }
        });
        
        if (!response.ok) {
          const data = await response.json();
          this.error = data.message || 'Erro ao carregar dados da empresa';
          this.loading = false;
          return;
        }
        
        const data = await response.json();
        this.company = data.company;
        console.log('Company data loaded:', this.company);
        
        // Buscar nome do grupo
        await this.fetchGroupName();
        
        // Buscar arquivos da empresa
        await this.fetchCompanyFiles();
        
        this.loading = false;
      } catch (error) {
        this.error = 'Erro ao conectar ao servidor';
        this.loading = false;
        console.error('Error fetching company data:', error);
      }
    },
    async fetchGroupName() {
      try {
        if (!this.company || !this.company.group_id) return;
        
        const userStr = localStorage.getItem('user');
        if (!userStr) return;
        
        const user = JSON.parse(userStr);
        
        const response = await fetch(`/api/groups/${this.company.group_id}`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'User-ID': user.id
          }
        });
        
        if (!response.ok) return;
        
        const data = await response.json();
        this.groupName = data.group.name;
      } catch (error) {
        console.error('Error fetching group name:', error);
      }
    },
    async fetchCompanyFiles() {
      try {
        const userStr = localStorage.getItem('user');
        if (!userStr) return;
        
        const user = JSON.parse(userStr);
        
        const response = await fetch(`/api/companies/${this.companyId}/files`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'User-ID': user.id
          }
        });
        
        if (!response.ok) {
          const data = await response.json();
          console.error('Error fetching files:', data.message);
          return;
        }
        
        const data = await response.json();
        this.files = data.files;
        console.log('Files loaded:', this.files);
      } catch (error) {
        console.error('Error fetching company files:', error);
      }
    },
    handleFileChange(event) {
      this.selectedFile = event.target.files[0];
    },
    async uploadFile() {
      if (!this.selectedFile) {
        this.error = 'Selecione um arquivo para enviar';
        return;
      }
      
      const fileExt = this.selectedFile.name.split('.').pop().toLowerCase();
      const allowedExts = ['csv', 'xls', 'xlsx', 'pdf'];
      
      if (!allowedExts.includes(fileExt)) {
        this.error = 'Formato de arquivo não permitido';
        return;
      }
      
      try {
        this.uploading = true;
        
        const userStr = localStorage.getItem('user');
        if (!userStr) {
          this.$router.push('/login');
          return;
        }
        
        const user = JSON.parse(userStr);
        
        const formData = new FormData();
        formData.append('file', this.selectedFile);
        
        const response = await fetch(`/api/companies/${this.companyId}/files`, {
          method: 'POST',
          headers: {
            'User-ID': user.id
          },
          body: formData
        });
        
        const data = await response.json();
        
        if (!response.ok) {
          this.error = data.message || 'Erro ao enviar arquivo';
          this.uploading = false;
          return;
        }
        
        // Limpar formulário e atualizar lista de arquivos
        this.$refs.fileInput.value = '';
        this.selectedFile = null;
        this.showUploadForm = false;
        await this.fetchCompanyFiles();
        
        this.uploading = false;
      } catch (error) {
        this.error = 'Erro ao conectar ao servidor';
        this.uploading = false;
        console.error('Error uploading file:', error);
      }
    },
    async downloadFile(fileId) {
      try {
        const userStr = localStorage.getItem('user');
        if (!userStr) {
          this.$router.push('/login');
          return;
        }
        
        const user = JSON.parse(userStr);
        
        // Criar um link temporário para download
        const a = document.createElement('a');
        a.href = `/api/files/${fileId}/download?user_id=${user.id}`;
        a.target = '_blank';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
      } catch (error) {
        this.error = 'Erro ao baixar arquivo';
        console.error('Error downloading file:', error);
      }
    },
    getFileIconClass(fileType) {
      if (!fileType) return 'generic-file';
      
      switch (fileType.toLowerCase()) {
        case 'csv':
          return 'csv-file';
        case 'xls':
        case 'xlsx':
          return 'excel-file';
        case 'pdf':
          return 'pdf-file';
        default:
          return 'generic-file';
      }
    },
    formatDate(dateString) {
      if (!dateString) return '';
      
      const options = { 
        day: '2-digit', 
        month: '2-digit', 
        year: 'numeric', 
        hour: '2-digit', 
        minute: '2-digit' 
      };
      
      try {
        return new Date(dateString).toLocaleDateString('pt-BR', options);
      } catch (error) {
        return dateString;
      }
    },
    goToGroupDetail(groupId) {
      this.$router.push(`/groups/${groupId}`);
    },
    goBack() {
      if (this.company && this.company.group_id) {
        this.$router.push(`/groups/${this.company.group_id}`);
      } else {
        this.$router.push('/');
      }
    }
  }
}
</script>

<style scoped>
.store-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  width: 100%;
  overflow: hidden;
}

.store-container {
  flex: 1;
  overflow-y: auto;
  padding: 2rem 3rem;
  display: flex;
  justify-content: center;
  background: linear-gradient(135deg, #142C4D, #204578);
}

.store-content {
  width: 100%;
  max-width: 1200px;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
  padding: 2.5rem 3rem;
  animation: fade-in 0.6s ease-out;
}

.page-header {
  text-align: left;
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #eaeaea;
}

.page-header h1 {
  color: #142C4D;
  font-size: 2.2rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.subtitle {
  color: #666;
  font-size: 1.1rem;
}

.section-card {
  background-color: #f9f9f9;
  border-radius: 8px;
  padding: 1.8rem;
  margin-bottom: 2rem;
}

.section-card h2 {
  color: #204578;
  font-size: 1.5rem;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid #e1e1e1;
  padding-bottom: 0.8rem;
}

.company-details {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.detail-row {
  display: flex;
  align-items: center;
}

.detail-label {
  font-weight: 600;
  color: #333;
  width: 150px;
  flex-shrink: 0;
}

.detail-value {
  color: #444;
}

.group-link {
  color: #204578;
  text-decoration: underline;
  cursor: pointer;
}

.group-link:hover {
  color: #142C4D;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid #e1e1e1;
  padding-bottom: 0.8rem;
}

.section-header h2 {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.upload-btn {
  padding: 0.7rem 1.2rem;
  background: linear-gradient(to right, #142C4D, #204578);
  border: none;
  border-radius: 8px;
  color: white;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.upload-btn:hover {
  background: linear-gradient(to right, #1a3760, #2a5b9e);
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(20, 44, 77, 0.3);
}

.upload-form {
  background-color: white;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  border: 1px solid #e1e1e1;
}

.form-group {
  margin-bottom: 1.2rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.6rem;
  font-size: 1rem;
  font-weight: 600;
  color: #333;
}

.file-types {
  font-size: 0.85rem;
  color: #666;
  margin-top: 0.5rem;
}

.files-list {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

.file-item {
  background-color: #fff;
  border-radius: 6px;
  border: 1px solid #eaeaea;
  padding: 1rem 1.2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: all 0.2s ease;
}

.file-item:hover {
  border-color: #d0d0d0;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.file-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.file-icon {
  width: 48px;
  height: 48px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.7rem;
  color: white;
}

.csv-file {
  background: linear-gradient(135deg, #20bf6b, #0fb9b1);
}

.excel-file {
  background: linear-gradient(135deg, #2ecc71, #26de81);
}

.pdf-file {
  background: linear-gradient(135deg, #eb3b5a, #fc5c65);
}

.generic-file {
  background: linear-gradient(135deg, #4b6584, #778ca3);
}

.file-details {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.file-name {
  font-weight: 600;
  color: #142C4D;
  font-size: 1rem;
}

.file-date {
  color: #666;
  font-size: 0.85rem;
}

.file-actions {
  display: flex;
  gap: 0.8rem;
}

.download-btn {
  padding: 0.5rem 1rem;
  background-color: #f0f0f0;
  border: 1px solid #ddd;
  border-radius: 6px;
  color: #333;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.download-btn:hover {
  background-color: #e0e0e0;
  transform: translateY(-2px);
}

.company-actions {
  display: flex;
  justify-content: center;
  margin-top: 2rem;
}

.secondary-button {
  padding: 0.9rem 2rem;
  background-color: #f0f0f0;
  border: 1px solid #ddd;
  border-radius: 8px;
  color: #333;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.secondary-button:hover {
  background-color: #e0e0e0;
  transform: translateY(-2px);
}

.error-alert {
  padding: 1rem 1.5rem;
  border-radius: 8px;
  margin-bottom: 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 1rem;
  background-color: #fee2e2;
  color: #b91c1c;
  animation: fade-in 0.3s ease;
}

.close-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.3rem;
  padding: 0 0.5rem;
  color: #b91c1c;
}

.loading-container, .loading-indicator, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem 0;
  text-align: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(32, 69, 120, 0.1);
  border-top: 4px solid #204578;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

.empty-state p {
  color: #666;
  font-style: italic;
  font-size: 1.1rem;
}

.action-button {
  padding: 0.9rem 2rem;
  background: linear-gradient(to right, #142C4D, #204578);
  border: none;
  border-radius: 8px;
  color: white;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 200px;
}

.action-button:hover {
  background: linear-gradient(to right, #1a3760, #2a5b9e);
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(20, 44, 77, 0.3);
}

.action-button:disabled {
  background: #cccccc;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* Animações */
@keyframes fade-in {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Responsividade */
@media (max-width: 1280px) {
  .store-content {
    max-width: 95%;
    padding: 2rem;
  }
}

@media (max-width: 768px) {
  .store-container {
    padding: 1.5rem;
  }
  
  .store-content {
    padding: 1.5rem;
  }
  
  .page-header h1 {
    font-size: 1.8rem;
  }
}

@media (max-width: 576px) {
  .store-container {
    padding: 1rem;
  }
  
  .store-content {
    padding: 1rem;
    border-radius: 8px;
  }
}
</style>