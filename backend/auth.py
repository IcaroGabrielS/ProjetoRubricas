import bcrypt
from database import get_user, add_user

def authenticate_user(username, password):
    user = get_user(username)
    if not user:
        return False

    user_id, db_username, hashed_password = user
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def register_user(username, password):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    add_user(username, hashed_password)
