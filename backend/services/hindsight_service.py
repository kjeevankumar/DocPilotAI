import os
import json
import time
import uuid
import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from backend.config import (
    HINDSIGHT_API_KEY,
    HINDSIGHT_BASE_URL,
    HINDSIGHT_BANK_ID,
    DATA_DIR
)

# Optional Hindsight SDK import
try:
    from hindsight_client import Hindsight
    HAS_HINDSIGHT_SDK = True
except ImportError:
    HAS_HINDSIGHT_SDK = False

LOCAL_BANK_FILE = DATA_DIR / "hindsight_local_bank.json"

DEFAULT_SEED_MEMORIES = [
    {
        "id": "mem_seed_001",
        "bank_id": "docpilot-legal-bank",
        "category": "Approved Exception",
        "content": "In prior Master Services Agreement review with Acme Corp, Executive Legal approved a 1x annual contract value liability cap exception (up to $500,000 maximum), superseding our default 2x cap requirement due to Acme Corp providing an active $5M commercial cyber/E&O certificate.",
        "tags": ["Acme Corp", "liability", "precedent", "approved_exception"],
        "source_doc": "MSA_AcmeCorp_2024_Executed.pdf",
        "timestamp": "2024-10-14T11:20:00Z",
        "confidence": 0.98
    },
    {
        "id": "mem_seed_002",
        "bank_id": "docpilot-legal-bank",
        "category": "Corporate Policy",
        "content": "Global Corporate Procurement Policy Section 4.2 mandates Net-30 or Net-45 payment terms. Net-60 or longer terms are strictly prohibited without CFO written authorization and must include a 2% 10-day early settlement discount option.",
        "tags": ["payment_terms", "finance", "policy", "procurement"],
        "source_doc": "Global_Procurement_Playbook_v3.pdf",
        "timestamp": "2024-11-01T09:00:00Z",
        "confidence": 0.95
    },
    {
        "id": "mem_seed_003",
        "bank_id": "docpilot-legal-bank",
        "category": "Compliance Precedent",
        "content": "All vendor software licenses and cloud agreements must mandate mutual indemnification for third-party intellectual property infringement. Unilateral customer-only indemnification must be redlined to mutual standard protection.",
        "tags": ["indemnification", "intellectual_property", "compliance", "policy"],
        "source_doc": "Legal_Redline_Standard_Guidance.pdf",
        "timestamp": "2024-12-05T14:30:00Z",
        "confidence": 0.96
    },
    {
        "id": "mem_seed_004",
        "bank_id": "docpilot-legal-bank",
        "category": "Regulatory Rule",
        "content": "Under corporate GDPR and SOC2 compliance commitments, all security incidents and personal data breach notifications must be communicated to our Security Office within 48 hours. Any vendor draft specifying 72 hours or 'commercially reasonable effort' must be amended to 48 hours maximum.",
        "tags": ["data_privacy", "security", "GDPR", "SOC2", "compliance"],
        "source_doc": "InfoSec_Vendor_Security_Requirements.pdf",
        "timestamp": "2025-01-10T16:45:00Z",
        "confidence": 0.99
    },
    {
        "id": "mem_seed_005",
        "bank_id": "docpilot-legal-bank",
        "category": "Negotiation Precedent",
        "content": "For multi-year vendor engagements, our negotiated baseline with CloudTech Solutions established a 30-day written notice termination for convenience with pro-rated refund of prepaid fees.",
        "tags": ["termination", "convenience", "vendor_history", "negotiation"],
        "source_doc": "CloudTech_Amendment_2.pdf",
        "timestamp": "2025-01-28T10:15:00Z",
        "confidence": 0.92
    }
]

