<template>
    <div>
      <!-- Alerta para dispositivos móveis -->
      <div v-if="isMobileDevice" class="mobile-warning">
        <div class="warning-icon">⚠️</div>
        <h2>Acesso não recomendado</h2>
        <p>Este site não foi projetado para dispositivos móveis. Por favor, acesse através de um computador para uma melhor experiência.</p>
      </div>
  
      <!-- Conteúdo principal -->
      <div v-else class="home-layout">
        <!-- Painel de upload de arquivos (visualmente à esquerda) -->
        <div class="content-panel">
          <div class="content-wrapper">
            <div class="home-header">
              <h1>Upload de Arquivos</h1>
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
                  <h3>{{ company.name }}</h3>
                  <div class="info-details">
                    <p><span class="info-label">CNPJ:</span> {{ company.cnpj }}</p>
                    <p><span class="info-label">Grupo:</span> 
                      <a @click="goToGroupDetail(company.group_id)" class="group-link">
                        {{ groupName }}
                      </a>
                    </p>
                  </div>
                </div>
              </div>
  
              <!-- Upload de Arquivos -->
              <div v-if="isAdmin" class="dashboard-summary">
                <div class="dashboard-item">
                  <h3>Enviar Arquivo</h3>
                  <p>Adicione arquivos para esta empresa</p>
                  
                  <form @submit.prevent="uploadFile" class="company-form">
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
                    
                    <button 
                      type="submit" 
                      class="submit-btn" 
                      :disabled="uploading || !selectedFile"
                    >
                      <span v-if="uploading" class="loading-spinner-small"></span>
                      {{ uploading ? 'Enviando...' : 'Enviar Arquivo' }}
                    </button>
                  </form>
                </div>
              </div>
              
              <!-- Botões de ação -->
              <div class="quick-actions">
                <button class="secondary-button" @click="goToCompanyDetail">Voltar para Detalhes da Empresa</button>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Painel de visualização de arquivos (visualmente à direita) -->
        <div class="content-panel">
          <div class="content-wrapper">
            <div class="home-header">
              <h1>Arquivos Disponíveis</h1>
            </div>
  
            <div v-if="loading" class="loading-indicator">
              <div class="loading-spinner"></div>
              <p>Carregando arquivos...</p>
            </div>
  
            <div v-else>
              <!-- Filtro de Arquivos -->
              <div class="dashboard-summary">
                <div class="dashboard-item">
                  <h3>Buscar Arquivos</h3>
                  <div class="filter-controls">
                    <div class="form-group">
                      <input 
                        type="text" 
                        v-model="searchQuery" 
                        placeholder="Buscar por nome de arquivo" 
                        class="search-input"
                      >
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Lista de Arquivos -->
              <div class="dashboard-summary">
                <div class="dashboard-item">
                  <h3>Arquivos ({{ filteredFiles.length }})</h3>
                  
                  <div v-if="!files || files.length === 0" class="empty-state">
                    <p>Nenhum arquivo foi adicionado a esta empresa.</p>
                  </div>
                  <div v-else-if="filteredFiles.length === 0" class="empty-state">
                    <p>Nenhum arquivo corresponde à busca.</p>
                  </div>
                  <div v-else class="files-list">
                    <div v-for="file in filteredFiles" :key="file.id" class="file-item">
                      <div class="file-info">
                        <div :class="['file-icon', getFileIconClass(file.file_type)]">
                          {{ file.file_type.toUpperCase() }}
                        </div>
                        <div class="file-details">
                          <div class="file-name">{{ file.filename }}</div>
                          <div class="file-description" v-if="file.description">{{ file.description }}</div>
                          <div class="file-meta">
                            <span class="file-category" v-if="file.category">{{ file.category }}</span>
                            <span class="file-date">Enviado em {{ formatDate(file.uploaded_at) }}</span>
                          </div>
                        </div>
                      </div>
                      <div class="file-actions">
                        <button class="download-btn" @click="downloadFile(file.id)">Download</button>
                        <button v-if="isAdmin" class="delete-btn small" @click="confirmDeleteFile(file)">Excluir</button>
                      </div>
                    </div>
                  </div>
                  
                  <!-- Paginação -->
                  <div v-if="files.length > itemsPerPage" class="pagination">
                    <button 
                      :disabled="currentPage === 1" 
                      @click="currentPage--" 
                      class="pagination-btn"
                    >
                      &laquo; Anterior
                    </button>
                    <span class="page-info">Página {{ currentPage }} de {{ totalPages }}</span>
                    <button 
                      :disabled="currentPage === totalPages" 
                      @click="currentPage++" 
                      class="pagination-btn"
                    >
                      Próximo &raquo;
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
  
      <!-- Modal de Confirmação de Exclusão de Arquivo -->
      <div v-if="fileToDelete" class="modal-overlay">
        <div class="modal-container">
          <div class="modal-header">
            <h3>Confirmação de Exclusão</h3>
          </div>
          <div class="modal-body">
            <div class="warning-icon modal-icon">⚠️</div>
            <p>Você está prestes a excluir o arquivo <strong>{{ fileToDelete.filename }}</strong>.</p>
            <p class="warning-text">Esta ação não pode ser desfeita!</p>
          </div>
          <div class="modal-footer">
            <button class="cancel-btn" @click="fileToDelete = null">Cancelar</button>
            <button 
              class="delete-btn"
              :disabled="deletingFile"
              @click="deleteFile"
            >
              {{ deletingFile ? 'Excluindo...' : 'Confirmar Exclusão' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: 'CompanyFilesView',
    data() {
      return {
        companyId: null,
        company: {},
        files: [],
        loading: true,
        error: '',
        success: '',
        isAdmin: false,
        groupName: '',
        isMobileDevice: false,
        
        // Upload de arquivos
        selectedFile: null,
        uploading: false,
  
        // Exclusão de arquivo
        fileToDelete: null,
        deletingFile: false,
        
        // Filtro e paginação
        searchQuery: '',
        currentPage: 1,
        itemsPerPage: 10
      }
    },
    computed: {
      filteredFiles() {
        let result = [...this.files];
        
        // Aplicar filtro de texto
        if (this.searchQuery.trim()) {
          const query = this.searchQuery.toLowerCase();
          result = result.filter(file => 
            file.filename.toLowerCase().includes(query) || 
            (file.description && file.description.toLowerCase().includes(query))
          );
        }
        
        // Ordenar por mais recentes primeiro (mantendo a ordenação padrão)
        result.sort((a, b) => new Date(b.uploaded_at) - new Date(a.uploaded_at));
        
        // Paginação
        const startIndex = (this.currentPage - 1) * this.itemsPerPage;
        const endIndex = startIndex + this.itemsPerPage;
        return result.slice(startIndex, endIndex);
      },
      totalPages() {
        return Math.ceil(this.files.length / this.itemsPerPage);
      }
    },
    created() {
      this.checkDeviceType();
      this.checkAccess();
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
    watch: {
      searchQuery() {
        this.currentPage = 1; // Reset para primeira página quando buscar
      }
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
          
          // Buscar nome do grupo se necessário
          if (this.company.group_id) {
            await this.fetchGroupName();
          }
          
          // Buscar arquivos
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
          
          if (!response.ok) {
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
          this.success = 'Arquivo enviado com sucesso!';
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
      confirmDeleteFile(file) {
        this.fileToDelete = file;
      },
      async deleteFile() {
        if (!this.fileToDelete) return;
        
        try {
          this.deletingFile = true;
          
          const userStr = localStorage.getItem('user');
          if (!userStr) {
            this.$router.push('/login');
            return;
          }
          
          const user = JSON.parse(userStr);
          
          const response = await fetch(`/api/files/${this.fileToDelete.id}`, {
            method: 'DELETE',
            headers: {
              'Content-Type': 'application/json',
              'User-ID': user.id
            }
          });
          
          if (!response.ok) {
            const data = await response.json();
            this.error = data.message || 'Erro ao excluir arquivo';
            this.deletingFile = false;
            this.fileToDelete = null;
            return;
          }
          
          this.success = 'Arquivo excluído com sucesso!';
          
          // Atualizar a lista de arquivos
          this.files = this.files.filter(file => file.id !== this.fileToDelete.id);
          
          this.deletingFile = false;
          this.fileToDelete = null;
        } catch (error) {
          this.error = 'Erro ao conectar ao servidor';
          this.deletingFile = false;
          this.fileToDelete = null;
          console.error('Error deleting file:', error);
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
      goToCompanyDetail() {
        this.$router.push(`/companies/${this.companyId}`);
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
  
  /* Painéis de conteúdo */
  .content-panel {
    width: 50%; /* 50% da largura menos metade do gap */
    background-color: white;
    border-radius: 12px;
    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
    animation: fade-in 0.8s ease-out;
    overflow: hidden;
  }
  
  /* Container do conteúdo para o painel de conteúdo */
  .content-wrapper {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    padding: 2rem;
    overflow-y: auto;
  }
  
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
    margin-bottom: 0.5rem;
  }
  
  .dashboard-item p {
    color: #666;
    font-size: 0.95rem;
    margin-bottom: 0.8rem;
  }
  
  .info-details {
    margin-top: 0.8rem;
    color: #555;
    font-size: 0.95rem;
  }
  
  .info-details p {
    margin-bottom: 0.5rem;
  }
  
  .info-label {
    font-weight: 600;
    color: #333;
    margin-right: 0.3rem;
  }
  
  .group-link {
    color: #204578;
    text-decoration: underline;
    cursor: pointer;
  }
  
  .group-link:hover {
    color: #142C4D;
  }
  
  /* Formulários */
  .company-form {
    margin-top: 1rem;
  }
  
  .form-group {
    margin-bottom: 1.2rem;
  }
  
  .form-group label {
    display: block;
    margin-bottom: 0.6rem;
    font-size: 0.95rem;
    font-weight: 600;
    color: #333;
  }
  
  .form-group input,
  .form-group select {
    width: 100%;
    padding: 0.8rem;
    border: 1px solid #ddd;
    border-radius: 6px;
    font-size: 1rem;
  }
  
  .form-group input:focus,
  .form-group select:focus {
    outline: none;
    border-color: #204578;
    box-shadow: 0 0 0 2px rgba(32, 69, 120, 0.2);
  }
  
  .file-types {
    font-size: 0.85rem;
    color: #666;
    margin-top: 0.5rem;
  }
  
  /* Lista de arquivos */
  .files-list {
    margin-top: 1rem;
  }
  
  .file-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem;
    border: 1px solid #eaeaea;
    border-radius: 6px;
    margin-bottom: 0.8rem;
    background-color: white;
    transition: all 0.2s ease;
  }
  
  .file-item:hover {
    border-color: #d1d5db;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
  }
  
  .file-info {
    display: flex;
    align-items: center;
    flex: 1;
  }
  
  .file-icon {
    width: 45px;
    height: 45px;
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.7rem;
    font-weight: 700;
    color: white;
    margin-right: 1rem;
  }
  
  .pdf-file {
    background-color: #dc2626;
  }
  
  .excel-file, .csv-file {
    background-color: #16a34a;
  }
  
  .generic-file {
    background-color: #6b7280;
  }
  
  .file-details {
    flex: 1;
    min-width: 0; /* Para permitir truncamento */
  }
  
  .file-name {
    font-weight: 600;
    font-size: 1rem;
    color: #374151;
    margin-bottom: 0.2rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  
  .file-description {
    font-size: 0.9rem;
    color: #6b7280;
    margin-bottom: 0.2rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  
  .file-meta {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    font-size: 0.8rem;
    color: #6b7280;
  }
  
  .file-category {
    background-color: #e5e7eb;
    padding: 0.2rem 0.5rem;
    border-radius: 4px;
    font-size: 0.75rem;
  }
  
  .file-actions {
    display: flex;
    gap: 0.5rem;
  }
  
  /* Controles de filtro */
  .filter-controls {
    margin-top: 0.8rem;
  }
  
  .search-input {
    width: 100%;
    padding: 0.8rem;
    border: 1px solid #ddd;
    border-radius: 6px;
    font-size: 0.95rem;
    margin-bottom: 0.8rem;
  }

/* Paginação */
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 1.5rem;
  gap: 1rem;
}

.pagination-btn {
  padding: 0.5rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background-color: white;
  color: #374151;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s ease;
}

.pagination-btn:hover:not(:disabled) {
  background-color: #f3f4f6;
  border-color: #9ca3af;
}

.pagination-btn:disabled {
  color: #9ca3af;
  border-color: #e5e7eb;
  cursor: not-allowed;
}

.page-info {
  color: #6b7280;
  font-size: 0.9rem;
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

.loading-spinner-small {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid #ffffff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-right: 8px;
  display: inline-block;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message, .success-message {
  flex-direction: row;
  justify-content: flex-start;
  background-color: #fdeded;
  border-left: 4px solid #ef4444;
  color: #b91c1c;
  padding: 1rem;
  border-radius: 6px;
  margin-bottom: 1.5rem;
  position: relative;
}

.success-message {
  background-color: #ecfdf5;
  border-left: 4px solid #10b981;
  color: #047857;
}

.error-icon, .success-icon {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background-color: #ef4444;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  margin-right: 1rem;
}

.success-icon {
  background-color: #10b981;
}

.close-btn {
  position: absolute;
  right: 10px;
  top: 10px;
  background: none;
  border: none;
  font-size: 1.2rem;
  color: #b91c1c;
  cursor: pointer;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn.success {
  color: #047857;
}

.empty-state {
  text-align: center;
  color: #6b7280;
  background-color: #f9fafb;
  padding: 2rem;
  border-radius: 8px;
  border: 1px dashed #d1d5db;
}

/* Botões */
.submit-btn, .secondary-button, .download-btn, .delete-btn {
  padding: 0.8rem 1.5rem;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.submit-btn {
  background-color: #204578;
  color: white;
  border: none;
}

.submit-btn:hover:not(:disabled) {
  background-color: #142C4D;
}

.submit-btn:disabled {
  background-color: #9ca3af;
  cursor: not-allowed;
}

.secondary-button {
  background-color: white;
  color: #204578;
  border: 1px solid #204578;
}

.secondary-button:hover {
  background-color: #f8f9fa;
  color: #142C4D;
}

.download-btn {
  background-color: #204578;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
}

.download-btn:hover {
  background-color: #142C4D;
}

.delete-btn {
  background-color: #ef4444;
  color: white;
  border: none;
}

.delete-btn.small {
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
}

.delete-btn:hover:not(:disabled) {
  background-color: #b91c1c;
}

.delete-btn:disabled {
  background-color: #f87171;
  cursor: not-allowed;
}

/* Modal de confirmação */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.modal-container {
  width: 90%;
  max-width: 500px;
  background-color: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  animation: modal-appear 0.3s ease-out;
}

@keyframes modal-appear {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.modal-header {
  background-color: #f9fafb;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h3 {
  margin: 0;
  color: #111827;
  font-size: 1.2rem;
}

.modal-body {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.modal-body p {
  color: #4b5563;
  margin-bottom: 0.5rem;
  text-align: center;
}

.warning-text {
  color: #ef4444;
  font-weight: 600;
}

.modal-icon {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.modal-footer {
  background-color: #f9fafb;
  padding: 1rem 1.5rem;
  display: flex;
  justify-content: flex-end;
  gap: 0.8rem;
  border-top: 1px solid #e5e7eb;
}

.cancel-btn {
  padding: 0.6rem 1.2rem;
  background-color: white;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  color: #374151;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.cancel-btn:hover {
  background-color: #f3f4f6;
  border-color: #9ca3af;
}

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}
</style>