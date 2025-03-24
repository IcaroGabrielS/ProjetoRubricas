<template>
  <div>
    <!-- Alerta para dispositivos móveis -->
    <div v-if="isMobileDevice" class="mobile-warning">
      <div class="warning-icon">⚠️</div>
      <h2>Acesso não recomendado</h2>
      <p>Este site não foi projetado para dispositivos móveis. Por favor, acesse através de um computador para uma melhor experiência.</p>
    </div>

    <!-- Layout principal - visível apenas em desktop -->
    <div v-else class="home-layout">
      <!-- Painel com o conteúdo principal (direita) -->
      <div class="content-panel">
        <div class="content-wrapper">
          <div class="home-header">
            <h1>Olá, {{ username }}!</h1>
            <p class="welcome-text">Você logou com sucesso.</p>
          </div>
          
          <div class="dashboard-summary">
            <div class="dashboard-item">
              <h3>Suas Empresas</h3>
              <p>Selecione uma empresa abaixo para acessar seus detalhes e arquivos.</p>
            </div>
          </div>
          
          <!-- Caixa de busca para empresas -->
          <div class="search-container">
            <div class="search-box">
              <input 
                type="text" 
                v-model="searchQuery" 
                placeholder="Pesquisar empresas..."
                class="search-input"
              >
              <span class="search-icon">
                <svg class="search-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <circle cx="11" cy="11" r="8"></circle>
                  <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                </svg>
              </span>
            </div>
          </div>
          
          <!-- Lista de empresas -->
          <div class="stores-section">
            <div v-if="companiesLoading" class="groups-loading-container">
              <div class="groups-loading-spinner"></div>
              <p>Carregando empresas...</p>
            </div>
            
            <div v-else-if="companiesError" class="error-message">
              <div class="error-icon">!</div>
              <p>{{ companiesError }}</p>
            </div>
            
            <div v-else-if="filteredCompanies.length === 0 && companies.length === 0" class="empty-state">
              <p>Você não tem acesso a empresas no momento.</p>
            </div>
            
            <div v-else-if="filteredCompanies.length === 0" class="empty-state">
              <p>Nenhuma empresa encontrada.</p>
            </div>
            
            <div v-else class="stores-list">
              <div 
                v-for="company in filteredCompanies" 
                :key="company.id" 
                class="store-item"
              >
                <div class="store-item-details">
                  <span class="store-name">{{ company.name }}</span>
                  <span class="company-cnpj" v-if="company.cnpj">CNPJ: {{ formatCNPJ(company.cnpj) }}</span>
                </div>
                <div class="store-item-actions">
                  <div class="arrow-container" @click="goToCompanyDetail(company.id)" title="Ver detalhes da empresa">
                    <span class="store-item-arrow">›</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Painel superior com o calendário (esquerda-superior) -->
      <div class="calendar-panel">
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
            <!-- Dias do mês anterior -->
            <div 
              v-for="(day, index) in getLastDaysOfPreviousMonth()" 
              :key="`prev-${index}`" 
              class="calendar-day faded"
            >
              {{ day }}
            </div>
            
            <!-- Dias do mês atual -->
            <div 
              v-for="day in daysInMonth" 
              :key="`curr-${day}`" 
              :class="['calendar-day', 
                       isToday(day) ? 'today' : '',
                       hasEvent(day) ? 'has-event' : '']"
              @click="dayClicked(day)"
            >
              {{ day }}
              <div v-if="hasEvent(day)" class="event-indicator"></div>
            </div>
            
            <!-- Dias do próximo mês -->
            <div 
              v-for="day in nextDaysCount" 
              :key="`next-${day}`" 
              class="calendar-day faded"
            >
              {{ day }}
            </div>
          </div>
        </div>
      </div>
      
      <!-- Painel inferior para eventos (esquerda-inferior) -->
      <div class="events-panel">
        <div class="events-content">
          <h3>Próximos Eventos</h3>
          <div v-if="eventsLoading" class="events-loading">
            <div class="events-loading-spinner"></div>
            <p>Carregando eventos...</p>
          </div>
          <div v-else-if="eventsError" class="error-message">
            <div class="error-icon">!</div>
            <p>{{ eventsError }}</p>
          </div>
          <div v-else-if="events.length === 0" class="empty-events">
            <p>Nenhum evento agendado para o período.</p>
          </div>
          <ul v-else class="events-list">
            <li 
              v-for="(event, index) in events" 
              :key="index" 
              class="event-item"
              :data-type="event.type"
            >
              {{ formatEventDate(event.date) }}: {{ event.title }}
            </li>
          </ul>
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
      // Usuário e empresas
      username: 'Usuário',
      isAdmin: false,
      companies: [],
      companiesLoading: true,
      companiesError: null,
      searchQuery: '',
      
      // Responsividade
      isMobileDevice: false,
      
      // Calendário
      weekdays: ['D', 'S', 'T', 'Q', 'Q', 'S', 'S'],
      monthNames: [
        'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
      ],
      currentMonth: new Date().getMonth(),
      currentYear: new Date().getFullYear(),
      
      // Eventos
      events: [],
      eventsLoading: false,
      eventsError: null,
      holidaysCache: {}, // Cache para armazenar feriados por ano
    }
  },
  computed: {
    filteredCompanies() {
      if (!this.searchQuery) {
        return this.companies;
      }
      
      const query = this.searchQuery.toLowerCase();
      return this.companies.filter(company => 
        company.name.toLowerCase().includes(query) || 
        (company.cnpj && company.cnpj.includes(query))
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
      const totalCells = 42; // Grid 7x6
      const usedCells = this.firstDayOfMonth.length + this.daysInMonth;
      return Array.from({ length: totalCells - usedCells }, (_, i) => i + 1);
    }
  },
  created() {
    this.checkDeviceType();
    this.loadUserInfo();
    this.fetchCompanies();
    this.fetchHolidaysAndEvents(); // Buscar feriados nacionais
    
    // Adicionar listener para verificar redimensionamento
    window.addEventListener('resize', this.checkDeviceType);
  },
  beforeUnmount() {
    // Remover listener ao destruir componente
    window.removeEventListener('resize', this.checkDeviceType);
  },
  methods: {
    // Métodos de verificação de dispositivo e carregamento de dados
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
    
    async fetchCompanies() {
      try {
        const userStr = localStorage.getItem('user');
        if (!userStr) {
          this.$router.push('/login');
          return;
        }
        
        const user = JSON.parse(userStr);
        
        const response = await fetch('/api/companies', {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${user.token}`,
            'Content-Type': 'application/json'
          }
        });
        
        const data = await response.json();
        
        if (!response.ok) {
          this.companiesError = data.message || 'Erro ao carregar empresas';
          this.companiesLoading = false;
          return;
        }
        
        this.companies = data.companies;
        this.companiesLoading = false;
      } catch (error) {
        this.companiesError = 'Erro ao conectar ao servidor';
        this.companiesLoading = false;
        console.error('Error fetching companies:', error);
      }
    },
    
    formatCNPJ(cnpj) {
      if (!cnpj) return '';
      
      // Remove qualquer caractere não numérico
      const numbers = cnpj.replace(/\D/g, '');
      
      // Aplica a formatação XX.XXX.XXX/XXXX-XX
      if (numbers.length === 14) {
        return numbers.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/g, '$1.$2.$3/$4-$5');
      }
      
      return cnpj; // Retorna o valor original se não conseguir formatar
    },
    
    // Navegação
    goToCompanyDetail(companyId) {
      this.$router.push(`/companies/${companyId}`);
    },
    
    // Métodos para o calendário
    prevMonth() {
      if (this.currentMonth === 0) {
        this.currentMonth = 11;
        this.currentYear--;
        // Carrega feriados do ano anterior se necessário
        this.fetchNationalHolidays(this.currentYear).then(() => this.combineAllEvents());
      } else {
        this.currentMonth--;
      }
      this.updateEventsForCurrentMonth();
    },
    
    nextMonth() {
      if (this.currentMonth === 11) {
        this.currentMonth = 0;
        this.currentYear++;
        // Carrega feriados do próximo ano se necessário
        this.fetchNationalHolidays(this.currentYear).then(() => this.combineAllEvents());
      } else {
        this.currentMonth++;
      }
      this.updateEventsForCurrentMonth();
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
      // Verifica se existe evento para este dia no mês atual
      return this.events.some(event => {
        const eventDate = new Date(event.date);
        return eventDate.getDate() === day && 
               eventDate.getMonth() === this.currentMonth &&
               eventDate.getFullYear() === this.currentYear;
      });
    },
    
    dayClicked(day) {
      // Mostra os eventos deste dia específico
      const eventsOnThisDay = this.events.filter(event => {
        const eventDate = new Date(event.date);
        return eventDate.getDate() === day && 
               eventDate.getMonth() === this.currentMonth &&
               eventDate.getFullYear() === this.currentYear;
      });
      
      if (eventsOnThisDay.length > 0) {
        console.log('Eventos neste dia:', eventsOnThisDay);
        // Aqui você pode implementar um modal ou uma exibição detalhada
        // dos eventos deste dia
      } else if (this.isAdmin) {
        // Se for admin, pode mostrar opção para adicionar evento
        console.log(`Nenhum evento no dia ${day}/${this.currentMonth + 1}/${this.currentYear}`);
      }
    },
    
    // Formata a data do evento para exibição
    formatEventDate(dateStr) {
      const date = new Date(dateStr);
      return `${date.getDate().toString().padStart(2, '0')}/${(date.getMonth() + 1).toString().padStart(2, '0')}`;
    },
    
    // Busca feriados da API e outros eventos
    async fetchHolidaysAndEvents() {
      this.eventsLoading = true;
      
      try {
        // Buscar feriados nacionais do Brasil para o ano corrente
        await this.fetchNationalHolidays(this.currentYear);
        
        // Se estamos perto do fim do ano, já carrega os feriados do próximo ano
        if (this.currentMonth >= 10) {
          await this.fetchNationalHolidays(this.currentYear + 1);
        }
        
        // Aqui você poderia adicionar outros eventos do sistema, se necessário
        this.combineAllEvents();
        
      } catch (error) {
        console.error('Erro ao carregar eventos:', error);
        this.eventsError = 'Erro ao carregar eventos. Por favor, tente novamente mais tarde.';
      } finally {
        this.eventsLoading = false;
      }
    },
    
    // Busca feriados nacionais de uma API pública
    async fetchNationalHolidays(year) {
      // Verifica se já temos os feriados desse ano em cache
      if (this.holidaysCache[year]) {
        return;
      }
      
      try {
        // Usando a API Nager.Date para buscar feriados do Brasil
        const response = await fetch(`https://date.nager.at/api/v3/PublicHolidays/${year}/BR`);
        
        if (!response.ok) {
          throw new Error(`Erro ao buscar feriados: ${response.status}`);
        }
        
        const holidays = await response.json();
        
        // Transformando os dados da API para o formato esperado pelo componente
        const formattedHolidays = holidays.map(holiday => ({
          date: holiday.date, // Formato ISO: YYYY-MM-DD
          title: holiday.localName,
          type: 'holiday',
          fixed: true
        }));
        
        // Armazena em cache
        this.holidaysCache[year] = formattedHolidays;
        
      } catch (error) {
        console.error(`Erro ao buscar feriados de ${year}:`, error);
        // Criar um array vazio em caso de erro para evitar novas requisições
        this.holidaysCache[year] = [];
      }
    },
    
    // Combina todos os eventos e os ordena por data
    combineAllEvents() {
      let allEvents = [];
      
      // Adiciona todos os feriados do cache
      Object.values(this.holidaysCache).forEach(holidays => {
        allEvents = [...allEvents, ...holidays];
      });
      
      // Adiciona outros eventos do sistema aqui, se houver
      
      // Filtra eventos apenas dos próximos 90 dias
      const today = new Date();
      const futureDate = new Date();
      futureDate.setDate(today.getDate() + 90);
      
      allEvents = allEvents.filter(event => {
        const eventDate = new Date(event.date);
        return eventDate >= today && eventDate <= futureDate;
      });
      
      // Ordena por data
      allEvents.sort((a, b) => new Date(a.date) - new Date(b.date));
      
      this.events = allEvents;
    },
    
    updateEventsForCurrentMonth() {
      this.combineAllEvents();
      if (this.currentMonth === 11) {
        this.fetchNationalHolidays(this.currentYear + 1);
      } 
      else if (this.currentMonth === 0) {
        this.fetchNationalHolidays(this.currentYear - 1);
      }
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

.home-layout {
  position: fixed;
  top: 75px;
  bottom: 20px;
  left: 20px;
  right: 20px;
  display: grid;
  grid-template-columns: 1fr 2fr;
  grid-template-rows: 1fr 1fr;
  gap: 20px;
}

.content-panel {
  grid-column: 2 / 3;
  grid-row: 1 / 3;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.calendar-panel {
  grid-column: 1 / 2;
  grid-row: 1 / 2;
  background: linear-gradient(135deg, #0D1B40 30%, #1E3A8A 70%);
  border-radius: 12px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  height: auto;
}

.events-panel {
  grid-column: 1 / 2;
  grid-row: 2 / 3;
  background: #1E3A8A;
  border-radius: 12px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  height: auto;
}

.events-content {
  color: white;
  padding: 20px;
  width: 100%;
  height: 100%;
  overflow-y: auto;
}

.events-content h3 {
  margin-bottom: 15px;
  font-size: 1.2rem;
  font-weight: 500;
  text-align: center;
}

.empty-events {
  text-align: center;
  font-style: italic;
  opacity: 0.7;
  padding: 20px 0;
}

.events-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.event-item {
  background-color: rgba(255, 255, 255, 0.1);
  padding: 10px 15px;
  margin-bottom: 8px;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.event-item:hover {
  background-color: rgba(255, 255, 255, 0.2);
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
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.welcome-text {
  color: #667;
  font-size: 1.1rem;
}

/* Elementos do dashboard */
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
}

.store-item-details {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  flex: 1;
}

.store-name {
  font-weight: 500;
  font-size: 0.95rem;
  color: #142C4D;
}

.company-cnpj {
  font-size: 0.8rem;
  color: #6c757d;
}

.store-item-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

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
}

.store-item-arrow {
  font-size: 1.5rem;
  font-weight: bold;
  color: #204578;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Indicador de carregamento */
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

/* Estilos para o calendário */
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
  font-weight: 500;
  margin: 0;
  color: #142C4D;
}

.calendar-nav-btn {
  background: none;
  border: none;
  color: #142C4D;
  font-size: 1.2rem;
  font-weight: 500;
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
  font-weight: 500;
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

.calendar-day.faded {
  color: #CBD5E1;
  cursor: default;
}

.calendar-day.faded:hover {
  background-color: transparent;
}

.calendar-day.today {
  background-color: #564fcc;
  color: white;
  font-weight: bold;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.4);
}

.calendar-day.has-event {
  font-weight: 500;
}

.event-indicator {
  position: absolute;
  bottom: 2px;
  width: 5px;
  height: 5px;
  background-color: #3b82f6;
  border-radius: 50%;
}

.events-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px 0;
}

.events-loading-spinner {
  width: 30px;
  height: 30px;
  border: 3px solid rgba(255, 255, 255, 0.2);
  border-top: 3px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 10px;
}
</style>