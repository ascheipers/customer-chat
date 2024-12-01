from flask import (
    Blueprint, request, jsonify
)
from flask_jwt_extended import create_access_token

from customer_chat.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route("/login", methods=["POST"])
def login():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    if not email or not password:
        return jsonify({"msg": "Bad username or password"}), 401

    db = get_db()
    agent = db.execute(
        'SELECT * FROM agent WHERE email = (?)', (email,)
    ).fetchone()

    access_token = create_access_token(identity=email)
    return jsonify(access_token=access_token)
