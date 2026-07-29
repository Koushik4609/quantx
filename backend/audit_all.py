import os
import re
import sys
import json
from fastapi.testclient import TestClient

sys.path.append(os.path.join(os.getcwd(), 'backend'))

try:
    from app.main import app
    from test_db import TestingSessionLocal, override_get_db
    from app.models.base import Base
    from test_db import engine
except Exception as e:
    print(f"Failed to import app: {e}")
    sys.exit(1)

import asyncio
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

asyncio.run(init_db())

# 1. Parse Frontend Routes
frontend_dir = "frontend/src/api"
pattern = re.compile(r'apiClient\.(get|post|put|delete)\s*\(\s*[`\'"](.*?)[`\'"]')

api_calls = []
for root, _, files in os.walk(frontend_dir):
    for file in files:
        if file.endswith(".ts"):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                matches = pattern.finditer(content)
                for match in matches:
                    method = match.group(1).upper()
                    url_raw = match.group(2)
                    api_calls.append({"method": method, "url_raw": url_raw, "file": file})

# 2. Setup Mock Data in DB
from app.models.schema import User, Portfolio
import uuid

async def setup_data():
    async with TestingSessionLocal() as session:
        u = User(id=uuid.UUID("123e4567-e89b-12d3-a456-426614174000"), email="test@test.com", password_hash="hash")
        p = Portfolio(id=uuid.UUID("123e4567-e89b-12d3-a456-426614174000"), user_id=u.id, name="Test", total_value=100)
        session.add(u)
        session.add(p)
        await session.commit()

asyncio.run(setup_data())

def test_all():
    report = ["# Architecture Audit Report\n"]
    report.append("## Frontend API Request Audit\n")
    report.append("| Method | Expected URL | Status | Response Sample |")
    report.append("|---|---|---|---|")
    
    mock_values = {
        "${userId}": "123e4567-e89b-12d3-a456-426614174000",
        "${portfolioId}": "123e4567-e89b-12d3-a456-426614174000",
        "${ticker}": "AAPL",
        "${symbol}": "AAPL",
        "${id}": "123e4567-e89b-12d3-a456-426614174000",
        "${bookmarkId}": "123e4567-e89b-12d3-a456-426614174000",
        "${query}": "Apple"
    }
    
    # Define valid mock payloads for POST requests to avoid 422
    mock_bodies = {
        "/news/summarize": {"url": "https://example.com"},
        "/news/bookmarks": {"user_id": "123e4567-e89b-12d3-a456-426614174000", "article_url": "https://example.com", "article_title": "Test"},
        "/learning/progress": {"user_id": "123e4567-e89b-12d3-a456-426614174000", "lesson_id": "123e4567-e89b-12d3-a456-426614174000", "score": 100},
        "/strategy/": {"user_id": "123e4567-e89b-12d3-a456-426614174000", "name": "Test", "symbol": "AAPL", "conditions": {}},
        "/strategy/123e4567-e89b-12d3-a456-426614174000/backtest": {},
        "/trading/buy": {"portfolio_id": "123e4567-e89b-12d3-a456-426614174000", "symbol": "AAPL", "quantity": 1, "price": 100},
        "/trading/sell": {"portfolio_id": "123e4567-e89b-12d3-a456-426614174000", "symbol": "AAPL", "quantity": 1, "price": 100},
        "/trading/portfolio": "123e4567-e89b-12d3-a456-426614174000",
        "/ai/chat": {"user_id": "123e4567-e89b-12d3-a456-426614174000", "portfolio_id": "123e4567-e89b-12d3-a456-426614174000", "message": "hello"},
        "/auth/login": {"email": "test@test.com", "password": "password"},
        "/auth/signup": {"email": "test@test.com", "password": "password"},
    }
    
    client = TestClient(app)
    
    for call in api_calls:
        method = call["method"]
        url = call["url_raw"]
        
        for k, v in mock_values.items():
            url = url.replace(k, v)
            
        if not url.startswith("/"):
            url = "/" + url
        url = url.replace("//", "/")
            
        try:
            if method == "GET":
                res = client.get(url)
            elif method == "POST":
                body = mock_bodies.get(url, {})
                if url == "/trading/portfolio":
                     res = client.post(url, json=body)
                else:
                     res = client.post(url, json=body)
            elif method == "DELETE":
                res = client.delete(url)
            elif method == "PUT":
                res = client.put(url, json={})
                
            status = res.status_code
            try:
                body = str(res.json())[:100]
            except:
                body = res.text[:100]
            
            body = body.replace("\n", "").replace("|", "\\|")
            mark = "✅" if status in [200, 201] else "❌"
            report.append(f"| {method} | `{url}` | {mark} {status} | `{body}` |")
        except Exception as e:
            report.append(f"| {method} | `{url}` | ❌ ERROR | {e} |")
            
    with open('/Users/koushikrajmajji/.gemini/antigravity-ide/brain/752e04ca-900e-42a4-957d-8855a63b9040/architecture_audit_report.md', 'w') as f:
        f.write("\n".join(report))
        
    print("Audit generated.")

if __name__ == "__main__":
    test_all()
