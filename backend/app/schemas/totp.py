from pydantic import BaseModel


class TotpStatusResponse(BaseModel):
    enabled: bool


class TotpSetupResponse(BaseModel):
    secret: str
    otpauth_uri: str


class TotpEnableRequest(BaseModel):
    secret: str
    code: str


class TotpEnableResponse(BaseModel):
    enabled: bool
    backup_codes: list[str]
