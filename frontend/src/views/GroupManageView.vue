<template>
  <div class="store-layout">
    <div class="store-container">
      <div class="store-content">
        <div class="page-header">
          <h1>Gerenciar Visibilidade do Grupo</h1>
          <p class="subtitle">Configure quais usuários podem acessar este grupo</p>
          <button v-if="isAdmin" class="delete-btn" @click="showDeleteConfirmation = true">Excluir Grupo</button>
        </div>
        
        <div v-if="error" class="error-alert">
          <span>{{ error }}</span>
          <button class="close-btn" @click="error = ''" aria-label="Fechar">&times;</button>
        </div>
        
        <div v-if="success" class="success-alert">
          <span>{{ success }}</span>
          <button class="close-btn" @click="success = ''" aria-label="Fechar">&times;</button>
        </div>

        <div v-if="loading" class="loading-container">
          <div class="loading-spinner"></div>
          <p>Carregando informações do grupo...</p>
        </div>
        
        <div v-else>
          <!-- Informações do Grupo -->
          <div class="section-card">
            <h2>{{ groupName }}</h2>
            <p class="group-description">
              <span class="label">ID:</span> {{ groupId }}
            </p>
            <p class="group-description">
              <span class="label">Criado em:</span> {{ formatDate(groupCreatedAt) }}
            </p>
            <p class="group-description">
              <span class="label">Criado por:</span> {{ groupCreator }}
            </p>
          </div>
          
          <!-- Usuários com Acesso -->
          <div class="section-card">
            <h2>Usuários com Acesso</h2>
            
            <div v-if="usersWithAccessLoading" class="loading-indicator">
              <div class="loading-spinner"></div>
              <p>Carregando usuários...</p>
            </div>
            
            <div v-else-if="usersWithAccess.length === 0" class="empty-state">
              <p>Nenhum usuário tem acesso a este grupo ainda.</p>
            </div>
            
            <div v-else class="users-list">
              <div v-for="user in usersWithAccess" :key="user.id" class="user-item">
                <div class="user-item-details">
                  <span class="user-name">{{ user.username }}</span>
                  <span class="user-type" :class="{ 'admin-type': user.is_admin }">
                    {{ user.is_admin ? 'Administrador' : 'Usuário Padrão' }}
                  </span>
                </div>
                <div class="user-actions">
                  <button 
                    class="delete-button" 
                    @click="confirmRemoveAccess(user)"
                    title="Remover acesso"
                    v-if="!user.is_admin"
                  >
                    ×
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Adicionar Usuário -->
          <div class="section-card">
            <h2>Adicionar Acesso para Usuários</h2>
            
            <div v-if="availableUsersLoading" class="loading-indicator">
              <div class="loading-spinner"></div>
              <p>Carregando usuários disponíveis...</p>
            </div>
            
            <div v-else-if="availableUsers.length === 0" class="empty-state">
              <p>Não há usuários disponíveis para adicionar.</p>
            </div>
            
            <div v-else>
              <div class="form-group">
                <label for="user-select">Selecione um usuário:</label>
                <select 
                  id="user-select" 
                  v-model="selectedUserId"
                  class="user-select"
                >
                  <option value="" disabled selected>-- Selecione um usuário --</option>
                  <option 
                    v-for="user in availableUsers" 
                    :key="user.id" 
                    :value="user.id"
                  >
                    {{ user.username }}
                  </option>
                </select>
              </div>
              
              <div class="button-container">
                <button 
                  @click="addUserAccess" 
                  class="action-button"
                  :disabled="!selectedUserId"
                >
                  Adicionar Acesso
                </button>
              </div>
            </div>
          </div>
          
          <div class="group-actions">
            <button class="secondary-button" @click="goBack">Voltar</button>
          </div>
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
          <p>Você está prestes a excluir o grupo <strong>{{ groupName }}</strong> e todas as suas empresas.</p>
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
            @click="deleteGroup"
          >
            {{ deletingGroup ? 'Excluindo...' : 'Confirmar Exclusão' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Modal de Confirmação para Remover Acesso -->
    <div class="modal" v-if="showRemoveModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Confirmar Remoção de Acesso</h3>
          <button class="close-modal-btn" @click="showRemoveModal = false">&times;</button>
        </div>
        <div class="modal-body">
          <p>Tem certeza que deseja remover o acesso do usuário <strong>{{ userToRemove?.username }}</strong> a este grupo?</p>
        </div>
        <div class="modal-actions">
          <button class="cancel-btn" @click="showRemoveModal = false">Cancelar</button>
          <button class="confirm-delete-btn" @click="removeUserAccess">Confirmar Remoção</button>
        </div>
      </div>
    </div>
  </div>
</template>
  
<script>
export default {
  name: 'GroupManageView',
  data() {
    return {
      groupId: null,
      groupName: '',
      groupCreatedAt: '',
      groupCreator: '',
      loading: true,
      error: '',
      success: '',
      usersWithAccess: [],
      usersWithAccessLoading: true,
      availableUsers: [],
      availableUsersLoading: true,
      selectedUserId: '',
      showRemoveModal: false,
      userToRemove: null,
      removeLoading: false,
      showDeleteConfirmation: false,
      confirmDeleteText: '',
      deletingGroup: false,
      isAdmin: true // Assuming isAdmin is determined elsewhere in your code
    }
  },
  created() {
    this.checkAdminAccess();
    this.groupId = this.$route.params.id;
    this.fetchGroupData();
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
        this.groupName = data.group.name;
        this.groupCreatedAt = data.group.created_at;
        
        // Buscar o nome do criador
        await this.fetchCreatorName(data.group.created_by);
        
        // Carregar usuários com acesso e usuários disponíveis
        await this.fetchUsersWithAccess();
        await this.fetchAvailableUsers();
        
        this.loading = false;
      } catch (error) {
        this.error = 'Erro ao conectar ao servidor';
        this.loading = false;
        console.error('Error fetching group data:', error);
      }
    },
    async fetchCreatorName(creatorId) {
      try {
        const userStr = localStorage.getItem('user');
        if (!userStr) {
          this.$router.push('/login');
          return;
        }
        
        const user = JSON.parse(userStr);
        
        const response = await fetch(`/api/users/${creatorId}`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'User-ID': user.id
          }
        });
        
        if (!response.ok) {
          this.groupCreator = `Usuário ID: ${creatorId}`;
          return;
        }
        
        const data = await response.json();
        this.groupCreator = data.user.username;
      } catch (error) {
        this.groupCreator = `Usuário ID: ${creatorId}`;
        console.error('Error fetching creator name:', error);
      }
    },
    async fetchUsersWithAccess() {
      try {
        this.usersWithAccessLoading = true;
        const userStr = localStorage.getItem('user');
        if (!userStr) {
          this.$router.push('/login');
          return;
        }
        
        const user = JSON.parse(userStr);
        
        const response = await fetch(`/api/groups/${this.groupId}/permissions`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'User-ID': user.id
          }
        });
        
        if (!response.ok) {
          const data = await response.json();
          this.error = data.message || 'Erro ao carregar permissões do grupo';
          this.usersWithAccessLoading = false;
          return;
        }
        
        const data = await response.json();
        this.usersWithAccess = data.users || [];
        
        // Adicionar administradores à lista (eles sempre têm acesso)
        await this.addAdminsToAccessList();
        
        this.usersWithAccessLoading = false;
      } catch (error) {
        this.error = 'Erro ao conectar ao servidor';
        this.usersWithAccessLoading = false;
        console.error('Error fetching users with access:', error);
      }
    },
    async addAdminsToAccessList() {
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
        
        if (!response.ok) {
          return;
        }
        
        const data = await response.json();
        const adminUsers = data.users.filter(u => u.is_admin);
        
        // Adicionar administradores que não estão já na lista
        for (const admin of adminUsers) {
          if (!this.usersWithAccess.find(u => u.id === admin.id)) {
            this.usersWithAccess.push(admin);
          }
        }
      } catch (error) {
        console.error('Error adding admins to access list:', error);
      }
    },
    async fetchAvailableUsers() {
      try {
        this.availableUsersLoading = true;
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
        
        if (!response.ok) {
          const data = await response.json();
          this.error = data.message || 'Erro ao carregar usuários';
          this.availableUsersLoading = false;
          return;
        }
        
        const data = await response.json();
        
        // Filtrar usuários que não são admin e que não têm acesso já
        const accessUserIds = this.usersWithAccess.map(u => u.id);
        this.availableUsers = data.users.filter(u => 
          !u.is_admin && !accessUserIds.includes(u.id)
        );
        
        this.availableUsersLoading = false;
      } catch (error) {
        this.error = 'Erro ao conectar ao servidor';
        this.availableUsersLoading = false;
        console.error('Error fetching available users:', error);
      }
    },
    async addUserAccess() {
      if (!this.selectedUserId) {
        this.error = 'Selecione um usuário para adicionar';
        return;
      }
      
      try {
        const userStr = localStorage.getItem('user');
        if (!userStr) {
          this.$router.push('/login');
          return;
        }
        
        const user = JSON.parse(userStr);
        
        const response = await fetch(`/api/groups/${this.groupId}/permissions`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'User-ID': user.id
          },
          body: JSON.stringify({
            user_id: this.selectedUserId
          })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
          this.error = data.message || 'Erro ao adicionar acesso';
          return;
        }
        
        // Encontrar o usuário adicionado para mostrar na mensagem de sucesso
        const addedUser = this.availableUsers.find(u => u.id === parseInt(this.selectedUserId));
        this.success = `Acesso concedido para ${addedUser ? addedUser.username : 'o usuário'}`;
        
        // Atualizar as listas
        this.selectedUserId = '';
        await this.fetchUsersWithAccess();
        await this.fetchAvailableUsers();
      } catch (error) {
        this.error = 'Erro ao conectar ao servidor';
        console.error('Error adding user access:', error);
      }
    },
    confirmRemoveAccess(user) {
      this.userToRemove = user;
      this.showRemoveModal = true;
    },
    async removeUserAccess() {
      if (!this.userToRemove) {
        return;
      }
      
      this.removeLoading = true;
      
      try {
        const userStr = localStorage.getItem('user');
        if (!userStr) {
          this.$router.push('/login');
          return;
        }
        
        const user = JSON.parse(userStr);
        
        const response = await fetch(`/api/groups/${this.groupId}/permissions`, {
          method: 'DELETE',
          headers: {
            'Content-Type': 'application/json',
            'User-ID': user.id
          },
          body: JSON.stringify({
            user_id: this.userToRemove.id
          })
        });
        
        if (!response.ok) {
          const data = await response.json();
          this.error = data.message || 'Erro ao remover acesso';
          this.showRemoveModal = false;
          this.removeLoading = false;
          return;
        }
        
        // Mostrar mensagem de sucesso
        this.success = `Acesso removido para ${this.userToRemove.username}`;
        
        // Fechar o modal
        this.showRemoveModal = false;
        this.removeLoading = false;
        
        // Atualizar as listas
        await this.fetchUsersWithAccess();
        await this.fetchAvailableUsers();
        this.userToRemove = null;
      } catch (error) {
        this.error = 'Erro ao conectar ao servidor';
        this.showRemoveModal = false;
        this.removeLoading = false;
        console.error('Error removing user access:', error);
      }
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
    },
    cancelDelete() {
      this.showDeleteConfirmation = false;
      this.confirmDeleteText = '';
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
    goBack() {
      // Navigate back to the group detail view
      this.$router.push(`/groups/${this.groupId}`);
    }
  }
}
</script>

