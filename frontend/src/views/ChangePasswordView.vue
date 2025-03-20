<template>
  <div>
    <div v-if="isMobileDevice" class="mobile-warning">
      <div class="warning-icon">⚠️</div>
      <h2>Acesso não recomendado</h2>
      <p>Este site não foi projetado para dispositivos móveis. Por favor, acesse através de um computador para uma melhor experiência.</p>
    </div>
    <div v-else class="home-layout">
      <div class="illustration-panel">
        <div class="large-svg-container">
          <img src="@/assets/change-password-image.svg" alt="Password Security Illustration" class="large-svg">
        </div>
      </div>
      <div class="content-panel">
        <div class="content-wrapper">
          <div class="home-header">
            <h1>Alterar Senha</h1>
          </div>
          
          <div class="dashboard-summary">
            <div class="dashboard-item">
              <h3>Senha Segura</h3>
              <p>Use 6+ caracteres com letras (maiúsculas e minúsculas), números e símbolos. Evite sequências óbvias.</p>
            </div>
          </div>
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
                    autocomplete="new-password"
                    autocorrect="off"
                    autocapitalize="off"
                    spellcheck="false"
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
                    autocomplete="new-password"
                    autocorrect="off"
                    autocapitalize="off"
                    spellcheck="false"
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
                <button type="submit" class="submit-btn" :disabled="isLoading || !isFormValid">
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
      let color = '#dc2626';
      let text = 'Fraca';
      if (password.length >= 6) strength += 1;
      if (password.length >= 10) strength += 1;
      if (/[0-9]/.test(password)) strength += 1;
      if (/[a-z]/.test(password)) strength += 1;
      if (/[A-Z]/.test(password)) strength += 1;
      if (/[^a-zA-Z0-9]/.test(password)) strength += 1;
      percentage = (strength / 6) * 100;
      if (strength <= 2) {
        color = '#dc2626';
        text = 'Fraca';
      } else if (strength <= 4) {
        color = '#f59e0b';
        text = 'Média';
      } else {
        color = '#10b981';
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
    window.addEventListener('resize', this.checkDeviceType);
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.checkDeviceType);
  },
  watch: {
    'passwordForm.newPassword': function(newValue) {
      if (newValue && newValue.length < 6) {
        this.passwordErrors.newPassword = 'A senha deve ter pelo menos 6 caracteres';
      } else {this.passwordErrors.newPassword = '';}
      
      if (newValue && this.passwordForm.confirmPassword && 
          newValue !== this.passwordForm.confirmPassword) {
        this.passwordErrors.confirmPassword = 'As senhas não coincidem';
      } else if (this.passwordForm.confirmPassword) {
        this.passwordErrors.confirmPassword = '';
      }
    },
    'passwordForm.confirmPassword': function(newValue) {
      if (newValue && this.passwordForm.newPassword && 
          newValue !== this.passwordForm.newPassword) {
        this.passwordErrors.confirmPassword = 'As senhas não coincidem';
      } else {this.passwordErrors.confirmPassword = '';}
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

        this.passwordForm = {
          newPassword: '',
          confirmPassword: ''
        };
        
        this.isLoading = false;
        
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
.mobile-warning {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: #142C4D;
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

.home-layout {
  position: fixed;
  top: 75px;
  left: 20px;
  right: 20px;
  bottom: 20px;
  display: flex;
  gap: 20px;
}

.content-panel {
  width: calc(50% - 10px); /* 50% da largura menos metade do gap */
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  overflow: hidden;
}

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

.password-form-container {
  margin-bottom: 1.5rem;
}

.password-form {
  background-color: #eeecff;
  padding: 1.5rem;
  border-radius: 8px;
  border: 1px solid #d8d6f8;
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
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 1rem;
  color: #333;
  background-color: #fff;
}

.password-input:focus {
  border-color: #564fcc;
  box-shadow: 0 0 0 3px rgba(86, 79, 204, 0.15);
  outline: none;
}

.invalid-input {
  border-color: #ef4444;
  background-color: #fee2e2;
}

.toggle-password {
  position: absolute;
  right: 10px;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1rem;
}

.error-text {
  color: #ef4444;
  font-size: 0.85rem;
  margin-top: 0.4rem;
  display: block;
}

.error-message {
  display: flex;
  align-items: center;
  padding: 1rem;
  background-color: #fee2e2;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  border: 1px solid #fecaca;
}

.error-icon {
  width: 24px;
  height: 24px;
  background-color: #ef4444;
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
  color: #666;
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
  background-color: #ecfdf5;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  border: 1px solid #a7f3d0;
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

.button-container {
  display: flex;
  justify-content: space-between;
  margin-top: 2rem;
}

.submit-btn {
  padding: 0.9rem 2rem;
  background-color: #564fcc;
  border: none;
  border-radius: 8px;
  color: white;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  min-width: 180px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.submit-btn:hover:not(:disabled) {
  background-color: #675ff5;
}

.submit-btn:disabled {
  background-color: #a8a5e0;
  cursor: not-allowed;
  opacity: 0.7;
}

.cancel-btn {
  padding: 0.9rem 2rem;
  background-color: #e5e5e5;
  border: none;
  border-radius: 8px;
  color: #333;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
}

.cancel-btn:hover {
  background-color: #b7b7b7;
}

.form-loading-indicator {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-right: 8px;
}

.password-strength {
  margin-top: 2rem;
  padding: 1.2rem;
  background-color: #f9f9f9;
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
  transition: width 0.5s;
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

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .home-layout {
    flex-direction: column;
    top: 65px;
  }
  
  .content-panel, .illustration-panel {
    width: 100%;
    margin-bottom: 15px;
  }
  
  .home-header h1 {
    font-size: 1.8rem;
  }
  
  .button-container {
    flex-direction: column;
    gap: 1rem;
  }
  
  .submit-btn, .cancel-btn {
    width: 100%;
  }
}
</style>