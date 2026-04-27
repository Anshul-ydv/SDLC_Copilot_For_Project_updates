"""
Security utilities for input validation and sanitization.
"""
import re
from typing import Tuple


# Prompt injection patterns to detect
INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions?",
    r"disregard\s+(all\s+)?(previous|prior|above)",
    r"forget\s+(all\s+)?(previous|prior|above)",
    r"system\s*:\s*you\s+are",
    r"new\s+instructions?",
    r"override\s+instructions?",
    r"reveal\s+(your\s+)?(system\s+)?prompt",
    r"show\s+(me\s+)?(your\s+)?(system\s+)?prompt",
    r"what\s+(is|are)\s+your\s+instructions?",
    r"print\s+(your\s+)?(system\s+)?prompt",
    r"output\s+(your\s+)?(system\s+)?prompt",
    r"<\s*script\s*>",  # XSS attempts
    r"javascript\s*:",
    r"on(load|error|click)\s*=",
    r"\{\{.*\}\}",  # Template injection
    r"\$\{.*\}",  # Template literal injection
]


def detect_prompt_injection(query: str) -> Tuple[bool, str]:
    """
    Detect potential prompt injection attempts.
    
    Args:
        query: User input query to check
        
    Returns:
        Tuple of (is_injection, reason)
    """
    query_lower = query.lower()
    
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, query_lower, re.IGNORECASE):
            return True, f"Potential prompt injection detected: pattern '{pattern}'"
    
    # Check for excessive special characters (potential obfuscation)
    special_char_ratio = sum(1 for c in query if not c.isalnum() and not c.isspace()) / max(len(query), 1)
    if special_char_ratio > 0.3:
        return True, "Excessive special characters detected"
    
    # Check for repeated instruction keywords
    instruction_keywords = ["ignore", "disregard", "forget", "override", "system", "prompt", "instructions"]
    keyword_count = sum(query_lower.count(keyword) for keyword in instruction_keywords)
    if keyword_count >= 3:
        return True, "Multiple instruction manipulation keywords detected"
    
    return False, ""


def sanitize_query(query: str) -> str:
    """
    Sanitize user query by removing potentially harmful content.
    
    Args:
        query: User input query
        
    Returns:
        Sanitized query string
    """
    # Remove HTML/script tags
    query = re.sub(r'<[^>]+>', '', query)
    
    # Remove template injection patterns
    query = re.sub(r'\{\{.*?\}\}', '', query)
    query = re.sub(r'\$\{.*?\}', '', query)
    
    # Remove excessive whitespace
    query = re.sub(r'\s+', ' ', query).strip()
    
    return query


def validate_query_safety(query: str) -> Tuple[bool, str]:
    """
    Validate query for safety before processing.
    
    Args:
        query: User input query
        
    Returns:
        Tuple of (is_safe, error_message)
    """
    # Check for injection
    is_injection, reason = detect_prompt_injection(query)
    if is_injection:
        return False, f"Query rejected: {reason}"
    
    # Check length
    if len(query) > 4000:
        return False, "Query exceeds maximum length of 4000 characters"
    
    if len(query.strip()) < 3:
        return False, "Query must be at least 3 characters"
    
    return True, ""
