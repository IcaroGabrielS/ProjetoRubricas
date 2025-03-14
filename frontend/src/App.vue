<template>
  <div id="app">
    <nav v-if="isLoggedIn" class="app-navbar">
      <div class="nav-container">
        <!-- Logo posicionado mais à esquerda -->
        <div class="nav-logo">
          <img src="@/assets/logo.svg" alt="Logo" class="logo-image" />
          <span class="logo-text">Portal do Cliente</span>
        </div>
        
        <!-- Links de navegação centralizados -->
        <div class="nav-links">
          <router-link to="/" class="nav-link">
            <svg class="nav-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
              <polyline points="9 22 9 12 15 12 15 22"></polyline>
            </svg>
            <span>Início</span>
          </router-link>
          <router-link v-if="isAdmin" to="/users" class="nav-link">
            <svg class="nav-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
              <circle cx="9" cy="7" r="4"></circle>
              <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
              <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
            </svg>
            <span>Usuários</span>
          </router-link>
        </div>
        
        <!-- Informações do usuário e botão de sair mais à direita -->
        <div class="user-info">
          <div class="username-dropdown">
            <div class="username" @click="toggleDropdown">
              <div class="avatar">{{ username.charAt(0) }}</div>
              {{ username }}
              <!-- Ícone de seta para dropdown -->
              <svg class="dropdown-icon" :class="{ 'dropdown-open': showDropdown }" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="6 9 12 15 18 9"></polyline>
              </svg>
            </div>

            <!-- Menu dropdown -->
            <div v-show="showDropdown" class="dropdown-menu">
              <router-link to="/change-password" class="dropdown-item" @click="showDropdown = false">
                <svg class="dropdown-item-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                  <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
                </svg>
                Alterar Senha
              </router-link>
            </div>
          </div>
          
          <button @click="logout" class="logout-btn">
            <svg class="logout-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
              <polyline points="16 17 21 12 16 7"></polyline>
              <line x1="21" y1="12" x2="9" y2="12"></line>
            </svg>
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
      username: 'IcaroGabrielS',
      showDropdown: false
    }
  },
  created() {
    this.checkLoginStatus();
    // Adiciona event listener para fechar o dropdown quando clicar fora
    document.addEventListener('click', this.closeDropdownOutside);
  },
  beforeUnmount() {
    // Remove event listener ao destruir o componente
    document.removeEventListener('click', this.closeDropdownOutside);
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
    },
    toggleDropdown(event) {
      // Impede que o evento se propague para o document
      event.stopPropagation();
      this.showDropdown = !this.showDropdown;
    },
    closeDropdownOutside(event) {
      const dropdown = document.querySelector('.username-dropdown');
      if (dropdown && !dropdown.contains(event.target)) {
        this.showDropdown = false;
      }
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
  --shadow-md: 0 4px 20px rgba(0, 0, 0, 0.1);
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
  min-width: 220px; /* Garante espaço suficiente para o logo */
  margin-right: auto; /* Empurra para a esquerda */
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
  gap: 12px;
  flex: 1;
  justify-content: center; /* Centraliza os links */
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
  width: 20px;
  height: 20px;
  margin-right: 8px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 16px;
  min-width: 220px; /* Garante espaço suficiente para informações do usuário */
  justify-content: flex-end; /* Alinha à direita */
  margin-left: auto; /* Empurra para a direita */
}

/* Estilos para o dropdown do usuário */
.username-dropdown {
  position: relative;
}

.username {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: var(--dark);
  font-size: 0.95rem;
  cursor: pointer;
  padding: 6px 10px;
  border-radius: var(--radius-md);
  transition: all 0.2s ease;
}

.username:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.dropdown-icon {
  width: 16px;
  height: 16px;
  margin-left: 2px;
  transition: transform 0.3s ease;
}

.dropdown-icon.dropdown-open {
  transform: rotate(180deg);
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

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  width: 200px;
  background-color: var(--white);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);
  margin-top: 8px;
  overflow: hidden;
  z-index: 1010;
  border: 1px solid var(--light);
  animation: fadeInDropdown 0.2s ease;
}

@keyframes fadeInDropdown {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

.dropdown-item {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  color: var(--dark);
  text-decoration: none;
  font-size: 0.9rem;
  transition: all 0.2s ease;
  gap: 10px;
}

.dropdown-item:hover {
  background-color: var(--light);
  color: var(--primary);
}

.dropdown-item-icon {
  width: 18px;
  height: 18px;
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
  display: flex;
  align-items: center;
  gap: 6px;
}

.logout-icon {
  width: 16px;
  height: 16px;
  stroke: currentColor;
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
    gap: 8px;
  }
  
  .nav-link {
    padding: 8px 16px;
  }
  
  .user-info, .nav-logo {
    min-width: auto;
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
  
  /* Ajuste para dropdown em mobile */
  .dropdown-menu {
    right: -50px;
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
    width: 24px;
    height: 24px;
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