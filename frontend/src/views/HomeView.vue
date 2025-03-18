<template>
  <div>
    <!-- Alerta para dispositivos móveis - sem alterações -->
    <div v-if="isMobileDevice" class="mobile-warning">
      <div class="warning-icon">⚠️</div>
      <h2>Acesso não recomendado</h2>
      <p>Este site não foi projetado para dispositivos móveis. Por favor, acesse através de um computador para uma melhor experiência.</p>
    </div>

    <!-- Conteúdo principal - visível apenas em desktop -->
    <div v-else class="home-layout">
      <!-- Painel com o conteúdo (visualmente à direita) -->
      <div class="content-panel">
        <div class="content-wrapper">
          <div class="home-header">
            <h1>Olá, {{ username }}!</h1>
            <p class="welcome-text">Você logou com sucesso.</p>
          </div>
          
          <div class="dashboard-summary">
            <div class="dashboard-item">
              <h3>Seus Grupos</h3>
              <p>Selecione um grupo abaixo para acessar seus detalhes e arquivos.</p>
            </div>
          </div>
          
          <!-- Caixa de busca para grupos -->
          <div class="search-container">
            <div class="search-box">
              <input 
                type="text" 
                v-model="searchQuery" 
                placeholder="Pesquisar grupos..."
                class="search-input"
              >
              <span class="search-icon">🔍</span>
            </div>
          </div>
          
          <!-- Lista de grupos -->
          <div class="stores-section">
            <!-- CORRIGIDO: Indicador de carregamento -->
            <div v-if="groupsLoading" class="groups-loading-container">
              <div class="groups-loading-spinner"></div>
              <p>Carregando grupos...</p>
            </div>
            
            <div v-else-if="groupsError" class="error-message">
              <div class="error-icon">!</div>
              <p>{{ groupsError }}</p>
            </div>
            
            <div v-else-if="filteredGroups.length === 0 && groups.length === 0" class="empty-state">
              <p>Você não tem acesso a nenhum grupo no momento.</p>
            </div>
            
            <div v-else-if="filteredGroups.length === 0" class="empty-state">
              <p>Nenhum grupo encontrado com esse nome.</p>
            </div>
            
            <div v-else class="stores-list">
              <div 
                v-for="group in filteredGroups" 
                :key="group.id" 
                class="store-item"
              >
                <div class="store-item-details">
                  <span class="store-name">{{ group.name }}</span>
                </div>
                <div class="store-item-actions">
                  <!-- Botão de gerenciamento removido, mantendo apenas a seta de navegação -->
                  <div class="arrow-container" @click="goToGroupDetail(group.id)" title="Ver detalhes do grupo">
                    <span class="store-item-arrow">›</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Botões de ação -->
          <div class="quick-actions">
            <button v-if="isAdmin" class="action-button admin" @click="showCreateGroupModal = true">Novo Grupo</button>
            <button v-if="isAdmin" class="action-button admin" @click="manageAccounts">Gerenciar Contas</button>
          </div>
        </div>
      </div>
      
      <!-- NOVO LAYOUT: Dois painéis à esquerda -->
      <!-- Painel superior com o calendário -->
      <div class="calendar-panel">
        <!-- Calendário completo -->
        <div class="full-calendar-container">
          <div class="calendar-header">
            <button @click="prevMonth" class="calendar-nav-btn">&lt;</button>
            <h3>{{ monthNames[currentMonth] }} {{ currentYear }}</h3>
            <button @click="nextMonth" class="calendar-nav-btn">&gt;</button>
          </div>
          
          <div class="calendar-weekdays">
            <div class="weekday" v-for="day in weekdays" :key="day">{{ day }}</div>
          </div>
          
          <div class="calendar-days">
            <!-- Dias anteriores ao mês atual (do mês anterior) -->
            <div 
              v-for="day in firstDayOfMonth" 
              :key="'prev-' + day" 
              class="calendar-day faded"
            >
              {{ getLastDaysOfPreviousMonth()[day - 1] }}
            </div>
            
            <!-- Dias do mês atual -->
            <div 
              v-for="day in daysInMonth" 
              :key="'curr-' + day" 
              :class="['calendar-day', 
                       isToday(day) ? 'today' : '',
                       hasEvent(day) ? 'has-event' : '']"
              @click="dayClicked(day)"
            >
              {{ day }}
              <div v-if="hasEvent(day)" class="event-indicator"></div>
            </div>
            
            <!-- Dias após o mês atual (do próximo mês) -->
            <div 
              v-for="day in nextDaysCount" 
              :key="'next-' + day" 
              class="calendar-day faded"
            >
              {{ day }}
            </div>
          </div>
        </div>
      </div>
      
      <!-- Painel inferior para futuras adições -->
      <div class="future-panel">
        <div class="future-content">
          <h3>Área reservada para futuras funcionalidades</h3>
          <p>Este espaço será utilizado para adicionar novas funcionalidades e informações relevantes.</p>
        </div>
      </div>
    </div>

    <!-- Modal para criar novo grupo - sem alterações -->
    <div v-if="showCreateGroupModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-container">
        <!-- Conteúdo do modal sem alterações -->
        <div class="modal-header">
          <h2>Criar Novo Grupo</h2>
          <button class="close-modal-btn" @click="closeModal">×</button>
        </div>
        
        <div class="modal-body">
          <form @submit.prevent="handleCreateGroup" class="create-group-form">
            <div class="form-group">
              <label for="name">Nome do Grupo:</label>
              <input 
                type="text" 
                id="name" 
                v-model="newGroup.name" 
                required
                placeholder="Digite o nome do grupo"
              >
            </div>
            
            <div class="button-container">
              <button type="submit" :disabled="createGroupLoading" class="submit-btn">
                <span v-if="createGroupLoading" class="form-loading-indicator"></span>
                {{ createGroupLoading ? 'Criando...' : 'Criar Grupo' }}
              </button>
            </div>
          </form>
          
          <div v-if="createGroupError" class="error-message">
            <div class="error-icon">!</div>
            <p>{{ createGroupError }}</p>
            <button class="close-btn" @click="createGroupError = null" aria-label="Fechar">×</button>
          </div>
          
          <div v-if="createGroupSuccess" class="success-message">
            <div class="success-icon">✓</div>
            <p>{{ createGroupSuccess }}</p>
            <div class="success-actions">
              <button @click="closeModal" class="action-btn view-btn">Voltar para Home</button>
              <button @click="resetCreateGroupForm" class="action-btn reset-btn">Criar outro grupo</button>
            </div>
          </div>
        </div>
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
      groups: [],
      groupsLoading: true,
      groupsError: null,
      searchQuery: '',
      isMobileDevice: false,
      
      // Novo Grupo Modal
      showCreateGroupModal: false,
      newGroup: {
        name: ''
      },
      createGroupLoading: false,
      createGroupError: null,
      createGroupSuccess: '',

      // Calendário
      weekdays: ['D', 'S', 'T', 'Q', 'Q', 'S', 'S'],
      monthNames: [
        'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
      ],
      currentMonth: new Date().getMonth(),
      currentYear: new Date().getFullYear(),
      today: new Date(),
      events: [], // Futuro: armazenar eventos aqui
    }
  },
  computed: {
    filteredGroups() {
      if (!this.searchQuery) {
        return this.groups;
      }
      
      const query = this.searchQuery.toLowerCase();
      return this.groups.filter(group => 
        group.name.toLowerCase().includes(query)
      );
    },
    // Cálculos para o calendário
    daysInMonth() {
      // Retorna o número de dias no mês atual
      return new Date(this.currentYear, this.currentMonth + 1, 0).getDate();
    },
    firstDayOfMonth() {
      // Obtém o dia da semana do primeiro dia do mês (0 = Domingo, 1 = Segunda, etc.)
      const firstDay = new Date(this.currentYear, this.currentMonth, 1).getDay();
      // Retorna um array com o número de dias necessários para preencher os espaços antes
      return Array.from({ length: firstDay }, (_, i) => i + 1);
    },
    nextDaysCount() {
      // Calcula quantos dias do próximo mês precisamos mostrar
      // Total de células em um grid 7x6 = 42
      const totalDays = 42;
      const usedDays = this.firstDayOfMonth.length + this.daysInMonth;
      return Array.from({ length: totalDays - usedDays }, (_, i) => i + 1);
    }
  },
  created() {
    this.checkDeviceType();
    this.loadUserInfo();
    this.fetchGroups();
    
    // Adicionar listener para verificar redimensionamento
    window.addEventListener('resize', this.checkDeviceType);
  },
  beforeUnmount() {
    // Remover listener ao destruir componente
    window.removeEventListener('resize', this.checkDeviceType);
  },
  methods: {
    // Métodos para calendário
    prevMonth() {
      if (this.currentMonth === 0) {
        this.currentMonth = 11;
        this.currentYear--;
      } else {
        this.currentMonth--;
      }
    },
    nextMonth() {
      if (this.currentMonth === 11) {
        this.currentMonth = 0;
        this.currentYear++;
      } else {
        this.currentMonth++;
      }
    },
    getLastDaysOfPreviousMonth() {
      // Obtém os últimos dias do mês anterior para exibir no calendário
      const lastDayPrevMonth = new Date(this.currentYear, this.currentMonth, 0).getDate();
      const daysNeeded = this.firstDayOfMonth.length;
      return Array.from({ length: daysNeeded }, (_, i) => lastDayPrevMonth - daysNeeded + i + 1);
    },
    isToday(day) {
      // Verifica se o dia é o dia atual
      const today = new Date();
      return day === today.getDate() && 
             this.currentMonth === today.getMonth() && 
             this.currentYear === today.getFullYear();
    },
    hasEvent(day) {
      // Futuro: verificar se existe evento para este dia
      // Por enquanto, vamos simular alguns eventos
      const randomDays = [];
      return randomDays.includes(day) && this.currentMonth === new Date().getMonth();
    },
    dayClicked(day) {
      // Futuro: abrir modal para adicionar/ver eventos
      console.log(`Dia clicado: ${day}/${this.currentMonth + 1}/${this.currentYear}`);
      // Se for admin, poderia mostrar um diálogo para adicionar evento
    },
    checkDeviceType() {
      this.isMobileDevice = window.innerWidth < 1024;
    },
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
    async fetchGroups() {
      try {
        const userStr = localStorage.getItem('user');
        if (!userStr) {
          this.$router.push('/login');
          return;
        }
        
        const user = JSON.parse(userStr);
        
        const response = await fetch('/api/groups', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'User-ID': user.id
          }
        });
        
        const data = await response.json();
        
        if (!response.ok) {
          this.groupsError = data.message || 'Erro ao carregar grupos';
          this.groupsLoading = false;
          return;
        }
        
        this.groups = data.groups;
        this.groupsLoading = false;
      } catch (error) {
        this.groupsError = 'Erro ao conectar ao servidor';
        this.groupsLoading = false;
        console.error('Error fetching groups:', error);
      }
    },
    goToGroupDetail(groupId) {
      this.$router.push(`/groups/${groupId}`);
    },
    manageGroupAccess(groupId) {
      this.$router.push(`/groups/manage/${groupId}`);
    },
    createGroup() {
      this.showCreateGroupModal = true;
    },
    manageAccounts() {
      this.$router.push('/users');
    },
    logout() {
      localStorage.removeItem('user');
      this.$router.push('/login');
    },
    
    // Métodos para o modal de criação de grupo
    closeModal() {
      if (!this.createGroupLoading) {
        this.showCreateGroupModal = false;
        
        // Se houver sucesso, recarrega os grupos ao fechar
        if (this.createGroupSuccess) {
          this.fetchGroups();
        }
        
        // Reseta o formulário e as mensagens
        this.resetCreateGroupForm();
        this.createGroupError = null;
        this.createGroupSuccess = '';
      }
    },
    resetCreateGroupForm() {
      this.newGroup = {
        name: ''
      };
      this.createGroupSuccess = '';
    },
    async handleCreateGroup() {
      this.createGroupLoading = true;
      this.createGroupError = null;
      
      try {
        const userStr = localStorage.getItem('user');
        if (!userStr) {
          this.$router.push('/login');
          return;
        }
        
        const user = JSON.parse(userStr);
        
        const response = await fetch('/api/groups', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'User-ID': user.id
          },
          body: JSON.stringify(this.newGroup)
        });
        
        const data = await response.json();
        
        if (!response.ok) {
          console.error('Erro no servidor:', data);
          this.createGroupError = data.message || 'Erro ao criar grupo';
          this.createGroupLoading = false;
          return;
        }
        
        this.createGroupSuccess = 'Grupo criado com sucesso!';
        this.createGroupLoading = false;
      } catch (error) {
        console.error('Erro ao conectar ao servidor:', error);
        this.createGroupError = 'Erro ao conectar ao servidor';
        this.createGroupLoading = false;
      }
    }
  }
}
</script>

