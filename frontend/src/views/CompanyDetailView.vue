<template>
  <div>
    <!-- Alerta para dispositivos móveis -->
    <div v-if="isMobileDevice" class="mobile-warning">
      <div class="warning-icon">⚠️</div>
      <h2>Acesso não recomendado</h2>
      <p>Este site não foi projetado para dispositivos móveis. Por favor, acesse através de um computador para uma melhor experiência.</p>
    </div>

    <!-- Conteúdo principal -->
    <div v-else class="home-layout">
      <!-- Painel com informações gerais (visualmente à esquerda) -->
      <div class="content-panel">
        <div class="content-wrapper">
          <div class="home-header">
            <h1>{{ company.name }}</h1>
          </div>

          <div v-if="error" class="error-message">
            <div class="error-icon">!</div>
            <p>{{ error }}</p>
            <button class="close-btn" @click="error = ''" aria-label="Fechar">×</button>
          </div>

          <div v-if="success" class="success-message">
            <div class="success-icon">✓</div>
            <p>{{ success }}</p>
            <button class="close-btn success" @click="success = ''" aria-label="Fechar">×</button>
          </div>

          <div v-if="loading" class="loading-indicator">
            <div class="loading-spinner"></div>
            <p>Carregando informações da empresa...</p>
          </div>

          <div v-else>
            <!-- Informações da Empresa -->
            <div class="dashboard-summary">
              <div class="dashboard-item">
                <h3>{{ company.name }}</h3>
                <div class="info-details">
                  <p><span class="info-label">ID:</span> {{ companyId }}</p>
                  <p><span class="info-label">Criado em:</span> {{ formatDate(company.created_at) }}</p>
                  <p><span class="info-label">CNPJ:</span> {{ company.cnpj }}</p>
                  <p><span class="info-label">Grupo:</span> 
                    <a @click="goToGroupDetail(company.group_id)" class="group-link">
                      {{ groupName }}
                    </a>
                  </p>
                </div>
              </div>
            </div>

            <!-- Zona de Edição -->
            <div v-if="isAdmin" class="dashboard-summary">
              <div class="dashboard-item">
                <h3>Editar Empresa</h3>
                <form @submit.prevent="updateCompany" class="company-form">
                  <div class="form-group">
                    <label for="companyName">Nome da Empresa:</label>
                    <input 
                      type="text" 
                      id="companyName" 
                      v-model="editCompany.name" 
                      required 
                      placeholder="Nome da Empresa"
                    >
                  </div>
                  
                  <div class="form-group">
                    <label for="companyCNPJ">CNPJ:</label>
                    <input 
                      type="text" 
                      id="companyCNPJ" 
                      v-model="editCompany.cnpj" 
                      @input="formatCNPJ"
                      required 
                      placeholder="XX.XXX.XXX/XXXX-XX"
                      :class="{ 'invalid-input': cnpjError }"
                    >
                    <small v-if="cnpjError" class="error-text">{{ cnpjError }}</small>
                  </div>
                  
                  <button 
                    type="submit" 
                    class="submit-btn" 
                    :disabled="updatingCompany || cnpjError !== ''"
                  >
                    <span v-if="updatingCompany" class="loading-spinner-small"></span>
                    {{ updatingCompany ? 'Atualizando...' : 'Atualizar Empresa' }}
                  </button>
                </form>
              </div>
            </div>

            <!-- Botão de excluir empresa -->
            <div v-if="isAdmin" class="dashboard-summary">
              <div class="dashboard-item danger-zone">
                <h3>Zona de Perigo</h3>
                <p>Cuidado! As ações abaixo são irreversíveis.</p>
                <div class="danger-actions">
                  <button class="delete-btn" @click="showDeleteConfirmation = true">
                    Excluir Empresa
                  </button>
                </div>
              </div>
            </div>
            
            <!-- Botões de ação -->
            <div class="quick-actions">
              <button class="secondary-button" @click="goBack">Voltar para o Grupo</button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Painel de arquivos e funcionários (visualmente à direita) -->
      <div class="content-panel">
        <div class="content-wrapper">
          <div v-if="loading" class="loading-indicator">
            <div class="loading-spinner"></div>
            <p>Carregando informações...</p>
          </div>

          <div v-else>
            <!-- Seção de Gerenciamento de Arquivos -->
            <div class="dashboard-summary">
              <div class="home-header">
                <h1>Arquivos</h1>
              </div>
              <div class="dashboard-item files-panel">
                <div class="files-content">
                  <div class="files-info">
                    <h3>Gerenciamento de Arquivos</h3>
                    <p v-if="files.length > 0" class="files-count">
                      {{ files.length }} {{ files.length === 1 ? 'arquivo disponível' : 'arquivos disponíveis' }}
                    </p>
                    <p v-else class="files-count">Nenhum arquivo disponível</p>
                  </div>
                  
                  <button class="file-manage-btn" @click="goToCompanyFiles">
                    <span class="file-icon">
                      <svg class="file-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
                      </svg>
                    </span>
                    Arquivos
                  </button>
                </div>
              </div>
            </div>

            <!-- Seção de Gerenciamento de Funcionários -->
            <div class="dashboard-summary">
              <div class="home-header">
                <h1>Funcionários</h1>
              </div>
              <div class="dashboard-item employees-panel">
                <div class="employees-content">
                  <div class="employees-info">
                    <h3>Gerenciamento de Funcionários</h3>
                    <p v-if="employees.length > 0" class="employees-count">
                      {{ employees.length }} {{ employees.length === 1 ? 'funcionário registrado' : 'funcionários registrados' }}
                    </p>
                    <p v-else class="employees-count">Nenhum funcionário registrado</p>
                  </div>
                  
                  <button class="employee-manage-btn" @click="showEmployeeManagement = true">
                    <span class="employee-icon">
                      <svg class="employee-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                          <circle cx="12" cy="7" r="4"></circle>
                      </svg>
                    </span>
                    Funcionários
                  </button>
                </div>

                <!-- Lista compacta de funcionários (exibe até 5) -->
                <div v-if="employees.length > 0" class="employee-list-preview">
                  <div v-for="employee in employeesPreview" :key="employee.id" class="employee-item-preview">
                    <div class="employee-name">{{ employee.name }}</div>
                    <div class="employee-cpf">CPF: {{ formatCPF(employee.cpf) }}</div>
                  </div>
                  <div v-if="employees.length > 5" class="more-employees">
                    + {{ employees.length - 5 }} mais...
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal de Confirmação de Exclusão (updated to match GroupManageView) -->
    <div v-if="showDeleteConfirmation" class="modal-overlay">
      <div class="modal-container">
        <div class="modal-header">
          <h3>Confirmação de Exclusão</h3>
          <button class="close-modal-btn" @click="cancelDelete">&times;</button>
        </div>
        <div class="modal-body">
          <p>Você está prestes a excluir a empresa <strong>{{ company.name }}</strong>, todos os seus arquivos e funcionários.</p>
          <p class="warning-text">Esta ação não pode ser desfeita!</p>
          
          <div class="confirmation-input">
            <label for="confirmText">Digite "EXCLUIR" para confirmar:</label>
            <input 
              type="text" 
              id="confirmText" 
              v-model="confirmDeleteText" 
              placeholder="EXCLUIR" 
              class="company-input"
            />
          </div>
        </div>
        <div class="modal-footer">
          <button class="cancel-btn" @click="cancelDelete">Cancelar</button>
          <button 
            class="delete-btn"
            :disabled="confirmDeleteText !== 'EXCLUIR' || deletingCompany"
            @click="deleteCompany"
          >
            {{ deletingCompany ? 'Excluindo...' : 'Confirmar Exclusão' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Modal de Gerenciamento de Funcionários -->
    <div v-if="showEmployeeManagement" class="modal-overlay">
      <div class="modal-container employee-modal">
        <div class="modal-header">
          <h3>Gerenciamento de Funcionários</h3>
          <button class="close-modal-btn" @click="showEmployeeManagement = false" aria-label="Fechar">×</button>
        </div>
        
        <div class="modal-body">
          <!-- Formulário para adicionar/editar funcionário -->
          <div class="employee-form-section">
            <h4>{{ isEditingEmployee ? 'Editar Funcionário' : 'Adicionar Novo Funcionário' }}</h4>
            <form @submit.prevent="saveEmployee" class="employee-form">
              <div class="form-group">
                <label for="employeeName">Nome:</label>
                <input 
                  type="text" 
                  id="employeeName" 
                  v-model="employeeForm.name" 
                  required 
                  placeholder="Nome do Funcionário"
                >
              </div>
              
              <div class="form-group">
                <label for="employeeCPF">CPF:</label>
                <input 
                  type="text" 
                  id="employeeCPF" 
                  v-model="employeeForm.cpf" 
                  @input="formatEmployeeCPF"
                  required 
                  placeholder="XXX.XXX.XXX-XX"
                  :class="{ 'invalid-input': cpfError }"
                  :disabled="isEditingEmployee"
                >
                <small v-if="cpfError" class="error-text">{{ cpfError }}</small>
              </div>
              
              <div class="form-actions">
                <button 
                  v-if="isEditingEmployee"
                  type="button" 
                  class="cancel-btn" 
                  @click="cancelEditEmployee"
                >
                  Cancelar
                </button>
                <button 
                  type="submit" 
                  class="submit-btn" 
                  :disabled="savingEmployee || cpfError !== ''"
                >
                  <span v-if="savingEmployee" class="loading-spinner-small"></span>
                  {{ isEditingEmployee ? 'Atualizar' : 'Adicionar' }}
                </button>
              </div>
            </form>
          </div>
          
          <!-- Lista de funcionários -->
          <div class="employee-list-section">
            <h4>Funcionários Cadastrados</h4>
            
            <div v-if="employeeLoading" class="loading-indicator">
              <div class="loading-spinner"></div>
              <p>Carregando funcionários...</p>
            </div>
            
            <div v-else-if="employees.length === 0" class="empty-state">
              <p>Nenhum funcionário cadastrado para esta empresa.</p>
            </div>
            
            <div v-else class="employee-list">
              <div v-for="employee in employees" :key="employee.id" class="employee-item">
                <div class="employee-details">
                  <div class="employee-name">{{ employee.name }}</div>
                  <div class="employee-cpf">CPF: {{ formatCPF(employee.cpf) }}</div>
                  <div class="employee-created">Criado em: {{ formatDate(employee.created_at) }}</div>
                </div>
                <div class="employee-actions">
                  <button class="edit-btn" @click="editEmployee(employee)">Editar</button>
                  <button class="delete-btn" @click="confirmDeleteEmployee(employee)">Excluir</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal de Confirmação de Exclusão de Funcionário -->
    <div v-if="showDeleteEmployeeConfirmation" class="modal-overlay">
      <div class="modal-container">
        <div class="modal-header">
          <h3>Confirmação de Exclusão</h3>
        </div>
        <div class="modal-body">
          <div class="warning-icon modal-icon">⚠️</div>
          <p>Você está prestes a excluir o funcionário <strong>{{ employeeToDelete?.name }}</strong>.</p>
          <p class="warning-text">Esta ação não pode ser desfeita!</p>
        </div>
        <div class="modal-footer">
          <button class="cancel-btn" @click="cancelDeleteEmployee">Cancelar</button>
          <button 
            class="delete-btn"
            :disabled="deletingEmployee"
            @click="deleteEmployee"
          >
            {{ deletingEmployee ? 'Excluindo...' : 'Confirmar Exclusão' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CompanyDetailView',
  data() {
    return {
      companyId: null,
      company: {},
      files: [],
      employees: [],
      loading: true,
      employeeLoading: false,
      error: '',
      success: '',
      isAdmin: false,
      groupName: '',
      isMobileDevice: false,
      showDeleteConfirmation: false,
      confirmDeleteText: '',
      deletingCompany: false,
      
      // Campos para edição da empresa
      editCompany: {
        name: '',
        cnpj: ''
      },
      cnpjError: '',
      updatingCompany: false,
      
      // Gerenciamento de funcionários
      showEmployeeManagement: false,
      employeeForm: {
        id: null,
        name: '',
        cpf: ''
      },
      isEditingEmployee: false,
      cpfError: '',
      savingEmployee: false,
      showDeleteEmployeeConfirmation: false,
      employeeToDelete: null,
      deletingEmployee: false
    }
  },
  computed: {
    // Retorna apenas os 5 primeiros funcionários para preview
    employeesPreview() {
      return this.employees.slice(0, 5);
    }
  },
  created() {
    this.checkDeviceType();
    this.checkAccess();
    
    // Obtém o ID da empresa da URL (agora é UUID, não precisa de parseInt)
    this.companyId = this.$route.params.id;
    this.fetchCompanyData();
    
    // Adicionar listener para verificar redimensionamento
    window.addEventListener('resize', this.checkDeviceType);
  },
  beforeUnmount() {
    // Remover listener ao destruir componente
    window.removeEventListener('resize', this.checkDeviceType);
  },
  methods: {
    checkDeviceType() {
      this.isMobileDevice = window.innerWidth < 1024;
    },
    checkAccess() {
      const userStr = localStorage.getItem('user');
      if (!userStr) {
        this.$router.push('/login');
        return;
      }
      
      const user = JSON.parse(userStr);
      this.isAdmin = user.is_admin === true;
    },
    async fetchCompanyData() {
      try {
        this.loading = true;
        this.error = ''; // Limpar erros anteriores
        const userStr = localStorage.getItem('user');
        if (!userStr) {
          this.$router.push('/login');
          return;
        }
        
        const user = JSON.parse(userStr);
        
        // Buscar dados da empresa
        console.log('Fetching company data for ID:', this.companyId);
        const response = await fetch(`/api/companies/${this.companyId}`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'User-ID': user.id
          }
        });
        
        if (!response.ok) {
          const data = await response.json();
          this.error = data.message || 'Erro ao carregar dados da empresa';
          this.loading = false;
          console.error('API error:', response.status, data);
          return;
        }
        
        const data = await response.json();
        this.company = data.company;
        console.log('Company data loaded:', this.company);
        
        // Preencher os campos de edição
        this.editCompany = {
          name: this.company.name,
          cnpj: this.company.cnpj
        };
        
        // Se a API já retorna os arquivos, podemos usar diretamente
        if (this.company.files) {
          this.files = this.company.files;
        } else {
          // Caso contrário, buscar arquivos separadamente
          await this.fetchCompanyFiles();
        }

        // Se a API já retorna os funcionários, podemos usar diretamente
        if (this.company.employees) {
          this.employees = this.company.employees;
        } else {
          // Caso contrário, buscar funcionários separadamente
          await this.fetchCompanyEmployees();
        }
        
        // Buscar nome do grupo se necessário
        if (this.company.group_id) {
          await this.fetchGroupName();
        }
        
        this.loading = false;
      } catch (error) {
        this.error = 'Erro ao conectar ao servidor';
        this.loading = false;
        console.error('Error fetching company data:', error);
      }
    },
    async fetchGroupName() {
      try {
        if (!this.company || !this.company.group_id) return;
        
        const userStr = localStorage.getItem('user');
        if (!userStr) return;
        
        const user = JSON.parse(userStr);
        
        // O ID do grupo é UUID, não precisa de conversão
        console.log('Fetching group name for UUID:', this.company.group_id);
        
        const response = await fetch(`/api/groups/${this.company.group_id}`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'User-ID': user.id
          }
        });
        
        if (!response.ok) {
          console.error('Failed to fetch group name, status:', response.status);
          return;
        }
        
        const data = await response.json();
        this.groupName = data.group.name;
      } catch (error) {
        console.error('Error fetching group name:', error);
      }
    },
    async fetchCompanyFiles() {
      try {
        const userStr = localStorage.getItem('user');
        if (!userStr) return;
        
        const user = JSON.parse(userStr);
        
        const response = await fetch(`/api/companies/${this.companyId}/files`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'User-ID': user.id
          }
        });
        
        if (!response.ok) {
          const data = await response.json();
          console.error('Error fetching files:', data.message);
          return;
        }
        
        const data = await response.json();
        this.files = data.files;
        console.log('Files loaded:', this.files);
      } catch (error) {
        console.error('Error fetching company files:', error);
      }
    },
    async fetchCompanyEmployees() {
      try {
        this.employeeLoading = true;
        const userStr = localStorage.getItem('user');
        if (!userStr) return;
        
        const user = JSON.parse(userStr);
        
        const response = await fetch(`/api/companies/${this.companyId}/employees`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'User-ID': user.id
          }
        });
        
        if (!response.ok) {
          const data = await response.json();
          console.error('Error fetching employees:', data.message);
          this.employeeLoading = false;
          return;
        }
        
        const data = await response.json();
        this.employees = data.employees;
        console.log('Employees loaded:', this.employees);
        this.employeeLoading = false;
      } catch (error) {
        console.error('Error fetching company employees:', error);
        this.employeeLoading = false;
      }
    },
    formatCNPJ() {
      // Remove qualquer caractere que não seja dígito
      let cnpj = this.editCompany.cnpj.replace(/\D/g, '');
      
      // Limita a 14 dígitos
      cnpj = cnpj.substring(0, 14);
      
      // Aplica a máscara XX.XXX.XXX/XXXX-XX
      if (cnpj.length > 0) {
        cnpj = cnpj.replace(/^(\d{2})(\d)/, '$1.$2');
        cnpj = cnpj.replace(/^(\d{2})\.(\d{3})(\d)/, '$1.$2.$3');
        cnpj = cnpj.replace(/\.(\d{3})(\d)/, '.$1/$2');
        cnpj = cnpj.replace(/(\d{4})(\d)/, '$1-$2');
      }
      
      this.editCompany.cnpj = cnpj;
      this.validateCNPJ();
    },
    validateCNPJ() {
      const cnpj = this.editCompany.cnpj.replace(/\D/g, '');
      
      if (cnpj.length === 0) {
        this.cnpjError = '';
        return;
      }
      
      if (cnpj.length !== 14) {
        this.cnpjError = 'CNPJ deve conter 14 dígitos.';
        return;
      }
      
      // Verificar se todos os dígitos são iguais
      if (/^(\d)\1+$/.test(cnpj)) {
        this.cnpjError = 'CNPJ inválido.';
        return;
      }
      
      // Validação dos dígitos verificadores
      // Primeiro dígito verificador
      let soma = 0;
      let peso = 2;
      
      for (let i = 11; i >= 0; i--) {
        soma += parseInt(cnpj.charAt(i)) * peso;
        peso = peso === 9 ? 2 : peso + 1;
      }
      
      let digito = 11 - (soma % 11);
      if (digito > 9) digito = 0;
      
      if (parseInt(cnpj.charAt(12)) !== digito) {
        this.cnpjError = 'CNPJ inválido.';
        return;
      }
      
      // Segundo dígito verificador
      soma = 0;
      peso = 2;
      
      for (let i = 12; i >= 0; i--) {
        soma += parseInt(cnpj.charAt(i)) * peso;
        peso = peso === 9 ? 2 : peso + 1;
      }
      
      digito = 11 - (soma % 11);
      if (digito > 9) digito = 0;
      
      if (parseInt(cnpj.charAt(13)) !== digito) {
        this.cnpjError = 'CNPJ inválido.';
        return;
      }
      
      this.cnpjError = '';
    },
    formatEmployeeCPF() {
      // Remove qualquer caractere que não seja dígito
      let cpf = this.employeeForm.cpf.replace(/\D/g, '');
      
      // Limita a 11 dígitos
      cpf = cpf.substring(0, 11);
      
      // Aplica a máscara XXX.XXX.XXX-XX
      if (cpf.length > 0) {
        cpf = cpf.replace(/^(\d{3})(\d)/, '$1.$2');
        cpf = cpf.replace(/^(\d{3})\.(\d{3})(\d)/, '$1.$2.$3');
        cpf = cpf.replace(/\.(\d{3})(\d)/, '.$1-$2');
      }
      
      this.employeeForm.cpf = cpf;
      this.validateCPF();
    },
    validateCPF() {
      const cpf = this.employeeForm.cpf.replace(/\D/g, '');
      
      if (cpf.length === 0) {
        this.cpfError = '';
        return;
      }
      
      if (cpf.length !== 11) {
        this.cpfError = 'CPF deve conter 11 dígitos.';
        return;
      }
      
      // Verificar se todos os dígitos são iguais
      if (/^(\d)\1+$/.test(cpf)) {
        this.cpfError = 'CPF inválido.';
        return;
      }
      
      // Validação dos dígitos verificadores
      // Primeiro dígito verificador
      let soma = 0;
      for (let i = 0; i < 9; i++) {
        soma += parseInt(cpf.charAt(i)) * (10 - i);
      }
      
      let resto = 11 - (soma % 11);
      let dv1 = resto > 9 ? 0 : resto;
      
      if (parseInt(cpf.charAt(9)) !== dv1) {
        this.cpfError = 'CPF inválido.';
        return;
      }
      
      // Segundo dígito verificador
      soma = 0;
      for (let i = 0; i < 10; i++) {
        soma += parseInt(cpf.charAt(i)) * (11 - i);
      }
      
      resto = 11 - (soma % 11);
      let dv2 = resto > 9 ? 0 : resto;
      
      if (parseInt(cpf.charAt(10)) !== dv2) {
        this.cpfError = 'CPF inválido.';
        return;
      }
      
      this.cpfError = '';
    },
    formatCPF(cpf) {
      if (!cpf) return '';
      
      // Se já estiver formatado, retorna como está
      if (cpf.includes('.') || cpf.includes('-')) {
        return cpf;
      }
      
      // Aplica a máscara XXX.XXX.XXX-XX
      cpf = cpf.replace(/^(\d{3})(\d{3})(\d{3})(\d{2})$/, '$1.$2.$3-$4');
      return cpf;
    },
    async updateCompany() {
      if (this.cnpjError) {
        return;
      }
      
      try {
        this.updatingCompany = true;
        const userStr = localStorage.getItem('user');
        if (!userStr) {
          this.$router.push('/login');
          return;
        }
        
        const user = JSON.parse(userStr);
        
        const response = await fetch(`/api/companies/${this.companyId}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'User-ID': user.id
          },
          body: JSON.stringify({
            name: this.editCompany.name,
            cnpj: this.editCompany.cnpj
          })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
          this.error = data.message || 'Erro ao atualizar empresa';
          this.updatingCompany = false;
          return;
        }
        
        // Atualizar dados da empresa
        this.company.name = this.editCompany.name;
        this.company.cnpj = this.editCompany.cnpj;
        
        this.success = 'Empresa atualizada com sucesso!';
        this.updatingCompany = false;
      } catch (error) {
        this.error = 'Erro ao conectar ao servidor';
        this.updatingCompany = false;
        console.error('Error updating company:', error);
      }
    },
    // Métodos para gerenciamento de funcionários
    editEmployee(employee) {
      this.isEditingEmployee = true;
      this.employeeForm = {
        id: employee.id,
        name: employee.name,
        cpf: employee.cpf
      };
    },
    cancelEditEmployee() {
      this.isEditingEmployee = false;
      this.employeeForm = {
        id: null,
        name: '',
        cpf: ''
      };
      this.cpfError = '';
    },
    async saveEmployee() {
      if (this.cpfError) {
        return;
      }
      
      try {
        this.savingEmployee = true;
        const userStr = localStorage.getItem('user');
        if (!userStr) {
          this.$router.push('/login');
          return;
        }
        
        const user = JSON.parse(userStr);
        
        if (this.isEditingEmployee) {
          // Atualizar funcionário existente
          const response = await fetch(`/api/employees/${this.employeeForm.id}`, {
            method: 'PUT',
            headers: {
              'Content-Type': 'application/json',
              'User-ID': user.id
            },
            body: JSON.stringify({
              name: this.employeeForm.name,
              cpf: this.employeeForm.cpf
            })
          });
          
          const data = await response.json();
          
          if (!response.ok) {
            this.error = data.message || 'Erro ao atualizar funcionário';
            this.savingEmployee = false;
            return;
          }
          
          // Atualiza o funcionário na lista
          const index = this.employees.findIndex(emp => emp.id === this.employeeForm.id);
          if (index !== -1) {
            this.employees[index] = data.employee;
          }
          
          this.success = 'Funcionário atualizado com sucesso!';
        } else {
          // Criar novo funcionário
          const response = await fetch(`/api/companies/${this.companyId}/employees`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'User-ID': user.id
            },
            body: JSON.stringify({
              name: this.employeeForm.name,
              cpf: this.employeeForm.cpf
            })
          });
          
          const data = await response.json();
          
          if (!response.ok) {
            this.error = data.message || 'Erro ao adicionar funcionário';
            this.savingEmployee = false;
            return;
          }
          
          // Adiciona o novo funcionário à lista
          this.employees.push(data.employee);
          this.success = 'Funcionário adicionado com sucesso!';
        }
        
        // Limpa o formulário e fecha o modo de edição
        this.cancelEditEmployee();
        this.savingEmployee = false;
      } catch (error) {
        this.error = 'Erro ao conectar ao servidor';
        this.savingEmployee = false;
        console.error('Error saving employee:', error);
      }
    },
    confirmDeleteEmployee(employee) {
      this.employeeToDelete = employee;
      this.showDeleteEmployeeConfirmation = true;
    },
    cancelDeleteEmployee() {
      this.employeeToDelete = null;
      this.showDeleteEmployeeConfirmation = false;
    },
    async deleteEmployee() {
      if (!this.employeeToDelete) {
        return;
      }
      
      try {
        this.deletingEmployee = true;
        const userStr = localStorage.getItem('user');
        if (!userStr) {
          this.$router.push('/login');
          return;
        }
        
        const user = JSON.parse(userStr);
        
        const response = await fetch(`/api/employees/${this.employeeToDelete.id}`, {
          method: 'DELETE',
          headers: {
            'Content-Type': 'application/json',
            'User-ID': user.id
          }
        });
        
        if (!response.ok) {
          const data = await response.json();
          this.error = data.message || 'Erro ao excluir funcionário';
          this.deletingEmployee = false;
          this.showDeleteEmployeeConfirmation = false;
          return;
        }
        
        // Remove o funcionário da lista
        this.employees = this.employees.filter(emp => emp.id !== this.employeeToDelete.id);
        this.success = 'Funcionário excluído com sucesso!';
        this.deletingEmployee = false;
        this.showDeleteEmployeeConfirmation = false;
        this.employeeToDelete = null;
      } catch (error) {
        this.error = 'Erro ao conectar ao servidor';
        this.deletingEmployee = false;
        this.showDeleteEmployeeConfirmation = false;
        console.error('Error deleting employee:', error);
      }
    },
    formatDate(dateString) {
      if (!dateString) return '';
      
      const options = { 
        day: '2-digit', 
        month: '2-digit', 
        year: 'numeric', 
        hour: '2-digit', 
        minute: '2-digit' 
      };
      
      try {
        return new Date(dateString).toLocaleDateString('pt-BR', options);
      } catch (error) {
        return dateString;
      }
    },
    goToGroupDetail(groupId) {
      // groupId agora é um UUID (string), não precisamos converter para número
      this.$router.push(`/groups/${groupId}`);
    },
    goBack() {
      if (this.company && this.company.group_id) {
        // company.group_id agora é um UUID (string)
        this.$router.push(`/groups/${this.company.group_id}`);
      } else {
        this.$router.push('/');
      }
    },
    goToCompanyFiles() {
      // Redirecionar para a página de gerenciamento de arquivos
      this.$router.push(`/companies/${this.companyId}/files`);
    },
    cancelDelete() {
      this.showDeleteConfirmation = false;
      this.confirmDeleteText = '';
    },
    async deleteCompany() {
      try {
        if (this.confirmDeleteText !== 'EXCLUIR') {
          return;
        }
        
        this.deletingCompany = true;
        const userStr = localStorage.getItem('user');
        if (!userStr) {
          this.$router.push('/login');
          return;
        }
        
        const user = JSON.parse(userStr);
        // Lembre-se que groupId agora é um UUID (string)
        const groupId = this.company.group_id; 
        
        console.log('Deleting company:', this.companyId);
        
        const response = await fetch(`/api/companies/${this.companyId}`, {
          method: 'DELETE',
          headers: {
            'Content-Type': 'application/json',
            'User-ID': user.id
          }
        });
        
        if (!response.ok) {
          const data = await response.json();
          this.error = data.message || 'Erro ao excluir a empresa';
          this.deletingCompany = false;
          this.showDeleteConfirmation = false;
          return;
        }
        
        console.log('Company deleted successfully');
        this.success = 'Empresa excluída com sucesso. Redirecionando...';
        this.deletingCompany = false;
        this.showDeleteConfirmation = false;
        
        // Redirecionar após 2 segundos para a página do grupo (usando UUID)
        setTimeout(() => {
          this.$router.push(`/groups/${groupId}`);
        }, 2000);
      } catch (error) {
        this.error = 'Erro ao conectar ao servidor';
        this.deletingCompany = false;
        this.showDeleteConfirmation = false;
        console.error('Error deleting company:', error);
      }
    }
  }
}
</script>

<style scoped>
/* Layout principal */
.home-layout {
  position: fixed;
  top: 75px;
  left: 20px;
  right: 20px;
  bottom: 20px;
  display: flex;
  gap: 20px;
}

/* Painéis de conteúdo */
.content-panel {
  width: 50%;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  overflow: hidden;
}

/* Container do conteúdo */
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
  font-weight: 500;
  margin-bottom: 0.5rem;
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
  margin-bottom: 0.8rem;
}

/* Zona de perigo */
.danger-zone {
  background-color: #fee2e2;
  border: 1px solid #fecaca;
}

/* Estilos de formulários */
.company-form, .employee-form {
  margin-top: 1rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #333;
}

input {
  width: 100%;
  padding: 0.9rem;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 1rem;
  color: #333;
  background-color: #fff;
}

input:focus {
  border-color: #564fcc;
  box-shadow: 0 0 0 3px rgba(86, 79, 204, 0.15);
  outline: none;
}

.invalid-input {
  border-color: #ef4444;
  background-color: #fee2e2;
}

.error-text {
  color: #ef4444;
  font-size: 0.85rem;
  margin-top: 0.4rem;
  display: block;
}

/* Botões */
.submit-btn, .secondary-button, .file-manage-btn, .employee-manage-btn {
  display: inline-block;
  padding: 0.8rem 1.5rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  border: none;
  font-size: 1rem;
  text-align: center;
}

.submit-btn, .file-manage-btn, .employee-manage-btn {
  background-color: #564fcc;
  color: white;
}

.submit-btn:hover:not(:disabled), .file-manage-btn:hover, .employee-manage-btn:hover {
  background-color: #675ff5;
}

.submit-btn:disabled {
  background-color: #a8a5e0;
  cursor: not-allowed;
}

.secondary-button {
  background-color: #e5e5e5;
  color: #333;
}

.secondary-button:hover {
  background-color: #b7b7b7;
}

.delete-btn {
  background-color: #ef4444;
  color: white;
  padding: 0.8rem 1.5rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  border: none;
  font-size: 1rem;
}

.delete-btn:hover:not(:disabled) {
  background-color: #ff5252;
}

.delete-btn:disabled {
  background-color: #fca5a5;
  cursor: not-allowed;
}

.edit-btn {
  background-color: #564fcc;
  color: white;
  padding: 0.6rem 1rem;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  border: none;
  font-size: 0.9rem;
  margin-right: 0.5rem;
}

.edit-btn:hover {
  background-color: #675ff5;
}

.cancel-btn {
  background-color: #e5e5e5;
  color: #333;
  padding: 0.8rem 1.5rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  border: none;
  font-size: 1rem;
}

.cancel-btn:hover {
  background-color: #b7b7b7;
}

/* Estados de carregamento */
.loading-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2rem;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(86, 79, 204, 0.2);
  border-top: 4px solid #564fcc;
  border-radius: 50%;
  margin-bottom: 1rem;
}

.loading-spinner-small {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid #fff;
  border-radius: 50%;
  margin-right: 8px;
}

.empty-state {
  text-align: center;
  padding: 2rem;
  color: #666;
}

/* Informações detalhadas */
.info-details {
  margin-top: 0.8rem;
}

.info-label {
  font-weight: 600;
  color: #333;
}

/* Mensagens de erro e sucesso */
.error-message, .success-message {
  display: flex;
  align-items: center;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
}

.error-message {
  background-color: #fee2e2;
  border: 1px solid #fecaca;
}

.success-message {
  background-color: #ecfdf5;
  border: 1px solid #a7f3d0;
}

.error-icon, .success-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  margin-right: 0.8rem;
  font-weight: bold;
}

.error-icon {
  background-color: #ef4444;
  color: white;
}

.success-icon {
  background-color: #10b981;
  color: white;
}

.close-btn {
  margin-left: auto;
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  color: #666;
}

/* Painéis específicos */
.files-panel, .employees-panel {
  background-color: #eeecff;
  border: 1px solid #d8d6f8;
}

.files-content, .employees-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.file-icon, .employee-icon {
  margin-right: 0.5rem;
  vertical-align: middle;
}

/* Estilo de links */
.group-link {
  color: #564fcc;
  text-decoration: underline;
  cursor: pointer;
}

.group-link:hover {
  color: #675ff5;
}

/* Lista de funcionários */
.employee-list, .employee-list-preview {
  margin-top: 1rem;
}

.employee-item, .employee-item-preview {
  padding: 1rem;
  border-bottom: 1px solid #eaeaea;
}

.employee-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.employee-item:last-child, .employee-item-preview:last-child {
  border-bottom: none;
}

.employee-details {
  display: flex;
  flex-direction: column;
}

.employee-name {
  font-weight: 600;
  color: #333;
}

.employee-cpf, .employee-created {
  font-size: 0.85rem;
  color: #666;
  margin-top: 0.2rem;
}

.employee-actions {
  display: flex;
}

.more-employees {
  text-align: center;
  padding: 0.5rem;
  color: #564fcc;
  font-weight: 500;
}

/* Formulário de funcionário */
.employee-form-section, .employee-list-section {
  margin-bottom: 2rem;
}

.employee-form-section h4, .employee-list-section h4 {
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #eaeaea;
  color: #204578;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1rem;
}

/* Aviso para dispositivos móveis */
.mobile-warning {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background-color: white;
  padding: 2rem;
  z-index: 1000;
}

.warning-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

/* Botões de ação rápida */
.quick-actions, .danger-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
}

/* Modal (utilizando o mesmo estilo do GroupManageView) */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-container {
  background-color: white;
  border-radius: 8px;
  width: 500px;
  max-width: 90%;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.employee-modal {
  width: 700px;
  max-width: 90%;
}

.modal-header {
  padding: 1rem;
  background-color: #ef4444;
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.close-modal-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: white;
  cursor: pointer;
}

.modal-body {
  padding: 1.5rem;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1rem;
  background-color: #f9f9f9;
}

.modal-icon {
  display: block;
  font-size: 2rem;
  text-align: center;
  margin-bottom: 1rem;
}

.warning-text {
  color: #ef4444;
  font-weight: 600;
  margin: 1rem 0;
}

.confirmation-input {
  margin-top: 1.5rem;
}

/* Responsividade */
@media (max-width: 768px) {
  .home-layout {
    flex-direction: column;
    top: 65px;
  }
  
  .content-panel {
    width: 100%;
    margin-bottom: 15px;
  }
  
  .home-header h1 {
    font-size: 1.8rem;
  }
  
  .quick-actions {
    flex-direction: column;
  }
  
  .submit-btn, .secondary-button, .delete-btn, .edit-btn, .cancel-btn {
    width: 100%;
  }
  
  .employee-item {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .employee-actions {
    margin-top: 1rem;
    width: 100%;
  }
  
  .employee-actions button {
    flex: 1;
  }
}
</style>