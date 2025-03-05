<template>
  <div class="users-container">
    <div class="users-card">
      <div class="users-header">
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
      
      <!-- Formulário para criar usuários -->
      <div class="section-card">
        <h2>Criar Novo Usuário</h2>
        <form class="user-form" @submit.prevent="createUser">
          <div class="form-group">
            <label for="username">Nome de Usuário</label>
            <input 
              type="text" 
              id="username" 
              v-model="newUser.username" 
              required
              placeholder="Digite o nome do usuário"
            >
          </div>
          
          <div class="form-group">
            <label for="password">Senha</label>
            <input 
              type="password" 
              id="password" 
              v-model="newUser.password" 
              required
              placeholder="Digite a senha"
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
          
          <button type="submit" class="action-button">Criar Usuário</button>
        </form>
      </div>
      
      <!-- Lista de usuários -->
      <div class="section-card">
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
      
      <div class="users-actions">
        <button class="secondary-button" @click="goBack">Voltar</button>
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
.users-container {
  width: 100vw;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  position: fixed;
  top: 0;
  left: 0;
}

.users-card {
  width: 100%;
  max-width: 700px;
  max-height: 90vh;
  padding: 2.5rem;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
  animation: fade-in 0.8s ease-out;
  position: relative;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.users-header {
  text-align: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #eaeaea;
}

.users-header h1 {
  color: #142C4D;
  font-size: 2.2rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.subtitle {
  color: #666;
  font-size: 1.1rem;
}

.section-card {
  background-color: #f9f9f9;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

.section-card h2 {
  color: #204578;
  font-size: 1.4rem;
  margin-bottom: 1rem;
  border-bottom: 1px solid #e1e1e1;
  padding-bottom: 0.5rem;
}

.user-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  margin-bottom: 0.8rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-size: 0.95rem;
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
  gap: 0.5rem;
}

.checkbox-group input {
  width: 18px;
  height: 18px;
}

.checkbox-group label {
  display: inline;
  margin-bottom: 0;
}

.users-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-height: 300px;
  overflow-y: auto;
}

.user-item {
  background-color: #fff;
  border-radius: 6px;
  border: 1px solid #eaeaea;
  padding: 0.8rem 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.user-name {
  font-weight: 600;
  font-size: 1rem;
  color: #142C4D;
  display: block;
}

.user-type {
  font-size: 0.8rem;
  color: #666;
  background-color: #f0f0f0;
  padding: 0.2rem 0.5rem;
  border-radius: 12px;
  display: inline-block;
  margin-top: 0.3rem;
}

.admin-type {
  background-color: #e0f2fe;
  color: #0077b6;
}

.action-button {
  padding: 0.9rem;
  background: linear-gradient(to right, #142C4D, #204578);
  border: none;
  border-radius: 8px;
  color: white;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-button:hover {
  background: linear-gradient(to right, #1a3760, #2a5b9e);
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(20, 44, 77, 0.3);
}

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
}

.users-actions {
  display: flex;
  justify-content: center;
  margin-top: 1rem;
}

.error-alert, .success-alert {
  padding: 0.8rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 0.9rem;
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
  font-size: 1.2rem;
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

.empty-state p {
  color: #666;
  font-style: italic;
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

/* Responsividade */
@media (max-width: 650px) {
  .users-card {
    max-width: 90%;
    padding: 2rem 1.5rem;
    margin-top: 2rem;
    margin-bottom: 2rem;
    max-height: 95vh;
  }
  
  .users-header h1 {
    font-size: 1.8rem;
  }
  
  .section-card {
    padding: 1rem;
  }
  
  .section-card h2 {
    font-size: 1.2rem;
  }
}
</style>