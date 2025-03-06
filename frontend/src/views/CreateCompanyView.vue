<template>
  <div class="store-layout">
    <div class="store-container">
      <div class="store-content">
        <div class="page-header">
          <h1>Criar Nova Empresa</h1>
        </div>

        <form @submit.prevent="handleCreateCompany" class="store-form">
          <div class="form-row">
            <div class="form-group">
              <label for="name">Nome da Empresa:</label>
              <input 
                type="text" 
                id="name" 
                v-model="company.name" 
                required
                placeholder="Digite o nome da empresa"
              >
            </div>
            
            <div class="form-group">
              <label for="state_registration">Inscrição Estadual:</label>
              <input 
                type="text" 
                id="state_registration" 
                v-model="company.state_registration" 
                required
                placeholder="Digite a inscrição estadual"
              >
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group full-width">
              <label for="cnpj">CNPJ:</label>
              <input 
                type="text" 
                id="cnpj" 
                v-model="company.cnpj" 
                required
                placeholder="Digite o CNPJ da empresa"
              >
            </div>
          </div>

          <div class="button-container">
            <button type="submit" :disabled="loading" class="submit-btn">
              <span v-if="loading" class="loading-indicator"></span>
              {{ loading ? 'Criando...' : 'Criar Empresa' }}
            </button>
          </div>
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
            <router-link to="/" class="action-btn view-btn">Voltar para Home</router-link>
            <button @click="resetForm" class="action-btn reset-btn">Criar outra empresa</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CreateCompanyView',
  data() {
    return {
      company: {
        name: '',
        state_registration: '',
        cnpj: ''
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
    async handleCreateCompany() {
      this.loading = true;
      this.error = null;
      
      try {
        const userStr = localStorage.getItem('user');
        if (!userStr) {
          this.$router.push('/login');
          return;
        }
        
        const user = JSON.parse(userStr);
        
        const response = await fetch('/api/companies', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'User-ID': user.id
          },
          body: JSON.stringify(this.company)
        });
        
        const data = await response.json();
        
        if (!response.ok) {
          this.error = data.message || 'Erro ao criar empresa';
          this.loading = false;
          return;
        }
        
        this.successMessage = 'Empresa criada com sucesso!';
        this.loading = false;
      } catch (error) {
        this.error = 'Erro ao conectar ao servidor';
        this.loading = false;
        console.error('Error creating company:', error);
      }
    },
    resetForm() {
      this.company = {
        name: '',
        state_registration: '',
        cnpj: ''
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
.store-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  width: 100%;
  overflow: hidden;
}

.store-container {
  flex: 1;
  overflow-y: auto;
  padding: 2rem 3rem;
  display: flex;
  justify-content: center;
}

.store-content {
  width: 100%;
  min-width: 1200px;
  max-width: 85%;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
  padding: 2.5rem 3rem;
  animation: fade-in 0.6s ease-out;
  overflow-y: auto;
  max-height: calc(100vh - 4rem);
}

.page-header {
  margin-bottom: 2.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #eaeaea;
}

.page-header h1 {
  color: #142C4D;
  font-size: 2.2rem;
  font-weight: 700;
}

.store-form {
  margin-bottom: 2rem;
}

.form-row {
  display: flex;
  gap: 2rem;
  margin-bottom: 1rem;
}

.form-group {
  margin-bottom: 1.5rem;
  text-align: left;
  flex: 1;
}

.full-width {
  width: 100%;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  color: #333;
}

.form-group input, .form-group textarea, .form-group select {
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

.form-group input:focus, .form-group textarea:focus, .form-group select:focus {
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

/* Estilo para o select */
.select-wrapper {
  position: relative;
}

.select-wrapper:after {
  content: "\25BC";
  position: absolute;
  right: 15px;
  top: 50%;
  transform: translateY(-50%);
  pointer-events: none;
  color: #555;
  font-size: 0.8rem;
}

select {
  appearance: none;
  cursor: pointer;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 0;
}

.loading-state .loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(32, 69, 120, 0.1);
  border-top-color: #204578;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1.5rem;
}

.button-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 1rem;
}

.submit-btn {
  padding: 1rem 2.5rem;
  background: linear-gradient(to right, #142C4D, #204578);
  border: none;
  border-radius: 8px;
  color: white;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 200px;
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
  padding: 1.2rem;
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
  gap: 1.5rem;
  margin-top: 1.5rem;
  justify-content: center;
}

.action-btn {
  padding: 0.8rem 1.5rem;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
  min-width: 180px;
  text-align: center;
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
</style>