<style scoped>
/* Estilos para o layout da página */
.store-layout {
  position: fixed;
  top: 100px;
  left: 50px;
  right: 50px;
  bottom: 30px;
  display: flex;
  justify-content: center;
  overflow: hidden;
}

.store-container {
  width: 100%;
  max-width: 1200px;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
  overflow: hidden;
  animation: fade-in 0.8s ease-out;
}

.store-content {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 2rem;
  overflow-y: auto;
}

/* Cabeçalho da página */
.page-header {
  position: relative;
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
  font-size: 1rem;
  margin-top: 0.5rem;
}

/* Cartões de seção */
.section-card {
  background-color: #f9f9f9;
  border-radius: 10px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.section-card h2 {
  color: #204578;
  font-size: 1.5rem;
  margin-bottom: 1rem;
  padding-bottom: 0.8rem;
  border-bottom: 1px solid #eaeaea;
}

/* Descrição do grupo */
.group-description {
  margin-bottom: 1rem;
  font-size: 1rem;
  color: #555;
}

.label {
  font-weight: 600;
  color: #333;
  margin-right: 0.5rem;
}

/* Lista de usuários */
.users-list {
  display: flex;
  flex-direction: column;
  gap: 0.7rem;
  margin-top: 1rem;
}

.user-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.8rem 1rem;
  background-color: white;
  border-radius: 6px;
  border: 1px solid #eaeaea;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: all 0.2s ease;
}

