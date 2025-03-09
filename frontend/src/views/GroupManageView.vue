<template>
    <div class="store-layout">
      <div class="store-container">
        <div class="store-content">
          <div class="page-header">
            <h1>Gerenciar Visibilidade do Grupo</h1>
            <p class="subtitle">Configure quais usuários podem acessar este grupo</p>
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
          
          <div v-else class="sections-row">
            <!-- Informações do Grupo -->
            <div class="section-card group-info-section">
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
            <div class="section-card users-section">
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
          </div>
          
          <!-- Adicionar Usuário -->
          <div class="section-card add-user-section">
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
      removeLoading: false
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
      } catch (error) {
        return dateString;
      }
    },
    goBack() {
      this.$router.push('/');
    }
  }
}
</script>

<style scoped>
.store-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  width: 100%;
  overflow: hidden;
}

.store-container {
  flex: 1;
  overflow-y: auto;
  padding: 2rem 3rem;
  display: flex;
  justify-content: center;
}

.store-content {
  width: 100%;
  min-width: 1200px;
  max-width: 85%;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
  padding: 2.5rem 3rem;
  animation: fade-in 0.6s ease-out;
  overflow-y: auto;
  max-height: calc(100vh - 4rem);
}

.page-header {
  text-align: left;
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
  font-size: 1.1rem;
}

.sections-row {
  display: flex;
  gap: 2.5rem;
  margin-bottom: 2rem;
}

.section-card {
  background-color: #f9f9f9;
  border-radius: 8px;
  padding: 1.8rem;
  flex: 1;
  margin-bottom: 2rem;
}

.group-info-section {
  flex-basis: 42%;
}

.users-section {
  flex-basis: 58%;
}

.section-card h2 {
  color: #204578;
  font-size: 1.5rem;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid #e1e1e1;
  padding-bottom: 0.8rem;
}

.group-description {
  margin-bottom: 1rem;
  line-height: 1.6;
  color: #444;
}

.label {
  font-weight: 600;
  color: #333;
  margin-right: 0.5rem;
}

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

.user-select {
  width: 100%;
  padding: 0.9rem;
  border: 2px solid #e1e1e1;
  border-radius: 8px;
  font-size: 1rem;
  color: #333;
  transition: all 0.3s ease;
  background-color: #fff;
  font-family: 'Outfit', sans-serif;
}

.user-select:focus {
  border-color: #204578;
  box-shadow: 0 0 0 3px rgba(32, 69, 120, 0.15);
  outline: none;
}

.button-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 1.5rem;
}

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

.action-button {
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
}

.action-button:hover {
  background: linear-gradient(to right, #1a3760, #2a5b9e);
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(20, 44, 77, 0.3);
}

.action-button:disabled {
  background: #cccccc;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

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

.group-actions {
  display: flex;
  justify-content: center;
  margin-top: 1rem;
}

.error-alert, .success-alert {
  padding: 1rem 1.5rem;
  border-radius: 8px;
  margin-bottom: 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 1rem;
  animation: fade-in 0.3s ease;
}

.error-alert {
  background-color: #fee2e2;
  color: #b91c1c;
}

.success-alert {
  background-color: #d1fae5;
  color: #047857;
}

.close-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.3rem;
  padding: 0 0.5rem;
  box-shadow: none;
}

.error-alert .close-btn {
  color: #b91c1c;
}

.success-alert .close-btn {
  color: #047857;
}

.loading-container, .loading-indicator, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem 0;
  text-align: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(32, 69, 120, 0.1);
  border-top: 4px solid #204578;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

.empty-state p {
  color: #666;
  font-style: italic;
  font-size: 1.1rem;
}

/* Modal styles */
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
  box-shadow: none;
}

.modal-body {
  padding: 1.5rem;
}

.modal-body p {
  margin-bottom: 0.8rem;
  font-size: 1.1rem;
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
  box-shadow: none;
}

.cancel-btn:hover {
  background-color: #e0e0e0;
  box-shadow: none;
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
  box-shadow: none;
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

/* Responsividade */
@media (max-width: 1280px) {
  .store-content {
    min-width: 95%;
    max-width: 95%;
    padding: 2rem;
  }
}

@media (max-width: 992px) {
  .sections-row {
    flex-direction: column;
  }
  
  .section-card {
    margin-bottom: 1.5rem;
  }
}

@media (max-width: 768px) {
  .store-container {
    padding: 1.5rem;
  }
  
  .store-content {
    padding: 1.5rem;
  }
  
  .page-header h1 {
    font-size: 1.8rem;
  }
}

@media (max-width: 576px) {
  .store-container {
    padding: 1rem;
  }
  
  .store-content {
    padding: 1rem;
    border-radius: 8px;
  }
  
  .button-container {
    flex-direction: column;
  }
  
  .action-button, .secondary-button {
    width: 100%;
    margin: 0.5rem 0;
  }
}
</style>