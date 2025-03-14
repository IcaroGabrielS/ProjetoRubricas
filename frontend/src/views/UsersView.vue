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

          <!-- Lista de usuários existentes com pesquisa integrada -->
          <div class="dashboard-summary">
            <div class="dashboard-item">
              <!-- Pesquisa integrada -->
              <div class="search-container">
                <input 
                  type="text" 
                  v-model="searchQuery" 
                  placeholder="Procurar por nome de usuário..."
                  class="search-input"
                >
              </div>
              
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
                      class="manage-button" 
                      @click="openManageUserModal(user)"
                      title="Gerenciar usuário"
                    >
                      Gerenciar
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
                <div class="form-group username-row">
                  <div class="input-wrapper">
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
                  
                  <div class="admin-checkbox">
                    <input 
                      type="checkbox" 
                      id="is_admin" 
                      v-model="newUser.is_admin"
                    >
                    <label for="is_admin">Usuário Administrador</label>
                  </div>
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

    <!-- Modal de Confirmação de Exclusão -->
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

    <!-- Modal de Gerenciamento de Usuário -->
    <div class="modal" v-if="showManageModal">
      <div class="modal-content manage-user-modal">
        <div class="modal-header">
          <h3>Gerenciar Usuário: {{ selectedUser?.username }}</h3>
          <button class="close-modal-btn" @click="closeManageUserModal">&times;</button>
        </div>
        <div class="modal-body">
          <div v-if="manageUserError" class="error-message">
            <div class="error-icon">!</div>
            <p>{{ manageUserError }}</p>
            <button class="close-btn" @click="manageUserError = ''" aria-label="Fechar">×</button>
          </div>

          <div v-if="manageUserSuccess" class="success-message">
            <div class="success-icon">✓</div>
            <p>{{ manageUserSuccess }}</p>
            <button class="close-btn" @click="manageUserSuccess = ''" aria-label="Fechar">×</button>
          </div>
          
          <!-- Seção de alteração de senha -->
          <div class="manage-section">
            <h4>Alterar Senha</h4>
            
            <div class="form-group">
              <label for="new-password">Nova Senha:</label>
              <input 
                type="password" 
                id="new-password" 
                v-model="editUserData.newPassword" 
                class="company-input"
                :disabled="changingPassword"
                placeholder="Digite a nova senha"
              >
            </div>
            
            <div class="form-group">
              <label for="confirm-password">Confirmar Senha:</label>
              <input 
                type="password" 
                id="confirm-password" 
                v-model="editUserData.confirmPassword" 
                class="company-input"
                :disabled="changingPassword"
                placeholder="Confirme a nova senha"
              >
            </div>
            
            <button 
              @click="changePassword" 
              class="action-btn password-btn"
              :disabled="changingPassword || !passwordsValid"
            >
              <span v-if="changingPassword" class="loading-spinner-small"></span>
              {{ changingPassword ? 'Alterando...' : 'Alterar Senha' }}
            </button>
          </div>
          
          <!-- Seção de grupos do usuário -->
          <div class="manage-section">
            <h4>Grupos Associados</h4>
            
            <div v-if="loadingUserGroups" class="loading-indicator">
              <div class="loading-spinner"></div>
              <p>Carregando grupos...</p>
            </div>
            
            <div v-else-if="userGroups.length === 0" class="empty-state">
              <p>Este usuário não participa de nenhum grupo.</p>
            </div>
            
            <div v-else class="user-groups-list">
              <div v-for="group in userGroups" :key="group.id" class="group-item">
                <span class="group-name">{{ group.name }}</span>
              </div>
            </div>
          </div>
          
          <!-- Seção para exclusão do usuário - versão compacta -->
          <div class="manage-section danger-section">
            <div class="danger-header">
              <h4>Zona de Perigo</h4>
              <button 
                @click="confirmDeleteUser(selectedUser)"
                class="action-btn delete-btn"
              >
                Excluir Usuário
              </button>
            </div>
          </div>
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
      searchQuery: '',
      creatingUser: false,
      
      // Novos campos para o modal de gerenciamento de usuário
      showManageModal: false,
      selectedUser: null,
      editUserData: {
        username: '',
        is_admin: false,
        newPassword: '',
        confirmPassword: ''
      },
      originalUserData: {
        username: '',
        is_admin: false
      },
      updatingUser: false,
      changingPassword: false,
      loadingUserGroups: false,
      userGroups: [],
      manageUserError: '',
      manageUserSuccess: ''
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
    },
    // Verifica se os dados do usuário foram alterados
    userInfoChanged() {
      return this.editUserData.username !== this.originalUserData.username ||
             this.editUserData.is_admin !== this.originalUserData.is_admin;
    },
    // Verifica se as senhas são válidas para alteração
    passwordsValid() {
      return this.editUserData.newPassword && 
             this.editUserData.newPassword === this.editUserData.confirmPassword &&
             this.editUserData.newPassword.length >= 6;
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
      // Se o modal de gerenciamento estiver aberto, feche-o
      if (this.showManageModal) {
        this.showManageModal = false;
      }
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
        
        // Fechar os modais
        this.showDeleteModal = false;
        this.showManageModal = false;
        this.deleteLoading = false;
        this.userToDelete = null;
        this.selectedUser = null;
        
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
    },
    
    // Novos métodos para gerenciamento de usuário
    openManageUserModal(user) {
      this.selectedUser = user;
      // Inicializa os dados para edição
      this.editUserData = {
        username: user.username,
        is_admin: user.is_admin,
        newPassword: '',
        confirmPassword: ''
      };
      // Guarda os valores originais para comparação
      this.originalUserData = {
        username: user.username,
        is_admin: user.is_admin
      };
      
      this.manageUserError = '';
      this.manageUserSuccess = '';
      
      this.showManageModal = true;
      
      // Carrega os grupos do usuário
      this.fetchUserGroups(user.id);
    },
    
    closeManageUserModal() {
      this.showManageModal = false;
      this.selectedUser = null;
      this.userGroups = [];
      this.manageUserError = '';
      this.manageUserSuccess = '';
    },
    
    async fetchUserGroups(userId) {
      this.loadingUserGroups = true;
      this.userGroups = [];
      
      try {
        const userStr = localStorage.getItem('user');
        if (!userStr) {
          this.$router.push('/login');
          return;
        }
        
        const currentUser = JSON.parse(userStr);
        
        // Buscar todos os grupos
        const response = await fetch('/api/groups', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'User-ID': currentUser.id
          }
        });
        
        const data = await response.json();
        
        if (!response.ok) {
          this.manageUserError = data.message || 'Erro ao carregar grupos';
          this.loadingUserGroups = false;
          return;
        }
        
        // Filtra apenas os grupos que o usuário selecionado tem permissão
        const userGroups = data.groups.filter(group => 
          group.allowed_users && group.allowed_users.includes(userId)
        );
        
        this.userGroups = userGroups;
        this.loadingUserGroups = false;
      } catch (error) {
        this.manageUserError = 'Erro ao conectar ao servidor';
        this.loadingUserGroups = false;
        console.error('Error fetching user groups:', error);
      }
    },
    
    async changePassword() {
      if (!this.passwordsValid) return;
      
      this.changingPassword = true;
      this.manageUserError = '';
      
      try {
        const userStr = localStorage.getItem('user');
        if (!userStr) {
          this.$router.push('/login');
          return;
        }
        
        const currentUser = JSON.parse(userStr);
        
        const response = await fetch(`/api/users/${this.selectedUser.id}/password`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'User-ID': currentUser.id
          },
          body: JSON.stringify({
            new_password: this.editUserData.newPassword
          })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
          this.manageUserError = data.message || 'Erro ao alterar senha';
          this.changingPassword = false;
          return;
        }
        
        // Limpar os campos de senha
        this.editUserData.newPassword = '';
        this.editUserData.confirmPassword = '';
        
        this.manageUserSuccess = 'Senha alterada com sucesso!';
        this.changingPassword = false;
      } catch (error) {
        this.manageUserError = 'Erro ao conectar ao servidor';
        this.changingPassword = false;
        console.error('Error changing password:', error);
      }
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

