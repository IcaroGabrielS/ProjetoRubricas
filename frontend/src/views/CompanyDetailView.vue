<template>
    <div class="store-layout">
      <div class="store-container">
        <div class="store-content">
          <div class="page-header">
            <h1>{{ group.name }}</h1>
            <p class="subtitle">Detalhes e empresas do grupo</p>
          </div>
          
          <div v-if="error" class="error-alert">
            <span>{{ error }}</span>
            <button class="close-btn" @click="error = ''" aria-label="Fechar">&times;</button>
          </div>
  
          <div v-if="loading" class="loading-container">
            <div class="loading-spinner"></div>
            <p>Carregando informações do grupo...</p>
          </div>
  
          <div v-else>
            <!-- Informações do Grupo -->
            <div class="section-card">
              <h2>Informações Gerais</h2>
              <div class="info-grid">
                <div class="info-item">
                  <div class="info-label">Código do Grupo:</div>
                  <div class="info-value">{{ group.id }}</div>
                </div>
                <div class="info-item">
                  <div class="info-label">Criado em:</div>
                  <div class="info-value">{{ formatDate(group.created_at) }}</div>
                </div>
                <div v-if="isAdmin" class="info-item">
                  <div class="info-label">Gerenciar Acesso:</div>
                  <div class="info-value">
                    <button class="manage-btn" @click="manageAccess(group.id)">Permissões de Usuários</button>
                  </div>
                </div>
              </div>
            </div>
  
            <!-- Lista de Empresas -->
            <div class="section-card">
              <div class="section-header">
                <h2>Empresas</h2>
                <button v-if="isAdmin" class="action-button" @click="showNewCompanyForm = !showNewCompanyForm">
                  {{ showNewCompanyForm ? 'Cancelar' : 'Nova Empresa' }}
                </button>
              </div>
  
              <!-- Formulário de Nova Empresa -->
              <div v-if="showNewCompanyForm && isAdmin" class="new-company-form">
                <form @submit.prevent="createCompany">
                  <div class="form-group">
                    <label for="companyName">Nome da Empresa:</label>
                    <input 
                      type="text" 
                      id="companyName" 
                      v-model="newCompany.name" 
                      required 
                      placeholder="Nome da Empresa"
                    >
                  </div>
                  <div class="form-group">
                    <label for="companyCNPJ">CNPJ:</label>
                    <input 
                      type="text" 
                      id="companyCNPJ" 
                      v-model="newCompany.cnpj" 
                      required 
                      placeholder="XX.XXX.XXX/XXXX-XX"
                    >
                  </div>
                  <button type="submit" class="submit-btn" :disabled="creatingCompany">
                    {{ creatingCompany ? 'Criando...' : 'Criar Empresa' }}
                  </button>
                </form>
              </div>
  
              <div v-if="!group.companies || group.companies.length === 0" class="empty-state">
                <p>Nenhuma empresa foi adicionada a este grupo.</p>
              </div>
  
              <div v-else class="companies-grid">
                <div 
                  v-for="company in group.companies" 
                  :key="company.id" 
                  class="company-card"
                  @click="goToCompanyDetail(company.id)"
                >
                  <div class="company-header">
                    <h3>{{ company.name }}</h3>
                  </div>
                  <div class="company-body">
                    <div class="company-info-row">
                      <span class="info-label">CNPJ:</span>
                      <span class="info-value">{{ company.cnpj }}</span>
                    </div>
                    <div class="company-info-row">
                      <span class="info-label">Criado em:</span>
                      <span class="info-value">{{ formatDate(company.created_at) }}</span>
                    </div>
                  </div>
                  <div class="company-footer">
                    <button class="detail-btn">Ver Detalhes</button>
                  </div>
                </div>
              </div>
            </div>
  
            <div class="group-actions">
              <button class="secondary-button" @click="goBack">Voltar para Home</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: 'GroupDetailView',
    data() {
      return {
        groupId: null,
        group: {},
        loading: true,
        error: '',
        isAdmin: false,
        showNewCompanyForm: false,
        newCompany: {
          name: '',
          cnpj: ''
        },
        creatingCompany: false
      }
    },
    created() {
      this.checkAccess();
      this.groupId = this.$route.params.name;
      this.fetchGroupData();
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
      async fetchGroupData() {
        try {
          this.loading = true;
          const userStr = localStorage.getItem('user');
          if (!userStr) {
            this.$router.push('/login');
            return;
          }
          
          const user = JSON.parse(userStr);
          
          const response = await fetch(`/api/groups/${this.groupId}`, {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json',
              'User-ID': user.id
            }
          });
          
          if (!response.ok) {
            const data = await response.json();
            this.error = data.message || 'Erro ao carregar dados do grupo';
            this.loading = false;
            return;
          }
          
          const data = await response.json();
          this.group = data.group;
          this.loading = false;
        } catch (error) {
          this.error = 'Erro ao conectar ao servidor';
          this.loading = false;
          console.error('Error fetching group data:', error);
        }
      },
      async createCompany() {
        try {
          this.creatingCompany = true;
          const userStr = localStorage.getItem('user');
          if (!userStr) {
            this.$router.push('/login');
            return;
          }
          
          const user = JSON.parse(userStr);
          
          const response = await fetch(`/api/groups/${this.groupId}/companies`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'User-ID': user.id
            },
            body: JSON.stringify(this.newCompany)
          });
          
          if (!response.ok) {
            const data = await response.json();
            this.error = data.message || 'Erro ao criar empresa';
            this.creatingCompany = false;
            return;
          }
          
          // Limpar o formulário e atualizar os dados do grupo
          this.newCompany = {
            name: '',
            cnpj: ''
          };
          this.showNewCompanyForm = false;
          
          await this.fetchGroupData();
          this.creatingCompany = false;
        } catch (error) {
          this.error = 'Erro ao conectar ao servidor';
          this.creatingCompany = false;
          console.error('Error creating company:', error);
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
      manageAccess(groupId) {
        this.$router.push(`/groups/manage/${groupId}`);
      },
      goBack() {
        this.$router.push('/');
      },
      goToCompanyDetail(companyId) {
        this.$router.push(`/companies/${companyId}`);
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
}

.store-content {
  width: 100%;
  min-width: 1200px;
  max-width: 85%;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
  padding: 2.5rem 3rem;
  animation: fade-in 0.6s ease-out;
  overflow-y: auto;
  max-height: calc(100vh - 4rem);
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
  margin-top: 1rem;
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
    min-width: 95%;
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