from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class SessionCreate(BaseModel):
    """Model for creating a new session"""
    session_name: Optional[str] = Field(None, description="Optional name for the session")


class SessionResponse(BaseModel):
    """Response model for session creation"""
    session_id: str = Field(..., description="Unique session identifier")
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    created_at: datetime = Field(..., description="Session creation timestamp")


class TokenRefresh(BaseModel):
    """Model for token refresh request"""
    refresh_token: str = Field(..., description="Valid refresh token")


class TokenResponse(BaseModel):
    """Response model for token operations"""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")


class Trading212APISetup(BaseModel):
    """Model for Trading 212 API key setup"""
    api_key: str = Field(..., min_length=1, description="Trading 212 API key")
    validate_connection: bool = Field(default=True, description="Whether to validate the API key")


class Trading212APIResponse(BaseModel):
    """Response model for Trading 212 API setup"""
    status: str = Field(..., description="Setup status")
    message: str = Field(..., description="Status message")
    account_info: Optional[dict] = Field(None, description="Account information if validation successful")


class SessionInfo(BaseModel):
    """Model for session information"""
    session_id: str = Field(..., description="Session identifier")
    created_at: datetime = Field(..., description="Session creation time")
    last_activity: datetime = Field(..., description="Last activity timestamp")
    trading212_connected: bool = Field(..., description="Whether Trading 212 API is connected")
    session_name: Optional[str] = Field(None, description="Optional session name")


class APIKeyValidation(BaseModel):
    """Model for API key validation response"""
    is_valid: bool = Field(..., description="Whether the API key is valid")
    account_id: Optional[str] = Field(None, description="Account ID if valid")
    account_type: Optional[str] = Field(None, description="Account type if valid")
    error_message: Optional[str] = Field(None, description="Error message if invalid")


class SessionUpdate(BaseModel):
    """Model for updating session information"""
    session_name: Optional[str] = Field(None, description="New session name")