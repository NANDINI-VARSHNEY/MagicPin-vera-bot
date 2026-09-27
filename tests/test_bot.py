import json
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.context_store import context_store

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_teardown():
    # Teardown before each test
    client.post("/v1/teardown")
    yield
    client.post("/v1/teardown")

def test_healthz_and_metadata():
    res = client.get("/v1/healthz")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert "uptime_seconds" in data
    assert data["contexts_loaded"]["category"] == 0

    res_meta = client.get("/v1/metadata")
    assert res_meta.status_code == 200
    meta = res_meta.json()
    assert "team_name" in meta
    assert "version" in meta

def test_context_push_and_versioning():
    payload = {"slug": "dentists", "voice": {"tone": "peer_clinical"}}
    
    # 1. First push
    res = client.post("/v1/context", json={
        "scope": "category",
        "context_id": "dentists",
        "version": 1,
        "payload": payload,
        "delivered_at": "2026-04-26T10:00:00Z"
    })
    assert res.status_code == 200
    assert res.json()["accepted"] is True

    # 2. Duplicate same version -> 409 stale_version per Example 1.5
    res_dup = client.post("/v1/context", json={
        "scope": "category",
        "context_id": "dentists",
        "version": 1,
        "payload": payload,
        "delivered_at": "2026-04-26T10:05:00Z"
    })
    assert res_dup.status_code == 409
    assert res_dup.json()["accepted"] is False
    assert res_dup.json()["reason"] == "stale_version"
    assert res_dup.json()["current_version"] == 1

    # 3. Higher version -> replaces atomically
    res_update = client.post("/v1/context", json={
        "scope": "category",
        "context_id": "dentists",
        "version": 2,
        "payload": {**payload, "version_note": "updated"},
        "delivered_at": "2026-04-26T10:10:00Z"
    })
    assert res_update.status_code == 200
    assert res_update.json()["accepted"] is True

    # 4. Lower version -> 409 stale version conflict
    res_stale = client.post("/v1/context", json={
        "scope": "category",
        "context_id": "dentists",
        "version": 1,
        "payload": payload,
        "delivered_at": "2026-04-26T10:15:00Z"
    })
    assert res_stale.status_code == 409
    assert res_stale.json()["accepted"] is False
    assert res_stale.json()["reason"] == "stale_version"
    assert res_stale.json()["current_version"] == 2

def test_tick_and_composition():
    # Push category
    client.post("/v1/context", json={
        "scope": "category",
        "context_id": "dentists",
        "version": 1,
        "payload": {
            "slug": "dentists",
            "voice": {"tone": "peer_clinical", "vocab_taboo": ["cure", "guaranteed"]},
            "digest": [
                {
                    "id": "d_fluoride",
                    "title": "Fluoride recall cuts caries 38%",
                    "source": "JIDA Oct 2026, p.14",
                    "trial_n": 2100
                }
            ]
        },
        "delivered_at": "2026-04-26T10:00:00Z"
    })

    # Push merchant
    client.post("/v1/context", json={
        "scope": "merchant",
        "context_id": "m_001",
        "version": 1,
        "payload": {
            "merchant_id": "m_001",
            "category_slug": "dentists",
            "identity": {"name": "Dr. Meera Clinic", "owner_first_name": "Meera", "locality": "Lajpat Nagar", "languages": ["en", "hi"]},
            "performance": {"views": 2410, "calls": 18, "delta_7d": {"calls_pct": -0.05}},
            "offers": [{"title": "Dental Cleaning @ ₹299", "status": "active"}]
        },
        "delivered_at": "2026-04-26T10:00:00Z"
    })

    # Push trigger
    client.post("/v1/context", json={
        "scope": "trigger",
        "context_id": "trg_001",
        "version": 1,
        "payload": {
            "id": "trg_001",
            "kind": "research_digest",
            "merchant_id": "m_001",
            "payload": {"category": "dentists", "top_item_id": "d_fluoride"},
            "suppression_key": "res:dentists:m_001:2026"
        },
        "delivered_at": "2026-04-26T10:00:00Z"
    })

    # Call tick
    res = client.post("/v1/tick", json={
        "now": "2026-04-26T10:30:00Z",
        "available_triggers": ["trg_001"]
    })
    assert res.status_code == 200
    actions = res.json()["actions"]
    assert len(actions) == 1
    act = actions[0]
    assert act["merchant_id"] == "m_001"
    assert "Dr. Meera" in act["body"]
    assert "JIDA" in act["body"]
    assert "cure" not in act["body"].lower()
    assert "guaranteed" not in act["body"].lower()

