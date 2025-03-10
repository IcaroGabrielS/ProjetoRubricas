<template>
  <div id="app">
    <nav v-if="isLoggedIn" class="app-navbar">
      <div class="nav-container">
        <div class="nav-logo">
          <img src="@/assets/logo.svg" alt="Logo" class="logo-image" />
          <span class="logo-text">Portal do Cliente</span>
        </div>
        <div class="nav-links">
          <router-link to="/" class="nav-link">
            <i class="nav-icon">🏠</i>
            <span>Home</span>
          </router-link>
          <router-link v-if="isAdmin" to="/users" class="nav-link">
            <i class="nav-icon">👥</i>
            <span>Usuários</span>
          </router-link>
        </div>
        <div class="user-info">
          <div class="username">
            <div class="avatar">{{ username.charAt(0) }}</div>
            {{ username }}
          </div>
          <button @click="logout" class="logout-btn">
            <span>Sair</span>
          </button>
        </div>
      </div>
    </nav>
    <main class="app-content">
      <router-view/>
    </main>
  </div>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      isLoggedIn: false,
      isAdmin: false,
      username: 'IcaroGabrielS'
    }
  },
  created() {
    this.checkLoginStatus();
  },
  methods: {
    checkLoginStatus() {
      const userStr = localStorage.getItem('user');
      if (userStr) {
        const user = JSON.parse(userStr);
        this.isLoggedIn = true;
        this.isAdmin = user.is_admin === true;
        this.username = user.username || 'IcaroGabrielS';
      } else {
        this.isLoggedIn = false;
        this.isAdmin = false;
        this.username = '';
      }
    },
    logout() {
      localStorage.removeItem('user');
      this.isLoggedIn = false;
      this.isAdmin = false;
      this.$router.push('/login');
    }
  },
  watch: {
    $route() {
      this.checkLoginStatus();
    }
  }
}
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

:root {
  /* Paleta de cores flat e elegante */
  --primary: #6c5ce7;           /* Roxo elegante */
  --primary-light: #8a7ef5;     /* Roxo claro */
  --accent: #00cec9;            /* Turquesa */
  --accent-light: #81ecec;      /* Turquesa claro */
  --danger: #ff7675;            /* Vermelho suave */
  --success: #55efc4;           /* Verde menta */
  --dark: #2d3436;              /* Cinza escuro */
  --dark-light: #636e72;        /* Cinza médio */
  --light: #dfe6e9;             /* Cinza claro */
  --white: #ffffff;             /* Branco */
  --card-bg: #ffffff;           /* Fundo de card */
  --bg-color: #f9fafe;          /* Fundo da aplicação */
  
  /* Parâmetros de design */
  --radius-sm: 10px;            /* Raio pequeno */
  --radius-md: 16px;            /* Raio médio */
  --radius-lg: 24px;            /* Raio grande */
  --radius-full: 100px;         /* Raio completo */
  
  /* Sombras */
  --shadow-sm: 0 2px 10px rgba(0, 0, 0, 0.05);
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  background-color: var(--bg-color);
  color: var(--dark);
  font-family: 'Outfit', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

#app {
  min-height: 100vh;
  padding-top: 70px;
}

.app-navbar {
  background: var(--white);
  height: 70px;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  box-shadow: var(--shadow-sm);
}

.nav-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px;
}

.nav-logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-image {
  width: 38px;
  height: 38px;
}

.logo-text {
  font-size: 1.4rem;
  font-weight: 600;
  color: var(--primary);
  letter-spacing: -0.5px;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 8px;
}

.nav-link {
  display: flex;
  align-items: center;
  color: var(--dark-light);
  text-decoration: none;
  padding: 10px 18px;
  border-radius: var(--radius-full);
  font-weight: 500;
  font-size: 0.95rem;
}

.nav-link:hover {
  background-color: var(--light);
  color: var(--primary);
}

.nav-link.router-link-exact-active {
  background-color: var(--primary);
  color: var(--white);
}

.nav-icon {
  margin-right: 8px;
  font-style: normal;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.username {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: var(--dark);
  font-size: 0.95rem;
}

.avatar {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-full);
  background-color: var(--accent);
  color: var(--white);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 1rem;
}

