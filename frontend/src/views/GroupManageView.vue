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
            <div class="users-actions">
              <button class="secondary-button" @click="goBack">Voltar para o Grupo</button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Painel direito - agora com criação de empresa e gerenciamento de acesso -->
      <div class="content-panel">
        <div class="content-wrapper">
          <!-- Seção de Criar Nova Empresa -->
          <div class="home-header">
            <h1>Gerenciar Recursos</h1>
          </div>

          <div v-if="loading" class="loading-indicator">
            <div class="loading-spinner"></div>
            <p>Carregando recursos...</p>
          </div>

          <div v-else>
            <!-- Criar nova empresa -->
            <div class="dashboard-summary">
              <div class="dashboard-item create-company">
                <h3>Criar Nova Empresa</h3>
                <p>Adicione uma nova empresa ao grupo</p>
                
                <form @submit.prevent="createCompany" class="company-form">
                  <div class="form-group">
                    <label for="companyName">Nome da Empresa:</label>
                    <input 
                      type="text" 
                      id="companyName" 
                      v-model="newCompany.name" 
                      required 
                      placeholder="Nome da Empresa"
                      class="company-input"
                    >
                  </div>
                  
                  <div class="form-group">
                    <label for="companyCNPJ">CNPJ:</label>
                    <input 
                      type="text" 
                      id="companyCNPJ" 
                      v-model="newCompany.cnpj" 
                      @input="formatCNPJ"
                      required 
                      placeholder="XX.XXX.XXX/XXXX-XX"
                      :class="{ 'invalid-input': cnpjError }"
                      class="company-input"
                    >
                    <small v-if="cnpjError" class="error-text">{{ cnpjError }}</small>
                  </div>
                  
                  <button 
                    type="submit" 
                    class="submit-btn" 
                    :disabled="creatingCompany || cnpjError !== ''"
                  >
                    <span v-if="creatingCompany" class="loading-spinner-small"></span>
                    {{ creatingCompany ? 'Criando...' : 'Criar Empresa' }}
                  </button>
                </form>
              </div>
            </div>

            <!-- Adicionar Usuário (movido para cima) -->
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
                      class="user-select company-input"
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
                      class="submit-btn"
                      :disabled="!selectedUserId"
                    >
                      Adicionar Acesso
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <!-- Usuários com Acesso -->
            <div class="dashboard-summary">
              <div class="dashboard-item">
                <h3>Usuários com Acesso</h3>
                <p>Estes usuários podem visualizar e interagir com este grupo.</p>
                
                <!-- Pesquisa de usuários -->
                <div class="search-container">
                  <div class="search-box">
                    <input 
                      type="text" 
                      v-model="searchQuery" 
                      placeholder="Procurar por nome de usuário..."
                      class="search-input"
                    >
                  </div>
                </div>
              
                <div v-if="usersWithAccessLoading" class="loading-indicator">
                  <div class="loading-spinner"></div>
                  <p>Carregando usuários...</p>
                </div>
                
                <div v-else-if="filteredUsersWithAccess.length === 0" class="empty-state">
                  <p>Nenhum usuário tem acesso a este grupo ainda.</p>
                </div>
                
                <div v-else class="users-list">
                  <div 
                    v-for="user in filteredUsersWithAccess" 
                    :key="user.id" 
                    class="user-item"
                  >
                    <div class="user-item-details">
                      <span class="user-name">{{ user.username }}</span>
                      <span class="user-type" :class="{ 'admin-type': user.is_admin }">
                        {{ user.is_admin ? 'Administrador' : 'Usuário Padrão' }}
                      </span>
                    </div>
                    <div class="user-actions">
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
          </div>
        </div>
      </div>
    </div>

    <!-- Modal de Confirmação de Exclusão -->
    <div v-if="showDeleteConfirmation" class="modal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Confirmação de Exclusão</h3>
          <button class="close-modal-btn" @click="cancelDelete">&times;</button>
        </div>
        <div class="modal-body">
          <p>Você está prestes a excluir o grupo <strong>{{ groupName }}</strong> e todas as suas empresas.</p>
          <p class="warning-text">Esta ação não pode ser desfeita!</p>
          
          <div class="confirmation-input">
            <label for="confirmText">Digite "EXCLUIR" para confirmar:</label>
            <input 
              type="text" 
              id="confirmText" 
              v-model="confirmDeleteText" 
              placeholder="EXCLUIR" 
              class="company-input"
            />
          </div>
        </div>
        <div class="modal-actions">
          <button class="cancel-btn" @click="cancelDelete">Cancelar</button>
          <button 
            class="confirm-delete-btn"
            :disabled="confirmDeleteText !== 'EXCLUIR' || deletingGroup"
            @click="deleteGroup"
          >
            {{ deletingGroup ? 'Excluindo...' : 'Confirmar Exclusão' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Modal de Confirmação para Remover Acesso -->
    <div v-if="showRemoveModal" class="modal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Confirmar Remoção de Acesso</h3>
          <button class="close-modal-btn" @click="showRemoveModal = false">&times;</button>
        </div>
        <div class="modal-body">
          <p>Tem certeza que deseja remover o acesso do usuário <strong>{{ userToRemove?.username }}</strong> a este grupo?</p>
          <p class="warning-text">Esta ação não pode ser desfeita.</p>
        </div>
        <div class="modal-actions">
          <button class="cancel-btn" @click="showRemoveModal = false">Cancelar</button>
          <button 
            class="confirm-delete-btn"
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
      isAdmin: true,
      // Novos campos para criação de empresa
      newCompany: {
        name: '',
        cnpj: ''
      },
      cnpjError: '',
      creatingCompany: false,
      // Novo campo para pesquisa de usuários
      searchQuery: ''
    }
  },
  computed: {
    // Filtrar usuários com acesso baseado na pesquisa
    filteredUsersWithAccess() {
      if (!this.searchQuery) {
        return this.usersWithAccess;
      }
      
      const query = this.searchQuery.toLowerCase();
      return this.usersWithAccess.filter(user => 
        user.username.toLowerCase().includes(query)
      );
    }
  },
  created() {
    this.checkAdminAccess();
    this.groupId = this.$route.params.id;
    if (!this.groupId) {
      console.error('ID de grupo não fornecido:', this.$route.params.id);
      this.error = 'ID de grupo não fornecido';
      this.loading = false;
      return;
    }
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
        
        const currentUser = JSON.parse(userStr);
        console.log('Fetching data for group:', this.groupId);
        
        const response = await fetch(`/api/groups/${this.groupId}`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'User-ID': currentUser.id
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
        if (data.group.created_by) {
          await this.fetchCreatorName(data.group.created_by);
        }
        
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
        
        const currentUser = JSON.parse(userStr);
        
        const response = await fetch(`/api/users/${creatorId}`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'User-ID': currentUser.id
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
        
        const currentUser = JSON.parse(userStr);
        
        const response = await fetch(`/api/groups/${this.groupId}/permissions`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'User-ID': currentUser.id
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
        
        const currentUser = JSON.parse(userStr);
        
        const response = await fetch('/api/users', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'User-ID': currentUser.id
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
        
        const currentUser = JSON.parse(userStr);
        
        const response = await fetch('/api/users', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'User-ID': currentUser.id
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
        
        const currentUser = JSON.parse(userStr);
        
        const response = await fetch(`/api/groups/${this.groupId}/permissions`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'User-ID': currentUser.id
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
        
        const currentUser = JSON.parse(userStr);
        
        const response = await fetch(`/api/groups/${this.groupId}/permissions`, {
          method: 'DELETE',
          headers: {
            'Content-Type': 'application/json',
            'User-ID': currentUser.id
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
        const currentUser = JSON.parse(userStr);
        console.log('Deleting group:', this.groupId);
        
        const response = await fetch(`/api/groups/${this.groupId}`, {
          method: 'DELETE',
          headers: {
            'Content-Type': 'application/json',
            'User-ID': currentUser.id
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
      // Navegação para o detalhe do grupo usando o UUID
      this.$router.push(`/groups/${this.groupId}`);
    },
    
    // Métodos para criação de empresa
    formatCNPJ() {
      // Remove qualquer caractere que não seja dígito
      let cnpj = this.newCompany.cnpj.replace(/\D/g, '');
      
      // Limita a 14 dígitos
      cnpj = cnpj.substring(0, 14);
      
      // Aplica a máscara XX.XXX.XXX/XXXX-XX
      if (cnpj.length > 0) {
        cnpj = cnpj.replace(/^(\d{2})(\d)/, '$1.$2');
        cnpj = cnpj.replace(/^(\d{2})\.(\d{3})(\d)/, '$1.$2.$3');
        cnpj = cnpj.replace(/\.(\d{3})(\d)/, '.$1/$2');
        cnpj = cnpj.replace(/(\d{4})(\d)/, '$1-$2');
      }
      
      this.newCompany.cnpj = cnpj;
      this.validateCNPJ();
    },
    validateCNPJ() {
      const cnpj = this.newCompany.cnpj.replace(/\D/g, '');
      
      if (cnpj.length === 0) {
        this.cnpjError = '';
        return;
      }
      
      if (cnpj.length !== 14) {
        this.cnpjError = 'CNPJ deve conter 14 dígitos.';
        return;
      }
      
      // Verificar se todos os dígitos são iguais
      if (/^(\d)\1+$/.test(cnpj)) {
        this.cnpjError = 'CNPJ inválido.';
        return;
      }
      
      // Validação dos dígitos verificadores
      // Primeiro dígito verificador
      let soma = 0;
      let peso = 2;
      
      for (let i = 11; i >= 0; i--) {
        soma += parseInt(cnpj.charAt(i)) * peso;
        peso = peso === 9 ? 2 : peso + 1;
      }
      
      let digito = 11 - (soma % 11);
      if (digito > 9) digito = 0;
      
      if (parseInt(cnpj.charAt(12)) !== digito) {
        this.cnpjError = 'CNPJ inválido.';
        return;
      }
      
      // Segundo dígito verificador
      soma = 0;
      peso = 2;
      
      for (let i = 12; i >= 0; i--) {
        soma += parseInt(cnpj.charAt(i)) * peso;
        peso = peso === 9 ? 2 : peso + 1;
      }
      
      digito = 11 - (soma % 11);
      if (digito > 9) digito = 0;
      
      if (parseInt(cnpj.charAt(13)) !== digito) {
        this.cnpjError = 'CNPJ inválido.';
        return;
      }
      
      this.cnpjError = '';
    },
    async createCompany() {
      if (this.cnpjError) {
        return;
      }
      
      try {
        this.creatingCompany = true;
        const userStr = localStorage.getItem('user');
        if (!userStr) {
          this.$router.push('/login');
          return;
        }
        const currentUser = JSON.parse(userStr);
        
        const response = await fetch(`/api/groups/${this.groupId}/companies`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'User-ID': currentUser.id
          },
          body: JSON.stringify(this.newCompany)
        });
        
        const data = await response.json();
        
        if (!response.ok) {
          this.error = data.message || 'Erro ao criar empresa';
          this.creatingCompany = false;
          return;
        }
        
        // Sucesso na criação da empresa
        this.success = `Empresa ${this.newCompany.name} criada com sucesso!`;
        
        // Limpar o formulário
        this.newCompany = {
          name: '',
          cnpj: ''
        };
        
        this.creatingCompany = false;
      } catch (error) {
        this.error = 'Erro ao conectar ao servidor';
        this.creatingCompany = false;
        console.error('Error creating company:', error);
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
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
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
  background-color: #eeecff; /* Adaptado para combinar com a cor do botão #564fcc */
  border: 1px solid #d8d6f8;
}

/* Zona de perigo */
.danger-zone {
  background-color: #fee2e2; /* Cor suave com base no botão vermelho #ef4444 */
  border: 1px solid #fecaca;
}

.company-form {
  margin-top: 1rem;
}

/* Estilo dos inputs similar ao UsersView */
.company-input {
  width: 100%;
  padding: 0.9rem;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 1rem;
  color: #333;
  background-color: #fff;
}

.company-input:focus {
  border-color: #564fcc;
  box-shadow: 0 0 0 3px rgba(86, 79, 204, 0.15);
  outline: none;
}

.invalid-input {
  border-color: #ef4444;
  background-color: #fee2e2;
}

.error-text {
  color: #ef4444;
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
  margin-bottom: 15px;
  color: #333;
  background-color: #f9f9f9;
}

.search-input:focus {
  border-color: #564fcc;
  box-shadow: 0 0 0 3px rgba(86, 79, 204, 0.15);
  outline: none;
  background-color: #fff;
}

.search-icon {
  position: absolute;
  right: 15px;
  top: 50%;
  color: #666;
}

/* Formulários */
.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #333;
}

/* Botões */
.submit-btn, .secondary-button {
  display: inline-block;
  padding: 0.8rem 1.5rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  border: none;
  font-size: 1rem;
  text-align: center;
}

.submit-btn {
  background-color: #564fcc;
  color: white;
}

.submit-btn:hover:not(:disabled) {
  background-color: #675ff5;
}

.submit-btn:disabled {
  background-color: #a8a5e0;
  cursor: not-allowed;
}

.secondary-button {
  background-color: #e5e5e5;
  color: #333;
}

.secondary-button:hover {
  background-color: #b7b7b7;
}

.delete-btn {
  background-color: #ef4444;
  color: white;
  padding: 0.8rem 1.5rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  border: none;
  font-size: 1rem;
}

.delete-btn:hover {
  background-color: #ff5252;
}

/* Lista de usuários */
.users-list {
  margin-top: 1rem;
}

.user-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #eaeaea;
}

.user-item:last-child {
  border-bottom: none;
}

.user-item-details {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-weight: 600;
  color: #333;
}

.user-type {
  font-size: 0.85rem;
  color: #666;
  margin-top: 0.2rem;
}

.admin-type {
  color: #564fcc;
  font-weight: 500;
}

.user-actions {
  display: flex;
  gap: 0.5rem;
}

.delete-button {
  background-color: #ef4444;
  color: white;
  border: none;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  cursor: pointer;
}

.delete-button:hover {
  background-color: #ff5252;
}

/* Estados de carregamento e vazios */
.loading-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2rem;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(86, 79, 204, 0.2);
  border-top: 4px solid #564fcc;
  border-radius: 50%;
  margin-bottom: 1rem;
}

.loading-spinner-small {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid #fff;
  border-radius: 50%;
  margin-right: 8px;
}

.empty-state {
  text-align: center;
  padding: 2rem;
  color: #666;
}

/* Informações detalhadas */
.info-details {
  margin-top: 0.8rem;
}

.info-label {
  font-weight: 600;
  color: #333;
}

/* Mensagens de erro e sucesso */
.error-message, .success-message {
  display: flex;
  align-items: center;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
}

.error-message {
  background-color: #fee2e2;
  border: 1px solid #fecaca;
}

.success-message {
  background-color: #ecfdf5;
  border: 1px solid #a7f3d0;
}

.error-icon, .success-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  margin-right: 0.8rem;
  font-weight: bold;
}

.error-icon {
  background-color: #ef4444;
  color: white;
}

.success-icon {
  background-color: #10b981;
  color: white;
}

.close-btn {
  margin-left: auto;
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  color: #666;
}

/* Modal */
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
  background-color: white;
  border-radius: 8px;
  width: 500px;
  max-width: 90%;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.modal-header {
  padding: 1rem;
  background-color: #ef4444; /* Cor vermelha para o cabeçalho do modal de exclusão */
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.close-modal-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: white;
  cursor: pointer;
}

.modal-body {
  padding: 1.5rem;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1rem;
  background-color: #f9f9f9;
}

.cancel-btn {
  background-color: #e5e5e5;
  color: #333;
  padding: 0.8rem 1.5rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  border: none;
}

.cancel-btn:hover {
  background-color: #b7b7b7;
}

.confirm-delete-btn {
  background-color: #ef4444;
  color: white;
  padding: 0.8rem 1.5rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  border: none;
}

.confirm-delete-btn:hover:not(:disabled) {
  background-color: #ff5252;
}

.confirm-delete-btn:disabled {
  background-color: #fca5a5;
  cursor: not-allowed;
}

.warning-text {
  color: #ef4444;
  font-weight: 600;
  margin: 1rem 0;
}

.confirmation-input {
  margin-top: 1.5rem;
}

/* Botões de ação */
.users-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
}

.button-container {
  margin-top: 1rem;
  display: flex;
  justify-content: flex-end;
}

.danger-actions {
  margin-top: 1rem;
}

/* Select boxes e dropdowns */
.user-select {
  width: 100%;
  padding: 0.9rem;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 1rem;
  color: #333;
  background-color: #fff;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' fill='%23333' viewBox='0 0 16 16'%3E%3Cpath d='M7.247 11.14 2.451 5.658C1.885 5.013 2.345 4 3.204 4h9.592a1 1 0 0 1 .753 1.659l-4.796 5.48a1 1 0 0 1-1.506 0z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 1rem center;
}

.user-select:focus {
  border-color: #564fcc;
  box-shadow: 0 0 0 3px rgba(86, 79, 204, 0.15);
  outline: none;
}

/* Responsividade para dispositivos móveis */
@media (max-width: 768px) {
  .home-layout {
    flex-direction: column;
    top: 65px;
  }
  
  .content-panel {
    width: 100%;
    margin-bottom: 15px;
  }
  
  .home-header h1 {
    font-size: 1.8rem;
  }
  
  .users-actions {
    flex-direction: column;
  }
  
  .submit-btn, .secondary-button, .delete-btn {
    width: 100%;
  }
}
</style>