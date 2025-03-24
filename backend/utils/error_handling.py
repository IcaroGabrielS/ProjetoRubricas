from flask import jsonify
import traceback
import logging

logger = logging.getLogger(__name__)

def handle_error(e, status_code=500, client_message=None):
    """
    Função helper para tratar erros de forma consistente
    
    Args:
        e: Exception ocorrida
        status_code: Código HTTP a ser retornado
        client_message: Mensagem a ser mostrada ao cliente (opcional)
    
    Returns:
        Resposta JSON com mensagem de erro e status code apropriado
    """
    # Logar o erro completo para debug server-side
    error_details = traceback.format_exc()
    logger.error(f"Erro: {str(e)}\n{error_details}")
    
    # Retornar mensagem customizada ou genérica com base no tipo de erro
    if client_message:
        message = client_message
    elif status_code == 404:
        message = "Recurso não encontrado"
    elif status_code == 400:
        message = str(e) if str(e) else "Requisição inválida"
    elif status_code == 403:
        message = "Acesso não autorizado"
    elif status_code == 401:
        message = "Autenticação necessária"
    else:
        message = "Erro interno do servidor"
    
    return jsonify({"message": message, "error": True}), status_code