<template>
  <div class="store-container">
    <div class="store-content">
      <div class="page-header">
        <h1>Lojas</h1>
        <div v-if="isAdmin" class="admin-actions">
          <router-link to="/stores/create" class="create-btn">Criar Nova Loja</router-link>
        </div>
      </div>
      
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Carregando...</p>
      </div>
      
      <div v-else-if="error" class="error-state">
        <div class="error-icon">!</div>
        <p>{{ error }}</p>
      </div>
      
      <div v-else-if="stores.length === 0" class="empty-state">
        <div class="empty-icon">📋</div>
        <p>Nenhuma loja cadastrada ainda.</p>
      </div>
      
      <div v-else class="stores-container">
        <div class="stores-grid">
          <div v-for="store in stores" :key="store.id" class="store-card">
            <div class="store-card-header">
              <h3>{{ store.name }}</h3>
            </div>
            <div class="store-card-body">
              <p><strong>Número da Loja:</strong> {{ store.store_number }}</p>
              <p><strong>Inscrição Estadual:</strong> {{ store.state_registration }}</p>
              <p><strong>Endereço:</strong> {{ store.address }}</p>
            </div>
            <div class="store-card-footer">
              <router-link :to="`/stores/${store.id}`" class="view-btn">Ver Detalhes</router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'StoreListView',
  data() {
    return {
      stores: [],
      loading: true,
      error: null,
      isAdmin: false
    }
  },
  created() {
    this.checkAdmin();
    this.fetchStores();
  },
  methods: {
    checkAdmin() {
      const userStr = localStorage.getItem('user');
      if (userStr) {
        const user = JSON.parse(userStr);
        this.isAdmin = user.is_admin === true;
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
          this.error = data.message || 'Erro ao carregar lojas';
          this.loading = false;
          return;
        }
        
        this.stores = data.stores;
        this.loading = false;
      } catch (error) {
        this.error = 'Erro ao conectar ao servidor';
        this.loading = false;
        console.error('Error fetching stores:', error);
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
  margin: 0;
  padding: 0;
}

body {
  font-family: 'Sarala', sans-serif;
  background: linear-gradient(135deg, #142C4D, #204578);
  color: #333;
}

/* Estilo da barra de rolagem */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
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
.store-container {
  min-height: 100vh;
  width: 100%;
  padding: 2rem;
  display: flex;
  justify-content: center;
}

.store-content {
  width: 100%;
  max-width: 1200px;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
  padding: 2rem;
  animation: fade-in 0.8s ease-out;
  display: flex;
  flex-direction: column;
  max-height: calc(100vh - 4rem); /* Limita a altura para permitir rolagem */
  overflow: hidden; /* Esconde overflow do conteúdo interno */
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #eaeaea;
}

.page-header h1 {
  color: #142C4D;
  font-size: 2rem;
  font-weight: 700;
}

.admin-actions {
  display: flex;
  gap: 1rem;
}

.create-btn {
  background: linear-gradient(to right, #142C4D, #204578);
  color: white;
  padding: 0.8rem 1.2rem;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.9rem;
  text-decoration: none;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  box-shadow: 0 4px 6px rgba(32, 69, 120, 0.15);
}

.create-btn:hover {
  background: linear-gradient(to right, #1a3760, #2a5b9e);
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(32, 69, 120, 0.3);
}

.create-btn:active {
  transform: translateY(0);
}

.stores-container {
  flex-grow: 1;
  overflow-y: auto; /* Habilita rolagem vertical */
  padding-right: 5px; /* Espaço para a barra de rolagem */
}

.stores-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr); /* Exatamente 3 lojas por linha */
  gap: 1.5rem;
  width: 100%;
  padding-bottom: 1rem; /* Espaço para evitar que o conteúdo fique muito próximo da barra de rolagem */
}

.store-card {
  background-color: #ffffff;
  border-radius: 10px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  transition: all 0.3s ease;
  border: 1px solid #eaeaea;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.store-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  border-color: #d1d1d1;
}

.store-card-header {
  padding: 1.2rem;
  background: linear-gradient(to right, #142C4D, #204578);
  color: white;
}

.store-card-header h3 {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.store-card-body {
  padding: 1.2rem;
  flex-grow: 1;
}

.store-card-body p {
  margin-bottom: 0.8rem;
  font-size: 0.95rem;
  line-height: 1.4;
  color: #555;
}

.store-card-body p strong {
  color: #333;
  font-weight: 600;
}

.store-card-body p:last-child {
  margin-bottom: 0;
}

.store-card-footer {
  padding: 1.2rem;
  border-top: 1px solid #eaeaea;
  text-align: right;
}

.view-btn {
  padding: 0.6rem 1rem;
  background-color: #204578;
  color: white;
  border-radius: 6px;
  text-decoration: none;
  font-size: 0.85rem;
  font-weight: 600;
  transition: all 0.3s ease;
  display: inline-block;
}

.view-btn:hover {
  background-color: #3c72c2;
  transform: translateY(-2px);
}

/* Estados de carregamento e erro */
.loading-state, .error-state, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 1rem;
  text-align: center;
  flex-grow: 1;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 5px solid #f3f3f3;
  border-top: 5px solid #204578;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

.error-icon, .empty-icon {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.error-icon {
  width: 60px;
  height: 60px;
  background-color: #fee2e2;
  color: #b91c1c;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
}

.empty-icon {
  font-size: 3rem;
}

.error-state p {
  color: #b91c1c;
  font-weight: 500;
}

.empty-state p, .loading-state p {
  color: #666;
  font-size: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes fade-in {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Responsividade */
@media (max-width: 1024px) {
  .stores-grid {
    grid-template-columns: repeat(2, 1fr); /* 2 lojas por linha em tablets */
  }
}

@media (max-width: 768px) {
  .store-container {
    padding: 1rem;
  }
  
  .store-content {
    padding: 1.5rem;
    max-height: calc(100vh - 2rem);
  }
  
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .admin-actions {
    width: 100%;
  }
  
  .create-btn {
    width: 100%;
    text-align: center;
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .stores-grid {
    grid-template-columns: 1fr; /* 1 loja por linha em dispositivos móveis */
  }
}
</style>