from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field

# --- Context Models ---
class ContextPushRequest(BaseModel):
    scope: Literal["category", "merchant", "customer", "trigger"]
    context_id: str
    version: int
    payload: Dict[str, Any]
    delivered_at: str

class ContextPushSuccessResponse(BaseModel):
    accepted: bool = True
    ack_id: str
    stored_at: str

class ContextPushConflictResponse(BaseModel):
    accepted: bool = False
    reason: str = "stale_version"
    current_version: int

class ContextPushErrorResponse(BaseModel):
    accepted: bool = False
    reason: str
    details: Optional[str] = None


# --- Tick Models ---
class TickRequest(BaseModel):
    now: str
    available_triggers: List[str] = Field(default_factory=list)

class TickAction(BaseModel):
    conversation_id: str
    merchant_id: str
    customer_id: Optional[str] = None
    send_as: str = "vera"
    trigger_id: str
    template_name: str
    template_params: List[Any] = Field(default_factory=list)
    body: str
    cta: str = "open_ended"
    suppression_key: str
    rationale: str

class TickResponse(BaseModel):
    actions: List[TickAction] = Field(default_factory=list)


# --- Reply Models ---
class ReplyRequest(BaseModel):
    conversation_id: str
    merchant_id: Optional[str] = None
    customer_id: Optional[str] = None
    from_role: str
    message: str
    received_at: str
    turn_number: int

class ReplyResponse(BaseModel):
    action: Literal["send", "wait", "end"]
    body: Optional[str] = None
    cta: Optional[str] = None
    wait_seconds: Optional[int] = None
    rationale: str


# --- Healthz & Metadata ---
class ContextCounts(BaseModel):
    category: int = 0
    merchant: int = 0
    customer: int = 0
    trigger: int = 0

class HealthzResponse(BaseModel):
    status: str = "ok"
    uptime_seconds: int
    contexts_loaded: ContextCounts

class MetadataResponse(BaseModel):
    team_name: str
    team_members: List[str]
    model: str
    approach: str
    contact_email: str
    version: str
    submitted_at: str
