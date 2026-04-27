"""
Role-Based Access Control (RBAC) utilities.
Implements the full RBAC matrix from SAD 5.2
"""
from typing import Dict, List, Tuple
from enum import Enum


class Permission(str, Enum):
    """Permission levels for RBAC matrix"""
    FULL = "full"  # ✓ Full access
    PARTIAL = "partial"  # ○ Partial/summary access
    DENIED = "denied"  # ✗ No access


class Feature(str, Enum):
    """Features that can be controlled by RBAC"""
    UPLOAD_DOCUMENTS = "upload_documents"
    APPLY_PRIORITY_TAG = "apply_priority_tag"
    GENERATE_BRD = "generate_brd"
    GENERATE_FRD = "generate_frd"
    GENERATE_TEST_PLAN = "generate_test_plan"
    GENERATE_API_SPEC = "generate_api_spec"
    GENERATE_TRACEABILITY_MATRIX = "generate_traceability_matrix"
    VIEW_OTHER_SESSIONS = "view_other_sessions"
    EXPORT_MARKDOWN = "export_markdown"


# RBAC Matrix from SAD §5.2
RBAC_MATRIX: Dict[Feature, Dict[str, Permission]] = {
    Feature.UPLOAD_DOCUMENTS: {
        "Business Analyst (BA)": Permission.FULL,
        "Functional BA (FBA)": Permission.FULL,
        "QA / Tester": Permission.FULL,
    },
    Feature.APPLY_PRIORITY_TAG: {
        "Business Analyst (BA)": Permission.DENIED,
        "Functional BA (FBA)": Permission.DENIED,
        "QA / Tester": Permission.FULL,
    },
    Feature.GENERATE_BRD: {
        "Business Analyst (BA)": Permission.FULL,
        "Functional BA (FBA)": Permission.PARTIAL,  # Summary only
        "QA / Tester": Permission.DENIED,
    },
    Feature.GENERATE_FRD: {
        "Business Analyst (BA)": Permission.DENIED,
        "Functional BA (FBA)": Permission.FULL,
        "QA / Tester": Permission.PARTIAL,  # Reference only
    },
    Feature.GENERATE_TEST_PLAN: {
        "Business Analyst (BA)": Permission.DENIED,
        "Functional BA (FBA)": Permission.DENIED,
        "QA / Tester": Permission.FULL,
    },
    Feature.GENERATE_API_SPEC: {
        "Business Analyst (BA)": Permission.DENIED,
        "Functional BA (FBA)": Permission.FULL,
        "QA / Tester": Permission.DENIED,
    },
    Feature.GENERATE_TRACEABILITY_MATRIX: {
        "Business Analyst (BA)": Permission.PARTIAL,
        "Functional BA (FBA)": Permission.PARTIAL,
        "QA / Tester": Permission.FULL,
    },
    Feature.VIEW_OTHER_SESSIONS: {
        "Business Analyst (BA)": Permission.DENIED,
        "Functional BA (FBA)": Permission.DENIED,
        "QA / Tester": Permission.DENIED,
    },
    Feature.EXPORT_MARKDOWN: {
        "Business Analyst (BA)": Permission.FULL,
        "Functional BA (FBA)": Permission.FULL,
        "QA / Tester": Permission.FULL,
    },
}


# Task type to feature mapping
TASK_TYPE_TO_FEATURE: Dict[str, Feature] = {
    "brd": Feature.GENERATE_BRD,
    "frd": Feature.GENERATE_FRD,
    "test_pack": Feature.GENERATE_TEST_PLAN,
    "api_spec": Feature.GENERATE_API_SPEC,
    "traceability_matrix": Feature.GENERATE_TRACEABILITY_MATRIX,
}


def check_permission(role: str, feature: Feature) -> Permission:
    """
    Check if a role has permission for a feature.
    
    Args:
        role: User role (e.g., "Business Analyst (BA)")
        feature: Feature to check
        
    Returns:
        Permission level (FULL, PARTIAL, or DENIED)
    """
    if feature not in RBAC_MATRIX:
        return Permission.DENIED
    
    role_permissions = RBAC_MATRIX[feature]
    return role_permissions.get(role, Permission.DENIED)


def validate_task_access(role: str, task_type: str) -> Tuple[bool, str, Permission]:
    """
    Validate if a role can perform a task type.
    
    Args:
        role: User role
        task_type: Task type (brd, frd, test_pack, etc.)
        
    Returns:
        Tuple of (is_allowed, message, permission_level)
    """
    if not task_type:
        return True, "", Permission.FULL
    
    # Map task type to feature
    feature = TASK_TYPE_TO_FEATURE.get(task_type)
    if not feature:
        return True, "", Permission.FULL
    
    # Check permission
    permission = check_permission(role, feature)
    
    if permission == Permission.DENIED:
        # Generate helpful error message
        allowed_roles = [
            role_name for role_name, perm in RBAC_MATRIX[feature].items()
            if perm in [Permission.FULL, Permission.PARTIAL]
        ]
        
        message = f"This document type is available for {', '.join(allowed_roles)} roles. Please open a new session with the appropriate role."
        return False, message, permission
    
    if permission == Permission.PARTIAL:
        # Partial access - add note to response
        if task_type == "brd" and role == "Functional BA (FBA)":
            message = "Note: As FBA, you can view BRD summaries. For full BRD generation, use Business Analyst role."
        elif task_type == "frd" and role == "QA / Tester":
            message = "Note: As QA, you can reference FRDs. For full FRD generation, use Functional BA role."
        elif task_type == "traceability_matrix" and role != "QA / Tester":
            message = "Note: Partial traceability matrix. For full matrix with test coverage, use QA role."
        else:
            message = ""
        
        return True, message, permission
    
    return True, "", permission


def can_apply_priority_tag(role: str) -> bool:
    """
    Check if role can apply priority tags to documents.
    
    Args:
        role: User role
        
    Returns:
        True if allowed, False otherwise
    """
    permission = check_permission(role, Feature.APPLY_PRIORITY_TAG)
    return permission == Permission.FULL


def get_role_capabilities(role: str) -> Dict[str, str]:
    """
    Get all capabilities for a role.
    
    Args:
        role: User role
        
    Returns:
        Dictionary of feature -> permission level
    """
    capabilities = {}
    for feature in Feature:
        permission = check_permission(role, feature)
        capabilities[feature.value] = permission.value
    
    return capabilities
