import ipaddress
import re
import uuid
from datetime import datetime, timezone
from urllib.parse import urlparse
from typing import List, Tuple, Optional
from ..models.schemas import (
    UrlAnalyzeRequest,
    UrlAnalyzeResponse,
    DomainDetails,
    Indicator,
    RiskLevel,
    Severity,
)

DISCLAIMER = (
    "This is a preliminary risk assessment based on automated pattern detection, "
    "not a security guarantee. Always verify consequential requests through official, "
    "independent channels."
)

POPULAR_BRANDS = [
    "paypal", "google", "microsoft", "apple", "amazon", "netflix",
    "chase", "bankofamerica", "wellsfargo", "citibank", "facebook",
    "instagram", "dropbox", "docuSign", "coinbase", "binance",
]

SUSPICIOUS_TLDS = {
    "tk", "ml", "ga", "cf", "gq", "top", "work", "click",
    "buzz", "country", "stream", "loan", "cam", "fit", "surf",
}

SENSITIVE_PATH_KEYWORDS = [
    "login", "signin", "sign-in", "log-in", "verify", "verification",
    "account", "update", "banking", "authenticate", "password", "reset", "wallet",
]

LOOKALIKE_MAPPINGS = [
    ("paypa1", "paypal"),
    ("g00gle", "google"),
    ("micros0ft", "microsoft"),
    ("app1e", "apple"),
    ("arnazon", "amazon"),
    ("netf1ix", "netflix"),
    ("faceb00k", "facebook"),
    ("wellsfarg0", "wellsfargo"),
]


