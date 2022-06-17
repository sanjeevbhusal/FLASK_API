from flask import Blueprint
from flask import request

main = Blueprint("main", __name__)

@main.route("/")
def home():
    return {"message" : "Welcome to the Home Page"}