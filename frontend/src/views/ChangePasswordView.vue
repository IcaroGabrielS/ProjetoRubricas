<template>
  <div>
    <!-- Alerta para dispositivos móveis -->
    <div v-if="isMobileDevice" class="mobile-warning">
      <div class="warning-icon">⚠️</div>
      <h2>Acesso não recomendado</h2>
      <p>Este site não foi projetado para dispositivos móveis. Por favor, acesse através de um computador para uma melhor experiência.</p>
    </div>

    <!-- Conteúdo principal - visível apenas em desktop -->
    <div v-else class="home-layout">
      <!-- Painel com a ilustração (visualmente à esquerda) -->
      <div class="illustration-panel">
        <div class="large-svg-container">
          <img src="@/assets/change-password-image.svg" alt="Password Security Illustration" class="large-svg">
        </div>
      </div>
      
      <!-- Painel com o conteúdo (visualmente à direita) -->
      <div class="content-panel">
        <div class="content-wrapper">
          <div class="home-header">
            <h1>Alterar Senha</h1>
          </div>
          
          <div class="dashboard-summary">
            <div class="dashboard-item">
              <h3>Dicas de Segurança</h3>
              <p>Uma senha segura deve conter pelo menos 6 caracteres, combinar letras, números e símbolos.</p>
            </div>
          </div>
          
          <!-- Formulário de alteração de senha -->
          <div class="password-form-container">
            <form @submit.prevent="changePassword" class="password-form">
              
              <div class="form-group">
                <label for="new-password">Nova Senha:</label>
                <div class="password-input-container">
                  <input 
                    :type="showNewPassword ? 'text' : 'password'" 
                    id="new-password" 
                    v-model="passwordForm.newPassword" 
                    required
                    placeholder="Digite sua nova senha"
                    class="password-input"
                    :class="{ 'invalid-input': passwordErrors.newPassword }"
                  >
                  <button 
                    type="button" 
                    class="toggle-password" 
                    @click="showNewPassword = !showNewPassword"
                  >
                    <svg v-if="showNewPassword" class="eye-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="#636e72" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                      <circle cx="12" cy="12" r="3"></circle>
                    </svg>
                    <svg v-else class="eye-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="#636e72" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
                      <line x1="1" y1="1" x2="23" y2="23"></line>
                    </svg>
                  </button>
                </div>
                <span v-if="passwordErrors.newPassword" class="error-text">{{ passwordErrors.newPassword }}</span>
              </div>
              
              <div class="form-group">
                <label for="confirm-password">Confirmar Nova Senha:</label>
                <div class="password-input-container">
                  <input 
                    :type="showConfirmPassword ? 'text' : 'password'" 
                    id="confirm-password" 
                    v-model="passwordForm.confirmPassword" 
                    required
                    placeholder="Confirme sua nova senha"
                    class="password-input"
                    :class="{ 'invalid-input': passwordErrors.confirmPassword }"
                  >
                  <button 
                    type="button" 
                    class="toggle-password" 
                    @click="showConfirmPassword = !showConfirmPassword"
                  >
                    <svg v-if="showConfirmPassword" class="eye-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="#636e72" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                      <circle cx="12" cy="12" r="3"></circle>
                    </svg>
                    <svg v-else class="eye-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="#636e72" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
                      <line x1="1" y1="1" x2="23" y2="23"></line>
                    </svg>
                  </button>
                </div>
                <span v-if="passwordErrors.confirmPassword" class="error-text">{{ passwordErrors.confirmPassword }}</span>
              </div>
              
              <div v-if="error" class="error-message">
                <div class="error-icon">!</div>
                <p>{{ error }}</p>
                <button class="close-btn" @click="error = ''" aria-label="Fechar">×</button>
              </div>
              
              <div v-if="success" class="success-message">
                <div class="success-icon">✓</div>
                <p>{{ success }}</p>
              </div>
              
              <div class="button-container">
                <button type="button" class="cancel-btn" @click="goBack">Cancelar</button>
                <button 
                  type="submit" 
                  class="submit-btn" 
                  :disabled="isLoading || !isFormValid"
                >
                  <span v-if="isLoading" class="form-loading-indicator"></span>
                  {{ isLoading ? 'Alterando...' : 'Alterar Senha' }}
                </button>
              </div>
            </form>
          </div>
          
          <div class="password-strength" v-if="passwordForm.newPassword">
            <h4>Força da Senha:</h4>
            <div class="strength-meter">
              <div 
                class="strength-bar" 
                :style="{ width: passwordStrength.percentage + '%', backgroundColor: passwordStrength.color }"
              ></div>
            </div>
            <p class="strength-text" :style="{ color: passwordStrength.color }">{{ passwordStrength.text }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ChangePasswordView',
  data() {
    return {
      passwordForm: {
        newPassword: '',
        confirmPassword: ''
      },
      passwordErrors: {
        newPassword: '',
        confirmPassword: ''
      },
      showNewPassword: false,
      showConfirmPassword: false,
      isLoading: false,
      success: '',
      error: '',
      isMobileDevice: false
    }
  },
  computed: {
    isFormValid() {
      return this.passwordForm.newPassword &&
             this.passwordForm.confirmPassword &&
             this.passwordForm.newPassword === this.passwordForm.confirmPassword &&
             this.passwordForm.newPassword.length >= 6;
    },
    passwordStrength() {
      const password = this.passwordForm.newPassword;
      if (!password) {
        return {
          percentage: 0,
          color: '#e1e1e1',
          text: ''
        };
      }
      
      let strength = 0;
      let percentage = 0;
      let color = '#dc2626'; // Vermelho (fraca)
      let text = 'Fraca';
      
      // Verificar comprimento
      if (password.length >= 6) strength += 1;
      if (password.length >= 10) strength += 1;
      
      // Verificar números
      if (/[0-9]/.test(password)) strength += 1;
      
      // Verificar letras minúsculas e maiúsculas
      if (/[a-z]/.test(password)) strength += 1;
      if (/[A-Z]/.test(password)) strength += 1;
      
      // Verificar caracteres especiais
      if (/[^a-zA-Z0-9]/.test(password)) strength += 1;
      
      // Calcular porcentagem baseado na força
      percentage = (strength / 6) * 100;
      
      // Definir cor e texto com base na força
      if (strength <= 2) {
        color = '#dc2626'; // Vermelho (fraca)
        text = 'Fraca';
      } else if (strength <= 4) {
        color = '#f59e0b'; // Amarelo (média)
        text = 'Média';
      } else {
        color = '#10b981'; // Verde (forte)
        text = 'Forte';
      }
      
      return {
        percentage,
        color,
        text
      };
    }
  },
  created() {
    this.checkDeviceType();
    this.checkIfLoggedIn();
    
    // Adicionar listener para verificar redimensionamento
    window.addEventListener('resize', this.checkDeviceType);
  },
  beforeUnmount() {
    // Remover listener ao destruir componente
    window.removeEventListener('resize', this.checkDeviceType);
  },
  watch: {
    'passwordForm.newPassword': function(newValue) {
      // Validar comprimento mínimo
      if (newValue && newValue.length < 6) {
        this.passwordErrors.newPassword = 'A senha deve ter pelo menos 6 caracteres';
      } else {
        this.passwordErrors.newPassword = '';
      }
      
      // Validar se confirmação coincide quando ambos estão preenchidos
      if (newValue && this.passwordForm.confirmPassword && 
          newValue !== this.passwordForm.confirmPassword) {
        this.passwordErrors.confirmPassword = 'As senhas não coincidem';
      } else if (this.passwordForm.confirmPassword) {
        this.passwordErrors.confirmPassword = '';
      }
    },
    'passwordForm.confirmPassword': function(newValue) {
      // Validar se confirmação coincide
      if (newValue && this.passwordForm.newPassword && 
          newValue !== this.passwordForm.newPassword) {
        this.passwordErrors.confirmPassword = 'As senhas não coincidem';
      } else {
        this.passwordErrors.confirmPassword = '';
      }
    }
  },
  methods: {
    checkDeviceType() {
      this.isMobileDevice = window.innerWidth < 1024;
    },
    checkIfLoggedIn() {
      const userStr = localStorage.getItem('user');
      if (!userStr) {
        this.$router.push('/login');
      }
    },
    async changePassword() {
      if (!this.isFormValid) return;
      
      this.isLoading = true;
      this.error = '';
      this.success = '';
      
      try {
        const userStr = localStorage.getItem('user');
        if (!userStr) {
          this.$router.push('/login');
          return;
        }
        
        const user = JSON.parse(userStr);
        
        // Usar a nova rota que não requer verificação de senha atual
        const response = await fetch(`/api/users/${user.id}/change_password_no_verify`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'User-ID': user.id
          },
          body: JSON.stringify({
            new_password: this.passwordForm.newPassword
          })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
          this.error = data.message || 'Erro ao alterar senha';
          this.isLoading = false;
          return;
        }
        
        this.success = 'Senha alterada com sucesso!';
        
        // Limpar o formulário
        this.passwordForm = {
          newPassword: '',
          confirmPassword: ''
        };
        
        this.isLoading = false;
        
        // Redirecionar para a home após alguns segundos
        setTimeout(() => {
          this.$router.push('/');
        }, 3000);
      } catch (error) {
        this.error = 'Erro ao conectar ao servidor';
        this.isLoading = false;
        console.error('Error changing password:', error);
      }
    },
    goBack() {
      this.$router.push('/');
    }
  }
}
</script>

