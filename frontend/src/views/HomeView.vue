<template>
  <div>
    <!-- Alerta para dispositivos móveis - sem alterações -->
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
            <!-- CORRIGIDO: Indicador de carregamento -->
            <div v-if="groupsLoading" class="groups-loading-container">
              <div class="groups-loading-spinner"></div>
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
                <div class="store-item-details">
                  <span class="store-name">{{ group.name }}</span>
                </div>
                <div class="store-item-actions">
                  <button 
                    v-if="isAdmin" 
                    class="manage-button" 
                    @click="manageGroupAccess(group.id)" 
                    title="Gerenciar acesso de usuários"
                  >
                    <span class="manage-icon">👥</span>
                    <span class="manage-text">Gerenciar</span>
                  </button>
                  <div class="arrow-container" @click="goToGroupDetail(group.id)" title="Ver detalhes do grupo">
                    <span class="store-item-arrow">›</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Botões de ação -->
          <div class="quick-actions">
            <button v-if="isAdmin" class="action-button admin" @click="showCreateGroupModal = true">Novo Grupo</button>
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

    <!-- Modal para criar novo grupo - sem alterações importantes -->
    <div v-if="showCreateGroupModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-container">
        <!-- Conteúdo do modal sem alterações -->
        <div class="modal-header">
          <h2>Criar Novo Grupo</h2>
          <button class="close-modal-btn" @click="closeModal">×</button>
        </div>
        
        <div class="modal-body">
          <form @submit.prevent="handleCreateGroup" class="create-group-form">
            <div class="form-group">
              <label for="name">Nome do Grupo:</label>
              <input 
                type="text" 
                id="name" 
                v-model="newGroup.name" 
                required
                placeholder="Digite o nome do grupo"
              >
            </div>
            
            <div class="button-container">
              <button type="submit" :disabled="createGroupLoading" class="submit-btn">
                <span v-if="createGroupLoading" class="form-loading-indicator"></span>
                {{ createGroupLoading ? 'Criando...' : 'Criar Grupo' }}
              </button>
            </div>
          </form>
          
          <div v-if="createGroupError" class="error-message">
            <div class="error-icon">!</div>
            <p>{{ createGroupError }}</p>
            <button class="close-btn" @click="createGroupError = null" aria-label="Fechar">×</button>
          </div>
          
          <div v-if="createGroupSuccess" class="success-message">
            <div class="success-icon">✓</div>
            <p>{{ createGroupSuccess }}</p>
            <div class="success-actions">
              <button @click="closeModal" class="action-btn view-btn">Voltar para Home</button>
              <button @click="resetCreateGroupForm" class="action-btn reset-btn">Criar outro grupo</button>
            </div>
          </div>
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
      isMobileDevice: false,
      
      // Novo Grupo Modal
      showCreateGroupModal: false,
      newGroup: {
        name: ''
      },
      createGroupLoading: false,
      createGroupError: null,
      createGroupSuccess: ''
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
      this.showCreateGroupModal = true;
    },
    manageAccounts() {
      this.$router.push('/users');
    },
    logout() {
      localStorage.removeItem('user');
      this.$router.push('/login');
    },
    
    // Métodos para o modal de criação de grupo
    closeModal() {
      if (!this.createGroupLoading) {
        this.showCreateGroupModal = false;
        
        // Se houver sucesso, recarrega os grupos ao fechar
        if (this.createGroupSuccess) {
          this.fetchGroups();
        }
        
        // Reseta o formulário e as mensagens
        this.resetCreateGroupForm();
        this.createGroupError = null;
        this.createGroupSuccess = '';
      }
    },
    resetCreateGroupForm() {
      this.newGroup = {
        name: ''
      };
      this.createGroupSuccess = '';
    },
    async handleCreateGroup() {
      this.createGroupLoading = true;
      this.createGroupError = null;
      
      try {
        const userStr = localStorage.getItem('user');
        if (!userStr) {
          this.$router.push('/login');
          return;
        }
        
        const user = JSON.parse(userStr);
        
        const response = await fetch('/api/groups', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'User-ID': user.id
          },
          body: JSON.stringify(this.newGroup)
        });
        
        const data = await response.json();
        
        if (!response.ok) {
          console.error('Erro no servidor:', data);
          this.createGroupError = data.message || 'Erro ao criar grupo';
          this.createGroupLoading = false;
          return;
        }
        
        this.createGroupSuccess = 'Grupo criado com sucesso!';
        this.createGroupLoading = false;
      } catch (error) {
        console.error('Erro ao conectar ao servidor:', error);
        this.createGroupError = 'Erro ao conectar ao servidor';
        this.createGroupLoading = false;
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

.store-item-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

/* Novo estilo para o contêiner da seta */
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

/* Estilo atualizado para o botão de gerenciamento */
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

/* NOVOS ESTILOS: Indicador de carregamento */
.groups-loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  text-align: center;
  width: 100%;
  height: 150px;
  margin: 1rem 0;
  background-color: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #eaeaea;
}

