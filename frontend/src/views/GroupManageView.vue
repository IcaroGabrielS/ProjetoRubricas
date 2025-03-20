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
  background-color: #f0f7ff; /* Fundo azulado similar ao de UsersView */
  border: 1px solid #d0e1fd;
}

.company-form {
  margin-top: 1rem;
}

/* Estilo dos inputs similar ao UsersView */
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
  margin-bottom: 15px;
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

/* Botão com gradiente igual ao de criar usuário */
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

.delete-btn {
  padding: 0.8rem 1.5rem;
  background-color: #ef4444;
  border: none;
  border-radius: 8px;
  color: white;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.delete-btn:hover:not(:disabled) {
  background-color: #dc2626;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(220, 38, 38, 0.3);
}

.delete-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
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

.confirmation-input {
  margin-top: 1.5rem;
}

.confirmation-input label {
  display: block;
  margin-bottom: 0.6rem;
  font-size: 1rem;
  font-weight: 600;
  color: #333;
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
  background: #EF4444;
  border: none;
  border-radius: 8px;
  color: white;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.confirm-delete-btn:hover:not(:disabled) {
  background: linear-gradient(to right, #d63031, #e84393);
  box-shadow: 0 5px 15px rgba(214, 48, 49, 0.3);
}

.confirm-delete-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

/* Informações detalhadas */
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

/* Seleção de usuário */
.user-select {
  margin-bottom: 1rem;
}

.button-container {
  display: flex;
  justify-content: flex-end;
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