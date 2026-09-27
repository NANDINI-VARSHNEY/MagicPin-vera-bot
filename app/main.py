import time
from datetime import datetime, timezone
import json
from pathlib import Path
from fastapi import FastAPI, status
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from app.ui import get_dashboard_html

from app.config import settings
from app.models import (
    ContextPushRequest,
    ContextPushSuccessResponse,
    ContextPushConflictResponse,
    TickRequest,
    TickResponse,
    ReplyRequest,
    ReplyResponse,
    HealthzResponse,
    MetadataResponse
)
from app.context_store import context_store
from app.decision_engine import decision_engine
from app.conversation_manager import conversation_manager

START_TIME = time.time()
app = FastAPI(title=settings.app_name, version=settings.version)

@app.get("/", response_class=HTMLResponse)
async def root():
    return HTMLResponse(content=get_dashboard_html())

@app.get("/download-zip")
async def download_zip():
    zip_path = Path(__file__).parent.parent / "magicpin-vera-bot.zip"
    if not zip_path.exists():
        return JSONResponse(status_code=404, content={"error": "File not found"})
    return FileResponse(
        path=str(zip_path),
        filename="magicpin-vera-bot.zip",
        media_type="application/zip"
    )

@app.post("/api/load-seeds")
async def load_seeds():
    dataset_dir = Path(__file__).parent.parent / "dataset"
    # Load categories
    cat_dir = dataset_dir / "categories"
    if cat_dir.exists():
        for f in cat_dir.glob("*.json"):
            data = json.load(open(f))
            slug = data.get("slug", f.stem)
            context_store.push("category", slug, 1, data, datetime.now(timezone.utc).isoformat())

    # Load merchants
    m_path = dataset_dir / "merchants_seed.json"
    if m_path.exists():
        merchants = json.load(open(m_path)).get("merchants", [])
        for m in merchants:
            context_store.push("merchant", m["merchant_id"], 1, m, datetime.now(timezone.utc).isoformat())

    # Load customers
    c_path = dataset_dir / "customers_seed.json"
    if c_path.exists():
        customers = json.load(open(c_path)).get("customers", [])
        for c in customers:
            context_store.push("customer", c["customer_id"], 1, c, datetime.now(timezone.utc).isoformat())

    # Load triggers
    t_path = dataset_dir / "triggers_seed.json"
    if t_path.exists():
        triggers = json.load(open(t_path)).get("triggers", [])
        for t in triggers:
            context_store.push("trigger", t["id"], 1, t, datetime.now(timezone.utc).isoformat())

    return {"status": "ok", "counts": context_store.get_counts()}

@app.get("/api/triggers")
async def get_triggers():
    results = []
    with context_store._lock:
        for (scope, cid), val in context_store._store.items():
            if scope == "trigger":
                trg = val["payload"]
                mid = trg.get("merchant_id", "")
                merchant = context_store.get_merchant(mid) if mid else None
                m_name = merchant.get("identity", {}).get("name", mid) if merchant else mid
                locality = merchant.get("identity", {}).get("locality", "") if merchant else ""
                
                payload = trg.get("payload", {})
                summary = payload.get("topic") or payload.get("event") or payload.get("intent_topic") or payload.get("metric") or payload.get("service_due") or trg.get("kind", "")
                
                results.append({
                    "id": cid,
                    "kind": trg.get("kind", ""),
                    "merchant_id": mid,
                    "merchant_name": m_name,
                    "locality": locality,
                    "urgency": trg.get("urgency", 1),
                    "summary": str(summary)
                })
    results.sort(key=lambda x: x["id"])
    return results

@app.get("/v1/healthz", response_model=HealthzResponse)
async def healthz():
    uptime = int(time.time() - START_TIME)
    counts = context_store.get_counts()
    return HealthzResponse(
        status="ok",
        uptime_seconds=uptime,
        contexts_loaded=counts
    )

@app.get("/v1/metadata", response_model=MetadataResponse)
async def metadata():
    return MetadataResponse(
        team_name=settings.team_name,
        team_members=settings.team_members,
        model=settings.llm_model or f"hybrid-composer ({settings.llm_provider})",
        approach="anti-hallucination grounded composer with deterministic guardrails & replay state machine",
        contact_email=settings.contact_email,
        version=settings.version,
        submitted_at="2026-04-26T08:00:00Z"
    )

@app.post("/v1/context")
async def push_context(req: ContextPushRequest):
    success, current_ver = context_store.push(
        scope=req.scope,
        context_id=req.context_id,
        version=req.version,
        payload=req.payload,
        delivered_at=req.delivered_at
    )
    if not success:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"accepted": False, "reason": "stale_version", "current_version": current_ver}
        )
    return {
        "accepted": True,
        "ack_id": f"ack_{req.context_id}_v{req.version}",
        "stored_at": datetime.now(timezone.utc).isoformat()
    }

@app.post("/v1/tick", response_model=TickResponse)
async def tick(req: TickRequest):
    actions = await decision_engine.evaluate_tick(req)
    return TickResponse(actions=actions)

@app.post("/v1/reply", response_model=ReplyResponse, response_model_exclude_none=True)
async def reply(req: ReplyRequest):
    resp = conversation_manager.handle_reply(
        conv_id=req.conversation_id,
        merchant_id=req.merchant_id,
        customer_id=req.customer_id,
        from_role=req.from_role,
        message=req.message,
        turn_number=req.turn_number
    )
    return resp

@app.post("/v1/teardown")
async def teardown():
    with context_store._lock:
        context_store._store.clear()
        context_store._sent_suppressions.clear()
    conversation_manager.conversations.clear()
    return {"status": "cleared"}
