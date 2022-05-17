from flask import Blueprint, jsonify
from api import cursor
# from flask_api.schema import user_schema

main = Blueprint("main", __name__)

@main.route("/")
def home():
    cursor.execute(""" SELECT * FROM users """)
    users = cursor.fetchall()
    return jsonify(users)