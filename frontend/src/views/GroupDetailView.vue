<template>
  <div>
    <!-- Alerta para dispositivos móveis (copiado do HomeView) -->
    <div v-if="isMobileDevice" class="mobile-warning">
      <div class="warning-icon">⚠️</div>
      <h2>Acesso não recomendado</h2>
      <p>Este site não foi projetado para dispositivos móveis. Por favor, acesse através de um computador para uma melhor experiência.</p>
    </div>

    <!-- Conteúdo principal - visível apenas em desktop -->
    <div v-else class="home-layout">
      <!-- Painel com o conteúdo (visualmente à esquerda) -->
      <div class="content-panel">
        <div class="content-wrapper">
          <div class="home-header">
            <h1>{{ group.name }}</h1>
          </div>

          <div v-if="error" class="error-message">
            <div class="error-icon">!</div>
            <p>{{ error }}</p>
            <button class="close-btn" @click="error = ''" aria-label="Fechar">×</button>
          </div>

          <div v-if="success" class="success-message">
            <div class="success-icon">✓</div>
            <p>{{ success }}</p>
            <button class="close-btn" @click="success = ''" aria-label="Fechar">×</button>
          </div>

          <div v-if="loading" class="loading-indicator">
            <div class="loading-spinner"></div>
            <p>Carregando informações do grupo...</p>
          </div>

          <div v-else>
            <!-- Informações do Grupo (Simplificadas) -->
            <div class="dashboard-summary">
              <div class="dashboard-item simplified">
                <div class="info-header">
                  <span class="info-label">ID: {{ group.id }}</span>
                  <span class="info-label">Criado em: {{ formatDate(group.created_at) }}</span>
                  <button v-if="isAdmin" class="manage-btn" @click="manageAccess(group.id)">
                    <span class="manage-text">Gerenciar Acesso</span>
                  </button>
                </div>
              </div>
            </div>

            <!-- Lista de Empresas -->
            <div class="dashboard-summary">
              <div class="dashboard-item">
                <h3>Empresas</h3>
                <p>Selecione uma empresa abaixo para acessar seus detalhes.</p>
              </div>
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

            <!-- Lista de empresas (estilo copiado de grupos no HomeView) -->
            <div class="stores-section">
              <div v-if="!group.companies || group.companies.length === 0" class="empty-state">
                <p>Nenhuma empresa foi adicionada a este grupo.</p>
              </div>
              
              <div v-else-if="filteredCompanies.length === 0" class="empty-state">
                <p>Nenhuma empresa encontrada com esse nome.</p>
              </div>

              <div v-else class="stores-list">
                <div 
                  v-for="company in filteredCompanies" 
                  :key="company.id" 
                  class="store-item"
                >
                  <div class="store-item-details">
                    <span class="store-name">{{ company.name }}</span>
                    <span class="store-info">CNPJ: {{ company.cnpj }}</span>
                  </div>
                  <div class="store-item-actions">
                    <!-- Botão "Gerenciar" removido daqui -->
                    <div class="arrow-container" @click="goToCompanyDetail(company.id)" title="Ver detalhes da empresa">
                      <span class="store-item-arrow">›</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Painel com a ilustração (visualmente à direita) -->
      <div class="illustration-panel">
        <div class="large-svg-container">
          <img src="@/assets/task-animate.svg" alt="Task Illustration" class="large-svg">
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
          <p>Você está prestes a excluir o grupo <strong>{{ group.name }}</strong> e todas as suas empresas.</p>
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
            :disabled="confirmDeleteText !== 'EXCLUIR' || deletingGroup"
            @click="deleteGroup">
            {{ deletingGroup ? 'Excluindo...' : 'Confirmar Exclusão' }}
          </button>
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
      success: '',
      isAdmin: false,
      searchQuery: '',
      isMobileDevice: false,
      showDeleteConfirmation: false,
      confirmDeleteText: '',
      deletingGroup: false
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
    this.checkDeviceType();
    this.checkAccess();
    // Não é mais necessário converter para inteiro, pois o ID agora é uma string UUID
    this.groupId = this.$route.params.id;
    // Verificar se o ID está presente, não é mais necessário verificar se é um número
    if (!this.groupId) {
      console.error('ID de grupo não fornecido:', this.$route.params.id);
      this.error = 'ID de grupo não fornecido';
      this.loading = false;
      return;
    }
    this.fetchGroupData();
    
    // Adicionar listener para verificar redimensionamento (copiado do HomeView)
    window.addEventListener('resize', this.checkDeviceType);
  },
  beforeUnmount() {
    // Remover listener ao destruir componente (copiado do HomeView)
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
    goToCompanyDetail(companyId) {
      this.$router.push(`/companies/${companyId}`);
    },
    cancelDelete() {
      this.showDeleteConfirmation = false;
      this.confirmDeleteText = '';
    },
    async deleteGroup() {
      try {
        if (this.confirmDeleteText !== 'EXCLUIR') {
          return;
        }
        
        this.deletingGroup = true;
        const userStr = localStorage.getItem('user');
        if (!userStr) {
          this.$router.push('/login');
          return;
        }
        const user = JSON.parse(userStr);
        console.log('Deleting group:', this.groupId);
        
        const response = await fetch(`/api/groups/${this.groupId}`, {
          method: 'DELETE',
          headers: {
            'Content-Type': 'application/json',
            'User-ID': user.id
          }
        });
        
        if (!response.ok) {
          const data = await response.json();
          this.error = data.message || 'Erro ao excluir o grupo';
          this.deletingGroup = false;
          this.showDeleteConfirmation = false;
          return;
        }
        
        console.log('Group deleted successfully');
        this.success = 'Grupo excluído com sucesso. Redirecionando...';
        this.deletingGroup = false;
        this.showDeleteConfirmation = false;
        
        // Redirecionar após 2 segundos
        setTimeout(() => {
          this.$router.push('/');
        }, 2000);
      } catch (error) {
        this.error = 'Erro ao conectar ao servidor';
        this.deletingGroup = false;
        this.showDeleteConfirmation = false;
        console.error('Error deleting group:', error);
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
  flex-direction: row-reverse; /* Mantém a ordem inversa (ilustração à direita) */
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

/* Painel de ilustração (visualmente à direita) */
.illustration-panel {
  width: calc(50% - 10px); /* 50% da largura menos metade do gap */
  background: linear-gradient(135deg, #0D1B40 30%, #1E3A8A 70%);
  border-radius: 12px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  overflow: hidden;
  animation: fade-in 0.8s ease-out;
}

/* Container e estilos para o SVG grande */
.large-svg-container {
  width: 90%;
  height: 90%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.large-svg {
  max-width: 100%;
  max-height: 100%;
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

/* Estilo para o bloco simplificado de informações */
.dashboard-item.simplified {
  padding: 0.8rem 1.2rem;
}

.info-header {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.info-label {
  font-size: 0.9rem;
  font-weight: 600;
  color: #666;
}

.dashboard-item h3 {
  color: #204578;
  font-size: 1.2rem;
  margin-bottom: 0.5rem;
}

.dashboard-item p {
  color: #666;
  font-size: 0.95rem;
}

/* Caixa de Busca */
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

/* Seção de empresas */
.stores-section {
  flex: 1;
  overflow-y: auto;
  margin-bottom: 1rem;
  max-height: calc(100% - 250px);
}

.stores-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.store-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.8rem 1rem;
  background-color: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #eaeaea;
  transition: all 0.2s ease;
}

.store-item:hover {
  background-color: #e9ecef;
  transform: translateY(-2px);
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.08);
}

.store-item-details {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  flex: 1;
}

.store-name {
  font-weight: 600;
  font-size: 0.95rem;
  color: #142C4D;
}

.store-info {
  font-size: 0.85rem;
  color: #666;
}

.store-item-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

/* Novo estilo para o contêiner da seta - copiado de HomeView */
.arrow-container {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  background-color: #e8f0fe;
  cursor: pointer;
  transition: all 0.2s ease;
}

.arrow-container:hover {
  background-color: #d0e1fd;
  transform: scale(1.1);
}

.store-item-arrow {
  font-size: 1.5rem;
  font-weight: bold;
  color: #204578;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Estilo atualizado para o botão de gerenciamento - copiado de HomeView */
.manage-button {
  min-width: 120px;
  height: 36px;
  border-radius: 6px;
  background-color: #f0f0f0;
  border: 1px solid #ddd;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  padding: 0 12px;
  font-size: 0.9rem;
  box-shadow: none;
  gap: 6px;
}

.manage-button:hover {
  background-color: #e0e0e0;
  transform: scale(1.05);
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.manage-icon {
  font-size: 1rem;
}

.manage-text {
  font-size: 0.85rem;
  font-weight: 500;
  color: #444;
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
  color: #b91c1c;
  cursor: pointer;
  font-size: 1.2rem;
  padding: 0 0.5rem;
  margin-left: auto;
}

.manage-btn {
  padding: 0.6rem 0.8rem;
  background: #142C4D;
  border: none;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-left: auto;
}

.manage-btn:hover {
  background: linear-gradient(to right, #1a3760, #2a5b9e);
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(20, 44, 77, 0.3);
}

.manage-btn .manage-text {
  color: white; /* ou qualquer outra cor desejada */
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
  font-weight: bold;
  margin-top: 0.5rem;
}

.confirmation-input {
  margin-top: 1.5rem;
  text-align: left;
}

.confirmation-input label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #333;
}

.confirmation-input input {
  width: 100%;
  padding: 0.7rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
}

.modal-footer {
  display: flex;
  padding: 1.2rem 1.5rem;
  background-color: #f8f8f8;
  border-top: 1px solid #eaeaea;
  justify-content: space-between;
}

.cancel-btn {
  padding: 0.7rem 1.2rem;
  background-color: #f0f0f0;
  border: none;
  border-radius: 6px;
  color: #333;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.cancel-btn:hover {
  background-color: #e0e0e0;
}

.delete-btn {
  padding: 0.7rem 1.2rem;
  background-color: #dc2626;
  border: none;
  border-radius: 6px;
  color: white;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.delete-btn:hover:not(:disabled) {
  background-color: #b91c1c;
}

.delete-btn:disabled {
  background-color: #f87171;
  cursor: not-allowed;
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