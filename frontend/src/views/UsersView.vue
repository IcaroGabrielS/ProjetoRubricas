<template>
  <div>
    <!-- Conteúdo principal -->
    <div class="home-layout">
      <!-- Painel esquerdo - Usuários existentes -->
      <div class="content-panel">
        <div class="content-wrapper">
          <div class="home-header">
            <h1>Gerenciar Usuários</h1>
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

          <!-- Pesquisa de usuários -->
          <div class="dashboard-summary">
            <div class="dashboard-item">
              <h3>Pesquisar usuários</h3>
              <div class="search-container">
                <div class="search-box">
                  <input 
                    type="text" 
                    v-model="searchQuery" 
                    placeholder="Procurar por nome de usuário..."
                    class="search-input"
                  >
                  <span class="search-icon">🔍</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Lista de usuários existentes -->
          <div class="dashboard-summary">
            <div class="dashboard-item">
              <div v-if="usersLoading" class="loading-indicator">
                <div class="loading-spinner"></div>
                <p>Carregando usuários...</p>
              </div>
              
              <div v-else-if="filteredUsers.length === 0" class="empty-state">
                <p>Não há usuários cadastrados além do seu ou correspondentes à pesquisa.</p>
              </div>
              
              <div v-else class="users-list">
                <div v-for="user in filteredUsers" :key="user.id" class="user-item">
                  <div class="user-item-details">
                    <span class="user-name">{{ user.username }}</span>
                    <span class="user-type" :class="{ 'admin-type': user.is_admin }">
                      {{ user.is_admin ? 'Administrador' : 'Usuário Padrão' }}
                    </span>
                  </div>
                  <div class="user-actions">
                    <button 
                      class="delete-button" 
                      @click="confirmDeleteUser(user)"
                      title="Remover usuário"
                    >
                      ×
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div class="users-actions">
            <button class="secondary-button" @click="goBack">Voltar</button>
          </div>
        </div>
      </div>
      
      <!-- Painel direito - Criar Novo Usuário -->
      <div class="content-panel">
        <div class="content-wrapper">
          <div class="home-header">
            <h1>Gerenciar Recursos</h1>
          </div>

          <!-- Formulário para criar usuários -->
          <div class="dashboard-summary">
            <div class="dashboard-item create-company">
              <h3>Criar Novo Usuário</h3>
              <p>Adicione um novo usuário ao sistema</p>
              
              <form @submit.prevent="createUser" class="company-form">
                <div class="form-group">
                  <label for="username">Nome de Usuário:</label>
                  <input 
                    type="text" 
                    id="username" 
                    v-model="newUser.username" 
                    required
                    placeholder="ID do novo Usuário"
                    class="company-input"
                  >
                </div>
                
                <div class="form-group">
                  <label for="password">Senha:</label>
                  <input 
                    type="password" 
                    id="password" 
                    v-model="newUser.password" 
                    required
                    placeholder="Nova Senha"
                    class="company-input"
                  >
                </div>
                
                <div class="form-group checkbox-group">
                  <input 
                    type="checkbox" 
                    id="is_admin" 
                    v-model="newUser.is_admin"
                  >
                  <label for="is_admin">Usuário Administrador</label>
                </div>
                
                <button 
                  type="submit" 
                  class="submit-btn" 
                  :disabled="creatingUser"
                >
                  <span v-if="creatingUser" class="loading-spinner-small"></span>
                  {{ creatingUser ? 'Criando...' : 'Criar Usuário' }}
                </button>
              </form>
            </div>
          </div>

          <!-- Informações adicionais sobre usuários -->
          <div class="dashboard-summary">
            <div class="dashboard-item">
              <h3>Tipos de Usuários</h3>
              <p><strong>Usuário Padrão:</strong> Pode acessar apenas os grupos compartilhados.</p>
              <p><strong>Administrador:</strong> Possui acesso completo a todos os grupos e pode gerenciar usuários.</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal de Confirmação -->
    <div class="modal" v-if="showDeleteModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Confirmar Exclusão</h3>
          <button class="close-modal-btn" @click="showDeleteModal = false">&times;</button>
        </div>
        <div class="modal-body">
          <p>Tem certeza que deseja excluir o usuário <strong>{{ userToDelete?.username }}</strong>?</p>
          <p class="warning-text">Esta ação não pode ser desfeita.</p>
        </div>
        <div class="modal-actions">
          <button class="cancel-btn" @click="showDeleteModal = false">Cancelar</button>
          <button class="confirm-delete-btn" @click="deleteUser">Confirmar Exclusão</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'UsersView',
  data() {
    return {
      users: [],
      usersLoading: true,
      error: '',
      success: '',
      newUser: {
        username: '',
        password: '',
        is_admin: false
      },
      showDeleteModal: false,
      userToDelete: null,
      deleteLoading: false,
      searchQuery: '', // Novo campo para busca
      creatingUser: false // Flag para controlar estado de criação
    }
  },
  computed: {
    // Filtrar usuários baseado na pesquisa
    filteredUsers() {
      if (!this.searchQuery) {
        return this.users;
      }
      
      const query = this.searchQuery.toLowerCase();
      return this.users.filter(user => 
        user.username.toLowerCase().includes(query)
      );
    }
  },
  created() {
    this.checkAdminAccess();
    this.fetchUsers();
  },
  methods: {
    checkAdminAccess() {
      const userStr = localStorage.getItem('user');
      if (!userStr) {
        this.$router.push('/login');
        return;
      }
      
      const user = JSON.parse(userStr);
      if (!user.is_admin) {
        // Redirecionar usuários não-admin para home
        this.$router.push('/');
      }
    },
    async fetchUsers() {
      try {
        const userStr = localStorage.getItem('user');
        if (!userStr) {
          this.$router.push('/login');
          return;
        }
        
        const user = JSON.parse(userStr);
        
        const response = await fetch('/api/users', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'User-ID': user.id
          }
        });
        
        const data = await response.json();
        
        if (!response.ok) {
          this.error = data.message || 'Erro ao carregar usuários';
          this.usersLoading = false;
          return;
        }
        
        // Filtrar o usuário atual da lista
        this.users = data.users.filter(u => u.id != user.id);
        this.usersLoading = false;
      } catch (error) {
        this.error = 'Erro ao conectar ao servidor';
        this.usersLoading = false;
        console.error('Error fetching users:', error);
      }
    },
    async createUser() {
      try {
        this.creatingUser = true;
        const userStr = localStorage.getItem('user');
        if (!userStr) {
          this.$router.push('/login');
          return;
        }
        
        const user = JSON.parse(userStr);
        
        const response = await fetch('/api/register', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'User-ID': user.id
          },
          body: JSON.stringify(this.newUser)
        });
        
        const data = await response.json();
        
        if (!response.ok) {
          this.error = data.message || 'Erro ao criar usuário';
          this.creatingUser = false;
          return;
        }
        
        // Limpar formulário e mostrar mensagem de sucesso
        this.success = `Usuário ${this.newUser.username} criado com sucesso!`;
        this.newUser = {
          username: '',
          password: '',
          is_admin: false
        };
        
        // Atualizar lista de usuários
        this.fetchUsers();
        this.creatingUser = false;
      } catch (error) {
        this.error = 'Erro ao conectar ao servidor';
        this.creatingUser = false;
        console.error('Error creating user:', error);
      }
    },
    confirmDeleteUser(user) {
      this.userToDelete = user;
      this.showDeleteModal = true;
    },
    async deleteUser() {
      if (!this.userToDelete) {
        return;
      }
      
      this.deleteLoading = true;
      
      try {
        const userStr = localStorage.getItem('user');
        if (!userStr) {
          this.$router.push('/login');
          return;
        }
        
        const user = JSON.parse(userStr);
        
        const response = await fetch(`/api/users/${this.userToDelete.id}`, {
          method: 'DELETE',
          headers: {
            'Content-Type': 'application/json',
            'User-ID': user.id
          }
        });
        
        if (!response.ok) {
          const data = await response.json();
          this.error = data.message || 'Erro ao excluir usuário';
          this.showDeleteModal = false;
          this.deleteLoading = false;
          return;
        }
        
        // Mostrar mensagem de sucesso
        this.success = `Usuário ${this.userToDelete.username} excluído com sucesso!`;
        
        // Fechar o modal
        this.showDeleteModal = false;
        this.deleteLoading = false;
        this.userToDelete = null;
        
        // Atualizar lista de usuários
        this.fetchUsers();
      } catch (error) {
        this.error = 'Erro ao conectar ao servidor';
        this.showDeleteModal = false;
        this.deleteLoading = false;
        console.error('Error deleting user:', error);
      }
    },
    goBack() {
      this.$router.push('/');
    }
  }
}
</script>

