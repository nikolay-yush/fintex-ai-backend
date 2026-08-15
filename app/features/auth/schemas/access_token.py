from pydantic import BaseModel, Field


class AccessTokenResponse(BaseModel):
    access_token: str = Field(..., min_length=8, description="Access token")