<template>
  <div>
    <!-- Alerta para dispositivos móveis -->
    <div v-if="isMobileDevice" class="mobile-warning">
      <div class="warning-icon">⚠️</div>
      <h2>Acesso não recomendado</h2>
      <p>Este site não foi projetado para dispositivos móveis. Por favor, acesse através de um computador para uma melhor experiência.</p>
    </div>

    <!-- Conteúdo principal - visível apenas em desktop -->
    <div v-else class="home-layout">
      <!-- Painel com as informações da empresa (visualmente à esquerda) -->
      <div class="content-panel">
        <div class="content-wrapper">
          <div class="home-header">
            <h1>{{ company.name }}</h1>
            <p class="welcome-text">Detalhes da empresa</p>
          </div>

          <div v-if="error" class="error-message">
            <div class="error-icon">!</div>
            <p>{{ error }}</p>
            <button class="close-btn" @click="error = ''" aria-label="Fechar">×</button>
          </div>

          <div v-if="success" class="success-message">
            <div class="success-icon">✓</div>
            <p>{{ success }}</p>
            <button class="close-btn success" @click="success = ''" aria-label="Fechar">×</button>
          </div>

          <div v-if="loading" class="loading-indicator">
            <div class="loading-spinner"></div>
            <p>Carregando informações da empresa...</p>
          </div>

          <div v-else>
            <!-- Informações da Empresa -->
            <div class="dashboard-summary">
              <div class="dashboard-item">
                <h3>Informações Gerais</h3>
                <div class="info-grid">
                  <div class="info-item">
                    <div class="info-label">Nome:</div>
                    <div class="info-value">{{ company.name }}</div>
                  </div>
                  <div class="info-item">
                    <div class="info-label">CNPJ:</div>
                    <div class="info-value">{{ company.cnpj }}</div>
                  </div>
                  <div class="info-item">
                    <div class="info-label">Criado em:</div>
                    <div class="info-value">{{ formatDate(company.created_at) }}</div>
                  </div>
                  <div class="info-item">
                    <div class="info-label">Grupo:</div>
                    <div class="info-value">
                      <a @click="goToGroupDetail(company.group_id)" class="group-link">
                        {{ groupName }}
                      </a>
                    </div>
                  </div>
                  <div v-if="isAdmin" class="info-item">
                    <div class="info-label">Ações Administrativas:</div>
                    <div class="info-value">
                      <button class="delete-btn" @click="showDeleteConfirmation = true">Excluir Empresa</button>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Botões de ação -->
            <div class="quick-actions">
              <button class="secondary-button" @click="goBack">Voltar para o Grupo</button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Painel com arquivos (visualmente à direita) -->
      <div class="files-panel">
        <div class="content-wrapper">
          <div class="files-header">
            <h2>Arquivos</h2>
            <button v-if="isAdmin" class="action-button admin" @click="showUploadForm = !showUploadForm">
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
              <button type="submit" class="submit-btn" :disabled="uploading">
                {{ uploading ? 'Enviando...' : 'Enviar Arquivo' }}
              </button>
            </form>
          </div>

          <div v-if="loading" class="loading-indicator">
            <div class="loading-spinner"></div>
            <p>Carregando arquivos...</p>
          </div>
          <div v-else-if="!files || files.length === 0" class="empty-state">
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
      </div>
    </div>

    <!-- Modal de Confirmação de Exclusão -->
    <div v-if="showDeleteConfirmation" class="modal-overlay">
      <div class="modal-container">
        <div class="modal-header">
          <h3>Confirmação de Exclusão</h3>
        </div>
        <div class="modal-body">
          <div class="warning-icon modal-icon">⚠️</div>
          <p>Você está prestes a excluir a empresa <strong>{{ company.name }}</strong> e todos os seus arquivos.</p>
          <p class="warning-text">Esta ação não pode ser desfeita!</p>
          
          <div class="confirmation-input">
            <label for="confirmText">Digite "EXCLUIR" para confirmar:</label>
            <input 
              type="text" 
              id="confirmText" 
              v-model="confirmDeleteText" 
              placeholder="EXCLUIR" 
            />
          </div>
        </div>
        <div class="modal-footer">
          <button class="cancel-btn" @click="cancelDelete">Cancelar</button>
          <button 
            class="delete-btn"
            :disabled="confirmDeleteText !== 'EXCLUIR' || deletingCompany"
            @click="deleteCompany"
          >
            {{ deletingCompany ? 'Excluindo...' : 'Confirmar Exclusão' }}
          </button>
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
      success: '',
      isAdmin: false,
      showUploadForm: false,
      groupName: '',
      selectedFile: null,
      uploading: false,
      isMobileDevice: false,
      showDeleteConfirmation: false,
      confirmDeleteText: '',
      deletingCompany: false
    }
  },
  created() {
    this.checkDeviceType();
    this.checkAccess();
    // IDs de empresa ainda são numéricos, então o parseInt é mantido
    this.companyId = parseInt(this.$route.params.id);
    if (isNaN(this.companyId)) {
      this.error = 'ID de empresa inválido';
      this.loading = false;
      return;
    }
    this.fetchCompanyData();
    
    // Adicionar listener para verificar redimensionamento
    window.addEventListener('resize', this.checkDeviceType);
  },
  beforeUnmount() {
    // Remover listener ao destruir componente
    window.removeEventListener('resize', this.checkDeviceType);
  },
  methods: {
    checkDeviceType() {
      this.isMobileDevice = window.innerWidth < 1024;
    },
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
        this.error = ''; // Limpar erros anteriores
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
          console.error('API error:', response.status, data);
          return;
        }
        
        const data = await response.json();
        this.company = data.company;
        console.log('Company data loaded:', this.company);
        
        // Se a API já retorna os arquivos, podemos usar diretamente
        if (this.company.files) {
          this.files = this.company.files;
        } else {
          // Caso contrário, buscar arquivos separadamente
          await this.fetchCompanyFiles();
        }
        
        // Buscar nome do grupo se necessário
        if (this.company.group_id) {
          await this.fetchGroupName();
        }
        
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
        
        // O ID do grupo agora é UUID, não precisa de conversão
        console.log('Fetching group name for UUID:', this.company.group_id);
        
        const response = await fetch(`/api/groups/${this.company.group_id}`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'User-ID': user.id
          }
        });
        
        if (!response.ok) {
          console.error('Failed to fetch group name, status:', response.status);
          return;
        }
        
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
      // groupId agora é um UUID (string), não precisamos converter para número
      this.$router.push(`/groups/${groupId}`);
    },
    goBack() {
      if (this.company && this.company.group_id) {
        // company.group_id agora é um UUID (string)
        this.$router.push(`/groups/${this.company.group_id}`);
      } else {
        this.$router.push('/');
      }
    },
    cancelDelete() {
      this.showDeleteConfirmation = false;
      this.confirmDeleteText = '';
    },
    async deleteCompany() {
      try {
        if (this.confirmDeleteText !== 'EXCLUIR') {
          return;
        }
        
        this.deletingCompany = true;
        const userStr = localStorage.getItem('user');
        if (!userStr) {
          this.$router.push('/login');
          return;
        }
        
        const user = JSON.parse(userStr);
        // Lembre-se que groupId agora é um UUID (string)
        const groupId = this.company.group_id; 
        
        console.log('Deleting company:', this.companyId);
        
        const response = await fetch(`/api/companies/${this.companyId}`, {
          method: 'DELETE',
          headers: {
            'Content-Type': 'application/json',
            'User-ID': user.id
          }
        });
        
        if (!response.ok) {
          const data = await response.json();
          this.error = data.message || 'Erro ao excluir a empresa';
          this.deletingCompany = false;
          this.showDeleteConfirmation = false;
          return;
        }
        
        console.log('Company deleted successfully');
        this.success = 'Empresa excluída com sucesso. Redirecionando...';
        this.deletingCompany = false;
        this.showDeleteConfirmation = false;
        
        // Redirecionar após 2 segundos para a página do grupo (usando UUID)
        setTimeout(() => {
          this.$router.push(`/groups/${groupId}`);
        }, 2000);
      } catch (error) {
        this.error = 'Erro ao conectar ao servidor';
        this.deletingCompany = false;
        this.showDeleteConfirmation = false;
        console.error('Error deleting company:', error);
      }
    }
  }
}
</script>

