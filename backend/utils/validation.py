import uuid
import re

def is_valid_uuid(value):
    """
    Valida se uma string é um UUID válido.
    
    Args:
        value: String para validar
        
    Returns:
        Boolean indicando se é um UUID válido
    """
    if not value or not isinstance(value, str):
        return False
    
    # Verificar se está no padrão de UUID
    uuid_pattern = re.compile(
        r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', 
        re.IGNORECASE
    )
    
    if not uuid_pattern.match(value):
        return False
    
    # Verificar se é um UUID válido
    try:
        uuid_obj = uuid.UUID(value)
        return str(uuid_obj) == value
    except (ValueError, AttributeError, TypeError):
        return False