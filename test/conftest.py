import pytest
from config import client
import base64
import itsdangerous

@pytest.fixture()
def generate_token():
    r = client.post("/login",  headers={
                'Authorization': 'Basic ' + base64.b64encode(bytes("bhusalsanjeev2333@gmail.com" + ":" + "password", 'ascii')).decode('ascii')
            })
    return r.json.get("token")