.logout-btn {
  background: var(--white);
  color: var(--danger);
  border: 1.5px solid var(--danger);
  padding: 8px 18px;
  border-radius: var(--radius-full);
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
}

.logout-btn:hover {
  background-color: var(--danger);
  color: var(--white);
}

.app-content {
  padding-top: 20px;
  min-height: calc(100vh - 70px);
}

/* Estilos globais para botões */
button {
  background-color: var(--primary);
  color: var(--white);
  border: none;
  padding: 12px 24px;
  border-radius: var(--radius-full);
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-family: 'Outfit', sans-serif;
  letter-spacing: 0.3px;
}

button:focus {
  outline: none;
}

/* Botões de ação principal */
.action-button {
  background-color: var(--accent);
}

/* Botões secundários */
.secondary-button {
  background: var(--white);
  color: var(--dark);
  border: 1.5px solid var(--light);
}

.secondary-button:hover {
  border-color: var(--primary-light);
  color: var(--primary);
}

/* Estilos globais para inputs */
input {
  font-family: 'Outfit', sans-serif;
  border: 1.5px solid var(--light);
  border-radius: var(--radius-md);
  padding: 12px 16px;
  font-size: 1rem;
  background-color: var(--white);
  color: var(--dark);
}

input:focus {
  border-color: var(--primary-light);
  box-shadow: 0 0 0 3px rgba(108, 92, 231, 0.1);
  outline: none;
}

/* Cards e containers */
.card {
  background-color: var(--card-bg);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
  border: 1px solid rgba(230, 235, 245, 0.5);
}

.card-header {
  background-color: var(--primary);
  color: var(--white);
  padding: 18px 24px;
  font-weight: 600;
  letter-spacing: -0.2px;
}

/* Section Cards */
.section-card {
  background-color: var(--white);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  padding: 24px;
  margin-bottom: 24px;
  border: 1px solid rgba(230, 235, 245, 0.5);
}

.section-card h2 {
  color: var(--primary);
  font-size: 1.4rem;
  margin-bottom: 1.2rem;
  font-weight: 600;
  border-bottom: 1px solid var(--light);
  padding-bottom: 12px;
  letter-spacing: -0.5px;
}

/* Alertas */
.error-alert, .success-alert {
  padding: 14px 20px;
  border-radius: var(--radius-md);
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 0.95rem;
}

.error-alert {
  background-color: rgba(255, 118, 117, 0.1);
  color: #ff4757;
  border-left: 4px solid #ff4757;
}

.success-alert {
  background-color: rgba(85, 239, 196, 0.1);
  color: #00b894;
  border-left: 4px solid #00b894;
}

/* Media queries para responsividade */
@media (max-width: 900px) {
  .nav-container {
    padding: 0 16px;
  }
  
  .logo-text {
    font-size: 1.2rem;
  }
  
  .nav-links {
    gap: 6px;
  }
  
  .nav-link {
    padding: 8px 16px;
  }
}

@media (max-width: 768px) {
  .app-navbar {
    height: auto;
    padding: 12px 0;
  }
  
  #app {
    padding-top: 120px;
  }
  
  .app-content {
    min-height: calc(100vh - 120px);
  }
  
  .nav-container {
    flex-direction: column;
    padding: 0 16px;
    gap: 12px;
  }
  
  .nav-links {
    order: 2;
    width: 100%;
    justify-content: center;
  }
  
  .user-info {
    order: 1;
    width: 100%;
    justify-content: space-between;
  }
}

@media (max-width: 480px) {
  .nav-links {
    gap: 4px;
  }
  
  .nav-link span {
    display: none;
  }
  
  .nav-icon {
    margin-right: 0;
    font-size: 1.2rem;
  }
  
  .app-navbar {
    padding: 10px 0;
  }
  
  #app {
    padding-top: 100px;
  }
  
  .app-content {
    min-height: calc(100vh - 100px);
  }
  
  .logo-text {
    font-size: 1.1rem;
  }
  
  .avatar {
    width: 28px;
    height: 28px;
    font-size: 0.9rem;
  }
}
</style>