.groups-loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(32, 69, 120, 0.1);
  border-top: 4px solid #204578;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

/* Estados de erro e vazio */
.error-message, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  text-align: center;
  width: 100%;
  margin: 1rem 0;
  background-color: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #eaeaea;
}

.error-message {
  background-color: #fee2e2;
  border-color: #fecaca;
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

/* Modal para criação de grupo */
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
  z-index: 1000;
  animation: fade-in 0.3s ease;
}

.modal-container {
  width: 90%;
  max-width: 600px;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
  overflow: hidden;
  animation: slide-up 0.4s ease;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  border-bottom: 1px solid #eaeaea;
}

.modal-header h2 {
  color: #142C4D;
  font-size: 1.8rem;
  margin: 0;
}

.close-modal-btn {
  background: none;
  border: none;
  font-size: 1.8rem;
  color: #666;
  cursor: pointer;
  transition: all 0.2s ease;
}

.close-modal-btn:hover {
  color: #142C4D;
  transform: scale(1.1);
}

.modal-body {
  padding: 2rem;
}

.create-group-form {
  margin-bottom: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
  text-align: left;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  color: #333;
}

.form-group input {
  width: 100%;
  padding: 0.9rem;
  border: 2px solid #e1e1e1;
  border-radius: 8px;
  font-size: 1rem;
  color: #333;
  transition: all 0.3s ease;
  background-color: #f9f9f9;
  font-family: 'Sarala', sans-serif;
}

.form-group input:focus {
  border-color: #204578;
  box-shadow: 0 0 0 3px rgba(32, 69, 120, 0.15);
  outline: none;
  background-color: #fff;
}

.form-group input::placeholder {
  color: #aaa;
}

.button-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 1rem;
}

.submit-btn {
  padding: 1rem 2.5rem;
  background: linear-gradient(to right, #142C4D, #204578);
  border: none;
  border-radius: 8px;
  color: white;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 200px;
}

.submit-btn:hover:not(:disabled) {
  background: linear-gradient(to right, #1a3760, #2a5b9e);
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(32, 69, 120, 0.3);
}

.submit-btn:active:not(:disabled) {
  transform: translateY(0);
}

.submit-btn:disabled {
  background: linear-gradient(to right, #6c757d, #495057);
  cursor: not-allowed;
}

/* Renomeado para evitar conflito */
.form-loading-indicator {
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 3px solid rgba(255,255,255,0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 1s ease-in-out infinite;
  margin-right: 10px;
}

.success-message {
  margin-top: 1.5rem;
  padding: 1.2rem;
  border-radius: 8px;
  display: flex;
  align-items: flex-start;
  background-color: #d1fae5;
  color: #065f46;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.success-icon {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background-color: #059669;
  color: white;
  font-weight: bold;
  font-size: 1.2rem;
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
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

.success-actions {
  display: flex;
  gap: 1.5rem;
  margin-top: 1.5rem;
  justify-content: center;
}

.action-btn {
  padding: 0.8rem 1.5rem;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
  min-width: 180px;
  text-align: center;
  border: none;
}

.view-btn {
  background-color: #204578;
  color: white;
}

.view-btn:hover {
  background-color: #142C4D;
  transform: translateY(-2px);
}

.reset-btn {
  background-color: #6c757d;
  color: white;
}

.reset-btn:hover {
  background-color: #5a6268;
  transform: translateY(-2px);
}

/* Animações */
@keyframes fade-in {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes slide-up {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>