<style scoped>
/* Os estilos permanecem inalterados, então mantive-os como estavam */
/* Alerta para dispositivos móveis */
.mobile-warning {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: linear-gradient(135deg, #142C4D, #204578);
  color: white;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 20px;
  z-index: 9999;
}

.warning-icon {
  font-size: 50px;
  margin-bottom: 20px;
}

.mobile-warning h2 {
  font-size: 24px;
  margin-bottom: 15px;
}

.mobile-warning p {
  font-size: 16px;
  max-width: 280px;
}

/* Layout principal - versão desktop */
.home-layout {
  position: fixed;
  top: 90px;
  left: 20px;
  right: 20px;
  bottom: 20px;
  display: flex;
  gap: 20px; /* Espaçamento entre os containers */
}

/* Painel de conteúdo (visualmente à direita) */
.content-panel {
  width: calc(50% - 10px); /* 50% da largura menos metade do gap */
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
  animation: fade-in 0.8s ease-out;
  overflow: hidden;
}

/* Painel de ilustração (visualmente à esquerda) */
.illustration-panel {
  width: calc(50% - 10px); /* 50% da largura menos metade do gap */
  background: linear-gradient(155deg, #f0f0f0 50%, #564FCC  50%);
  border-radius: 12px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  overflow: hidden;
  animation: fade-in 0.8s ease-out;
}

/* Container e estilos para o SVG grande */
.large-svg-container {
  width: 90%;
  height: 90%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.large-svg {
  max-width: 100%;
  max-height: 100%;
}

/* Container do conteúdo para o painel de conteúdo */
.content-wrapper {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 2rem;
  overflow-y: auto;
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

.dashboard-summary {
  margin-bottom: 1.5rem;
}

.dashboard-item {
  padding: 1.2rem;
  background-color: #f8f9fa;
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

/* Formulário de alteração de senha */
.password-form-container {
  margin-bottom: 1.5rem;
}

.password-form {
  background-color: #f0f7ff;
  padding: 1.5rem;
  border-radius: 8px;
  border: 1px solid #d0e1fd;
}

.form-group {
  margin-bottom: 1.5rem;
  text-align: left;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  color: #333;
}

.password-input-container {
  position: relative;
  display: flex;
  align-items: center;
}

.password-input {
  width: 100%;
  padding: 0.9rem;
  border: 2px solid #d0e1fd;
  border-radius: 8px;
  font-size: 1rem;
  color: #333;
  transition: all 0.3s ease;
  background-color: #fff;
}

.password-input:focus {
  border-color: #204578;
  box-shadow: 0 0 0 3px rgba(32, 69, 120, 0.15);
  outline: none;
}

.invalid-input {
  border-color: #f87171;
  background-color: #fff5f5;
}

.toggle-password {
  position: absolute;
  right: 10px;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.2s ease;
}

.toggle-password:hover {
  transform: scale(1.2);
}

.error-text {
  color: #dc2626;
  font-size: 0.85rem;
  margin-top: 0.4rem;
  display: block;
}

/* Mensagens de erro e sucesso */
.error-message {
  display: flex;
  align-items: center;
  padding: 1rem;
  background-color: #fee2e2;
  border-radius: 8px;
  margin-bottom: 1.5rem;
}

.error-icon {
  width: 24px;
  height: 24px;
  background-color: #dc2626;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  margin-right: 0.8rem;
  flex-shrink: 0;
}

.close-btn {
  background: none;
  border: none;
  color: #b91c1c;
  cursor: pointer;
  font-size: 1.2rem;
  padding: 0 0.5rem;
  margin-left: auto;
  flex-shrink: 0;
}

.success-message {
  display: flex;
  align-items: center;
  padding: 1rem;
  background-color: #d1fae5;
  border-radius: 8px;
  margin-bottom: 1.5rem;
}

.success-icon {
  width: 24px;
  height: 24px;
  background-color: #10b981;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  margin-right: 0.8rem;
  flex-shrink: 0;
}

/* Botões */
.button-container {
  display: flex;
  justify-content: space-between;
  margin-top: 2rem;
}

.submit-btn {
  padding: 0.9rem 2rem;
  background: linear-gradient(to right, #142C4D, #204578);
  border: none;
  border-radius: 8px;
  color: white;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 180px;
  display: flex;
  justify-content: center;
    align-items: center;
  }
  
  .submit-btn:hover:not(:disabled) {
    background: linear-gradient(to right, #1a3760, #2a5b9e);
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(20, 44, 77, 0.3);
  }
  
  .submit-btn:disabled {
    background: linear-gradient(to right, #6c757d, #495057);
    cursor: not-allowed;
    opacity: 0.7;
  }
  
  .cancel-btn {
    padding: 0.9rem 2rem;
    background-color: #f1f1f1;
    border: 1px solid #e1e1e1;
    border-radius: 8px;
    color: #333;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
  }
  
  .cancel-btn:hover {
    background-color: #e5e5e5;
    transform: translateY(-2px);
  }
  
  /* Indicador de carregamento */
  .form-loading-indicator {
    width: 18px;
    height: 18px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-top: 2px solid white;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-right: 8px;
  }
  
  /* Indicador de força da senha */
  .password-strength {
    margin-top: 2rem;
    padding: 1.2rem;
    background-color: #f8f9fa;
    border-radius: 8px;
  }
  
  .password-strength h4 {
    color: #333;
    font-size: 1rem;
    margin-bottom: 0.8rem;
  }
  
  .strength-meter {
    height: 8px;
    background-color: #e1e1e1;
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 0.5rem;
  }
  
  .strength-bar {
    height: 100%;
    border-radius: 4px;
    transition: width 0.5s ease, background-color 0.5s ease;
  }
  
  .strength-text {
    font-size: 0.9rem;
    font-weight: 600;
    text-align: right;
  }
  
  .toggle-password {
    background: none;
    border: none;
    cursor: pointer;
    padding: 5px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .eye-icon {
    width: 24px;
    height: 24px;
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
</style>