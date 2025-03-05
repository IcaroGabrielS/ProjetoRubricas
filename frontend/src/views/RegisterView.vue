<template>
  <div class="register-container">
    <div class="register-card">
      <div class="register-header">
        <h1>Registro</h1>
        <p class="welcome-text">Crie sua conta no sistema</p>
      </div>
      
      <div v-if="error" class="error-alert">
        <span>{{ error }}</span>
        <button class="close-btn" @click="error = ''" aria-label="Fechar">&times;</button>
      </div>
      
      <form class="register-form" @submit.prevent="handleRegister">
        <div class="form-group">
          <label for="username">Usuário</label>
          <input 
            type="text" 
            id="username" 
            v-model="username" 
            required
            autocomplete="username"
            autofocus
            placeholder="Escolha um nome de usuário"
          >
        </div>
        
        <div class="form-group">
          <label for="password">Senha</label>
          <input 
            type="password" 
            id="password" 
            v-model="password" 
            required
            autocomplete="new-password"
            placeholder="Crie uma senha"
          >
        </div>
        
        <button type="submit" class="register-button">Registrar</button>
      </form>
      
      <div class="register-footer">
        <p>Já tem uma conta? <router-link to="/login">Login</router-link></p>
        <p class="current-info">
          <span>2025-03-04 22:05:55</span>
          <span class="user-info">IcaroGabrielS</span>
        </p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'RegisterView',
  data() {
    return {
      username: '',
      password: '',
      error: ''
    }
  },
  methods: {
    async handleRegister() {
      try {
        const response = await fetch('/api/register', {
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
          this.error = data.message || 'Erro ao registrar';
          return;
        }
        
        // Redireciona para a página de login após o registro bem-sucedido
        this.$router.push('/login');
      } catch (error) {
        this.error = 'Erro ao conectar ao servidor';
        console.error('Register error:', error);
      }
    }
  }
}
</script>

<style>
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
.register-container {
  width: 100vw;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  position: fixed;
  top: 0;
  left: 0;
}

.register-card {
  width: 100%;
  max-width: 420px;
  padding: 2.5rem;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
  animation: fade-in 0.8s ease-out;
  position: absolute;
}

.register-header {
  text-align: center;
  margin-bottom: 2rem;
}

.register-header h1 {
  color: #142C4D;
  font-size: 2.2rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.welcome-text {
  color: #666;
  font-size: 1rem;
}

.register-form {
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

.register-button {
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

.register-button:hover {
  background: linear-gradient(to right, #1a3760, #2a5b9e);
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(20, 44, 77, 0.3);
}

.register-button:active {
  transform: translateY(0);
}

.register-footer {
  text-align: center;
  font-size: 0.9rem;
  color: #666;
}

.register-footer a {
  color: #204578;
  font-weight: 600;
  text-decoration: none;
  transition: color 0.2s;
}

.register-footer a:hover {
  color: #3c72c2;
  text-decoration: underline;
}

.current-info {
  display: flex;
  justify-content: space-between;
  margin-top: 1.2rem;
  font-size: 0.8rem;
  color: #999;
}

.user-info {
  font-weight: 500;
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
  .register-card {
    max-width: 90%;
    padding: 2rem 1.5rem;
  }
  
  .register-header h1 {
    font-size: 1.8rem;
  }
  
  .form-group input {
    padding: 0.8rem;
  }
}
</style>