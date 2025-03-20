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

          <AlertMessage 
            :type="'error'" 
            :message="error" 
            v-if="error" 
            @close="error = ''" 
          />

          <AlertMessage 
            :type="'success'" 
            :message="success" 
            v-if="success" 
            @close="success = ''" 
          />

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
              
              <LoadingState v-if="usersLoading" message="Carregando usuários..." />
              
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
                    :class="['company-input', {'invalid-input': showNewUserPasswordError}]"
                  >
                  <span v-if="showNewUserPasswordError" class="error-text">
                    A senha deve ter pelo menos 6 caracteres
                  </span>
                </div>
                
                <button 
                  type="submit" 
                  class="submit-btn" 
                  :disabled="creatingUser || !isNewUserPasswordValid"
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
          <p v-if="userToDelete">
            Tem certeza que deseja excluir o usuário <strong>{{ userToDelete.username }}</strong>?
          </p>
          <p class="warning-text">Esta ação não pode ser desfeita.</p>
        </div>
        <div class="modal-actions">
          <button class="cancel-btn" @click="showDeleteModal = false">Cancelar</button>
          <button 
            class="confirm-delete-btn" 
            @click="deleteUser" 
            :disabled="deleteLoading"
          >
            <span v-if="deleteLoading" class="loading-spinner-small"></span>
            {{ deleteLoading ? 'Excluindo...' : 'Confirmar Exclusão' }}
          </button>
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
          <AlertMessage 
            :type="'error'" 
            :message="manageUserError" 
            v-if="manageUserError" 
            @close="manageUserError = ''" 
          />

          <AlertMessage 
            :type="'success'" 
            :message="manageUserSuccess" 
            v-if="manageUserSuccess" 
            @close="manageUserSuccess = ''" 
          />
          
          <!-- Seção de alteração de senha -->
          <div class="manage-section">
            <h4>Alterar Senha</h4>
            
            <div class="form-group">
              <label for="new-password">Nova Senha:</label>
              <input 
                type="password" 
                id="new-password" 
                v-model="editUserData.newPassword" 
                :class="['company-input', {'invalid-input': showEditPasswordError}]"
                :disabled="changingPassword"
                placeholder="Digite a nova senha"
              >
              <span v-if="showEditPasswordError" class="error-text">
                A senha deve ter pelo menos 6 caracteres
              </span>
            </div>
            
            <div class="form-group">
              <label for="confirm-password">Confirmar Senha:</label>
              <input 
                type="password" 
                id="confirm-password" 
                v-model="editUserData.confirmPassword" 
                :class="['company-input', {'invalid-input': showPasswordMatchError}]"
                :disabled="changingPassword"
                placeholder="Confirme a nova senha"
              >
              <span v-if="showPasswordMatchError" class="error-text">
                As senhas não coincidem
              </span>
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
            
            <LoadingState v-if="loadingUserGroups" message="Carregando grupos..." />
            
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
// Componente para mensagens de alerta (erro e sucesso)
const AlertMessage = {
  props: {
    type: String,
    message: String
  },
  template: `
    <div :class="type + '-message'">
      <div :class="type + '-icon'">{{ type === 'error' ? '!' : '✓' }}</div>
      <p>{{ message }}</p>
      <button class="close-btn" @click="$emit('close')" aria-label="Fechar">×</button>
    </div>
  `
};

// Componente para estado de carregamento
const LoadingState = {
  props: {
    message: {
      type: String,
      default: 'Carregando...'
    }
  },
  template: `
    <div class="loading-indicator">
      <div class="loading-spinner"></div>
      <p>{{ message }}</p>
    </div>
  `
};

