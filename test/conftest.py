import pytest
from config import app, db


@pytest.fixture(scope="module")
def client() :
    with app.app_context():
        db.drop_all()
        db.create_all()
        return app.test_client()
    
    
# import base64
# import itsdangerous

# @pytest.fixture()
# def generate_token():
#     r = client.post("/login",  headers={
#                 'Authorization': 'Basic ' + base64.b64encode(bytes("bhusalsanjeev2333@gmail.com" + ":" + "password", 'ascii')).decode('ascii')
#             })
#     return r.json.get("token")
