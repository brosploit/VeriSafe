from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    NEEDS_REVIEW = "Needs Review"


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Channel(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    CHAT = "chat"
    SOCIAL = "social"
    OTHER = "other"


class Indicator(BaseModel):
    category: str
    signal: str
    severity: Severity
    explanation: str
    matched_text: Optional[str] = None


class MessageAnalyzeRequest(BaseModel):
    message_text: str = Field(
        ...,
        min_length=1,
        max_length=50000,
        description="The raw text of the message to inspect.",
    )
    sender: Optional[str] = Field(
        None,
        max_length=255,
        description="Sender display name, phone number, or email address.",
    )
    channel: Channel = Field(
        default=Channel.OTHER,
        description="Communication channel where the message appeared.",
    )


class InputSummary(BaseModel):
    channel: Optional[str] = None
    char_count: Optional[int] = None
    detected_urls: Optional[List[str]] = None


class MessageAnalyzeResponse(BaseModel):
    analysis_id: str
    timestamp: str
    input_summary: InputSummary
    risk_level: RiskLevel
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    assessment_disclaimer: str
    summary: str
    indicators: List[Indicator]
    recommendations: List[str]


class UrlAnalyzeRequest(BaseModel):
    url: str = Field(
        ...,
        min_length=1,
        max_length=2048,
        description="Target web link (HTTP/HTTPS) to evaluate.",
    )
    context: Optional[str] = Field(
        None,
        max_length=500,
        description="Optional context where the URL was found.",
    )


class DomainDetails(BaseModel):
    domain: Optional[str] = None
    tld: Optional[str] = None
    subdomains: Optional[List[str]] = None
    is_ip_address: Optional[bool] = None
    has_homoglyphs: Optional[bool] = None


class UrlAnalyzeResponse(BaseModel):
    analysis_id: str
    timestamp: str
    target_url: str
    normalized_url: Optional[str] = None
    risk_level: RiskLevel
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    assessment_disclaimer: str
    domain_details: Optional[DomainDetails] = None
    summary: str
    indicators: List[Indicator]
    recommendations: List[str]


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str = "VeriSafe API"
    version: str = "0.1.0"
    timestamp: Optional[str] = None

