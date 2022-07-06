from flask_restful import Resource
from marshmallow import ValidationError
from requests.exceptions import HTTPError
from flask import Response
class Main(Resource) :
    def get(self) :
       return {"message" : "Welcome"}
    