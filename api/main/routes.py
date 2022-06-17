from flask import Blueprint
from flask import request

main = Blueprint("main", __name__)

@main.route("/")
def home():
    import pdb;pdb.set_trace()
    return {"message" : "Welcome to the Home Page"}