export default {
  name: 'UsersView',
  components: {
    AlertMessage,
    LoadingState
  },
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
    // Verificações de senha para o novo usuário
    isNewUserPasswordValid() {
      return this.newUser.password.length >= 6;
    },
    showNewUserPasswordError() {
      return this.newUser.password.length > 0 && !this.isNewUserPasswordValid;
    },
    
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
    
    // Verificações para alteração de senha
    passwordsValid() {
      return this.editUserData.newPassword && 
             this.editUserData.newPassword === this.editUserData.confirmPassword &&
             this.editUserData.newPassword.length >= 6;
    },
    
    showEditPasswordError() {
      return this.editUserData.newPassword.length > 0 && 
             this.editUserData.newPassword.length < 6;
    },
    
    showPasswordMatchError() {
      return this.editUserData.confirmPassword.length > 0 && 
             this.editUserData.newPassword !== this.editUserData.confirmPassword;
    }
  },
  created() {
    this.checkAdminAccess();
    this.fetchUsers();
  },
  methods: {
    // Helper para fazer requisições API com headers padrão
    async apiRequest(endpoint, options = {}) {
      const userStr = localStorage.getItem('user');
      if (!userStr) {
        this.$router.push('/login');
        throw new Error('Usuário não autenticado');
      }
      
      const user = JSON.parse(userStr);
      
      const defaultOptions = {
        headers: {
          'Content-Type': 'application/json',
          'User-ID': user.id
        }
      };
      
      const mergedOptions = {
        ...defaultOptions,
        ...options,
        headers: {
          ...defaultOptions.headers,
          ...(options.headers || {})
        }
      };
      
      const response = await fetch(endpoint, mergedOptions);
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.message || 'Erro na requisição');
      }
      
      return data;
    },
    
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
      this.usersLoading = true;
      this.error = '';
      
      try {
        const userStr = localStorage.getItem('user');
        if (!userStr) {
          this.$router.push('/login');
          return;
        }
        
        const currentUser = JSON.parse(userStr);
        
        const data = await this.apiRequest('/api/users');
        
        // Filtrar o usuário atual da lista
        this.users = data.users.filter(u => u.id != currentUser.id);
      } catch (error) {
        this.error = error.message || 'Erro ao carregar usuários';
        console.error('Error fetching users:', error);
      } finally {
        this.usersLoading = false;
      }
    },
    
    async createUser() {
      // Verificar se a senha atende aos requisitos
      if (!this.isNewUserPasswordValid) {
        this.error = 'A senha deve ter pelo menos 6 caracteres';
        return;
      }
      
      this.creatingUser = true;
      this.error = '';
      
      try {
        await this.apiRequest('/api/register', {
          method: 'POST',
          body: JSON.stringify(this.newUser)
        });
        
        // Limpar formulário e mostrar mensagem de sucesso
        this.success = `Usuário ${this.newUser.username} criado com sucesso!`;
        this.newUser = {
          username: '',
          password: '',
          is_admin: false
        };
        
        // Atualizar lista de usuários
        await this.fetchUsers();
      } catch (error) {
        this.error = error.message || 'Erro ao criar usuário';
        console.error('Error creating user:', error);
      } finally {
        this.creatingUser = false;
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
        await this.apiRequest(`/api/users/${this.userToDelete.id}`, {
          method: 'DELETE'
        });
        
        // Mostrar mensagem de sucesso
        this.success = `Usuário ${this.userToDelete.username} excluído com sucesso!`;
        
        // Fechar os modais
        this.showDeleteModal = false;
        this.showManageModal = false;
        this.userToDelete = null;
        this.selectedUser = null;
        
        // Atualizar lista de usuários
        await this.fetchUsers();
      } catch (error) {
        this.error = error.message || 'Erro ao excluir usuário';
        console.error('Error deleting user:', error);
        this.showDeleteModal = false;
      } finally {
        this.deleteLoading = false;
      }
    },
    
    goBack() {
      this.$router.push('/');
    },
    
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
        // Buscar todos os grupos
        const data = await this.apiRequest('/api/groups');
        
        // Filtra apenas os grupos que o usuário selecionado tem permissão
        this.userGroups = data.groups.filter(group => 
          group.allowed_users && group.allowed_users.includes(userId)
        );
      } catch (error) {
        this.manageUserError = error.message || 'Erro ao carregar grupos';
        console.error('Error fetching user groups:', error);
      } finally {
        this.loadingUserGroups = false;
      }
    },
    
    async changePassword() {
      if (!this.passwordsValid) return;
      
      this.changingPassword = true;
      this.manageUserError = '';
      
      try {
        await this.apiRequest(`/api/users/${this.selectedUser.id}/password`, {
          method: 'PUT',
          body: JSON.stringify({
            new_password: this.editUserData.newPassword
          })
        });
        
        // Limpar os campos de senha
        this.editUserData.newPassword = '';
        this.editUserData.confirmPassword = '';
        
        this.manageUserSuccess = 'Senha alterada com sucesso!';
      } catch (error) {
        this.manageUserError = error.message || 'Erro ao alterar senha';
        console.error('Error changing password:', error);
      } finally {
        this.changingPassword = false;
      }
    }
  }
}
</script>