<style scoped>
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

/* Layout principal - versão desktop ATUALIZADO */
.home-layout {
  position: fixed;
  top: 100px;
  left: 50px;
  right: 50px;
  bottom: 30px;
  display: grid;
  grid-template-columns: 1fr 1fr; /* Divide em duas colunas */
  grid-template-rows: 1fr; /* Uma única linha para o painel da direita */
  gap: 20px;
}

/* Painel de conteúdo (visualmente à direita) */
.content-panel {
  grid-column: 2 / 3; /* Posiciona na segunda coluna */
  grid-row: 1 / 3;   /* Ocupa as duas linhas do grid */
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  height: 100%;
}

/* Layout principal - o elemento que atua como container pai */
.home-layout {
  position: fixed;
  top: 100px;
  left: 50px;
  right: 50px;
  bottom: 30px;
  display: grid;
  grid-template-columns: 1fr 2fr; /* Proporção 1:2 entre esquerda e direita */
  grid-template-rows: 1fr 1fr; /* Duas linhas de igual altura */
  gap: 20px; /* Espaçamento uniforme entre todos os elementos */
}

/* Painel de conteúdo (visualmente à direita) */
.content-panel {
  grid-column: 2 / 3; /* Posiciona na segunda coluna */
  grid-row: 1 / 3;   /* Ocupa as duas linhas do grid */
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* Novos painéis à esquerda */
.calendar-panel {
  grid-column: 1 / 2; /* Posiciona na primeira coluna */
  grid-row: 1 / 2;   /* Ocupa a primeira linha */
  background: linear-gradient(135deg, #0D1B40 30%, #1E3A8A 70%);
  border-radius: 12px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 0; /* Remove margin e usa o gap do grid */
  height: auto; /* Altura automática baseada no grid */
}

.future-panel {
  grid-column: 1 / 2; /* Posiciona na primeira coluna */
  grid-row: 2 / 3;   /* Ocupa a segunda linha */
  background: #1E3A8A;
  border-radius: 12px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 0; /* Remove margin e usa o gap do grid */
  height: auto; /* Altura automática baseada no grid */
}

.future-content {
  color: white;
  text-align: center;
  padding: 20px;
}

.future-content h3 {
  margin-bottom: 15px;
  font-size: 1.2rem;
  font-weight: 600;
}

.future-content p {
  font-size: 0.9rem;
  opacity: 0.8;
}

/* ESTILOS ATUALIZADOS PARA O CALENDÁRIO */
.full-calendar-container {
  width: 100%;
  background-color: white;
  border-radius: 12px;
  padding: 16px;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.calendar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(20, 44, 77, 0.1);
}

.calendar-header h3 {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0;
  color: #142C4D;
}

/* Botões de navegação modernizados */
.calendar-nav-btn {
  background: none;
  border: none;
  color: #142C4D;
  font-size: 1.2rem;
  font-weight: 600;
  padding: 5px 10px;
  cursor: pointer;
  transition: all 0.2s;
  border-radius: 5px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.calendar-nav-btn:hover {
  color: #3b82f6;
  transform: scale(1.1);
  background-color: rgba(59, 130, 246, 0.1);
}

.calendar-weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 2px;
  margin-bottom: 10px;
}

.weekday {
  text-align: center;
  font-weight: 600;
  font-size: 0.85rem;
  padding: 5px 0;
  color: #142C4D;
}

.calendar-days {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  grid-template-rows: repeat(6, 1fr);
  gap: 3px;
  flex: 1;
}

.calendar-day {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  height: auto;
  min-height: 28px;
  border-radius: 8px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s;
  color: #333;
}

.calendar-day:hover {
  background-color: rgba(59, 130, 246, 0.1);
}

.calendar-day.today {
  background-color: #3b82f6;
  color: white;
  font-weight: bold;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.4);
}

.calendar-day.faded {
  color: #CBD5E1;
  cursor: default;
}

.calendar-day.faded:hover {
  background-color: transparent;
}

.calendar-day.has-event::after {
  content: '';
  position: absolute;
  bottom: 3px;
  width: 5px;
  height: 5px;
  background-color: #f59e0b;
  border-radius: 50%;
}

.event-indicator {
  position: absolute;
  bottom: 3px;
  width: 5px;
  height: 5px;
  background-color: #f59e0b;
  border-radius: 50%;
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

/* Caixa de Busca */
.search-container {
  margin-bottom: 1.5rem;
}

.search-box {
  position: relative;
  width: 100%;
}

.search-input {
  width: 100%;
  padding: 12px 40px 12px 15px;
  border: 2px solid #e1e1e1;
  border-radius: 8px;
  font-size: 1rem;
  color: #333;
  transition: all 0.3s ease;
  background-color: #f9f9f9;
}

.search-input:focus {
  border-color: #204578;
  box-shadow: 0 0 0 3px rgba(32, 69, 120, 0.15);
  outline: none;
  background-color: #fff;
}

.search-icon {
  position: absolute;
  right: 15px;
  top: 50%;
  transform: translateY(-50%);
  color: #666;
  font-size: 1.2rem;
}

/* Seção de lojas */
.stores-section {
  flex: 1;
  overflow-y: auto;
  margin-bottom: 1rem;
  max-height: calc(100% - 250px);
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
  flex: 1;
}

.store-name {
  font-weight: 600;
  font-size: 0.95rem;
  color: #142C4D;
}

.store-item-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

/* Novo estilo para o contêiner da seta */
.arrow-container {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  background-color: #e8f0fe;
  cursor: pointer;
  transition: all 0.2s ease;
}

.arrow-container:hover {
  background-color: #d0e1fd;
  transform: scale(1.1);
}

.store-item-arrow {
  font-size: 1.5rem;
  font-weight: bold;
  color: #204578;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* NOVOS ESTILOS: Indicador de carregamento */
.groups-loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  text-align: center;
  width: 100%;
  height: 150px;
  margin: 1rem 0;
  background-color: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #eaeaea;
}

.groups-loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(32, 69, 120, 0.1);
  border-top: 4px solid #204578;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes fade-in {
  0% { opacity: 0; }
  100% { opacity: 1; }
}

/* Estados de erro e vazio */
.error-message, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  text-align: center;
  width: 100%;
  margin: 1rem 0;
  background-color: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #eaeaea;
}

