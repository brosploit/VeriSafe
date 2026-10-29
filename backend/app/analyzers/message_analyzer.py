import re
import uuid
from datetime import datetime, timezone
from typing import List, Tuple
from ..models.schemas import (
    MessageAnalyzeRequest,
    MessageAnalyzeResponse,
    InputSummary,
    Indicator,
    RiskLevel,
    Severity,
)

DISCLAIMER = (
    "This is a preliminary risk assessment based on automated pattern detection, "
    "not a security guarantee. Always verify consequential requests through official, "
    "independent channels."
)

URL_REGEX = re.compile(r"https?://[^\s<>\"']+|www\.[^\s<>\"']+", re.IGNORECASE)
IP_IN_URL_REGEX = re.compile(r"https?://(?:\d{1,3}\.){3}\d{1,3}(?::\d+)?(?:/.*)?", re.IGNORECASE)

URGENCY_PATTERNS = [
    (
        re.compile(r"\b(urgent|immediately|action required|final notice|act now|limited time|within (?:24|48|\d+) hours?|within \d+ (?:mins?|minutes?))\b", re.IGNORECASE),
        "Artificial Time Pressure",
        "High urgency wording is commonly used in social engineering attacks to induce panic and force hurried decisions.",
        Severity.HIGH,
    ),
    (
        re.compile(r"\b(account (?:has been |will be )?(?:suspended|locked|terminated|disabled|restricted|deactivated))\b", re.IGNORECASE),
        "Threat of Account Interruption",
        "Claims of impending account suspension are a frequent lure to deceive users into visiting spoofed login pages.",
        Severity.HIGH,
    ),
]

CREDENTIAL_PATTERNS = [
    (
        re.compile(r"\b(otp|one[- ]time password|passcode|security code|verification code)\b", re.IGNORECASE),
        "Sensitive OTP / Code Solicitation",
        "Legitimate institutions do not request one-time passwords (OTPs) or passcodes through inbound messages or links.",
        Severity.CRITICAL,
    ),
    (
        re.compile(r"\b(enter (?:your )?(?:password|pin|credentials)|verify (?:your )?(?:identity|account|password))\b", re.IGNORECASE),
        "Direct Credential Request",
        "Requests to enter or confirm passwords or personal identification numbers via messaging channels are high-risk indicators.",
        Severity.CRITICAL,
    ),
    (
        re.compile(r"\b(ssn|social security number|credit card number|cvv|card expiration)\b", re.IGNORECASE),
        "Personal / Financial Data Harvesting",
        "Solicitation of highly sensitive personal identity and financial coordinates is characteristic of identity theft.",
        Severity.CRITICAL,
    ),
]

FINANCIAL_PATTERNS = [
    (
        re.compile(r"\b(wire transfer|cryptocurrency|bitcoin|gift cards?|western union|moneygram)\b", re.IGNORECASE),
        "Untraceable Payment Solicitation",
        "Demands for irreversible payment methods like gift cards or cryptocurrency are standard flags in advance-fee scams.",
        Severity.HIGH,
    ),
    (
        re.compile(r"\b(won (?:a |the )?(?:lottery|prize|\$[\d,]+)|inheritance|claim your (?:reward|prize|cash)|unclaimed funds)\b", re.IGNORECASE),
        "Prize or Lottery Bait",
        "Unexpected winnings or prize claims are designed to entice recipients into paying upfront fees or disclosing data.",
        Severity.HIGH,
    ),
]

IMPERSONATION_PATTERNS = [
    (
        re.compile(r"\b(paypal|chase(?:\s+bank)?|wells fargo|bank of america|citibank|apple(?:\s+support)?|microsoft(?:\s+security)?|amazon(?:\s+support)?|netflix|irs|tax refund|usps|fedex|dhl|ups delivery)\b", re.IGNORECASE),
        "Brand or Authority Reference",
        "The message references a major brand, institution, or delivery service frequently targeted by impersonation campaigns.",
        Severity.MEDIUM,
    ),
]


