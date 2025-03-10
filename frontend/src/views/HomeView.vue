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
      <!-- Painel com o conteúdo (visualmente à esquerda) -->
      <div class="content-panel">
        <div class="content-wrapper">
          <div class="home-header">
            <h1>Olá, {{ username }}!</h1>
            <p class="welcome-text">Você logou com sucesso.</p>
          </div>
          
          <div class="dashboard-summary">
            <div class="dashboard-item">
              <h3>Seus Grupos</h3>
              <p>Selecione um grupo abaixo para acessar seus detalhes e arquivos.</p>
            </div>
          </div>
          
          <!-- Caixa de busca para grupos -->
          <div class="search-container">
            <div class="search-box">
              <input 
                type="text" 
                v-model="searchQuery" 
                placeholder="Pesquisar grupos..."
                class="search-input"
              >
              <span class="search-icon">🔍</span>
            </div>
          </div>
          
          <!-- Lista de grupos -->
          <div class="stores-section">
            <div v-if="groupsLoading" class="loading-indicator">
              <div class="loading-spinner"></div>
              <p>Carregando grupos...</p>
            </div>
            
            <div v-else-if="groupsError" class="error-message">
              <div class="error-icon">!</div>
              <p>{{ groupsError }}</p>
            </div>
            
            <div v-else-if="filteredGroups.length === 0 && groups.length === 0" class="empty-state">
              <p>Você não tem acesso a nenhum grupo no momento.</p>
            </div>
            
            <div v-else-if="filteredGroups.length === 0" class="empty-state">
              <p>Nenhum grupo encontrado com esse nome.</p>
            </div>
            
            <div v-else class="stores-list">
              <div 
                v-for="group in filteredGroups" 
                :key="group.id" 
                class="store-item"
              >
                <div class="store-item-details" @click="goToGroupDetail(group.id)">
                  <span class="store-name">{{ group.name }}</span>
                </div>
                <div class="store-item-actions">
                  <button 
                    v-if="isAdmin" 
                    class="manage-button" 
                    @click="manageGroupAccess(group.id)" 
                    title="Gerenciar acesso de usuários"
                  >
                    👥
                  </button>
                  <span class="store-item-arrow" @click="goToGroupDetail(group.id)">›</span>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Botões de ação -->
          <div class="quick-actions">
            <button v-if="isAdmin" class="action-button admin" @click="createGroup">Novo Grupo</button>
            <button v-if="isAdmin" class="action-button admin" @click="manageAccounts">Gerenciar Contas</button>
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
  </div>
</template>

<script>
export default {
  name: 'HomeView',
  data() {
    return {
      username: 'Usuário',
      isAdmin: false,
      groups: [],
      groupsLoading: true,
      groupsError: null,
      searchQuery: '',
      isMobileDevice: false
    }
  },
  computed: {
    filteredGroups() {
      if (!this.searchQuery) {
        return this.groups;
      }
      
      const query = this.searchQuery.toLowerCase();
      return this.groups.filter(group => 
        group.name.toLowerCase().includes(query)
      );
    }
  },
  created() {
    this.checkDeviceType();
    this.loadUserInfo();
    this.fetchGroups();
    
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
    loadUserInfo() {
      const userStr = localStorage.getItem('user');
      if (userStr) {
        const user = JSON.parse(userStr);
        this.username = user.username;
        this.isAdmin = user.is_admin === true;
      } else {
        this.$router.push('/login');
      }
    },
    async fetchGroups() {
      try {
        const userStr = localStorage.getItem('user');
        if (!userStr) {
          this.$router.push('/login');
          return;
        }
        
        const user = JSON.parse(userStr);
        
        const response = await fetch('/api/groups', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'User-ID': user.id
          }
        });
        
        const data = await response.json();
        
        if (!response.ok) {
          this.groupsError = data.message || 'Erro ao carregar grupos';
          this.groupsLoading = false;
          return;
        }
        
        this.groups = data.groups;
        this.groupsLoading = false;
      } catch (error) {
        this.groupsError = 'Erro ao conectar ao servidor';
        this.groupsLoading = false;
        console.error('Error fetching groups:', error);
      }
    },
    goToGroupDetail(groupId) {
      this.$router.push(`/groups/${groupId}`);
    },
    manageGroupAccess(groupId) {
      this.$router.push(`/groups/manage/${groupId}`);
    },
    createGroup() {
      this.$router.push('/groups/create');
    },
    manageAccounts() {
      this.$router.push('/users');
    },
    logout() {
      localStorage.removeItem('user');
      this.$router.push('/login');
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

.welcome-text {
  color: #666;
  font-size: 1.1rem;
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

/* Seção de lojas */
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
  cursor: pointer;
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
  cursor: pointer;
}

.store-name {
  font-weight: 600;
  font-size: 0.95rem;
  color: #142C4D;
}

.store-item-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.store-item-arrow {
  font-size: 1.5rem;
  font-weight: bold;
  color: #204578;
  cursor: pointer;
}

.manage-button {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background-color: #f0f0f0;
  border: 1px solid #ddd;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  padding: 0;
  font-size: 0.9rem;
  box-shadow: none;
}

.manage-button:hover {
  background-color: #e0e0e0;
  transform: scale(1.1);
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

/* Estados de loading, erro e vazio */
.loading-indicator, .error-message, .empty-state {
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

.error-message p {
  color: #b91c1c;
}

.empty-state p {
  color: #666;
  font-style: italic;
}

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

.action-button.logout {
  background: linear-gradient(to right, #d63031, #e84393);
}

.action-button.logout:hover {
  background: linear-gradient(to right, #c0392b, #d63031);
  box-shadow: 0 5px 15px rgba(214, 48, 49, 0.3);
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