def analyze_url_content(payload: UrlAnalyzeRequest) -> UrlAnalyzeResponse:
    raw_url = payload.url.strip()
    context = (payload.context or "").strip()

    if not (raw_url.startswith("http://") or raw_url.startswith("https://")):
        raw_url = f"https://{raw_url}"

    parsed = urlparse(raw_url)
    hostname = (parsed.hostname or "").lower()
    port = parsed.port
    path = parsed.path.lower()
    query = parsed.query.lower()
    scheme = parsed.scheme.lower()

    is_ip = False
    try:
        ipaddress.ip_address(hostname)
        is_ip = True
    except ValueError:
        is_ip = False

    parts = hostname.split(".")
    tld = parts[-1] if len(parts) > 1 and not is_ip else ""
    subdomains = parts[:-2] if len(parts) > 2 and not is_ip else []
    apex_domain = ".".join(parts[-2:]) if len(parts) >= 2 and not is_ip else hostname

    has_homoglyphs = False
    indicators: List[Indicator] = []

    if is_ip:
        indicators.append(
            Indicator(
                category="network_infrastructure",
                signal="Raw IP Address Hostname",
                severity=Severity.CRITICAL,
                explanation="Legitimate web portals use registered domain names. Bare IP address hosts are heavily favored by attackers to circumvent domain reputation systems.",
                matched_text=hostname,
            )
        )

    if parsed.username or parsed.password:
        indicators.append(
            Indicator(
                category="url_syntax",
                signal="Embedded URL User Credentials",
                severity=Severity.CRITICAL,
                explanation="URLs containing embedded usernames or passwords ('@' syntax) are frequently used in phishing attacks to obscure the true destination hostname.",
                matched_text=f"{parsed.username}@{hostname}",
            )
        )

    if "xn--" in hostname:
        has_homoglyphs = True
        indicators.append(
            Indicator(
                category="homoglyph",
                signal="Internationalized Domain (Punycode)",
                severity=Severity.HIGH,
                explanation="The domain uses Punycode encoding ('xn--'), which can be used to display Cyrillic or Greek look-alike characters that deceive human eyes into reading a trusted brand name.",
                matched_text=hostname,
            )
        )

    for lookalike, genuine in LOOKALIKE_MAPPINGS:
        if lookalike in hostname:
            has_homoglyphs = True
            indicators.append(
                Indicator(
                    category="typosquatting",
                    signal="Brand Typosquatting / Character Substitution",
                    severity=Severity.CRITICAL,
                    explanation=f"The domain name appears to substitute numbers or look-alike glyphs ('{lookalike}') to deceptively imitate '{genuine}'.",
                    matched_text=lookalike,
                )
            )

    if not is_ip:
        for brand in POPULAR_BRANDS:
            if brand in hostname:
                official_apex = f"{brand}.com"
                if apex_domain != official_apex and not apex_domain.endswith(f".{official_apex}"):
                    indicators.append(
                        Indicator(
                            category="subdomain_deception",
                            signal=f"Deceptive {brand.capitalize()} Brand Impersonation",
                            severity=Severity.CRITICAL,
                            explanation=f"The brand name '{brand}' appears in the hostname, but the registered root domain is '{apex_domain}', indicating a brand spoofing lure.",
                            matched_text=hostname,
                        )
                    )

    if tld in SUSPICIOUS_TLDS:
        indicators.append(
            Indicator(
                category="tld_reputation",
                signal=f"High-Risk Top-Level Domain (.{tld})",
                severity=Severity.HIGH,
                explanation=f"The domain utilizes the '.{tld}' top-level domain, which has a statistically elevated association with temporary spam and phishing campaigns.",
                matched_text=f".{tld}",
            )
        )

    has_sensitive_keyword = any(kw in path or kw in query for kw in SENSITIVE_PATH_KEYWORDS)
    if scheme == "http":
        severity = Severity.HIGH if has_sensitive_keyword else Severity.MEDIUM
        indicators.append(
            Indicator(
                category="protocol_security",
                signal="Unencrypted HTTP Connection",
                severity=severity,
                explanation="The connection does not employ HTTPS encryption. Any credentials, session cookies, or personal data transmitted over it can be intercepted.",
                matched_text=raw_url[:15],
            )
        )

    if len(subdomains) >= 3:
        indicators.append(
            Indicator(
                category="domain_structure",
                signal="Excessive Subdomain Depth",
                severity=Severity.MEDIUM,
                explanation="Chaining three or more subdomain levels is a technique frequently used to push the actual registered domain out of view on mobile screens.",
                matched_text=".".join(subdomains),
            )
        )

    if has_sensitive_keyword and (is_ip or tld in SUSPICIOUS_TLDS or len(subdomains) > 0 or has_homoglyphs):
        matched_kw = next(kw for kw in SENSITIVE_PATH_KEYWORDS if kw in path or kw in query)
        indicators.append(
            Indicator(
                category="credential_pathway",
                signal="Sensitive Authentication / Account Path",
                severity=Severity.HIGH,
                explanation=f"The URL pathway targets sensitive account operations ('{matched_kw}') on a domain with existing suspicious structural flags.",
                matched_text=matched_kw,
            )
        )

    critical_count = sum(1 for i in indicators if i.severity == Severity.CRITICAL)
    high_count = sum(1 for i in indicators if i.severity == Severity.HIGH)
    medium_count = sum(1 for i in indicators if i.severity == Severity.MEDIUM)

    if not hostname or len(hostname) < 3:
        risk_level = RiskLevel.NEEDS_REVIEW
        confidence_score = 0.50
        summary = "The provided URL appears incomplete or malformed and cannot be reliably evaluated."
    elif critical_count >= 1 or high_count >= 2:
        risk_level = RiskLevel.HIGH
        confidence_score = min(0.98, 0.85 + (critical_count * 0.06) + (high_count * 0.04))
        summary = (
            "High risk of deceptive or malicious activity detected. The URL displays characteristics "
            "typical of credential phishing, domain typosquatting, or host spoofing."
        )
    elif high_count == 1 or medium_count >= 2:
        risk_level = RiskLevel.MEDIUM
        confidence_score = min(0.88, 0.75 + (high_count * 0.08) + (medium_count * 0.04))
        summary = (
            "Suspicious characteristics were identified in the URL structure or security configuration. "
            "Exercise caution before visiting this address."
        )
    elif medium_count == 1:
        risk_level = RiskLevel.MEDIUM
        confidence_score = 0.75
        summary = "A potential anomaly was detected. Verify the destination domain before entering any information."
    else:
        risk_level = RiskLevel.LOW
        confidence_score = 0.92
        summary = (
            "No prominent phishing, homoglyph, or deceptive infrastructure markers were found for this URL. "
            "Standard security diligence still applies."
        )

    recommendations: List[str] = []
    if risk_level == RiskLevel.HIGH:
        recommendations.append("Do not visit this website or input any usernames, passwords, or payment info.")
        recommendations.append(f"If you intended to reach an official service, manually navigate to their official website via a bookmark or search engine.")
        recommendations.append("Report this URL to anti-phishing protection feeds (e.g. Google Safe Browsing or PhishTank).")
    elif risk_level == RiskLevel.MEDIUM:
        recommendations.append("Carefully check the address bar in your browser to confirm the exact apex domain matches your expectations.")
        recommendations.append("Ensure the connection uses HTTPS before submitting any forms or interaction.")
    elif risk_level == RiskLevel.NEEDS_REVIEW:
        recommendations.append("Check that the URL is complete, including a valid domain and protocol.")
    else:
        recommendations.append("Ensure the URL begins with 'https://' and has a valid SSL/TLS certificate.")
        recommendations.append("Never enter sensitive credentials on sites reached through unsolicited messages.")

    domain_details = DomainDetails(
        domain=hostname,
        tld=tld if tld else None,
        subdomains=subdomains if subdomains else None,
        is_ip_address=is_ip,
        has_homoglyphs=has_homoglyphs,
    )

    return UrlAnalyzeResponse(
        analysis_id=f"url_anlz_{uuid.uuid4().hex[:12]}",
        timestamp=datetime.now(timezone.utc).isoformat(),
        target_url=payload.url,
        normalized_url=f"{scheme}://{hostname}{parsed.path}" if hostname else payload.url,
        risk_level=risk_level,
        confidence_score=round(confidence_score, 2),
        assessment_disclaimer=DISCLAIMER,
        domain_details=domain_details,
        summary=summary,
        indicators=indicators,
        recommendations=recommendations,
    )