.error-message {
  background-color: #fee2e2;
  border-color: #fecaca;
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
  margin-bottom: 0;
  margin-top: auto;
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

/* Modal para criação de grupo */
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
  animation: fade-in 0.3s ease;
}

.modal-container {
  width: 90%;
  max-width: 600px;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.3);
  overflow: hidden;
  animation: slide-up 0.4s ease;
}

@keyframes slide-up {
  0% { transform: translateY(30px); opacity: 0; }
  100% { transform: translateY(0); opacity: 1; }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #eaeaea;
  background: linear-gradient(to right, #142C4D, #204578);
  color: white;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.4rem;
  font-weight: 600;
}

.close-modal-btn {
  background: none;
  border: none;
  color: white;
  font-size: 1.8rem;
  line-height: 1;
  cursor: pointer;
  transition: all 0.2s;
}

.close-modal-btn:hover {
  transform: scale(1.2);
  color: #f8f9fa;
}

.modal-body {
  padding: 1.5rem;
}

.create-group-form {
  margin-bottom: 1.5rem;
}

.form-group {
  margin-bottom: 1.2rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #333;
}

.form-group input {
  width: 100%;
  padding: 12px 15px;
  border: 2px solid #e1e1e1;
  border-radius: 8px;
  font-size: 1rem;
  color: #333;
  transition: all 0.3s ease;
}

.form-group input:focus {
  border-color: #204578;
  box-shadow: 0 0 0 3px rgba(32, 69, 120, 0.15);
  outline: none;
}

.button-container {
  display: flex;
  justify-content: flex-end;
}

.submit-btn {
  background: linear-gradient(to right, #142C4D, #204578);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.submit-btn:hover:not(:disabled) {
  background: linear-gradient(to right, #1a3760, #2a5b9e);
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(20, 44, 77, 0.3);
}

.submit-btn:disabled {
  background: linear-gradient(to right, #a3a3a3, #c0c0c0);
  cursor: not-allowed;
}

.form-loading-indicator {
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top: 3px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

/* Mensagens de sucesso e erro */
.success-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 1.5rem;
  background-color: #ecfdf5;
  border: 1px solid #a7f3d0;
  border-radius: 8px;
  margin-top: 1.5rem;
}

.success-icon {
  width: 40px;
  height: 40px;
  background-color: #10b981;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  margin-bottom: 0.8rem;
}

.success-message p {
  color: #047857;
  font-weight: 500;
  margin-bottom: 1rem;
}

.success-actions {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.action-btn {
  padding: 10px 16px;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.view-btn {
  background-color: #3b82f6;
  color: white;
  border: none;
}

.view-btn:hover {
  background-color: #2563eb;
}

.reset-btn {
  background-color: white;
  color: #333;
  border: 1px solid #d1d5db;
}

.reset-btn:hover {
  background-color: #f3f4f6;
}

.close-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  background: none;
  border: none;
  color: #b91c1c;
  font-size: 1.2rem;
  cursor: pointer;
}

.close-btn:hover {
  color: #991b1b;
}
</style>