import pytest
from utils import get_jwt

@pytest.mark.parametrize("username, email, password, is_admin, expected", [
    ("test", "test@gmail.com", "password", False, 201),
    ("testadmin", "test_admin@gmail.com", "admin_password", True, 201),
])
def test_register_user(client, username, email, password, is_admin, expected) :
    data= {"username" : username, "email" : email,  "password": password, "is_admin" : is_admin}
    r = client.post("/register", json = data)
    assert r.status_code == expected

@pytest.mark.parametrize("user_id, title, content, image, category, expected", [
    (1, "FIrst Post", "Second Post Content", "image.xyz", "LatestOffer", 201 ),
    (2, "Second Post", "Second Post Content", "dog.xyz", "NewEvent", 201 ),
    (3, "First Post", "Third Post Content", "image.png", "LatestOffer", 404),
    (1, "Third Post", None, "image.png", "LatestOffer", 400),
    (1, "Third Post", "Fourth Post Content", "image.png", "LatestOffe", 400)
])
def test_create_post(client, user_id, title, content, image, category, expected):
    data = {"title" : title, "content" : content, "image" : image, "category" : category}
    jwt = get_jwt(user_id)
    r = client.post("/posts/new", data=data, headers={
        "access_token" : jwt
    })
    assert r.status_code == expected
    
    
def test_get_all_posts(client) :
    r = client.get("/posts")
    assert r.status_code == 200
    
@pytest.mark.parametrize("post_id, expected", [
    (1, 200), (3, 404)
])
def test_get_single_post(client, post_id, expected) :
    r = client.get(f"/posts/{post_id}")
    assert r.status_code == expected
    
@pytest.mark.parametrize("user_id, post_id, title, content, category, expected", [
    (3, 1, "new title", "new content", "NewEvent", 404),
    (1, 3, "new title", "new content", "NewEvent", 404 ),
    (1, 1, "new title", None, "NewEvent", 400 ),
    (1, 2, "new title", "new content", "NewEvent", 403 ),
    (1, 1, "new title", "new content", "NewEvent", 200),
    (2, 1, "new title", "new content", "NewEvent", 200),
])
def test_update_post(client, user_id, post_id, title, content, category, expected) :
    data = {"title" : title, "content" : content, "category" : category}
    jwt = get_jwt(user_id)
    r = client.put(f"/posts/{post_id}", headers= {
        "access_token" : jwt
    }, json = data)
    assert r.status_code == expected
    
    
@pytest.mark.parametrize("user_id, post_id, expected", [
    (3, 1,  404),
    (1, 3,  404 ),
    (1, 2,  403 ),
    (1, 1,  200),
    (2, 2, 200)
])
def test_delete_post(client, user_id, post_id, expected) :
    jwt = get_jwt(user_id)
    r = client.delete(f"/posts/{post_id}", headers= {
        "access_token" : jwt
    })
    assert r.status_code == expected
