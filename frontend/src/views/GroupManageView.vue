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
      
      try {
        const date = new Date(dateString);
        
        if (isNaN(date.getTime())) {
          return dateString; // Retorna a string original se não for uma data válida
        }
        
        return date.toLocaleString('pt-BR', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit'
        });
      } catch (error) {}}}}
       </script>