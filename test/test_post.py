from config import client

def test_create_post(generate_token):
    r = client.post("/posts/new", headers = {"access_token" : generate_token}, json={"title" : "I am a title", 'content' : "I am a content"})
    assert r.json.get("message") == "Post has been Created"
    assert r.status_code == 200
    
def test_create_post_failure_1(generate_token):
    r = client.post("/posts/new", headers = {"access_token" : generate_token}, json={"tite" : "I am a title", 'content' : "I am a content"})
    assert r.json.get("message").get("tite")[0] == "Unknown field."
    assert r.json.get("message").get("title")[0] == "Missing data for required field."
    assert r.status_code == 400
    
def test_get_posts():
    r = client.get("/posts")
    assert r.status_code == 200
    
def test_get_single_post_failure():
    r = client.get("/posts/1")
    assert r.status_code == 200
    
def test_get_single_post_failure():
    r = client.get("/posts/100000000000000000000000")
    assert r.json.get("message") == "The Post doesnot exist"
    assert r.status_code == 404
    


    