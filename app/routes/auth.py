from flask import Blueprint, request
from ..controllers.auth import register, login

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register_route():
    return register(request.json)

@auth_bp.route('/login', methods=['POST'])
def login_route():
    return login(request.json)