<style scoped>
/* Alerta para dispositivos móveis */
.mobile-warning {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: linear-gradient(135deg, #142C4D, #204578);
  color: white;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 20px;
  z-index: 9999;
}

.warning-icon {
  font-size: 50px;
  margin-bottom: 20px;
}

.mobile-warning h2 {
  font-size: 24px;
  margin-bottom: 15px;
}

.mobile-warning p {
  font-size: 16px;
  max-width: 280px;
}

/* Layout principal - versão desktop */
.home-layout {
  position: fixed;
  top: 100px;
  left: 50px;
  right: 50px;
  bottom: 30px;
  display: flex;
  gap: 20px; /* Espaçamento entre os containers */
}

/* Painel de conteúdo (visualmente à esquerda) */
.content-panel {
  width: calc(50% - 10px); /* 50% da largura menos metade do gap */
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
  animation: fade-in 0.8s ease-out;
  overflow: hidden;
}

/* Painel de arquivos (visualmente à direita) */
.files-panel {
  width: calc(50% - 10px); /* 50% da largura menos metade do gap */
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
  animation: fade-in 0.8s ease-out;
  overflow: hidden;
}

/* Container do conteúdo */
.content-wrapper {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 2rem;
  overflow-y: auto;
}

/* Cabeçalho da empresa */
.home-header {
  text-align: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #eaeaea;
  position: relative;
}

.home-header h1 {
  color: #142C4D;
  font-size: 2.2rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.welcome-text {
  color: #666;
  font-size: 1.1rem;
}

/* Cabeçalho de arquivos */
.files-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #eaeaea;
}

.files-header h2 {
  color: #142C4D;
  font-size: 1.8rem;
  font-weight: 600;
  margin: 0;
}

/* Seção de resumo no dashboard */
.dashboard-summary {
  margin-bottom: 1.5rem;
}

.dashboard-item {
  padding: 1.2rem;
  background-color: #f9f9f9;
  border-radius: 8px;
  margin-bottom: 1rem;
}

.dashboard-item h3 {
  color: #204578;
  font-size: 1.2rem;
  margin-bottom: 1rem;
}

.dashboard-item p {
  color: #666;
  font-size: 0.95rem;
}

/* Grid de informações */
.info-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.info-label {
  font-size: 0.9rem;
  font-weight: 600;
  color: #666;
}

.info-value {
  font-size: 1.1rem;
  color: #333;
}

.group-link {
  color: #204578;
  text-decoration: underline;
  cursor: pointer;
}

.group-link:hover {
  color: #142C4D;
}

/* Lista de arquivos */
.files-list {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
  margin-top: 1.2rem;
}

.file-item {
  background-color: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #eaeaea;
  padding: 1rem 1.2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: all 0.2s ease;
}

.file-item:hover {
  background-color: #e9ecef;
  transform: translateY(-2px);
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.08);
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

/* Formulário de upload */
.upload-form {
  background-color: white;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  border: 1px solid #eaeaea;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
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

.submit-btn {
  padding: 0.8rem 1.5rem;
  background: linear-gradient(to right, #142C4D, #204578);
  border: none;
  border-radius: 8px;
  color: white;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.submit-btn:hover:not(:disabled) {
  background: linear-gradient(to right, #1a3760, #2a5b9e);
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(20, 44, 77, 0.3);
}

.submit-btn:disabled {
  background: #c0c0c0;
  cursor: not-allowed;
}

/* Estados de loading, erro e sucesso */
.loading-indicator, .error-message, .empty-state, .success-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  text-align: center;
}

.loading-spinner {
  width: 30px;
  height: 30px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #204578;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 0.8rem;
}

.error-icon {
  width: 30px;
  height: 30px;
  background-color: #fee2e2;
  color: #b91c1c;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  margin-bottom: 0.8rem;
}

.success-icon {
  width: 30px;
  height: 30px;
  background-color: #d1fae5;
  color: #065f46;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  margin-bottom: 0.8rem;
}

.error-message p {
  color: #b91c1c;
}

.success-message p {
  color: #065f46;
}

.empty-state p {
  color: #666;
  font-style: italic;
}

.close-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.2rem;
  padding: 0 0.5rem;
  margin-left: auto;
  color: #b91c1c;
}

.close-btn.success {
  color: #065f46;
}

/* Botões de ação */
.quick-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 0;
  margin-top: auto;
}

.action-button {
  flex: 1;
  min-width: 150px;
  padding: 0.8rem;
  border: none;
  border-radius: 8px;
  color: white;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-button.admin {
  background: linear-gradient(to right, #142C4D, #204578);
}

.action-button.admin:hover {
  background: linear-gradient(to right, #1a3760, #2a5b9e);
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(20, 44, 77, 0.3);
}

.secondary-button {
  flex: 1;
  min-width: 150px;
  padding: 0.8rem;
  background: transparent;
  border: 2px solid #204578;
  border-radius: 8px;
  color: #204578;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.secondary-button:hover {
  background-color: rgba(32, 69, 120, 0.1);
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(20, 44, 77, 0.1);
}

/* Botão de exclusão */
.delete-btn {
  padding: 0.7rem 1.2rem;
  background: linear-gradient(to right, #991b1b, #b91c1c);
  border: none;
  border-radius: 8px;
  color: white;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.delete-btn:hover:not(:disabled) {
  background: linear-gradient(to right, #7f1d1d, #991b1b);
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(185, 28, 28, 0.3);
}

.delete-btn:disabled {
  background: #c0c0c0;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* Modal de confirmação de exclusão */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  animation: fade-in 0.3s ease;
}

.modal-container {
  width: 90%;
  max-width: 500px;
  background-color: white;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.3);
  animation: slide-in 0.4s ease;
}

@keyframes slide-in {
  0% { opacity: 0; transform: translateY(-30px); }
  100% { opacity: 1; transform: translateY(0); }
}

.modal-header {
  background-color: #f8f8f8;
  padding: 1.2rem 1.5rem;
  border-bottom: 1px solid #eaeaea;
}

.modal-header h3 {
  margin: 0;
  color: #333;
  font-size: 1.3rem;
}

.modal-body {
  padding: 1.5rem;
  text-align: center;
}

.modal-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.warning-text {
  color: #b91c1c;
  font-weight: 600;
  margin: 1rem 0;
}

.confirmation-input {
  margin-top: 1.5rem;
  text-align: left;
}

.confirmation-input label {
  display: block;
  margin-bottom: 0.5rem;
  font-size: 0.95rem;
  font-weight: 600;
}

.confirmation-input input {
  width: 100%;
  padding: 0.8rem;
  border: 2px solid #ddd;
  border-radius: 6px;
  font-size: 0.95rem;
  transition: all 0.2s ease;
}

.confirmation-input input:focus {
  border-color: #204578;
  outline: none;
  box-shadow: 0 0 0 3px rgba(32, 69, 120, 0.1);
}

.modal-footer {
  padding: 1.2rem 1.5rem;
  background-color: #f8f8f8;
  border-top: 1px solid #eaeaea;
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

.cancel-btn {
  padding: 0.8rem 1.5rem;
  background: transparent;
  border: 2px solid #6b7280;
  border-radius: 8px;
  color: #6b7280;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.cancel-btn:hover {
  background-color: rgba(107, 114, 128, 0.1);
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(107, 114, 128, 0.1);
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
@media (max-width: 1024px) {
  .home-layout {
    left: 20px;
    right: 20px;
  }
}

@media (max-width: 768px) {
  .home-layout {
    flex-direction: column;
    gap: 10px;
  }
  
  .content-panel, .files-panel {
    width: 100%;
  }

  .content-panel {
    height: 45%;
  }

  .files-panel {
    height: 55%;
  }
  
  .modal-container {
    width: 95%;
  }
}
</style>