.user-item:hover {
  background-color: #f5f9ff;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.user-item-details {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.user-name {
  font-weight: 600;
  font-size: 1rem;
  color: #333;
}

.user-type {
  font-size: 0.85rem;
  color: #666;
  background-color: #f0f0f0;
  padding: 0.2rem 0.5rem;
  border-radius: 10px;
  display: inline-block;
}

.admin-type {
  background-color: #e6f0fd;
  color: #204578;
}

/* Botões de ação */
.user-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.delete-button {
  width: 26px;
  height: 26px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #fee2e2;
  color: #b91c1c;
  border: none;
  border-radius: 50%;
  font-size: 1.3rem;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.2s ease;
}

.delete-button:hover {
  background-color: #fecaca;
  transform: scale(1.1);
}

/* Formulário para adicionar usuários */
.form-group {
  margin-bottom: 1.2rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.8rem;
  font-weight: 600;
  color: #333;
}

.user-select {
  width: 100%;
  padding: 0.7rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  background-color: white;
  font-size: 1rem;
  color: #333;
}

.user-select:focus {
  outline: none;
  border-color: #204578;
  box-shadow: 0 0 0 3px rgba(32, 69, 120, 0.1);
}

.button-container {
  display: flex;
  justify-content: flex-end;
}

.action-button {
  padding: 0.7rem 1.2rem;
  background: linear-gradient(to right, #142C4D, #204578);
  border: none;
  border-radius: 6px;
  color: white;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-button:hover:not(:disabled) {
  background: linear-gradient(to right, #1a3760, #2a5b9e);
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(20, 44, 77, 0.3);
}

.action-button:disabled {
  background: #c0c0c0;
  cursor: not-allowed;
}

/* Botões de ação do grupo */
.group-actions {
  display: flex;
  justify-content: center;
  margin-top: 1.5rem;
}

.secondary-button {
  padding: 0.8rem 2rem;
  background: transparent;
  border: 2px solid #204578;
  border-radius: 6px;
  color: #204578;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.secondary-button:hover {
  background-color: rgba(32, 69, 120, 0.1);
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(20, 44, 77, 0.1);
}

/* Estados vazios e de carregamento */
.empty-state {
  background-color: #f9f9f9;
  padding: 1.5rem;
  border-radius: 6px;
  text-align: center;
  color: #666;
  font-style: italic;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 2rem;
  text-align: center;
}

.loading-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  text-align: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #204578;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Alertas e mensagens */
.error-alert, .success-alert {
  padding: 1rem 1.5rem;
  border-radius: 6px;
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  animation: fade-in 0.3s ease-out;
}

.error-alert {
  background-color: #fee2e2;
  color: #b91c1c;
}

.success-alert {
  background-color: #d1fae5;
  color: #065f46;
}

.close-btn {
  background: none;
  border: none;
  color: inherit;
  font-size: 1.2rem;
  font-weight: bold;
  cursor: pointer;
  padding: 0;
  margin-left: 10px;
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
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.cancel-btn:hover {
  background-color: #e0e0e0;
}

.delete-btn {
  padding: 0.7rem 1.2rem;
  background: linear-gradient(to right, #991b1b, #b91c1c);
  border: none;
  border-radius: 8px;
  color: white;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.delete-btn:hover:not(:disabled) {
  background: linear-gradient(to right, #7f1d1d, #991b1b);
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(185, 28, 28, 0.3);
}

.delete-btn:disabled {
  background: #c0c0c0;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* Modal para remover acesso */
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
}

.modal-content {
  width: 90%;
  max-width: 450px;
  background-color: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  animation: fade-in 0.3s ease-out;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  background-color: #f8f8f8;
  border-bottom: 1px solid #eaeaea;
}

.close-modal-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  line-height: 1;
  color: #666;
  cursor: pointer;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.8rem;
  padding: 1rem 1.5rem;
  background-color: #f8f8f8;
  border-top: 1px solid #eaeaea;
}

.confirm-delete-btn {
  padding: 0.7rem 1.2rem;
  background-color: #b91c1c;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.confirm-delete-btn:hover {
  background-color: #991b1b;
}

@keyframes fade-in {
  0% { opacity: 0; }
  100% { opacity: 1; }
}

@media (max-width: 1024px) {
  .store-layout {
    left: 20px;
    right: 20px;
  }
  
  .section-card {
    padding: 1.2rem;
  }
}
</style>