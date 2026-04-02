"""
Smoke tests for the SDLC Automation Copilot backend.
Run with:  cd backend && python -m pytest tests/ -v
"""

import importlib
import pytest


# ── 1. Model import test ────────────────────────────────────────────────
def test_models_import():
    """Verify that all SQLAlchemy models can be imported without errors."""
    models = importlib.import_module("app.models")
    assert hasattr(models, "User"), "User model missing"
    assert hasattr(models, "Document"), "Document model missing"
    assert hasattr(models, "ChatSession"), "ChatSession model missing"
    assert hasattr(models, "ChatMessage"), "ChatMessage model missing"


# ── 2. Table creation test ──────────────────────────────────────────────
def test_tables_create():
    """Verify all tables can be created in an in-memory SQLite DB."""
    from sqlalchemy import create_engine, inspect
    from app.models import Base

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)

    inspector = inspect(engine)
    table_names = inspector.get_table_names()

    assert "users" in table_names
    assert "documents" in table_names
    assert "chat_sessions" in table_names
    assert "chat_messages" in table_names


# ── 3. User model fields test ──────────────────────────────────────────
def test_user_has_required_columns():
    """Verify the User model has all SAD-required columns."""
    from sqlalchemy import inspect as sa_inspect
    from app.models import User

    columns = {c.key for c in sa_inspect(User).mapper.column_attrs}
    required = {"id", "username", "email", "hashed_password", "role", "created_at"}
    assert required.issubset(columns), f"Missing columns: {required - columns}"


# ── 4. Document model fields test ──────────────────────────────────────
def test_document_has_required_columns():
    """Verify the Document model has all SAD-required columns."""
    from sqlalchemy import inspect as sa_inspect
    from app.models import Document

    columns = {c.key for c in sa_inspect(Document).mapper.column_attrs}
    required = {"id", "filename", "file_path", "file_size", "file_type", "upload_date", "status", "metadata_json"}
    assert required.issubset(columns), f"Missing columns: {required - columns}"
