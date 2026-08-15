from pydantic import BaseModel, Field


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., min_length=8, description="Refresh token")