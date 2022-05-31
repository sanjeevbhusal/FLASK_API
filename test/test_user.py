from config import client, random_email
import base64


def test_register_user():
    r = client.post("/register", json={"username": "Sanjeev Bhusal", "email" : random_email, "password" : "password"} )
    assert r.status_code == 201
        
def test_register_user_failure_1():
    r = client.post("/register", json={"username": "Sanjeev Bhusal", "email" : random_email, "password" : "password"} )
    assert r.status_code == 409
    
def test_register_user_failure_2():
    r = client.post("/register", json={"username": "Sanjeev Bhusal", "emai" : random_email, "password" : "password"} )
    assert r.status_code == 400
    
def test_login_user():
    r = client.post("/login",  headers={
                'Authorization': 'Basic ' + base64.b64encode(bytes(random_email + ":" + "password", 'ascii')).decode('ascii')
            })
    assert r.status_code == 200
    

def test_login_user_failure_1():
    r = client.post("/login", headers={
                'Authorization': 'Basic ' + base64.b64encode(bytes("thisemaildoesnotexist@gmail.com" + ":" + "password", 'ascii')).decode('ascii')
            })
    assert r.status_code == 404
    assert r.json.get("message") == "Couldn't find your Moru Account"
        
def test_login_user_failure_2():
    r = client.post("/login", headers={
                'Authorization': 'Basic ' + base64.b64encode(bytes(random_email + ":" + "passwordd", 'ascii')).decode('ascii')
            })
    assert r.status_code == 401
    assert r.json.get("message") == "Please Enter Correct Password"
    



    