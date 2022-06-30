import pytest 
from utils import get_jwt


@pytest.mark.parametrize("username, email, password, is_admin, expected", [
    ("test", "test@gmail.com", "password", False, 201),
    ("testadmin", "test_admin@gmail.com", "admin_password", True, 201),
    (None, "test@gmail.com", "password", False, 400),
    ("test", "test@gmail.com", "password", False, 409)
])
def test_register_user(client, username, email, password, is_admin, expected) :
    data= {"username" : username, "email" : email,  "password": password, "is_admin" : is_admin}
    r = client.post("/register", json = data)
    assert r.status_code == expected
    
@pytest.mark.parametrize("email, password, expected", [
    ("test@gmail.com", "password", 200),
    ("test_admin@gmail.com", "admin_password", 200),
    (None, "passwor", 400),
    ("test@gmail.com", "passwor", 401),
    ("admin@gmail.com", "admin_password", 404),
])
def test_login_user(client, email, password, expected) :
    data = {"email" : email, "password" : password, }
    r = client.post("/login", json = data)
    assert r.status_code == expected
    
def test_get_users_list(client) :
    r= client.get("/users")
    assert r.status_code == 200
    
@pytest.mark.parametrize("user_id, expected", [
    (1, 200), (3, 404)
])    
def test_get_user_by_id(client, user_id, expected) :
    r = client.get(f"/users/{user_id}")
    assert r.status_code == expected
        
@pytest.mark.parametrize("logged_in_user_id, user_id_to_be_updated, username, expected", [
    (1, 1, "sanjeev", 200),
    (1, 2, "sanjeev", 403),
    (2, 2, "sanjeev", 200),
    (2, 1, "sanjeev", 200),
    (4, 1, "sanjeev", 404),
])   
def test_update_user(client, logged_in_user_id, user_id_to_be_updated, username, expected) :
    data = {"username" : username}
    jwt = get_jwt(logged_in_user_id)
    r = client.put(f"/users/{ user_id_to_be_updated}", headers = {
        "access_token" :  jwt 
    }, json = data )
    assert r.status_code == expected   
    
@pytest.mark.parametrize("logged_in_user_id, user_id_to_be_deleted, expected", [
    (1, 2,  403),
    (1, 1,  200),
    (2, 3,  404),
    (2, 2,  200),
    (2, 2, 404)
])      
def test_delete_user(client, logged_in_user_id, user_id_to_be_deleted, expected) :
    jwt = get_jwt(logged_in_user_id) 
    r = client.delete(f"/users/{user_id_to_be_deleted}", headers={
        "access_token" : jwt
    })
    assert r.status_code == expected
    
    


