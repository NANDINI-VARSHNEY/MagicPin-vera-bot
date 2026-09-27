"""
Test the exact Judge Simulator scenarios in-process using TestClient.
Ensures 100% judge compliance without requiring external TCP network permissions.
"""

import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture(autouse=True)
def teardown():
    client.post("/v1/teardown")
    yield
    client.post("/v1/teardown")


def test_judge_warmup_scenario():
    # 1. healthz
    res = client.get("/v1/healthz")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"

    # 2. metadata
    meta = client.get("/v1/metadata").json()
    assert "team_name" in meta
    assert "model" in meta

    # 3. Context push - categories
    root = Path(__file__).parent.parent
    cat_dir = root / "dataset" / "categories"
    for f in cat_dir.glob("*.json"):
        data = json.load(open(f))
        slug = data.get("slug", f.stem)
        r = client.post("/v1/context", json={
            "scope": "category", "context_id": slug, "version": 1,
            "payload": data, "delivered_at": "2026-04-26T10:00:00Z"
        })
        assert r.status_code == 200
        assert r.json()["accepted"] is True

    # 4. Context push - merchants
    m_path = root / "dataset" / "merchants_seed.json"
    merchants = json.load(open(m_path)).get("merchants", [])
    for m in merchants[:5]:
        r = client.post("/v1/context", json={
            "scope": "merchant", "context_id": m["merchant_id"], "version": 1,
            "payload": m, "delivered_at": "2026-04-26T10:00:00Z"
        })
        assert r.status_code == 200
        assert r.json()["accepted"] is True

    # 5. Verify healthz loaded counts
    hz = client.get("/v1/healthz").json()
    assert hz["contexts_loaded"]["category"] == len(list(cat_dir.glob("*.json")))
    assert hz["contexts_loaded"]["merchant"] == 5


def test_judge_auto_reply_scenario():
    mid = "m_001_drmeera"
    auto_msg = "Thank you for contacting us! Our team will respond shortly."

    ended = False
    for i in range(1, 5):
        res = client.post("/v1/reply", json={
            "conversation_id": f"conv_auto_{i}",
            "merchant_id": mid,
            "customer_id": None,
            "from_role": "merchant",
            "message": auto_msg,
            "received_at": "2026-04-26T10:45:00Z",
            "turn_number": i + 1
        })
        assert res.status_code == 200
        data = res.json()
        if data["action"] == "end":
            ended = True
            break
        elif data["action"] == "wait":
            assert data["wait_seconds"] == 1800

    assert ended, "Judge scenario: Bot must end after detecting repeated auto-replies"


def test_judge_intent_transition_scenario():
    mid = "m_001_drmeera"
    commitment = "Ok lets do it. Whats next?"

    res = client.post("/v1/reply", json={
        "conversation_id": "conv_intent_1",
        "merchant_id": mid,
        "customer_id": None,
        "from_role": "merchant",
        "message": commitment,
        "received_at": "2026-04-26T10:45:00Z",
        "turn_number": 2
    })
    assert res.status_code == 200
    data = res.json()
    assert data["action"] == "send"

    body_lower = data["body"].lower()
    actioning = ["done", "sending", "draft", "here", "confirm", "proceed", "next"]
    qualifying = ["would you", "do you", "can you tell", "what if", "how about"]

    assert any(w in body_lower for w in actioning), "Must switch to action mode with actioning words"
    assert not any(w in body_lower for w in qualifying), "Must not continue qualifying after commitment"


def test_judge_hostile_scenario():
    mid = "m_001_drmeera"
    hostile = "Stop messaging me. This is useless spam."

    res = client.post("/v1/reply", json={
        "conversation_id": "conv_hostile_1",
        "merchant_id": mid,
        "customer_id": None,
        "from_role": "merchant",
        "message": hostile,
        "received_at": "2026-04-26T10:45:00Z",
        "turn_number": 2
    })
    assert res.status_code == 200
    data = res.json()
    assert data["action"] == "end", "Must gracefully exit on hostile/stop message"


def test_judge_curveball_gst_scenario():
    mid = "m_001_drmeera"
    gst_msg = "Btw can you also help me with my GST filing this month?"

    res = client.post("/v1/reply", json={
        "conversation_id": "conv_curveball_1",
        "merchant_id": mid,
        "customer_id": None,
        "from_role": "merchant",
        "message": gst_msg,
        "received_at": "2026-04-26T10:45:00Z",
        "turn_number": 2
    })
    assert res.status_code == 200
    data = res.json()
    assert data["action"] == "send"
    assert "ca" in data["body"].lower() or "gst" in data["body"].lower()
    assert data["cta"] == "open_ended"


def test_judge_abstract_request_scenario():
    mid = "m_001_drmeera"
    req_msg = "Yes please send the abstract. Also draft the patient WhatsApp."

    res = client.post("/v1/reply", json={
        "conversation_id": "conv_abstract_1",
        "merchant_id": mid,
        "customer_id": None,
        "from_role": "merchant",
        "message": req_msg,
        "received_at": "2026-04-26T10:45:00Z",
        "turn_number": 2
    })
    assert res.status_code == 200
    data = res.json()
    assert data["action"] == "send"
    assert "abstract" in data["body"].lower() or "draft" in data["body"].lower()
    assert data["cta"] in ("binary", "binary_yes_no")