<style scoped>
/* Layout principal - versão desktop */
.home-layout {
  position: fixed;
  top: 75px;
  left: 20px;
  right: 20px;
  bottom: 20px;
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
  font-weight: 500;
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
  box-shadow: 0 5px 15px rgba(20, 44, 77, 0.15);
}

/* Botões secundários */
.secondary-button {
  padding: 0.8rem 1.5rem;
  background-color: #f0f0f0;
  border: 1px solid #ddd;
  border-radius: 8px;
  color: #333;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.secondary-button:hover {
  background-color: #e0e0e0;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.users-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 1rem;
}

/* Estados de loading, erro e sucesso */
.loading-indicator, .error-message, .empty-state, .success-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 1rem 1.5rem;
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

.error-message, .success-message {
  flex-direction: row;
  align-items: flex-start;
  text-align: left;
  background-color: #fee2e2;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
  position: relative;
}

.success-message {
  background-color: #d1fae5;
}

.error-message p {
  color: #b91c1c;
  margin: 0 0 0 0.8rem;
  flex: 1;
}

.success-message p {
  color: #065f46;
  margin: 0 0 0 0.8rem;
  flex: 1;
}

.empty-state p {
  color: #666;
  font-style: italic;
}

.close-btn {
  background: none;
  border: none;
  color: inherit;
  cursor: pointer;
  font-size: 1.2rem;
  padding: 0 0.5rem;
  margin-left: auto;
}

/* Grupos do usuário */
.user-groups-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-height: 200px;
  overflow-y: auto;
}

.group-item {
  background-color: #f8f9fa;
  padding: 0.8rem;
  border-radius: 6px;
  border: 1px solid #eaeaea;
}

.group-name {
  font-weight: 600;
  color: #142C4D;
  font-size: 0.95rem;
}

/* Estilo para o modal */
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
}

.modal-content {
  background-color: white;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.3);
  overflow: hidden;
}

.modal-header {
  background-color: #f8f8f8;
  padding: 1.2rem 1.5rem;
  border-bottom: 1px solid #eaeaea;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  color: #333;
  font-size: 1.3rem;
}

.modal-body {
  padding: 1.5rem;
}

.modal-actions {
  display: flex;
  padding: 1.2rem 1.5rem;
  background-color: #f8f8f8;
  border-top: 1px solid #eaeaea;
  justify-content: flex-end;
  gap: 1rem;
}

.manage-user-modal {
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
}

.close-modal-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #666;
}

.manage-section {
  margin-bottom: 1.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #eaeaea;
}

.manage-section:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.manage-section h4 {
  color: #204578;
  font-size: 1.1rem;
  margin-bottom: 1rem;
}

.action-btn {
  padding: 0.7rem 1.2rem;
  border: none;
  border-radius: 6px;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.password-btn {
  background-color: #204578;
  color: white;
}

.password-btn:hover:not(:disabled) {
  background-color: #1a3760;
}

.password-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.cancel-btn {
  background-color: #f0f0f0;
  color: #333;
}

.cancel-btn:hover {
  background-color: #e0e0e0;
}

.confirm-delete-btn {
  background-color: #dc2626;
  color: white;
  display: flex;
  align-items: center;
}

.confirm-delete-btn:hover:not(:disabled) {
  background-color: #b91c1c;
}

.confirm-delete-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.warning-text {
  color: #b91c1c;
  font-weight: 600;
}

/* Animações */
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes fade-in {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>