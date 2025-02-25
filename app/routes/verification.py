from flask import Blueprint
from flask_jwt_extended import jwt_required
from ..controllers.verification import verify_identity, simple_check

verification_bp = Blueprint('verification', __name__)

@verification_bp.route('/verify-identity', methods=['POST'])
@jwt_required()
def verify_identity_route():
    return verify_identity()

@verification_bp.route('/simple-check', methods=['POST'])
@jwt_required()
def simple_check_route():
    return simple_check()