from config import app, db
from flask import current_app
import base64
import pytest 

@pytest.fixture
def client() :
    with app.app_context():
        db.drop_all()
        db.create_all()
        return app.test_client()

@pytest.mark.parametrize("username, email, password, expected", [
    ("sanjeev", "bhusalsanjeev23@gmail.com", "password", 201),
    ("sanjeev", "bhusalsanjeev23", "password", 400),
    ("sanjeev", "bhusalsanjeev23@gmail.com", "password", 409), 
])
def test_register_user(client, username, email, password, expected):
    r = client.post("/register", json={"username": username, "email" : email, "password" : password} )
    assert r.status_code == expected
    
# @pytest.mark.parametrize("email, password, expected", [
#     ("bhusalsanjeev23@gmail.com", "password", 200),
#     ("bhusasanjeev", "password", 400),
#     ("bhusalsanjeev23@gmail.com", "passwor", 401),
#     ("bhusalsanjeev24@gmail.com", "password", 404)
# ])
# def test_login_user(email, password, expected):
#     r = client.post("/login",  headers={
#                 'Authorization': 'Basic ' + base64.b64encode(bytes(email + ":" + password, 'ascii')).decode('ascii')
#             })
#     assert r.status_code == expected
    

# def test_get_users_list() :
#     r= client.get("/users")
#     assert r.status_code == 200
    
# @pytest.mark.parametrize("id, expected", [
#     (1, 200),
#     (2, 404)
# ])
# def test_get_user_by_id(id, expected) :
#     r  = client.get(f"/users/{id}")
#     assert r.status_code == expected

#jwt token, user_id, updatingvalues

# @pytest.fixture
# def get_normal_user_jwt() :
#     # r = client.post("/register", json={"username" : "Sanjeev", "email" : "bhusalsanjeev23@gmail.com", "password" : "password"})
#     r = client.post("/login",  headers={
#                 'Authorization': 'Basic ' + base64.b64encode(bytes("bhusalsanjeev23@gmail.com" + ":" + "password", 'ascii')).decode('ascii') })
#     return r.get_json()["token"]

# def get_admin_jwt() :
#     # r = client.post("/register", json={"username" : "Sanjeev", "email" : "bhusalsanjeev23@gmail.com", "password" : "password"})
#     r = client.post("/login",  headers={
#                 'Authorization': 'Basic ' + base64.b64encode(bytes("bhusalsanjeev233@gmail.com" + ":" + "password", 'ascii')).decode('ascii') })
#     return r.get_json()["token"]


# @pytest.mark.parametrize("user_id, username, expected", [
#     (11, "Sanjeev1", 200 ), 
#     (12, "Sanjeev1", 403),
# ])
# def test_update_user(get_normal_user_jwt, user_id, username, expected) :
#     r = client.put(f"/users/{user_id}", headers = {
#         "access_token" : get_normal_user_jwt
#     }, json = {"username" : username})
#     assert r.status_code== expected
    
# @pytest.mark.parametrize("user_id, username, expected", [
#     (11, "Sanjeev1", 200 ), 
#     (12, "Sanjeev1", 403),
# ])
# def test_update_user_by_admin(get_admin_jwt, user_id, username, expected) :
#     r = client.put(f"/users/{user_id}", headers = {
#         "access_token" : get_admin_jwt
#     }, json = {"username" : username})
#     assert r.status_code== expected
    
