from flask import request, jsonify
from models import User
from functools import wraps

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = request.headers.get('User-ID')
        if not user_id:
            return jsonify({"message": "Authentication required"}), 401
        
        user = User.query.get(user_id)
        if not user or not user.is_admin:
            return jsonify({"message": "Admin access required"}), 403
        
        return f(*args, **kwargs)
    return decorated_function

def user_has_group_access(user_id, group_id):
    from models import GroupPermission
    user = User.query.get(user_id)
    
    if user and user.is_admin:
        return True
    
    permission = GroupPermission.query.filter_by(user_id=user_id, group_id=group_id).first()
    return permission is not None