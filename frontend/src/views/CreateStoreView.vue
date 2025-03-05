<template>
  <div class="create-store-container">
    <div class="create-store-content">
      <div class="page-header">
        <h1>Criar Nova Loja</h1>
      </div>

      <form @submit.prevent="handleCreateStore" class="store-form">
        <div class="form-group">
          <label for="name">Nome do Grupo:</label>
          <input 
            type="text" 
            id="name" 
            v-model="store.name" 
            required
            placeholder="Digite o nome do grupo"
          >
        </div>
        
        <div class="form-group">
          <label for="state_registration">Inscrição Estadual:</label>
          <input 
            type="text" 
            id="state_registration" 
            v-model="store.state_registration" 
            required
            placeholder="Digite a inscrição estadual"
          >
        </div>
        
        <div class="form-group">
          <label for="store_number">Número da Loja:</label>
          <input 
            type="number" 
            id="store_number" 
            v-model="store.store_number" 
            required
            placeholder="Digite o número da loja"
          >
        </div>
        
        <div class="form-group">
          <label for="address">Endereço:</label>
          <textarea 
            id="address" 
            v-model="store.address" 
            required
            rows="3"
            placeholder="Digite o endereço completo"
          ></textarea>
        </div>
        
        <button type="submit" :disabled="loading" class="submit-btn">
          <span v-if="loading" class="loading-indicator"></span>
          {{ loading ? 'Criando...' : 'Criar Loja' }}
        </button>
      </form>
      
      <div v-if="error" class="error-message">
        <div class="error-icon">!</div>
        <p>{{ error }}</p>
        <button class="close-btn" @click="error = null" aria-label="Fechar">×</button>
      </div>
      
      <div v-if="successMessage" class="success-message">
        <div class="success-icon">✓</div>
        <p>{{ successMessage }}</p>
        <div class="success-actions">
          <router-link to="/stores" class="action-btn view-btn">Ver lista de lojas</router-link>
          <button @click="resetForm" class="action-btn reset-btn">Criar outra loja</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CreateStoreView',
  data() {
    return {
      store: {
        name: '',
        state_registration: '',
        store_number: '',
        address: ''
      },
      loading: false,
      error: null,
      successMessage: ''
    }
  },
  created() {
    this.checkIfAdmin();
  },
  methods: {
    checkIfAdmin() {
      const userStr = localStorage.getItem('user');
      if (!userStr) {
        this.$router.push('/login');
        return;
      }
      
      const user = JSON.parse(userStr);
      if (!user.is_admin) {
        this.$router.push('/');
      }
    },
    async handleCreateStore() {
      this.loading = true;
      this.error = null;
      
      try {
        const userStr = localStorage.getItem('user');
        if (!userStr) {
          this.$router.push('/login');
          return;
        }
        
        const user = JSON.parse(userStr);
        
        const response = await fetch('/api/stores', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'User-ID': user.id
          },
          body: JSON.stringify(this.store)
        });
        
        const data = await response.json();
        
        if (!response.ok) {
          this.error = data.message || 'Erro ao criar loja';
          this.loading = false;
          return;
        }
        
        this.successMessage = 'Loja criada com sucesso!';
        this.loading = false;
      } catch (error) {
        this.error = 'Erro ao conectar ao servidor';
        this.loading = false;
        console.error('Error creating store:', error);
      }
    },
    resetForm() {
      this.store = {
        name: '',
        state_registration: '',
        store_number: '',
        address: ''
      };
      this.successMessage = '';
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
.create-store-container {
  min-height: 100vh;
  width: 100%;
  padding: 2rem;
  display: flex;
  justify-content: center;
  align-items: center;
}

.create-store-content {
  width: 100%;
  max-width: 650px;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
  padding: 2rem;
  animation: fade-in 0.8s ease-out;
}

.page-header {
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #eaeaea;
  text-align: center;
}

.page-header h1 {
  color: #142C4D;
  font-size: 2rem;
  font-weight: 700;
}

.store-form {
  margin-bottom: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
  text-align: left;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-size: 0.95rem;
  font-weight: 600;
  color: #333;
}

.form-group input, .form-group textarea {
  width: 100%;
  padding: 0.9rem;
  border: 2px solid #e1e1e1;
  border-radius: 8px;
  font-size: 1rem;
  color: #333;
  transition: all 0.3s ease;
  background-color: #f9f9f9;
  font-family: 'Sarala', sans-serif;
}

.form-group input:focus, .form-group textarea:focus {
  border-color: #204578;
  box-shadow: 0 0 0 3px rgba(32, 69, 120, 0.15);
  outline: none;
  background-color: #fff;
}

.form-group input::placeholder, .form-group textarea::placeholder {
  color: #aaa;
}

.form-group textarea {
  resize: vertical;
  min-height: 100px;
}

.submit-btn {
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
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.submit-btn:hover:not(:disabled) {
  background: linear-gradient(to right, #1a3760, #2a5b9e);
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(32, 69, 120, 0.3);
}

.submit-btn:active:not(:disabled) {
  transform: translateY(0);
}

.submit-btn:disabled {
  background: linear-gradient(to right, #6c757d, #495057);
  cursor: not-allowed;
}

.loading-indicator {
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 3px solid rgba(255,255,255,0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 1s ease-in-out infinite;
  margin-right: 10px;
}

.error-message, .success-message {
  margin-top: 1.5rem;
  padding: 1rem;
  border-radius: 8px;
  display: flex;
  align-items: flex-start;
}

.error-message {
  background-color: #fee2e2;
  color: #b91c1c;
}

.success-message {
  background-color: #d1fae5;
  color: #065f46;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.error-icon, .success-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 1rem;
  flex-shrink: 0;
}

.error-icon {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background-color: #b91c1c;
  color: white;
  font-weight: bold;
}

.success-icon {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background-color: #059669;
  color: white;
  font-weight: bold;
  font-size: 1.2rem;
  margin-bottom: 0.5rem;
}

.close-btn {
  background: none;
  border: none;
  color: #b91c1c;
  cursor: pointer;
  font-size: 1.2rem;
  padding: 0 0.5rem;
  margin-left: auto;
}

.success-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
  flex-wrap: wrap;
  justify-content: center;
}

.action-btn {
  padding: 0.7rem 1.2rem;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
}

.view-btn {
  background-color: #204578;
  color: white;
}

.view-btn:hover {
  background-color: #142C4D;
  transform: translateY(-2px);
}

.reset-btn {
  background-color: #6c757d;
  color: white;
  border: none;
}

.reset-btn:hover {
  background-color: #5a6268;
  transform: translateY(-2px);
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
@media (max-width: 768px) {
  .create-store-container {
    padding: 1rem;
  }
  
  .create-store-content {
    padding: 1.5rem;
  }
}

@media (max-width: 480px) {
  .success-actions {
    flex-direction: column;
    width: 100%;
  }
  
  .action-btn {
    width: 100%;
    text-align: center;
  }
}
</style>