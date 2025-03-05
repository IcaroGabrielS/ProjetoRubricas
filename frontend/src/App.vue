<template>
  <div id="app">
    <nav v-if="isLoggedIn">
      <div class="nav-container">
        <div class="nav-links">
          <router-link to="/">Home</router-link>
          <router-link v-if="isAdmin" to="/stores/create"> | Criar Loja</router-link>
        </div>
        <div class="user-info">
          <span>{{ username }}</span>
          <span class="datetime">{{ currentDateTime }}</span>
          <button @click="logout" class="logout-btn">Logout</button>
        </div>
      </div>
    </nav>
    <router-view/>
  </div>
</template>

<script>
export default {
  name: 'App',
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
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  margin-top: 60px;
}

nav {
  padding: 10px;
  background-color: #f8f9fa;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.nav-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.nav-links a {
  font-weight: bold;
  color: #2c3e50;
  margin-right: 10px;
  text-decoration: none;
}

.nav-links a.router-link-exact-active {
  color: #42b983;
}

.user-info {
  display: flex;
  align-items: center;
}

.user-info span {
  margin-right: 15px;
  font-weight: bold;
}

.datetime {
  font-size: 0.85rem;
  color: #666;
  font-weight: normal;
}

.logout-btn {
  background-color: #dc3545;
  color: white;
  border: none;
  padding: 5px 10px;
  border-radius: 4px;
  cursor: pointer;
}

.logout-btn:hover {
  background-color: #c82333;
}

button {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

button:hover {
  background-color: #000000;
}

.content {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

@media (max-width: 768px) {
  .nav-container {
    flex-direction: column;
    padding: 10px;
  }
  
  .nav-links {
    margin-bottom: 10px;
  }
  
  .user-info {
    width: 100%;
    justify-content: space-between;
  }
  
  #app {
    margin-top: 90px;
  }
}

@media (max-width: 480px) {
  .datetime {
    display: none;
  }
}
</style>