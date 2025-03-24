<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <h1>CLIENTE CONTÁGIL</h1>
        <h2 class="welcome-text">Login</h2>
      </div>
      
      <div v-if="error" class="error-alert">
        <span>{{ error }}</span>
        <button class="close-btn" @click="error = ''" aria-label="Fechar">&times;</button>
      </div>
      
      <form class="login-form" @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="username">Usuário</label>
          <input 
            type="text" 
            id="username" 
            v-model="username" 
            required
            autocomplete="username"
            autofocus
            placeholder="Digite seu usuário"
          >
        </div>
        
        <div class="form-group">
          <label for="password">Senha</label>
          <input 
            type="password" 
            id="password" 
            v-model="password" 
            required
            autocomplete="current-password"
            placeholder="Digite sua senha"
          >
        </div>
        
        <button type="submit" class="login-button" :disabled="isLoading">
          <span v-if="isLoading">Processando...</span>
          <span v-else>Entrar</span>
        </button>
      </form>
      
      <div class="login-footer">
        <!-- Footer content -->
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'

export default {
  name: 'LoginView',
  setup() {
    const username = ref('')
    const password = ref('')
    const error = ref('')
    const isLoading = ref(false)

    return {
      username,
      password,
      error,
      isLoading
    }
  },
  methods: {
    async handleLogin() {
      this.isLoading = true
      this.error = ''
      
      try {
        const response = await fetch('/api/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            username: this.username,
            password: this.password
          }),
        });
        
        const data = await response.json();
        
        if (!response.ok) {
          // Trata ambos os formatos de mensagem de erro (message ou mensagem)
          this.error = data.mensagem || data.message || 'Erro ao fazer login';
          this.isLoading = false;
          return;
        }
        
        // Armazena informações do usuário incluindo o token JWT
        const userData = {
          id: data.user_id,
          username: data.username,
          is_admin: data.is_admin,
          token: data.token
        };
        
        // Salva no localStorage
        localStorage.setItem('user', JSON.stringify(userData));
        
        // Configura o token para futuras requisições, se estiver usando Axios ou similar
        // this.$http.defaults.headers.common['Authorization'] = `Bearer ${data.token}`;
        
        // Verificar token automaticamente
        this.setupTokenRefresh();
        
        // Redireciona para a página inicial
        this.$router.push('/');
      } catch (error) {
        this.error = 'Erro ao conectar ao servidor';
        console.error('Login error:', error);
      } finally {
        this.isLoading = false;
      }
    },
    
    setupTokenRefresh() {
      // Implementação para verificar o token
      // Esta função pode ser chamada periodicamente ou em eventos específicos
      const verifyToken = async () => {
        try {
          const userData = JSON.parse(localStorage.getItem('user'));
          if (!userData || !userData.token) return;
          
          const response = await fetch('/api/verify-token', {
            method: 'GET',
            headers: {
              'Authorization': `Bearer ${userData.token}`
            }
          });
          
          if (!response.ok) {
            // Token inválido, volta para a tela de login
            localStorage.removeItem('user');
            this.$router.push('/login');
          }
        } catch (error) {
          console.error('Token verification error:', error);
        }
      };
      
      // Verificar token a cada 30 minutos
      this.tokenInterval = setInterval(verifyToken, 30 * 60 * 1000);
    }
  },
  beforeUnmount() {
    // Limpar o intervalo quando o componente for desmontado
    if (this.tokenInterval) clearInterval(this.tokenInterval);
  }
}
</script>

<style>
/* CSS permanece o mesmo */
@import url('https://fonts.googleapis.com/css2?family=Sarala:wght@400;700&display=swap');

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html, body {
  height: 100%;
  overflow: hidden; /* Previne rolagem em toda a página */
  margin: 0;
  padding: 0;
}

body {
  font-family: 'Sarala', sans-serif;
  background: linear-gradient(135deg, #142C4D, #204578);
  color: #333;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>

<style scoped>
.login-container {
  width: 100vw;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  position: fixed;
  top: 0;
  left: 0;
}

.login-card {
  width: 100%;
  max-width: 420px;
  padding: 2.5rem;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
  animation: fade-in 0.8s ease-out;
  position: relative;
}

.login-header {
  text-align: center;
  margin-bottom: 2rem;
}

.login-header h1 {
  color: #142C4D;
  font-size: 2.2rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.welcome-text {
  color: #666;
  font-size: 1rem;
}

.login-form {
  margin-bottom: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-size: 0.95rem;
  font-weight: 600;
  color: #333;
}

.form-group input {
  width: 100%;
  padding: 0.9rem;
  border: 2px solid #e1e1e1;
  border-radius: 8px;
  font-size: 1rem;
  color: #333;
  transition: all 0.3s ease;
  background-color: #f9f9f9;
}

.form-group input:focus {
  border-color: #204578;
  box-shadow: 0 0 0 3px rgba(32, 69, 120, 0.15);
  outline: none;
  background-color: #fff;
}

.form-group input::placeholder {
  color: #aaa;
}

.login-button {
  width: 100%;
  padding: 1rem;
  background: linear-gradient(to right, #142C4D, #204578);
  border: none;
  border-radius: 8px;
  color: white;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 0.5rem;
}

.login-button:hover:not(:disabled) {
  background: linear-gradient(to right, #1a3760, #2a5b9e);
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(20, 44, 77, 0.3);
}

.login-button:active:not(:disabled) {
  transform: translateY(0);
}

.login-button:disabled {
  background: #b3b3b3;
  cursor: not-allowed;
}

.login-footer {
  text-align: center;
  font-size: 0.9rem;
  color: #666;
  margin-top: 1.5rem;
}

.login-footer a {
  color: #204578;
  font-weight: 600;
  text-decoration: none;
  transition: color 0.2s;
}

.login-footer a:hover {
  color: #3c72c2;
  text-decoration: underline;
}

.error-alert {
  background-color: #fee2e2;
  color: #b91c1c;
  padding: 0.8rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 0.9rem;
  animation: fade-in 0.3s ease;
}

.close-btn {
  background: none;
  border: none;
  color: #b91c1c;
  cursor: pointer;
  font-size: 1.2rem;
  padding: 0 0.5rem;
}

/* Animações */
@keyframes fade-in {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Responsividade */
@media (max-width: 480px) {
  .login-card {
    max-width: 90%;
    padding: 2rem 1.5rem;
  }
  
  .login-header h1 {
    font-size: 1.8rem;
  }
  
  .form-group input {
    padding: 0.8rem;
  }
}
</style>