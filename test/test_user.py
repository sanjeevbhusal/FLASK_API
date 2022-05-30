from config import client, random_email
import base64

        
        
def test_homepage():
    r = client.get("/")
    assert r.json.get("message") == "Welcome to the Home Page"
    assert r.status_code == 200

def test_register_user():
    print(random_email)
    r = client.post("/register", json={"username": "Sanjeev Bhusal", "email" : random_email, "password" : "password"} )
    assert r.json.get("message") == "You are registered Succesfully"
    assert r.status_code == 201
        
def test_register_user_failure_1():
    r = client.post("/register", json={"username": "Sanjeev Bhusal", "email" : random_email, "password" : "password"} )
    assert r.status_code == 409
    assert r.json.get("message") == "The Email is already Registered"
    

def test_register_user_failure_2():
    r = client.post("/register", json={"username": "Sanjeev Bhusal", "emai" : random_email, "password" : "password"} )
    assert r.status_code == 400
    assert r.json.get("message").get("emai")[0] == "Unknown field."
    assert r.json.get("message").get("email")[0] == "Missing data for required field."
    
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
    



    