<style scoped>
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

/* Criar empresa/usuário estilo */
.create-company {
  background-color: #f0f7ff; /* Fundo azulado similar ao de GroupManageView */
  border: 1px solid #d0e1fd;
}

.company-form {
  margin-top: 1rem;
}

/* Estilo dos inputs similar ao GroupManageView */
.company-input {
  width: 100%;
  padding: 0.9rem;
  border: 2px solid #d0e1fd;
  border-radius: 8px;
  font-size: 1rem;
  color: #333;
  transition: all 0.3s ease;
  background-color: #fff;
}

.company-input:focus {
  border-color: #204578;
  box-shadow: 0 0 0 3px rgba(32, 69, 120, 0.15);
  outline: none;
}

.invalid-input {
  border-color: #f87171;
  background-color: #fff5f5;
}

.error-text {
  color: #dc2626;
  font-size: 0.85rem;
  margin-top: 0.4rem;
  display: block;
}

/* Pesquisa */
.search-container {
  margin-top: 0.8rem;
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

/* Formulário */
.form-group {
  margin-bottom: 1.2rem;
  text-align: left;
}

.form-group label {
  display: block;
  margin-bottom: 0.6rem;
  font-size: 1rem;
  font-weight: 600;
  color: #333;
}

.checkbox-group {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  margin-bottom: 1.5rem;
}

.checkbox-group input {
  width: 20px;
  height: 20px;
  cursor: pointer;
}

.checkbox-group label {
  display: inline;
  margin-bottom: 0;
  font-size: 1rem;
  cursor: pointer;
}

/* Botão com gradiente igual ao de criar empresa */
.submit-btn {
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
  display: flex;
  justify-content: center;
  align-items: center;
  margin-left: auto;
}

.submit-btn:hover:not(:disabled) {
  background: linear-gradient(to right, #1a3760, #2a5b9e);
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(20, 44, 77, 0.3);
}

.submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

/* Loading spinner pequeno para botão de submit */
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

/* Lista de usuários */
.users-list {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
  max-height: 350px;
  overflow-y: auto;
}

.user-item {
  background-color: #fff;
  border-radius: 6px;
  border: 1px solid #eaeaea;
  padding: 1rem 1.2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: all 0.2s ease;
}

.user-item:hover {
  border-color: #d0d0d0;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.user-item-details {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.user-name {
  font-weight: 600;
  font-size: 1.1rem;
  color: #142C4D;
  display: block;
}

.user-type {
  font-size: 0.85rem;
  color: #666;
  background-color: #f0f0f0;
  padding: 0.3rem 0.7rem;
  border-radius: 12px;
  display: inline-block;
  margin-top: 0.5rem;
}

.admin-type {
  background-color: #e0f2fe;
  color: #0077b6;
}

.user-actions {
  display: flex;
  gap: 0.8rem;
}

.delete-button {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: #fff;
  border: 1px solid #ff7675;
  color: #ff7675;
  font-size: 1.4rem;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  padding: 0;
  transition: all 0.2s ease;
}

.delete-button:hover {
  background-color: #ff7675;
  color: white;
  transform: scale(1.1);
}

/* Botões */
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

.users-actions {
  display: flex;
  justify-content: center;
  margin-top: 1rem;
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
  color: #666;
  cursor: pointer;
  font-size: 1.2rem;
  padding: 0 0.5rem;
}

/* Modal de confirmação */
.modal {
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

.modal-content {
  background-color: white;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
  animation: slide-up 0.3s ease;
  overflow: hidden;
}

.modal-header {
  background: linear-gradient(to right, #ff7675, #fab1a0);
  padding: 1.2rem 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  color: white;
  margin: 0;
  font-size: 1.3rem;
}

.close-modal-btn {
  background: none;
  border: none;
  color: white;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0;
  line-height: 1;
}

.modal-body {
  padding: 1.5rem;
}

.modal-body p {
  margin-bottom: 0.8rem;
  font-size: 1.1rem;
}

.warning-text {
  color: #b91c1c;
  font-weight: 600;
  font-size: 0.95rem;
}

.modal-actions {
  padding: 1rem 1.5rem;
  background-color: #f9f9f9;
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

.cancel-btn {
  padding: 0.7rem 1.5rem;
  background-color: #f0f0f0;
  border: 1px solid #ddd;
  border-radius: 8px;
  color: #333;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.cancel-btn:hover {
  background-color: #e0e0e0;
}

.confirm-delete-btn {
  padding: 0.7rem 1.5rem;
  background: linear-gradient(to right, #ff7675, #fab1a0);
  border: none;
  border-radius: 8px;
  color: white;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.confirm-delete-btn:hover {
  background: linear-gradient(to right, #d63031, #e84393);
  box-shadow: 0 5px 15px rgba(214, 48, 49, 0.3);
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