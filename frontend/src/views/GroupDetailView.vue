<template>
  <div class="store-layout">
    <div class="store-container">
      <div class="store-content">
        <div class="page-header">
          <h1>{{ group.name }}</h1>
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
              <button v-if="isAdmin" class="action-button" @click="toggleNewCompanyForm">
                {{ showNewCompanyForm ? 'Cancelar' : 'Nova Empresa' }}
              </button>
            </div>
            
            <!-- Caixa de busca para empresas -->
            <div class="search-container">
              <div class="search-box">
                <input 
                  type="text" 
                  v-model="searchQuery" 
                  placeholder="Pesquisar empresas..."
                  class="search-input"
                >
                <span class="search-icon">🔍</span>
              </div>
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
            
            <div v-else-if="filteredCompanies.length === 0" class="empty-state">
              <p>Nenhuma empresa encontrada com esse nome.</p>
            </div>

            <div v-else class="companies-grid">
              <div 
                v-for="company in filteredCompanies" 
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
      creatingCompany: false,
      searchQuery: ''
    }
  },
  computed: {
    filteredCompanies() {
      if (!this.group.companies) return [];
      
      if (!this.searchQuery) {
        return this.group.companies;
      }
      
      const query = this.searchQuery.toLowerCase();
      return this.group.companies.filter(company => 
        company.name.toLowerCase().includes(query) || 
        company.cnpj.toLowerCase().includes(query)
      );
    }
  },
  created() {
    this.checkAccess();
    this.groupId = parseInt(this.$route.params.id);
    if (isNaN(this.groupId)) {
      console.error('ID de grupo inválido:', this.$route.params.id);
      this.error = 'ID de grupo inválido';
      this.loading = false;
      return;
    }
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
    toggleNewCompanyForm() {
      this.showNewCompanyForm = !this.showNewCompanyForm;
      if (!this.showNewCompanyForm) {
        // Reset form when closing
        this.newCompany = {
          name: '',
          cnpj: ''
        };
      }
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
        console.log('Fetching data for group:', this.groupId);
        
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
        console.log('Group data loaded:', this.group);
        this.loading = false;
      } catch (error) {
        this.error = 'Erro ao conectar ao servidor';
        this.loading = false;
        console.error('Error fetching group data:', error);
      }
    },
    async createCompany() {
      try {
        console.log('Creating company...');
        if (!this.newCompany.name || !this.newCompany.cnpj) {
          this.error = 'Preencha todos os campos obrigatórios';
          return;
        }
        
        this.creatingCompany = true;
        const userStr = localStorage.getItem('user');
        if (!userStr) {
          this.$router.push('/login');
          return;
        }
        
        const user = JSON.parse(userStr);
        console.log('Sending request to create company in group:', this.groupId);
        console.log('Company data:', this.newCompany);
        
        const response = await fetch(`/api/groups/${this.groupId}/companies`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'User-ID': user.id
          },
          body: JSON.stringify(this.newCompany)
        });
        
        const data = await response.json();
        
        if (!response.ok) {
          this.error = data.message || 'Erro ao criar empresa';
          this.creatingCompany = false;
          return;
        }
        
        console.log('Company created successfully');
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
/* Layout básico ajustado para as margens específicas, sem barra de rolagem na página principal */
.store-layout {
  width: 100%;
  height: 100vh;
  overflow: hidden;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #142C4D, #204578);
}

.store-container {
  position: absolute;
  top: 110px;
  left: 30px;
  right: 30px;
  bottom: 30px;
  overflow-y: auto;
  display: flex;
  justify-content: center;
}

