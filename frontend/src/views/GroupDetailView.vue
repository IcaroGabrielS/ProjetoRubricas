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
          <h1>{{ group.name }}</h1>
          <div class="header-info">
            <div class="date-info">{{ currentDateTime }}</div>
            <div class="user-info">{{ currentUser }}</div>
          </div>
        </div>
        
        <div class="store-info-card">
          <div class="card-header">
            <h2>Informações do Grupo</h2>
          </div>
          
          <div class="info-grid">
            <div class="info-item">
              <div class="info-label">
                <i class="info-icon">🏢</i>
                Nome do Grupo
              </div>
              <div class="info-value">{{ group.name }}</div>
            </div>
            
            <div class="info-item">
              <div class="info-label">
                <i class="info-icon">🗓️</i>
                Data de Criação
              </div>
              <div class="info-value">{{ formatDate(group.created_at) }}</div>
            </div>
          </div>
        </div>
        
        <div class="file-section">
          <div class="file-section-header">
            <h2>Empresas do Grupo</h2>
            <div class="file-count" v-if="group.companies">
              {{ group.companies.length }} empresa(s)
            </div>
          </div>
          
          <div v-if="isAdmin" class="upload-card">
            <div class="upload-header">
              <h3>Adicionar Empresa</h3>
            </div>
            
            <form @submit.prevent="addCompany" class="upload-form">
              <div class="form-group">
                <label for="companyName" class="file-label">
                  Nome da Empresa
                  <input 
                    type="text" 
                    id="companyName" 
                    v-model="newCompany.name" 
                    required
                    placeholder="Digite o nome da empresa"
                  >
                </label>
              </div>
              
              <div class="form-group">
                <label for="companyCnpj" class="file-label">
                  CNPJ
                  <input 
                    type="text" 
                    id="companyCnpj" 
                    v-model="newCompany.cnpj" 
                    required
                    placeholder="Digite o CNPJ da empresa"
                  >
                </label>
              </div>
              
              <button type="submit" :disabled="companyLoading" class="upload-btn">
                <span v-if="companyLoading" class="loading-indicator small"></span>
                {{ companyLoading ? 'Adicionando...' : 'Adicionar Empresa' }}
              </button>
            </form>
            
            <div v-if="companyError" class="error-message">
              <div class="error-icon small">!</div>
              <p>{{ companyError }}</p>
              <button class="close-btn" @click="companyError = null" aria-label="Fechar">×</button>
            </div>
            
            <div v-if="companySuccess" class="success-message">
              <div class="success-icon small">✓</div>
              <p>{{ companySuccess }}</p>
            </div>
          </div>
          
          <div class="files-card">
            <div class="files-header">
              <h3>Empresas Disponíveis</h3>
            </div>
            
            <div v-if="group.companies && group.companies.length === 0" class="no-files">
              <div class="empty-icon">📂</div>
              <p>Nenhuma empresa disponível para este grupo.</p>
            </div>
            
            <div v-else class="files-table-container">
              <table class="files-table">
                <thead>
                  <tr>
                    <th>Nome da Empresa</th>
                    <th>CNPJ</th>
                    <th>Data de Criação</th>
                    <th>Ação</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="company in group.companies" :key="company.id">
                    <td>{{ company.name }}</td>
                    <td>{{ company.cnpj }}</td>
                    <td>{{ formatDate(company.created_at) }}</td>
                    <td>
                      <a :href="`/companies/${company.id}`" class="view-btn">
                        Ver Detalhes
                      </a>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
        
        <div class="actions">
          <router-link to="/" class="back-btn">
            <span class="back-icon">←</span>
            Voltar para Home
          </router-link>
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
      group: {
        id: null,
        name: '',
        created_at: null,
        created_by: null,
        companies: []
      },
      loading: true,
      error: null,
      isAdmin: false,
      newCompany: {
        name: '',
        cnpj: ''
      },
      companyLoading: false,
      companyError: null,
      companySuccess: null,
      currentDateTime: new Date().toLocaleString(),
      currentUser: 'IcaroGabrielS'
    }
  },
  created() {
    this.checkAdmin();
    this.fetchGroupDetails();
    this.updateDateTime();
  },
  methods: {
    checkAdmin() {
      const userStr = localStorage.getItem('user');
      if (userStr) {
        const user = JSON.parse(userStr);
        this.isAdmin = user.is_admin === true;
      }
    },
    async fetchGroupDetails() {
      try {
        const userStr = localStorage.getItem('user');
        if (!userStr) {
          this.$router.push('/login');
          return;
        }
        
        const user = JSON.parse(userStr);
        const groupId = this.$route.params.name;
        
        const response = await fetch(`/api/groups/${groupId}`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'User-ID': user.id
          }
        });
        
        const data = await response.json();
        
        if (!response.ok) {
          this.error = data.message || 'Erro ao carregar detalhes do grupo';
          this.loading = false;
          return;
        }
        
        this.group = data.group;
        this.loading = false;
      } catch (error) {
        this.error = 'Erro ao conectar ao servidor';
        this.loading = false;
        console.error('Error fetching group details:', error);
      }
    },
    async addCompany() {
      if (!this.newCompany.name || !this.newCompany.cnpj) {
        this.companyError = 'Por favor, preencha todos os campos.';
        return;
      }
      
      this.companyLoading = true;
      this.companyError = null;
      this.companySuccess = null;
      
      try {
        const userStr = localStorage.getItem('user');
        if (!userStr) {
          this.$router.push('/login');
          return;
        }
        
        const user = JSON.parse(userStr);
        
        const response = await fetch(`/api/groups/${this.group.id}/companies`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'User-ID': user.id
          },
          body: JSON.stringify(this.newCompany)
        });
        
        const data = await response.json();
        
        if (!response.ok) {
          this.companyError = data.message || 'Erro ao adicionar empresa';
          this.companyLoading = false;
          return;
        }
        
        this.companySuccess = 'Empresa adicionada com sucesso!';
        this.companyLoading = false;
        this.newCompany = {
          name: '',
          cnpj: ''
        };
        
        // Atualiza a lista de empresas
        this.fetchGroupDetails();
      } catch (error) {
        this.companyError = 'Erro ao conectar ao servidor';
        this.companyLoading = false;
        console.error('Error adding company:', error);
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
    updateDateTime() {
      setInterval(() => {
        this.currentDateTime = new Date().toLocaleString();
      }, 1000);
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

.store-detail-container {
  margin-top: 60px; /* Altura da navbar */
  height: calc(100vh - 60px); /* Altura total da viewport menos a altura da navbar */
  display: flex;
  align-items: flex-start;
  justify-content: center;
  font-family: 'Sarala', sans-serif;
  padding: 20px;
  overflow-y: auto; /* Habilita a rolagem vertical */
}

.store-detail-content {
  width: 1200px; /* Largura fixa para desktop */
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
  padding: 2rem;
  animation: fade-in 0.8s ease-out;
  overflow: visible; /* Mantém o conteúdo visível */
  margin-bottom: 20px; /* Espaço no final */
}

/* Estado de carregamento */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 1rem;
  text-align: center;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 5px solid #f3f3f3;
  border-top: 5px solid #204578;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

/* Estado de erro */
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 1rem;
  text-align: center;
}

.error-icon {
  width: 60px;
  height: 60px;
  background-color: #fee2e2;
  color: #b91c1c;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 2rem;
  margin-bottom: 1rem;
}

.error-state p {
  color: #b91c1c;
  font-weight: 500;
  font-size: 1.1rem;
}

/* Cabeçalho da página */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #204578;
}

