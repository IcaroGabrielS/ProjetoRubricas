<template>
  <div>
    <!-- Conteúdo principal -->
    <div class="home-layout">
      <!-- Painel com informações gerais (visualmente à esquerda) -->
      <div class="content-panel">
        <div class="content-wrapper">
          <div class="home-header">
            <h1>Gerenciar Grupo</h1>
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
            <!-- Informações do Grupo -->
            <div class="dashboard-summary">
              <div class="dashboard-item">
                <h3>{{ groupName }}</h3>
                <div class="info-details">
                  <p><span class="info-label">ID:</span> {{ groupId }}</p>
                  <p><span class="info-label">Criado em:</span> {{ formatDate(groupCreatedAt) }}</p>
                  <p><span class="info-label">Criado por:</span> {{ groupCreator }}</p>
                </div>
              </div>
            </div>

            <!-- Botão de excluir grupo -->
            <div v-if="isAdmin" class="dashboard-summary">
              <div class="dashboard-item danger-zone">
                <h3>Zona de Perigo</h3>
                <p>Cuidado! As ações abaixo são irreversíveis.</p>
                <div class="danger-actions">
                  <button class="delete-btn" @click="showDeleteConfirmation = true">
                    Excluir Grupo
                  </button>
                </div>
              </div>
            </div>
            
            <!-- Botões de ação -->
            <div class="quick-actions">
              <button class="secondary-button" @click="goBack">Voltar para o Grupo</button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Painel de gerenciamento de acesso (visualmente à direita) -->
      <div class="content-panel">
        <div class="content-wrapper">
          <div class="home-header">
            <h1>Gerenciar Visibilidade</h1>
          </div>

          <div v-if="loading" class="loading-indicator">
            <div class="loading-spinner"></div>
            <p>Carregando permissões...</p>
          </div>

          <div v-else>
            <!-- Usuários com Acesso -->
            <div class="dashboard-summary">
              <div class="dashboard-item">
                <h3>Usuários com Acesso</h3>
                <p>Estes usuários podem visualizar e interagir com este grupo.</p>
              
                <div v-if="usersWithAccessLoading" class="loading-indicator">
                  <div class="loading-spinner"></div>
                  <p>Carregando usuários...</p>
                </div>
                
                <div v-else-if="usersWithAccess.length === 0" class="empty-state">
                  <p>Nenhum usuário tem acesso a este grupo ainda.</p>
                </div>
                
                <div v-else class="stores-list">
                  <div 
                    v-for="user in usersWithAccess" 
                    :key="user.id" 
                    class="store-item"
                  >
                    <div class="store-item-details">
                      <span class="store-name">{{ user.username }}</span>
                      <span class="store-info" :class="{ 'admin-type': user.is_admin }">
                        {{ user.is_admin ? 'Administrador' : 'Usuário Padrão' }}
                      </span>
                    </div>
                    <div class="store-item-actions">
                      <button 
                        v-if="!user.is_admin" 
                        class="delete-button" 
                        @click="confirmRemoveAccess(user)"
                        title="Remover acesso"
                      >
                        ×
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Adicionar Usuário -->
            <div class="dashboard-summary">
              <div class="dashboard-item">
                <h3>Adicionar Acesso para Usuários</h3>
                
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
            </div>
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
    <div v-if="showRemoveModal" class="modal-overlay">
      <div class="modal-container">
        <div class="modal-header">
          <h3>Confirmar Remoção de Acesso</h3>
        </div>
        <div class="modal-body">
          <p>Tem certeza que deseja remover o acesso do usuário <strong>{{ userToRemove?.username }}</strong> a este grupo?</p>
        </div>
        <div class="modal-footer">
          <button class="cancel-btn" @click="showRemoveModal = false">Cancelar</button>
          <button 
            class="delete-btn"
            :disabled="removeLoading"
            @click="removeUserAccess"
          >
            {{ removeLoading ? 'Removendo...' : 'Confirmar Remoção' }}
          </button>
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

.info-details {
  margin-top: 0.8rem;
  color: #555;
  font-size: 0.95rem;
}

.info-details p {
  margin-bottom: 0.5rem;
}

.info-label {
  font-weight: 600;
  color: #333;
  margin-right: 0.3rem;
}

/* Zona de perigo */
.dashboard-item.danger-zone {
  background-color: #fee2e2;
  border: 1px solid #fca5a5;
}

.dashboard-item.danger-zone h3 {
  color: #b91c1c;
}

.danger-actions {
  margin-top: 1rem;
  display: flex;
  justify-content: flex-end;
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

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
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

.empty-state {
  background-color: #f9f9f9;
  padding: 1.5rem;
  border-radius: 6px;
  text-align: center;
  color: #666;
  font-style: italic;
}

/* Usuários com acesso */
.stores-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-top: 0.8rem;
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
  background-color: #f0f0f0;
  padding: 0.2rem 0.5rem;
  border-radius: 10px;
  display: inline-block;
  width: fit-content;
}

.admin-type {
  background-color: #e6f0fd;
  color: #204578;
}

.store-item-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

/* Botão para remover acesso */
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
  margin-bottom: 0.6rem;
  font-size: 1rem;
  font-weight: 600;
  color: #333;
}

.user-select {
  width: 100%;
  padding: 0.8rem 1rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 0.95rem;
  background-color: white;
  transition: all 0.2s ease;
}

.user-select:focus {
  border-color: #204578;
  outline: none;
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

/* Botões de ação */
.quick-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 0;
  margin-top: auto;
}

.secondary-button {
  flex: 1;
  min-width: 150px;
  padding: 0.8rem;
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

.delete-btn {
  padding: 0.7rem 1.2rem;
  background-color: #dc2626;
  border: none;
  border-radius: 6px;
  color: white;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.delete-btn:hover:not(:disabled) {
  background-color: #b91c1c;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(185, 28, 28, 0.3);
}

.delete-btn:disabled {
  background-color: #ef4444;
  opacity: 0.7;
  cursor: not-allowed;
}

/* Modals */
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

@keyframes fade-in {
  0% { opacity: 0; }
  100% { opacity: 1; }
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

.warning-icon {
  color: #b91c1c;
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

.close-btn {
  background: none;
  border: none;
  font-size: 1.25rem;
  font-weight: bold;
  color: inherit;
  cursor: pointer;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Dispositivos móveis */
@media (max-width: 1024px) {
  .home-layout {
    flex-direction: column;
    top: 80px;
    left: 20px;
    right: 20px;
    bottom: 20px;
  }
  
  .content-panel {
    width: 100%;
    height: 50%;
    min-height: 300px;
  }
  
  .content-wrapper {
    padding: 1.5rem;
  }
  
  .home-header h1 {
    font-size: 1.8rem;
  }
}
</style>