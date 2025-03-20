import uuid

def is_valid_uuid(val):
    """Valida se uma string é um UUID válido"""
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False