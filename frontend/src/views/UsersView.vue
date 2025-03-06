<template>
  <div class="store-layout">
    <div class="store-container">
      <div class="store-content">
        <div class="page-header">
          <h1>Gerenciar Usuários</h1>
          <p class="subtitle">Crie e gerencie contas de usuários</p>
        </div>
        
        <div v-if="error" class="error-alert">
          <span>{{ error }}</span>
          <button class="close-btn" @click="error = ''" aria-label="Fechar">&times;</button>
        </div>
        
        <div v-if="success" class="success-alert">
          <span>{{ success }}</span>
          <button class="close-btn" @click="success = ''" aria-label="Fechar">&times;</button>
        </div>
        
        <!-- Layout de duas seções lado a lado -->
        <div class="sections-row">
          <!-- Formulário para criar usuários -->
          <div class="section-card create-section">
            <h2>Criar Novo Usuário</h2>
            <form class="user-form" @submit.prevent="createUser">
              <div class="form-row">
                <div class="form-group">
                  <label for="username">Nome de Usuário</label>
                  <input 
                    type="text" 
                    id="username" 
                    v-model="newUser.username" 
                    required
                    placeholder="ID do novo Usuário"
                  >
                </div>
                
                <div class="form-group">
                  <label for="password">Senha</label>
                  <input 
                    type="password" 
                    id="password" 
                    v-model="newUser.password" 
                    required
                    placeholder="Nova Senha"
                  >
                </div>
              </div>
              
              <div class="form-group checkbox-group">
                <input 
                  type="checkbox" 
                  id="is_admin" 
                  v-model="newUser.is_admin"
                >
                <label for="is_admin">Usuário Administrador</label>
              </div>
              
              <div class="button-container">
                <button type="submit" class="action-button">Criar Usuário</button>
              </div>
            </form>
          </div>
          
          <!-- Lista de usuários -->
          <div class="section-card users-section">
            <h2>Usuários Existentes</h2>
            
            <div v-if="usersLoading" class="loading-indicator">
              <div class="loading-spinner"></div>
              <p>Carregando usuários...</p>
            </div>
            
            <div v-else-if="users.length === 0" class="empty-state">
              <p>Não há usuários cadastrados além do seu.</p>
            </div>
            
            <div v-else class="users-list">
              <div v-for="user in users" :key="user.id" class="user-item">
                <div class="user-item-details">
                  <span class="user-name">{{ user.username }}</span>
                  <span class="user-type" :class="{ 'admin-type': user.is_admin }">
                    {{ user.is_admin ? 'Administrador' : 'Usuário Padrão' }}
                  </span>
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
      }
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
      } catch (error) {
        this.error = 'Erro ao conectar ao servidor';
        console.error('Error creating user:', error);
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
}

.create-section {
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

.form-row {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 1rem;
}

.form-row .form-group {
  flex: 1;
}

.user-form {
  display: flex;
  flex-direction: column;
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

.form-group input[type="text"],
.form-group input[type="password"] {
  width: 100%;
  padding: 0.9rem;
  border: 2px solid #e1e1e1;
  border-radius: 8px;
  font-size: 1rem;
  color: #333;
  transition: all 0.3s ease;
  background-color: #fff;
}

.form-group input:focus {
  border-color: #204578;
  box-shadow: 0 0 0 3px rgba(32, 69, 120, 0.15);
  outline: none;
}

.checkbox-group {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  margin-top: 0.5rem;
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
}

.error-alert .close-btn {
  color: #b91c1c;
}

.success-alert .close-btn {
  color: #047857;
}

.loading-indicator, .empty-state {
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

/* Animações */
@keyframes fade-in {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>