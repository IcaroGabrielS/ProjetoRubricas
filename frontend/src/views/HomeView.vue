<template>
  <div class="home-container">
    <div class="home-card">
      <div class="home-header">
        <h1>Bem-vindo, {{ username }}!</h1>
        <p class="welcome-text">Você está logado com sucesso.</p>
        <div class="datetime">{{ currentDateTime }}</div>
      </div>
      
      <div class="dashboard-summary">
        <div class="dashboard-item">
          <h3>Suas Lojas</h3>
          <p>Selecione uma loja abaixo para acessar seus detalhes e arquivos.</p>
        </div>
      </div>
      
      <!-- Lista de lojas -->
      <div class="stores-section">
        <div v-if="storesLoading" class="loading-indicator">
          <div class="loading-spinner"></div>
          <p>Carregando lojas...</p>
        </div>
        
        <div v-else-if="storesError" class="error-message">
          <div class="error-icon">!</div>
          <p>{{ storesError }}</p>
        </div>
        
        <div v-else-if="stores.length === 0" class="empty-state">
          <p>Você não tem acesso a nenhuma loja no momento.</p>
        </div>
        
        <div v-else class="stores-list">
          <div 
            v-for="store in stores" 
            :key="store.id" 
            class="store-item"
            @click="goToStoreDetail(store.id)"
          >
            <div class="store-item-details">
              <span class="store-name">{{ store.name }}</span>
              <span class="store-number">#{{ store.store_number }}</span>
            </div>
            <div class="store-item-arrow">
              <span>›</span>
            </div>
          </div>
        </div>
      </div>
      
      <div class="quick-actions">
        <button v-if="isAdmin" class="action-button admin" @click="createStore">Nova Loja</button>
        <button v-if="isAdmin" class="action-button admin" @click="manageAccounts">Gerenciar Contas</button>
        <button class="action-button logout" @click="logout">Sair</button>
      </div>
      
      <div class="home-footer">
        <span class="user-info">{{ username }} | {{ isAdmin ? 'Administrador' : 'Usuário Padrão' }}</span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'HomeView',
  data() {
    return {
      username: 'Usuário',
      isAdmin: false,
      stores: [],
      storesLoading: true,
      storesError: null,
      currentDateTime: '2025-03-05 17:43:15'
    }
  },
  created() {
    this.loadUserInfo();
    this.fetchStores();
  },
  methods: {
    loadUserInfo() {
      const userStr = localStorage.getItem('user');
      if (userStr) {
        const user = JSON.parse(userStr);
        this.username = user.username;
        this.isAdmin = user.is_admin === true;
      } else {
        this.$router.push('/login');
      }
    },
    async fetchStores() {
      try {
        const userStr = localStorage.getItem('user');
        if (!userStr) {
          this.$router.push('/login');
          return;
        }
        
        const user = JSON.parse(userStr);
        
        const response = await fetch('/api/stores', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'User-ID': user.id
          }
        });
        
        const data = await response.json();
        
        if (!response.ok) {
          this.storesError = data.message || 'Erro ao carregar lojas';
          this.storesLoading = false;
          return;
        }
        
        this.stores = data.stores;
        this.storesLoading = false;
      } catch (error) {
        this.storesError = 'Erro ao conectar ao servidor';
        this.storesLoading = false;
        console.error('Error fetching stores:', error);
      }
    },
    goToStoreDetail(storeId) {
      this.$router.push(`/stores/${storeId}`);
    },
    createStore() {
      this.$router.push('/stores/create');
    },
    manageAccounts() {
      // Implementar futuramente a navegação para gerenciamento de contas
      alert('Funcionalidade em desenvolvimento');
    },
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

/* Estilo da barra de rolagem */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 10px;
}

::-webkit-scrollbar-thumb {
  background: #204578;
  border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
  background: #142C4D;
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
  max-height: 90vh;
  padding: 2.5rem;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
  animation: fade-in 0.8s ease-out;
  position: relative;
  display: flex;
  flex-direction: column;
  overflow: hidden;
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

.welcome-text {
  color: #666;
  font-size: 1.1rem;
}

.datetime {
  position: absolute;
  top: 0;
  right: 0;
  font-size: 0.8rem;
  color: #666;
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

/* Seção de lojas */
.stores-section {
  flex: 1;
  overflow-y: auto;
  margin-bottom: 1.5rem;
  max-height: 250px;
}

.stores-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.store-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.8rem 1rem;
  background-color: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #eaeaea;
  cursor: pointer;
  transition: all 0.2s ease;
}

.store-item:hover {
  background-color: #e9ecef;
  transform: translateY(-2px);
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.08);
}

.store-item-details {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.store-name {
  font-weight: 600;
  font-size: 0.95rem;
  color: #142C4D;
}

.store-number {
  font-size: 0.8rem;
  color: #666;
}

.store-item-arrow {
  font-size: 1.5rem;
  font-weight: bold;
  color: #204578;
}

/* Estados de loading, erro e vazio */
.loading-indicator, .error-message, .empty-state {
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

.error-message p {
  color: #b91c1c;
}

.empty-state p {
  color: #666;
  font-style: italic;
}

.quick-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1rem;
}

.action-button {
  flex: 1;
  min-width: 150px;
  padding: 0.8rem;
  border: none;
  border-radius: 8px;
  color: white;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-button.admin {
  background: linear-gradient(to right, #142C4D, #204578);
}

.action-button.admin:hover {
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

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
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