.store-content {
  width: 100%;
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

/* Caixa de pesquisa */
.search-container {
  margin-bottom: 1.5rem;
}

.search-box {
  position: relative;
  width: 100%;
}

.search-input {
  width: 100%;
  padding: 12px 40px 12px 15px;
  border: 2px solid #e1e1e1;
  border-radius: 8px;
  font-size: 1rem;
  color: #333;
  transition: all 0.3s ease;
  background-color: #f9f9f9;
}

.search-input:focus {
  border-color: #204578;
  box-shadow: 0 0 0 3px rgba(32, 69, 120, 0.15);
  outline: none;
  background-color: #fff;
}

.search-icon {
  position: absolute;
  right: 15px;
  top: 50%;
  transform: translateY(-50%);
  color: #666;
  font-size: 1.2rem;
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

.success-alert {
  padding: 1rem 1.5rem;
  border-radius: 8px;
  margin-bottom: 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 1rem;
  background-color: #d1fae5;
  color: #065f46;
  animation: fade-in 0.3s ease;
}

.close-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.3rem;
  padding: 0 0.5rem;
}

.close-btn.error {
  color: #b91c1c;
}

.close-btn.success {
  color: #065f46;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 0;
  text-align: center;
}

.loading-spinner {
  width: 48px;
  height: 48px;
  border: 5px solid rgba(32, 69, 120, 0.1);
  border-top: 5px solid #204578;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1.5rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes fade-in {
  0% { opacity: 0; transform: translateY(10px); }
  100% { opacity: 1; transform: translateY(0); }
}

.section-card {
  background-color: #f9f9f9;
  border-radius: 8px;
  padding: 1.8rem;
  margin-bottom: 2rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.section-card h2 {
  color: #204578;
  font-size: 1.5rem;
  margin-bottom: 1.5rem;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
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

.manage-btn {
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

.manage-btn:hover {
  background: linear-gradient(to right, #1a3760, #2a5b9e);
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(20, 44, 77, 0.3);
}

.new-company-form {
  background-color: white;
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.6rem;
  font-size: 1rem;
  font-weight: 600;
  color: #333;
}

.form-group input {
  width: 100%;
  padding: 0.8rem 1rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 0.95rem;
  background-color: white;
  transition: all 0.2s ease;
}

.form-group input:focus {
  border-color: #204578;
  outline: none;
  box-shadow: 0 0 0 3px rgba(32, 69, 120, 0.1);
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

.companies-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-top: 1.5rem;
}

.company-card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  transition: all 0.3s ease;
  cursor: pointer;
}

.company-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

.company-header {
  padding: 1.2rem;
  background-color: #204578;
  color: white;
}

.company-header h3 {
  font-size: 1.2rem;
  font-weight: 600;
  margin: 0;
}

.company-body {
  padding: 1.2rem;
}

.company-info-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.8rem;
}

.company-info-row:last-child {
  margin-bottom: 0;
}

.company-footer {
  padding: 1rem;
  background-color: #f5f5f5;
  text-align: center;
}

.detail-btn {
  padding: 0.6rem 1.2rem;
  background-color: transparent;
  border: 1.5px solid #204578;
  border-radius: 6px;
  color: #204578;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.detail-btn:hover {
  background-color: #204578;
  color: white;
}

.user-selection-container {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
  align-items: flex-end;
}

select {
  width: 100%;
  padding: 0.8rem 1rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 0.95rem;
  background-color: white;
  cursor: pointer;
  transition: border 0.2s ease;
  appearance: auto; /* Use native select appearance */
}

select:focus {
  border-color: #204578;
  outline: none;
  box-shadow: 0 0 0 3px rgba(32, 69, 120, 0.1);
}

.action-button {
  padding: 0.8rem 1.2rem;
  background: linear-gradient(to right, #142C4D, #204578);
  border: none;
  border-radius: 8px;
  color: white;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  height: fit-content;
}

.action-button:hover {
  background: linear-gradient(to right, #1a3760, #2a5b9e);
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(20, 44, 77, 0.3);
}

.action-button:disabled {
  background: #c0c0c0;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.empty-state {
  padding: 2rem;
  text-align: center;
  color: #666;
  font-style: italic;
  background-color: #f5f5f5;
  border-radius: 8px;
  margin-top: 1rem;
}

.group-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 2rem;
}

.secondary-button {
  padding: 0.8rem 1.5rem;
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

/* Ajustes de responsividade para o layout reposicionado */
@media (max-width: 1024px) {
  .store-container {
    top: 110px;
    left: 20px;
    right: 20px;
    bottom: 20px;
  }
  
  .store-content {
    padding: 2rem;
  }
  
  .companies-grid {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  }
}

@media (max-width: 768px) {
  .store-container {
    top: 100px;
    left: 15px;
    right: 15px;
    bottom: 15px;
  }
  
  .store-content {
    padding: 1.5rem;
  }
  
  .page-header h1 {
    font-size: 1.8rem;
  }
  
  .companies-grid {
    grid-template-columns: 1fr;
  }
  
  .section-card {
    padding: 1.5rem;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
}

</style>