def analyze_message_content(payload: MessageAnalyzeRequest) -> MessageAnalyzeResponse:
    text = payload.message_text
    sender = (payload.sender or "").strip()
    channel = payload.channel.value

    # Extract embedded URLs
    found_urls = URL_REGEX.findall(text)

    indicators: List[Indicator] = []

    # Check Urgency
    for pattern, signal, explanation, severity in URGENCY_PATTERNS:
        match = pattern.search(text)
        if match:
            indicators.append(
                Indicator(
                    category="urgency",
                    signal=signal,
                    severity=severity,
                    explanation=explanation,
                    matched_text=match.group(0),
                )
            )

    # Check Credential Solicitation
    for pattern, signal, explanation, severity in CREDENTIAL_PATTERNS:
        match = pattern.search(text)
        if match:
            indicators.append(
                Indicator(
                    category="credential_solicitation",
                    signal=signal,
                    severity=severity,
                    explanation=explanation,
                    matched_text=match.group(0),
                )
            )

    # Check Financial Scams
    for pattern, signal, explanation, severity in FINANCIAL_PATTERNS:
        match = pattern.search(text)
        if match:
            indicators.append(
                Indicator(
                    category="financial_coercion",
                    signal=signal,
                    severity=severity,
                    explanation=explanation,
                    matched_text=match.group(0),
                )
            )

    # Check Brand Impersonation in text
    for pattern, signal, explanation, severity in IMPERSONATION_PATTERNS:
        match = pattern.search(text)
        if match:
            indicators.append(
                Indicator(
                    category="sender_impersonation",
                    signal=signal,
                    severity=severity,
                    explanation=explanation,
                    matched_text=match.group(0),
                )
            )

    # Inspect Sender Address if provided
    if sender:
        sender_lower = sender.lower()
        suspicious_sender_keywords = ["security", "support", "alert", "verify", "service", "admin", "billing"]
        contains_keyword = any(kw in sender_lower for kw in suspicious_sender_keywords)
        generic_domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "proton.me", "protonmail.com"]
        uses_free_mail = any(sender_lower.endswith(f"@{dom}") for dom in generic_domains)
        if contains_keyword and uses_free_mail:
            indicators.append(
                Indicator(
                    category="sender_impersonation",
                    signal="Mismatched Official Sender",
                    severity=Severity.HIGH,
                    explanation=f"Sender claims institutional authority ('{sender}') but sends from a public/free email provider.",
                    matched_text=sender,
                )
            )

    # Inspect embedded URLs
    for url in found_urls:
        if IP_IN_URL_REGEX.search(url):
            indicators.append(
                Indicator(
                    category="embedded_url",
                    signal="IP-Based Embedded Link",
                    severity=Severity.CRITICAL,
                    explanation="An embedded link utilizes a raw numeric IP address rather than a registered domain name, a hallmark of malicious infrastructure.",
                    matched_text=url,
                )
            )
        elif url.lower().startswith("http://"):
            indicators.append(
                Indicator(
                    category="embedded_url",
                    signal="Unencrypted HTTP Link",
                    severity=Severity.MEDIUM,
                    explanation="The embedded link does not enforce HTTPS encryption, leaving data transmitted across it vulnerable to interception.",
                    matched_text=url,
                )
            )

    # Calculate Risk Level & Confidence
    critical_count = sum(1 for i in indicators if i.severity == Severity.CRITICAL)
    high_count = sum(1 for i in indicators if i.severity == Severity.HIGH)
    medium_count = sum(1 for i in indicators if i.severity == Severity.MEDIUM)

    word_count = len(text.strip().split())

    if word_count < 3 and not found_urls:
        risk_level = RiskLevel.NEEDS_REVIEW
        confidence_score = 0.50
        summary = "The provided message is too brief or ambiguous to perform a conclusive heuristic evaluation."
    elif critical_count >= 1 or (high_count >= 1 and (medium_count >= 1 or len(found_urls) >= 1)):
        risk_level = RiskLevel.HIGH
        confidence_score = min(0.96, 0.82 + (critical_count * 0.06) + (high_count * 0.04))
        summary = (
            "This message exhibits strong warning signs of social engineering or phishing, "
            "including urgent pressure, credential solicitation, or suspicious link structures."
        )
    elif high_count >= 1 or medium_count >= 2:
        risk_level = RiskLevel.MEDIUM
        confidence_score = min(0.88, 0.72 + (high_count * 0.08) + (medium_count * 0.05))
        summary = (
            "Several anomalous indicators were detected. The communication warrants heightened scrutiny "
            "before any links are clicked or information is shared."
        )
    elif medium_count == 1:
        risk_level = RiskLevel.MEDIUM
        confidence_score = 0.74
        summary = "A potential risk indicator was identified. Proceed with normal caution and verify sender identity."
    else:
        risk_level = RiskLevel.LOW
        confidence_score = 0.88
        summary = "No obvious hallmarks of phishing, aggressive coercion, or credential harvesting were detected in this message."

    # Build Recommendations
    recommendations: List[str] = []
    if critical_count > 0 or high_count > 0:
        recommendations.append("Do not click links, open attachments, or reply with passwords, OTPs, or financial details.")
        recommendations.append("Contact the organization directly using a phone number from your official billing statement or their verified website.")
        recommendations.append("Flag or report the communication as spam or phishing inside your email or messaging client.")
    elif risk_level == RiskLevel.MEDIUM:
        recommendations.append("Inspect the sender address and any embedded links closely before taking action.")
        recommendations.append("Do not enter login credentials on any page reached directly through this communication.")
        recommendations.append("Confirm the request through an independent communication channel if uncertain.")
    elif risk_level == RiskLevel.NEEDS_REVIEW:
        recommendations.append("Provide a larger snippet or additional message context for a more comprehensive assessment.")
        recommendations.append("Avoid interacting with any unverified links or contacts.")
    else:
        recommendations.append("Maintain standard digital safety precautions.")
        recommendations.append("Always verify unexpected requests involving payments or account modifications through trusted channels.")

    return MessageAnalyzeResponse(
        analysis_id=f"msg_anlz_{uuid.uuid4().hex[:12]}",
        timestamp=datetime.now(timezone.utc).isoformat(),
        input_summary=InputSummary(
            channel=channel,
            char_count=len(text),
            detected_urls=found_urls,
        ),
        risk_level=risk_level,
        confidence_score=round(confidence_score, 2),
        assessment_disclaimer=DISCLAIMER,
        summary=summary,
        indicators=indicators,
        recommendations=recommendations,
    )