/* Pesquisa - modificada para remover ícone e ajustar espaçamento */
.search-container {
  margin-bottom: 1rem;
}

.search-input {
  width: 100%;
  padding: 12px 15px;
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

/* Estilo para a linha de nome de usuário com checkbox à direita */
.username-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;  /* Alinha os elementos na parte inferior */
  gap: 1rem;
}

.input-wrapper {
  flex-grow: 1;
  flex-basis: 60%; /* Ajusta a largura do campo de nome de usuário */
}

/* Estilo do checkbox de administrador */
.admin-checkbox {
  display: inline-flex;
  align-items: center;
  background-color: #edf5ff;
  padding: 0.5rem 0.8rem;
  border-radius: 6px;
  border: 1px solid #c5dbff;
  transition: all 0.2s ease;
  height: 52px; /* Mesma altura do campo de input */
}

.admin-checkbox:hover {
  background-color: #dfeaff;
}

.admin-checkbox input {
  width: 18px;
  height: 18px;
  cursor: pointer;
  margin-right: 0.5rem;
}

.admin-checkbox label {
  display: inline;
  margin-bottom: 0;
  font-size: 0.95rem;
  cursor: pointer;
  font-weight: 600;
  color: #204578;
  white-space: nowrap;
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

/* Estilo para o modal compacto de perigo */
.danger-section {
  background-color: #fff5f5;
  border: 1px solid #fee2e2;
  border-radius: 8px;
  padding: 1rem;
}

.danger-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.danger-header h4 {
  color: #dc2626;
  margin: 0;
}

.delete-btn {
  background-color: #dc2626;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 0.7rem 1.2rem;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.delete-btn:hover {
  background-color: #b91c1c;
}

/* Botão manage */
.manage-button {
  padding: 0.6rem 1.2rem;
  background: linear-gradient(to right, #142C4D, #204578);
  border: none;
  border-radius: 6px;
  color: white;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.manage-button:hover {
  background: linear-gradient(to right, #1a3760, #2a5b9e);
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(20, 44, 77, 0.3);
}

/* Botão secundário */
.secondary-button {
  padding: 0.8rem 1.8rem;
  background-color: #f3f4f6;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  color: #374151;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: block;
  margin: 0 auto;
}

.secondary-button:hover {
  background-color: #e5e7eb;
}

.users-actions {
  margin-top: 1.5rem;
  text-align: center;
}

/* Estilos para modais */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  animation: fade-in 0.2s ease-out;
}

.modal-content {
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.manage-user-modal {
  max-width: 600px;
}

.modal-header {
  padding: 1.5rem;
  border-bottom: 1px solid #eaeaea;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  color: #142C4D;
  margin: 0;
  font-size: 1.5rem;
}

.close-modal-btn {
  background: none;
  border: none;
  font-size: 1.8rem;
  color: #6b7280;
  cursor: pointer;
  transition: color 0.2s ease;
}

.close-modal-btn:hover {
  color: #1f2937;
}

.modal-body {
  padding: 1.5rem;
  overflow-y: auto;
}

.modal-actions {
  padding: 1.5rem;
  border-top: 1px solid #eaeaea;
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

.cancel-btn {
  padding: 0.7rem 1.5rem;
  background-color: #f3f4f6;
  border: 2px solid #e5e7eb;
  border-radius: 6px;
  color: #374151;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.cancel-btn:hover {
  background-color: #e5e7eb;
}

.confirm-delete-btn {
  padding: 0.7rem 1.5rem;
  background-color: #dc2626;
  border: none;
  border-radius: 6px;
  color: white;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.confirm-delete-btn:hover {
  background-color: #b91c1c;
}

.warning-text {
  color: #dc2626;
  font-weight: 600;
}

/* Estilos para as seções do modal de gerenciamento */
.manage-section {
  margin-bottom: 2rem;
  padding: 1.2rem;
  background-color: #f9f9f9;
  border-radius: 8px;
  border: 1px solid #eaeaea;
}

.manage-section:last-child {
  margin-bottom: 0;
}

.manage-section h4 {
  color: #204578;
  font-size: 1.1rem;
  margin-top: 0;
  margin-bottom: 1rem;
}

/* Estilos para ações nos modais de gerenciamento */
.action-btn {
  padding: 0.8rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.update-btn {
  background-color: #3b82f6;
  color: white;
}

.update-btn:hover:not(:disabled) {
  background-color: #2563eb;
}

.password-btn {
  background-color: #10b981;
  color: white;
}

.password-btn:hover:not(:disabled) {
  background-color: #059669;
}

.action-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Estilos para a lista de grupos do usuário */
.user-groups-list {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  max-height: 150px;
  overflow-y: auto;
}

.group-item {
  background-color: #fff;
  border-radius: 4px;
  border: 1px solid #d1d5db;
  padding: 0.7rem 1rem;
  display: flex;
  align-items: center;
}

.group-name {
  font-size: 0.95rem;
  color: #374151;
}

/* Admin checkbox dentro do formulário de edição */
.admin-checkbox-wrapper {
  margin-bottom: 1.5rem;
}

.admin-checkbox.wide {
  width: 100%;
  justify-content: flex-start;
  padding: 0.8rem;
}

/* Estados vazios */
.empty-state {
  padding: 1.5rem;
  text-align: center;
  color: #6b7280;
}

/* Mensagens de erro e sucesso */
.error-message, .success-message {
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  position: relative;
}

.error-message {
  background-color: #fee2e2;
  border: 1px solid #fecaca;
}

.success-message {
  background-color: #d1fae5;
  border: 1px solid #a7f3d0;
}

.error-icon, .success-icon {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  margin-right: 0.8rem;
}

.error-icon {
  background-color: #dc2626;
  color: white;
}

.success-icon {
  background-color: #10b981;
  color: white;
}

.error-message p, .success-message p {
  margin: 0;
  flex-grow: 1;
}

.error-message p {
  color: #991b1b;
}

.success-message p {
  color: #065f46;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  line-height: 1;
  cursor: pointer;
  padding: 0;
}

.error-message .close-btn {
  color: #991b1b;
}

.success-message .close-btn {
  color: #065f46;
}

/* Loading indicator */
.loading-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(32, 69, 120, 0.3);
  border-top: 4px solid #204578;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* Media queries para responsividade */
@media (max-width: 1024px) {
  .home-layout {
    flex-direction: column;
    left: 30px;
    right: 30px;
  }
  
  .content-panel {
    width: 100%;
    margin-bottom: 20px;
  }
}

@media (max-width: 640px) {
  .home-layout {
    top: 80px;
    left: 20px;
    right: 20px;
  }
  
  .content-wrapper {
    padding: 1.5rem;
  }
  
  .username-row {
    flex-direction: column;
  }
  
  .admin-checkbox {
    height: auto;
    margin-top: 0.5rem;
  }
  
  .submit-btn {
    width: 100%;
  }
}
</style>