.page-header h1 {
  color: #142C4D;
  font-size: 2rem;
  font-weight: 700;
  margin: 0;
}

.header-info {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  font-size: 0.9rem;
}

.date-info {
  color: #666;
  margin-bottom: 0.2rem;
}

.user-info {
  color: #142C4D;
  font-weight: 600;
}

/* Card de informações da loja */
.store-info-card {
  background: linear-gradient(to right bottom, #ffffff, #f8f9fa);
  border-radius: 10px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  margin-bottom: 2rem;
}

.card-header {
  background: linear-gradient(to right, #142C4D, #204578);
  padding: 1rem 1.5rem;
}

.card-header h2 {
  color: white;
  font-size: 1.4rem;
  font-weight: 600;
  margin: 0;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr); /* Sempre duas colunas para desktop */
  gap: 1.5rem;
  padding: 1.5rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.info-label {
  display: flex;
  align-items: center;
  font-weight: 600;
  color: #495057;
  font-size: 0.95rem;
}

.info-icon {
  margin-right: 0.5rem;
  font-style: normal;
}

.info-value {
  font-size: 1.1rem;
  color: #333;
  padding: 0.5rem;
  background-color: #f8f9fa;
  border-radius: 5px;
  border-left: 3px solid #204578;
}

/* Seção de arquivos */
.file-section {
  margin-top: 2rem;
}

.file-section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.file-section-header h2 {
  color: #142C4D;
  font-size: 1.6rem;
  font-weight: 700;
  margin: 0;
}

.file-count {
  background-color: #e9ecef;
  color: #495057;
  padding: 0.3rem 0.8rem;
  border-radius: 15px;
  font-size: 0.85rem;
  font-weight: 500;
}

/* Card de upload */
.upload-card {
  background-color: #f8f9fa;
  border-radius: 10px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  margin-bottom: 1.5rem;
}

.upload-header {
  background: linear-gradient(to right, #204578, #3c72c2);
  padding: 1rem 1.5rem;
}

.upload-header h3 {
  color: white;
  font-size: 1.2rem;
  font-weight: 600;
  margin: 0;
}

.upload-form {
  padding: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.file-label {
  display: flex;
  align-items: center;
  padding: 0.8rem 1rem;
  background-color: white;
  border: 2px dashed #ced4da;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.file-label:hover {
  border-color: #204578;
  background-color: #f0f4f8;
}

.file-icon {
  font-size: 1.5rem;
  margin-right: 0.8rem;
}

.file-text {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-input {
  position: absolute;
  left: -9999px;
}

small {
  display: block;
  margin-top: 0.5rem;
  color: #6c757d;
  font-size: 0.85rem;
}

.upload-btn {
  width: 100%;
  padding: 0.8rem;
  background: linear-gradient(to right, #204578, #3c72c2);
  border: none;
  border-radius: 8px;
  color: white;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  justify-content: center;
  align-items: center;
}

.upload-btn:hover:not(:disabled) {
  background: linear-gradient(to right, #1a3760, #2a5b9e);
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(32, 69, 120, 0.2);
}

.upload-btn:disabled {
  background: linear-gradient(to right, #6c757d, #495057);
  cursor: not-allowed;
}

.loading-indicator.small {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-right: 0.5rem;
}

/* Mensagens de erro e sucesso */
.error-message, .success-message {
  margin-top: 1rem;
  padding: 0.8rem 1rem;
  border-radius: 8px;
  display: flex;
  align-items: flex-start;
}

.error-message {
  background-color: #fee2e2;
  color: #b91c1c;
}

.success-message {
  background-color: #d1fae5;
  color: #065f46;
  align-items: center;
}

.error-icon.small, .success-icon.small {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 0.8rem;
  flex-shrink: 0;
}

.error-icon.small {
  background-color: #b91c1c;
  color: white;
  font-weight: bold;
  font-size: 1rem;
}

.success-icon.small {
  background-color: #059669;
  color: white;
  font-weight: bold;
  font-size: 1rem;
}

.close-btn {
  background: none;
  border: none;
  color: #b91c1c;
  cursor: pointer;
  font-size: 1.2rem;
  padding: 0 0.5rem;
  margin-left: auto;
}

/* Card de arquivos */
.files-card {
  background-color: #f8f9fa;
  border-radius: 10px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.files-header {
  background: linear-gradient(to right, #204578, #3c72c2);
  padding: 1rem 1.5rem;
}

.files-header h3 {
  color: white;
  font-size: 1.2rem;
  font-weight: 600;
  margin: 0;
}

.files-table-container {
  padding: 1rem;
  max-height: 300px; /* Altura máxima para a tabela */
  overflow-y: auto; /* Adiciona rolagem vertical apenas para a tabela */
}

.files-table {
  width: 100%;
  border-collapse: collapse;
}

.files-table th, .files-table td {
  padding: 0.8rem;
  text-align: left;
}

.files-table th {
  background-color: #e9ecef;
  color: #495057;
  font-weight: 600;
  position: sticky;
  top: 0; /* Mantém o cabeçalho da tabela fixo durante rolagem */
}

.files-table tr {
  border-bottom: 1px solid #dee2e6;
  transition: background-color 0.2s ease;
}

.files-table tr:hover {
  background-color: #f0f4f8;
}

.file-name {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.file-type-icon {
  font-size: 1.2rem;
}

.download-btn {
  display: inline-block;
  background-color: #204578;
  color: white;
  padding: 0.4rem 0.8rem;
  border-radius: 4px;
  text-decoration: none;
  font-size: 0.85rem;
  font-weight: 600;
  transition: all 0.3s ease;
}

.download-btn:hover {
  background-color: #142C4D;
  transform: translateY(-2px);
  box-shadow: 0 3px 8px rgba(32, 69, 120, 0.3);
}

/* Estado vazio */
.no-files {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  text-align: center;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  color: #6c757d;
}

.no-files p {
  color: #6c757d;
  font-size: 1rem;
}

/* Botão de voltar */
.actions {
  margin-top: 2rem;
  margin-bottom: 1rem;
  text-align: center;
}

.back-btn {
  display: inline-flex;
  align-items: center;
  background: linear-gradient(to right, #6c757d, #495057);
  color: white;
  padding: 0.7rem 1.2rem;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.3s ease;
}

.back-btn:hover {
  background: linear-gradient(to right, #5a6268, #3d4246);
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(108, 117, 125, 0.3);
}

.back-icon {
  margin-right: 0.5rem;
  font-size: 1.1rem;
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
</style>