def test_auto_reply_hell():
    conv_id = "conv_test_auto"
    auto_msg = "Thank you for contacting us! Our team will respond shortly."

    # Turn 1: Bot might wait
    res1 = client.post("/v1/reply", json={
        "conversation_id": conv_id,
        "merchant_id": "m_001",
        "from_role": "merchant",
        "message": auto_msg,
        "received_at": "2026-04-26T10:00:00Z",
        "turn_number": 1
    })
    assert res1.status_code == 200
    assert res1.json()["action"] in ["wait", "end"]

    # Turn 2: Repeated auto-reply -> Bot MUST END
    res2 = client.post("/v1/reply", json={
        "conversation_id": conv_id,
        "merchant_id": "m_001",
        "from_role": "merchant",
        "message": auto_msg,
        "received_at": "2026-04-26T10:05:00Z",
        "turn_number": 2
    })
    assert res2.status_code == 200
    assert res2.json()["action"] == "end"

def test_intent_transition():
    conv_id = "conv_test_intent"
    res = client.post("/v1/reply", json={
        "conversation_id": conv_id,
        "merchant_id": "m_001",
        "from_role": "merchant",
        "message": "Ok lets do it. Whats next?",
        "received_at": "2026-04-26T10:10:00Z",
        "turn_number": 2
    })
    assert res.status_code == 200
    data = res.json()
    assert data["action"] == "send"
    body = data["body"].lower()
    
    actioning = ["done", "sending", "draft", "here", "confirm", "proceed", "next"]
    qualifying = ["would you", "do you", "can you tell", "what if", "how about"]
    
    assert any(w in body for w in actioning)
    assert not any(w in body for w in qualifying)

def test_hostile_handling():
    conv_id = "conv_test_hostile"
    res = client.post("/v1/reply", json={
        "conversation_id": conv_id,
        "merchant_id": "m_001",
        "from_role": "merchant",
        "message": "Stop messaging me. This is useless spam.",
        "received_at": "2026-04-26T10:15:00Z",
        "turn_number": 2
    })
    assert res.status_code == 200
    data = res.json()
    assert data["action"] == "end" or (data["action"] == "send" and any(w in data["body"].lower() for w in ["sorry", "apolog", "won't"]))

def test_curveball_query():
    conv_id = "conv_test_curveball"
    res = client.post("/v1/reply", json={
        "conversation_id": conv_id,
        "merchant_id": "m_001",
        "from_role": "merchant",
        "message": "Btw can you also help me with my GST filing this month?",
        "received_at": "2026-04-26T10:20:00Z",
        "turn_number": 2
    })
    assert res.status_code == 200
    data = res.json()
    assert data["action"] == "send"
    assert "ca" in data["body"].lower() or "gst" in data["body"].lower()

