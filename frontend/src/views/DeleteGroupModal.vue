<template>
    <div v-if="show" class="modal-overlay">
      <div class="modal-container">
        <div class="modal-header">
          <h3>Confirmação de Exclusão</h3>
        </div>
        <div class="modal-body">
          <div class="warning-icon modal-icon">⚠️</div>
          <p>Você está prestes a excluir o grupo <strong>{{ groupName }}</strong> e todas as suas empresas.</p>
          <p class="warning-text">Esta ação não pode ser desfeita!</p>
          
          <div class="confirmation-input">
            <label for="confirmText">Digite "EXCLUIR" para confirmar:</label>
            <input 
              type="text" 
              id="confirmText" 
              v-model="confirmDeleteText" 
              placeholder="EXCLUIR" 
            />
          </div>
        </div>
        <div class="modal-footer">
          <button class="cancel-btn" @click="cancelDelete">Cancelar</button>
          <button 
            class="delete-btn"
            :disabled="confirmDeleteText !== 'EXCLUIR' || deletingGroup"
            @click="deleteGroup"
          >
            {{ deletingGroup ? 'Excluindo...' : 'Confirmar Exclusão' }}
          </button>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: 'DeleteGroupModal',
    props: {
      show: {
        type: Boolean,
        required: true
      },
      groupName: {
        type: String,
        required: true
      },
      confirmDeleteText: {
        type: String,
        required: true
      },
      deletingGroup: {
        type: Boolean,
        required: true
      }
    },
    methods: {
      cancelDelete() {
        this.$emit('cancel-delete');
      },
      deleteGroup() {
        this.$emit('confirm-delete');
      }
    }
  };
  </script>
  
  <style scoped>
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
    animation: fade-in 0.3s ease;
  }
  
  .modal-container {
    width: 90%;
    max-width: 500px;
    background-color: white;
    border-radius: 10px;
    overflow: hidden;
    box-shadow: 0 15px 30px rgba(0, 0, 0, 0.3);
    animation: slide-in 0.4s ease;
  }
  
  @keyframes slide-in {
    0% { opacity: 0; transform: translateY(-30px); }
    100% { opacity: 1; transform: translateY(0); }
  }
  
  .modal-header {
    background-color: #f8f8f8;
    padding: 1.2rem 1.5rem;
    border-bottom: 1px solid #eaeaea;
  }
  
  .modal-header h3 {
    margin: 0;
    color: #333;
    font-size: 1.3rem;
  }
  
  .modal-body {
    padding: 1.5rem;
    text-align: center;
  }
  
  .modal-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
  }
  
  .modal-body .warning-text {
    color: #b91c1c;
    margin: 1rem 0;
  }
  
  .confirmation-input label {
    font-weight: bold;
  }
  
  .confirmation-input input {
    width: calc(100% - 3rem);
    padding: 0.5rem;
    margin-top: 1rem;
  }
  
  .modal-footer {
    padding: 1rem 1.5rem;
    background-color: #f9f9f9;
    display: flex;
    justify-content: flex-end;
    gap: 1rem;
  }
  
  .cancel-btn {
    padding: 0.7rem 1.5rem;
    background-color: #f0f0f0;
    border: 1px solid #ddd;
    border-radius: 8px;
    color: #333;
    font-size: 1rem;
    cursor: pointer;
    transition: all 0.2s ease;
  }
  
  .cancel-btn:hover {
    background-color: #e0e0e0;
  }
  
  .delete-btn {
    padding: 0.7rem 1.5rem;
    background: linear-gradient(to right, #ff7675, #fab1a0);
    border: none;
    border-radius: 8px;
    color: white;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
  }
  
  .delete-btn:hover:not(:disabled) {
    background: linear-gradient(to right, #7f1d1d, #991b1b);
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(185, 28, 28, 0.3);
  }
  
  .delete-btn:disabled {
    background: #c0c0c0;
    cursor: not-allowed;
  }
  </style>