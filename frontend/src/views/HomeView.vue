<template>
  <div class="home-container">
    <div class="home-card">
      <div class="home-header">
        <h1>Bem-vindo, {{ username }}!</h1>
        <p class="welcome-text">Você está logado com sucesso.</p>
      </div>
      
      <div class="dashboard-summary">
        <div class="dashboard-item">
          <h3>Visão Geral</h3>
          <p>Acesse os recursos do sistema a partir deste painel.</p>
        </div>
      </div>
      
      <div class="quick-actions">
        <button class="action-button">Gerenciar Lojas</button>
        <button class="action-button">Gerenciar Contas</button>
        <button class="action-button logout" @click="logout">Sair</button>
      </div>
      
      <div class="home-footer">
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'HomeView',
  data() {
    return {
      username: 'Usuário'
    }
  },
  created() {
    const userStr = localStorage.getItem('user');
    if (userStr) {
      const user = JSON.parse(userStr);
      this.username = user.username;
    }
  },
  methods: {
    logout() {
      localStorage.removeItem('user');
      this.$router.push('/login');
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
.home-container {
  width: 100vw;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  position: fixed;
  top: 0;
  left: 0;
}

.home-card {
  width: 100%;
  max-width: 600px;
  padding: 2.5rem;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
  animation: fade-in 0.8s ease-out;
  position: absolute;
}

.home-header {
  text-align: center;
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #eaeaea;
}

.home-header h1 {
  color: #142C4D;
  font-size: 2.2rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.welcome-text {
  color: #666;
  font-size: 1.1rem;
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
}

.quick-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.action-button {
  flex: 1;
  min-width: 150px;
  padding: 0.8rem;
  background: linear-gradient(to right, #142C4D, #204578);
  border: none;
  border-radius: 8px;
  color: white;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-button:hover {
  background: linear-gradient(to right, #1a3760, #2a5b9e);
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(20, 44, 77, 0.3);
}

.action-button.logout {
  background: linear-gradient(to right, #d63031, #e84393);
}

.action-button.logout:hover {
  background: linear-gradient(to right, #c0392b, #d63031);
  box-shadow: 0 5px 15px rgba(214, 48, 49, 0.3);
}

.home-footer {
  text-align: center;
  font-size: 0.9rem;
  color: #666;
  padding-top: 1rem;
  border-top: 1px solid #eaeaea;
}

.user-info {
  font-weight: 500;
}

/* Animações */
@keyframes fade-in {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Responsividade */
@media (max-width: 650px) {
  .home-card {
    max-width: 90%;
    padding: 2rem 1.5rem;
  }
  
  .home-header h1 {
    font-size: 1.8rem;
  }
  
  .quick-actions {
    flex-direction: column;
  }
  
  .action-button {
    width: 100%;
  }
}
</style>