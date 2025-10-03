from pydantic import BaseModel, Field
from typing import Annotated, Optional
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from enum import Enum

# ==================== Enums ====================

class QueryType(str, Enum):
    """Types of legal queries supported."""
    CLAUSE_SEARCH = "clause_search"
    COMPLIANCE_CHECK = "compliance_check"
    DOCUMENT_SUMMARY = "document_summary"
    RISK_ASSESSMENT = "risk_assessment"
    GENERAL_INQUIRY = "general_inquiry"


# ==================== Pydantic Models ====================

class QueryClassifier(BaseModel):
    """Classifies the type of legal query."""
    
    query_type: QueryType = Field(
        description="Type of legal query being made"
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence score of the classification"
    )
    key_terms: list[str] = Field(
        default_factory=list,
        description="Key legal terms identified in the query"
    )


# ==================== State Management ====================

class LegalChatState(TypedDict):
    """Enhanced state for legal document review chatbot."""
    
    messages: Annotated[list, add_messages]
    query_type: Optional[str]
    document_content: Optional[str]
    document_metadata: Optional[dict]
    analysis_results: Optional[dict]
    routing_decision: Optional[str]