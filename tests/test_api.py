import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "VeriSafe API"


def test_favicon_no_content():
    response = client.get("/favicon.ico")
    assert response.status_code in (200, 204)


def test_docs_available():
    response = client.get("/docs")
    assert response.status_code == 200


def test_root_serves_spa_or_welcome():
    response = client.get("/")
    assert response.status_code == 200


def test_analyze_message_high_risk():
    payload = {
        "message_text": "URGENT: Your bank account has been locked. Click http://192.168.1.1/verify immediately and enter your OTP.",
        "sender": "security-alert@verify-online-bank.cc",
        "channel": "sms",
    }
    response = client.post("/api/messages/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["risk_level"] == "High"
    assert data["confidence_score"] >= 0.80
    assert len(data["indicators"]) >= 2


def test_analyze_message_low_risk():
    payload = {
        "message_text": "Hey Sarah, let's meet tomorrow at 10 AM in the conference room for the project kickoff.",
        "sender": "sarah@company.internal",
        "channel": "email",
    }
    response = client.post("/api/messages/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["risk_level"] == "Low"


def test_analyze_message_validation_error():
    payload = {"message_text": "", "channel": "sms"}
    response = client.post("/api/messages/analyze", json=payload)
    assert response.status_code == 422


def test_analyze_url_typosquatting_high_risk():
    payload = {
        "url": "https://secure-login.paypa1-update.com/account/login",
        "context": "Received via SMS",
    }
    response = client.post("/api/urls/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["risk_level"] == "High"
    assert data["domain_details"]["has_homoglyphs"] is True


def test_analyze_url_ip_host():
    payload = {"url": "http://192.168.1.1/login"}
    response = client.post("/api/urls/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["risk_level"] == "High"
    assert data["domain_details"]["is_ip_address"] is True


def test_analyze_url_safe():
    payload = {"url": "https://github.com/fastapi/fastapi"}
    response = client.post("/api/urls/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["risk_level"] == "Low"


def test_analyze_url_validation_error():
    payload = {"url": ""}
    response = client.post("/api/urls/analyze", json=payload)
    assert response.status_code == 422

