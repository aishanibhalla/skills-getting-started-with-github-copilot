import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data

def test_signup_and_unregister():
    # Use a unique email for testing
    test_email = "testuser@mergington.edu"
    activity = "Chess Club"

    # Ensure not already signed up
    client.post(f"/activities/{activity}/unregister", json={"email": test_email})

    # Sign up
    response = client.post(f"/activities/{activity}/signup?email={test_email}")
    assert response.status_code == 200
    assert f"Signed up {test_email}" in response.json()["message"]

    # Check participant is added
    activities = client.get("/activities").json()
    assert test_email in activities[activity]["participants"]

    # Unregister
    response = client.post(f"/activities/{activity}/unregister", json={"email": test_email})
    assert response.status_code == 200
    assert f"Unregistered {test_email}" in response.json()["message"]

    # Check participant is removed
    activities = client.get("/activities").json()
    assert test_email not in activities[activity]["participants"]


def test_signup_duplicate():
    activity = "Chess Club"
    email = "michael@mergington.edu"  # Already present
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


def test_unregister_not_found():
    activity = "Chess Club"
    email = "notregistered@mergington.edu"
    response = client.post(f"/activities/{activity}/unregister", json={"email": email})
    assert response.status_code == 400
    assert "not registered" in response.json()["detail"]


def test_signup_invalid_email():
    activity = "Chess Club"
    
    # Test empty email
    response = client.post(f"/activities/{activity}/signup?email=")
    assert response.status_code == 400
    assert "Invalid email format" in response.json()["detail"]
    
    # Test malformed email (no @)
    response = client.post(f"/activities/{activity}/signup?email=invalidemail")
    assert response.status_code == 400
    assert "Invalid email format" in response.json()["detail"]
    
    # Test malformed email (no domain)
    response = client.post(f"/activities/{activity}/signup?email=invalid@")
    assert response.status_code == 400
    assert "Invalid email format" in response.json()["detail"]
    
    # Test malformed email (no TLD)
    response = client.post(f"/activities/{activity}/signup?email=invalid@domain")
    assert response.status_code == 400
    assert "Invalid email format" in response.json()["detail"]
    
    # Test malformed email (spaces)
    response = client.post(f"/activities/{activity}/signup?email=invalid email@domain.com")
    assert response.status_code == 400
    assert "Invalid email format" in response.json()["detail"]
    
    # Test malformed email (consecutive dots)
    response = client.post(f"/activities/{activity}/signup?email=user..name@domain.com")
    assert response.status_code == 400
    assert "Invalid email format" in response.json()["detail"]
    
    # Test malformed email (leading dot)
    response = client.post(f"/activities/{activity}/signup?email=.user@domain.com")
    assert response.status_code == 400
    assert "Invalid email format" in response.json()["detail"]
    
    # Test malformed email (trailing dot)
    response = client.post(f"/activities/{activity}/signup?email=user.@domain.com")
    assert response.status_code == 400
    assert "Invalid email format" in response.json()["detail"]


def test_signup_valid_email():
    activity = "Chess Club"
    
    # Test various valid email formats
    valid_emails = [
        "newuser@mergington.edu",
        "user.name@mergington.edu",
        "user_name@mergington.edu",
        "user123@mergington.edu",
        "a@mergington.edu",
    ]
    
    for email in valid_emails:
        # First unregister in case email exists
        client.post(f"/activities/{activity}/unregister", json={"email": email})
        
        # Try to sign up with valid email
        response = client.post(f"/activities/{activity}/signup?email={email}")
        # Should succeed (200) or fail because already signed up (400) or activity full (400)
        # but should NOT fail due to invalid email format
        assert response.status_code in [200, 400], f"Unexpected status code for {email}"
        if response.status_code == 400:
            # If it fails, it should NOT be due to email format
            detail = response.json()["detail"]
            assert "Invalid email format" not in detail, f"Email {email} incorrectly marked as invalid"
        
        # Clean up - unregister the user
        client.post(f"/activities/{activity}/unregister", json={"email": email})


def test_signup_with_plus_sign_properly_encoded():
    """Test that emails with + signs work when properly URL-encoded"""
    from urllib.parse import quote
    
    activity = "Chess Club"
    # Email with plus sign (used for plus-addressing/subaddressing)
    email = "user+tag@mergington.edu"
    
    # First unregister in case email exists
    client.post(f"/activities/{activity}/unregister", json={"email": email})
    
    # Properly URL-encode the email (+ becomes %2B)
    encoded_email = quote(email, safe='@')
    
    # Try to sign up with properly encoded email
    response = client.post(f"/activities/{activity}/signup?email={encoded_email}")
    
    # Should succeed (200) or fail for reasons other than email format
    assert response.status_code in [200, 400], f"Unexpected status code for {email}"
    if response.status_code == 400:
        # If it fails, it should NOT be due to email format
        detail = response.json()["detail"]
        assert "Invalid email format" not in detail, f"Email {email} incorrectly marked as invalid when properly URL-encoded"
    
    # Clean up - unregister the user
    client.post(f"/activities/{activity}/unregister", json={"email": email})
