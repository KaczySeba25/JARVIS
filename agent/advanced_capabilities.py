"""Honest local helpers for memory, evidence, plans and safety diagnostics."""
from __future__ import annotations
import hashlib, json, re

def execute(name: str, argument=None):
    value = "" if argument is None else str(argument).strip()
    if name == "semantic_memory_retriever":
        try:
            from memory_store import recall
            return {"query": value, "matches": recall(value, limit=8), "mode": "local_lexical"}
        except Exception as exc:
            return {"query": value, "matches": [], "error": type(exc).__name__}
    if name == "evidence_reconciler":
        claims = [line.strip() for line in value.splitlines() if line.strip()]
        return {"claims": claims, "conflicts": "not_assessed", "status": "needs_source_comparison", "needs_sources": bool(claims)}
    if name == "claim_provenance":
        sources = []
        if value:
            try:
                from jarvis_core import DB_FILE
                import sqlite3
                with sqlite3.connect(DB_FILE) as db:
                    if db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='knowledge'").fetchone():
                        sources = [{"title": row[0], "url": row[1], "fetched_at": row[2]} for row in db.execute("SELECT title,url,fetched_at FROM knowledge WHERE conclusion LIKE ? ORDER BY fetched_at DESC LIMIT 5", (f"%{value[:100]}%",))]
            except Exception:
                sources = []
        return {"claim": value, "claim_id": hashlib.sha256(value.encode()).hexdigest()[:16], "sources": sources, "confidence": "source_found" if sources else "unverified"}
    if name == "structured_output_validator":
        try: data=json.loads(value)
        except json.JSONDecodeError: return {"valid":False,"error":"invalid_json"}
        return {"json_valid":isinstance(data,(dict,list)),"schema_valid":False,"type":type(data).__name__,"reason":"No JSON schema was supplied."}
    if name == "plan_optimizer":
        steps=list(dict.fromkeys(x.strip() for x in value.splitlines() if x.strip())); return {"steps":steps,"removed_duplicates":max(0,len(value.splitlines())-len(steps))}
    if name == "dependency_graph_builder": return {"edges":[{"from":a.strip(),"to":b.strip()} for a,b in (x.split("->",1) for x in value.splitlines() if "->" in x)]}
    if name == "sandbox_policy_engine": return {"allowed":False,"reason":"this helper does not enforce operating-system isolation","operation":value}
    if name == "rollback_orchestrator": return {"rollback_performed":False,"action":"plan_only","checkpoint":value or "before_operation"}
    if name == "workflow_scheduler": return {"queue_plan":[x.strip() for x in value.split(",") if x.strip()],"scheduled":False}
    if name == "event_bus": return {"event":value,"event_id":hashlib.sha256(value.encode()).hexdigest()[:16],"persisted":False}
    if name == "recovery_coordinator": return {"failure":value,"actions":["capture_error","bounded_retry_if_safe","review"],"recovery_performed":False}
    if name == "adaptive_model_router": return {"selected":"current_configured_provider","selection_performed":False,"criteria":value.split(",") if value else ["quality","privacy","latency"]}
    if name == "context_compressor": return {"normalized_text":" ".join(value.split()),"compression_performed":False,"original_chars":len(value)}
    if name == "conversation_summarizer": return {"input_excerpt":value[:1000],"summary_created":False,"open_questions":"not_assessed"}
    if name == "benchmark_runner": return {"status":"not_run","target":value or "skill_contract","measurements":[]}
    if name == "adversarial_test_harness": return {"cases":["empty_input","malformed_input","repeated_input","oversized_input"],"executed":False}
    if name == "prompt_injection_firewall":
        patterns=("ignore previous", "ignore all instructions", "system prompt", "reveal secret", "bypass", "zignoruj instrukcje", "ujawnij hasło", "pomiń zasady")
        hits=[x for x in patterns if x in value.casefold()]
        return {"suspicious":bool(hits),"matches":hits,"content_blocked":False,"requires_model_review":bool(hits)}
    if name == "secret_scanner":
        hits=re.findall(r"(?:gsk_[A-Za-z0-9_-]{12,}|sk-[A-Za-z0-9_-]{12,}|(?:api[_-]?key|password|passwd|token|secret)\s*[:=]\s*[^\s,;]+)",value,re.I); return {"found":bool(hits),"count":len(hits)}
    if name == "privacy_redactor":
        redacted=re.sub(r"[\w.+-]+@[\w.-]+\.\w+","[EMAIL]",value)
        redacted=re.sub(r"(?i)(?:gsk_[A-Za-z0-9_-]{12,}|sk-[A-Za-z0-9_-]{12,}|(?:api[_-]?key|password|passwd|token|secret)\s*[:=]\s*[^\s,;]+)","[SECRET]",redacted)
        redacted=re.sub(r"(?<!\w)(?:\+44\s?\d{2,4}|0\d{2,4})(?:[\s().-]*\d){6,10}(?!\w)","[PHONE]",redacted)
        redacted=re.sub(r"\b[A-Z]{1,2}\d[A-Z\d]?\s?\d[A-Z]{2}\b","[UK_POSTCODE]",redacted,flags=re.I)
        redacted=re.sub(r"\b\d{9,}\b","[NUMBER]",redacted)
        return {"text":redacted,"changed":redacted!=value}
    if name == "cost_budget_guard": return {"within_budget":None,"budget":value or "not_configured","checked":False}
    if name == "latency_optimizer": return {"recommendations":["measure_first","bound_timeouts","cache_read_only_results"],"metrics_measured":False}
    if name == "knowledge_expiry_manager": return {"freshness":"unknown","requires_refresh":True,"reason":"No source timestamps supplied."}
    if name == "source_quality_ranker": return {"sources":[{"source":value,"score":0,"reason":"unrated"}] if value else []}
    if name == "hypothesis_tracker": return {"hypothesis":value,"status":"untested","evidence":[]}
    if name == "experiment_manager": return {"hypothesis":value,"stop_condition":"user_defined","approved":False}
    if name == "decision_simulator": return {"options":[x.strip() for x in value.split(",") if x.strip()],"simulation_performed":False,"consequences":"not_assessed"}
    if name == "intent_resolver": return {"input":value,"intent":"requires_reasoning","missing":"not_assessed_by_this_helper"}
    if name == "multimodal_document_pipeline": return {"path":value,"mode":"metadata_only","content_read":False}
    if name == "notification_router": return {"priority":"not_assessed","channel":"not_configured","sent":False,"message":value}
    if name == "human_handoff_manager": return {"handoff_required":True,"context":value,"next_action":"review"}
    raise ValueError(f"Unknown capability: {name}")

