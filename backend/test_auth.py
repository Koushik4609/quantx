import os
import pytest
from fastapi.testclient import TestClient
from app.main import app

# Set the emulator host so our test connects to the local Firebase emulator
os.environ["FIREBASE_AUTH_EMULATOR_HOST"] = "127.0.0.1:9099"
os.environ["FIREBASE_API_KEY"] = "fake-api-key"

client = TestClient(app)

TEST_USER = {
    "email": "test_user_auth@example.com",
    "password": "SecurePassword123!"
}

def test_signup():
    response = client.post("/auth/signup", json=TEST_USER)
    
    # If the user already exists in the emulator from a previous test run,
    # it might return 400 EMAIL_EXISTS, which is also fine.
    if response.status_code == 400 and "EMAIL_EXISTS" in response.text:
        return
        
    assert response.status_code == 200
    data = response.json()
    assert "idToken" in data
    assert data["email"] == TEST_USER["email"]

def test_login_and_protected_route():
    # 1. Login
    response = client.post("/auth/login", json=TEST_USER)
    assert response.status_code == 200
    data = response.json()
    token = data["idToken"]
    
    # 2. Access protected route WITH token
    headers = {"Authorization": f"Bearer {token}"}
    protected_response = client.get("/protected", headers=headers)
    assert protected_response.status_code == 200
    protected_data = protected_response.json()
    assert protected_data["email"] == TEST_USER["email"]
    
    # 3. Access protected route WITHOUT token
    unauthorized_response = client.get("/protected")
    assert unauthorized_response.status_code == 403 # FastAPI HTTPBearer returns 403 when missing

def test_protected_route_invalid_token():
    headers = {"Authorization": "Bearer invalid_jwt_token_here"}
    response = client.get("/protected", headers=headers)
    assert response.status_code == 401