def test_customer_recall_tick():
    # Push category
    client.post("/v1/context", json={
        "scope": "category",
        "context_id": "dentists",
        "version": 1,
        "payload": {
            "slug": "dentists",
            "voice": {"tone": "peer_clinical"}
        },
        "delivered_at": "2026-04-26T10:00:00Z"
    })
    # Push merchant
    client.post("/v1/context", json={
        "scope": "merchant",
        "context_id": "m_001",
        "version": 1,
        "payload": {
            "merchant_id": "m_001",
            "category_slug": "dentists",
            "identity": {"name": "Dr. Meera Clinic", "locality": "Lajpat Nagar"},
            "offers": [{"title": "Dental Cleaning @ ₹299", "status": "active"}]
        },
        "delivered_at": "2026-04-26T10:00:00Z"
    })
    # Push customer
    client.post("/v1/context", json={
        "scope": "customer",
        "context_id": "c_001",
        "version": 1,
        "payload": {
            "customer_id": "c_001",
            "merchant_id": "m_001",
            "identity": {"name": "Priya", "language_pref": "hi-en mix"},
            "relationship": {"last_visit": "2026-05-12", "services_received": ["cleaning"]}
        },
        "delivered_at": "2026-04-26T10:00:00Z"
    })
    # Push trigger
    client.post("/v1/context", json={
        "scope": "trigger",
        "context_id": "trg_cust",
        "version": 1,
        "payload": {
            "id": "trg_cust",
            "kind": "recall_due",
            "merchant_id": "m_001",
            "customer_id": "c_001",
            "suppression_key": "recall:c_001:2026"
        },
        "delivered_at": "2026-04-26T10:00:00Z"
    })

    res = client.post("/v1/tick", json={
        "now": "2026-04-26T11:00:00Z",
        "available_triggers": ["trg_cust"]
    })
    assert res.status_code == 200
    actions = res.json()["actions"]
    assert len(actions) == 1
    act = actions[0]
    assert act["send_as"] == "merchant_on_behalf"
    assert act["template_name"] == "merchant_recall_reminder_v1"
    assert act["cta"] == "multi_choice_slot"
    assert "Priya" in act["body"]

def test_bot_compose_standalone():
    from bot import compose
    cat = {"slug": "dentists", "voice": {"tone": "peer_clinical", "vocab_taboo": ["cure", "guaranteed"]}}
    mx = {"identity": {"name": "Dr. Meera", "locality": "Lajpat Nagar"}, "offers": []}
    trg = {"id": "t1", "kind": "cde_opportunity", "payload": {"credits": 2}, "suppression_key": "cde:1"}
    
    res = compose(cat, mx, trg, None)
    assert res["send_as"] == "vera"
    assert "Dr. Meera" in res["body"]
    assert "cde:1" == res["suppression_key"]
    assert res["cta"] == "open_ended"
    assert "cure" not in res["body"].lower()
    assert "guaranteed" not in res["body"].lower()

    # Customer facing
    cust = {"identity": {"name": "Aditya"}, "relationship": {"last_visit": "2026-04-10"}}
    trg_cust = {"id": "t2", "kind": "appointment_tomorrow", "payload": {"slot_time": "11:00 AM"}}
    res_cust = compose(cat, mx, trg_cust, cust)
    assert res_cust["send_as"] == "merchant_on_behalf"
    assert "Aditya" in res_cust["body"]
    assert "11:00 AM" in res_cust["body"]
    assert res_cust["cta"] == "binary"

def test_conversation_handlers_respond():
    from conversation_handlers import respond
    
    # 1. Commitment signal
    state = {"turn_number": 2, "history": []}
    r1 = respond(state, "Ok lets do it. Whats next?")
    assert r1["action"] == "send"
    assert "Done" in r1["body"]
    assert "would you" not in r1["body"].lower()

    # 2. Hostile signal
    r2 = respond(state, "Stop messaging me. This is useless spam.")
    assert r2["action"] == "end"

    # 3. Auto-reply signal
    r3 = respond(state, "Thank you for contacting us! Our team will respond shortly.")
    assert r3["action"] == "end"

def test_submission_jsonl_validity():
    import json
    from pathlib import Path
    
    sub_path = Path(__file__).parent.parent / "submission.jsonl"
    assert sub_path.exists(), "submission.jsonl must exist"
    
    lines = [line.strip() for line in sub_path.read_text().splitlines() if line.strip()]
    assert len(lines) == 30, f"Expected 30 lines in submission.jsonl, got {len(lines)}"
    
    required_keys = {"test_id", "body", "cta", "send_as", "suppression_key", "rationale"}
    for idx, line in enumerate(lines, 1):
        data = json.loads(line)
        assert required_keys.issubset(data.keys()), f"Line {idx} missing keys: {required_keys - set(data.keys())}"
        assert data["test_id"].startswith("T")
        assert len(data["body"].strip()) > 10
        assert data["send_as"] in ("vera", "merchant_on_behalf")