class HindsightService:
    """
    Hindsight Persistent Memory Service.
    Wraps Vectorize Hindsight Client with seamless local fallback/hybrid caching
    for resilient hackathon demos and enterprise memory operations.
    """

    def __init__(self):
        self.api_key = HINDSIGHT_API_KEY.strip() if HINDSIGHT_API_KEY else ""
        self.base_url = HINDSIGHT_BASE_URL.strip() if HINDSIGHT_BASE_URL else "https://api.hindsight.vectorize.io"
        self.bank_id = HINDSIGHT_BANK_ID.strip() if HINDSIGHT_BANK_ID else "docpilot-legal-bank"
        self.client = None

        if HAS_HINDSIGHT_SDK and self.api_key:
            try:
                self.client = Hindsight(
                    base_url=self.base_url,
                    api_key=self.api_key
                )
                print(f"[HINDSIGHT] Connected to Hindsight Cloud at {self.base_url} (Bank: {self.bank_id})")
            except Exception as e:
                print(f"[HINDSIGHT] ⚠️ Could not initialize Hindsight Cloud client: {e}. Using resilient local bank.")
                self.client = None
        else:
            print(f"[HINDSIGHT] Initialized in Hybrid Local Mode (Bank: {self.bank_id})")

        self._ensure_local_bank()

    def _ensure_local_bank(self):
        """Ensures the local bank file exists with initial high-value seed memories."""
        if not LOCAL_BANK_FILE.exists():
            self._save_local_bank(DEFAULT_SEED_MEMORIES)
        else:
            try:
                with open(LOCAL_BANK_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if not isinstance(data, list) or len(data) == 0:
                        self._save_local_bank(DEFAULT_SEED_MEMORIES)
            except Exception:
                self._save_local_bank(DEFAULT_SEED_MEMORIES)

    def _load_local_bank(self) -> List[Dict[str, Any]]:
        try:
            with open(LOCAL_BANK_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return DEFAULT_SEED_MEMORIES.copy()

    def _save_local_bank(self, memories: List[Dict[str, Any]]):
        try:
            with open(LOCAL_BANK_FILE, "w", encoding="utf-8") as f:
                json.dump(memories, f, indent=2)
        except Exception as e:
            print(f"[HINDSIGHT] Error writing to local bank: {e}")

    def is_cloud_connected(self) -> bool:
        return self.client is not None and bool(self.api_key)

    def get_status(self) -> Dict[str, Any]:
        memories = self._load_local_bank()
        categories: Dict[str, int] = {}
        for m in memories:
            cat = m.get("category", "General")
            categories[cat] = categories.get(cat, 0) + 1

        return {
            "connected": self.is_cloud_connected(),
            "mode": "Hindsight Cloud (Vectorize)" if self.is_cloud_connected() else "Hindsight Autonomous Engine (Local Bank)",
            "bank_id": self.bank_id,
            "base_url": self.base_url,
            "total_memories": len(memories),
            "categories": categories,
            "supported_operations": ["Recall", "Retain", "Reflect", "Teach"]
        }

    def recall(self, query: str, bank_id: Optional[str] = None, top_k: int = 4) -> List[Dict[str, Any]]:
        """
        Recall relevant historical precedents, policies, and approved exceptions.
        """
        active_bank = bank_id or self.bank_id
        results: List[Dict[str, Any]] = []

        # 1. Try Cloud Hindsight if configured
        if self.client:
            try:
                cloud_res = self.client.recall(bank_id=active_bank, query=query)
                if cloud_res and hasattr(cloud_res, "results"):
                    for item in cloud_res.results[:top_k]:
                        results.append({
                            "id": getattr(item, "id", str(uuid.uuid4())),
                            "bank_id": active_bank,
                            "content": getattr(item, "text", str(item)),
                            "category": "Cloud Memory",
                            "tags": getattr(item, "tags", []),
                            "source_doc": getattr(item, "document_id", "Hindsight Cloud"),
                            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                            "confidence": round(float(getattr(item, "score", 0.90)), 2)
                        })
            except Exception as e:
                print(f"[HINDSIGHT] Cloud recall warning: {e}. Falling back to local bank.")

        # 2. Local semantic scoring and recall
        local_memories = self._load_local_bank()
        query_words = set(query.lower().replace(",", " ").replace(".", " ").replace(";", " ").split())
        scored: List[tuple] = []

        for m in local_memories:
            content_lower = m.get("content", "").lower()
            tags_lower = [t.lower() for t in m.get("tags", [])]
            category_lower = m.get("category", "").lower()

            # Calculate match score based on keyword overlaps and tag weight
            match_score = 0.0
            for w in query_words:
                if len(w) <= 2:
                    continue
                if w in tags_lower:
                    match_score += 0.35
                if w in category_lower:
                    match_score += 0.25
                if w in content_lower:
                    match_score += 0.15

            # If query specifically mentions entity or clause (e.g. "Acme Corp", "liability", "indemnification")
            for t in tags_lower:
                if t in query.lower():
                    match_score += 0.40

            if match_score > 0.15:
                # Normalize confidence to 0.70 - 0.99
                calc_confidence = min(0.99, max(0.65, 0.60 + (match_score * 0.15)))
                item_copy = m.copy()
                item_copy["confidence"] = round(calc_confidence, 2)
                scored.append((match_score, item_copy))

        scored.sort(key=lambda x: x[0], reverse=True)
        top_local = [item for _, item in scored[:top_k]]

        # Merge with cloud results, deduplicating
        seen_texts = set()
        final_list = []
        for r in results + top_local:
            summary_snippet = r["content"][:60]
            if summary_snippet not in seen_texts:
                seen_texts.add(summary_snippet)
                final_list.append(r)

        return final_list[:top_k]

    def retain(
        self,
        content: str,
        category: str = "Learned Precedent",
        tags: Optional[List[str]] = None,
        source_doc: Optional[str] = None,
        bank_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Retain a new memory item into Hindsight.
        """
        active_bank = bank_id or self.bank_id
        mem_id = f"mem_{uuid.uuid4().hex[:8]}"
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        tags_list = tags or []

        # 1. Cloud Retain if active
        cloud_retained = False
        if self.client:
            try:
                self.client.retain(
                    bank_id=active_bank,
                    content=content,
                    tags=tags_list,
                    metadata={**(metadata or {}), "category": category, "source_doc": source_doc or "DocPilot"}
                )
                cloud_retained = True
            except Exception as e:
                print(f"[HINDSIGHT] Cloud retain warning: {e}")

        # 2. Local Bank Retain
        new_memory = {
            "id": mem_id,
            "bank_id": active_bank,
            "category": category,
            "content": content,
            "tags": tags_list,
            "source_doc": source_doc or "User Input",
            "timestamp": timestamp,
            "confidence": 0.95,
            "cloud_synced": cloud_retained
        }

        local_memories = self._load_local_bank()
        local_memories.insert(0, new_memory)
        self._save_local_bank(local_memories)

        print(f"[HINDSIGHT] ✅ Retained new memory [{mem_id}]: '{content[:70]}...'")
        return new_memory

    def list_memories(self, bank_id: Optional[str] = None, search: Optional[str] = None) -> List[Dict[str, Any]]:
        memories = self._load_local_bank()
        if not search:
            return memories
        search_lower = search.lower()
        return [
            m for m in memories
            if search_lower in m.get("content", "").lower()
            or any(search_lower in t.lower() for t in m.get("tags", []))
            or search_lower in m.get("category", "").lower()
        ]

    def reset_bank(self) -> List[Dict[str, Any]]:
        """Reset bank to pristine demo seed state."""
        self._save_local_bank(DEFAULT_SEED_MEMORIES)
        return DEFAULT_SEED_MEMORIES.copy()

# Singleton instance
hindsight_service = HindsightService()
