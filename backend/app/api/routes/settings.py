from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_admin, require_admin_password
from app.core.security import build_totp_uri, generate_backup_codes, generate_totp_secret, verify_totp_code
from app.crud.users import set_backup_codes, set_totp_secret
from app.models.user import User
from app.schemas.totp import TotpEnableRequest, TotpEnableResponse, TotpSetupResponse, TotpStatusResponse

router = APIRouter(prefix="/settings", tags=["settings"], dependencies=[Depends(require_admin)])


@router.get("/totp", response_model=TotpStatusResponse)
def get_totp_status(user: User = Depends(require_admin)) -> TotpStatusResponse:
    return TotpStatusResponse(enabled=bool(user.totp_secret))


@router.post("/totp/setup", response_model=TotpSetupResponse)
def setup_totp(user: User = Depends(require_admin)) -> TotpSetupResponse:
    secret = generate_totp_secret()
    return TotpSetupResponse(secret=secret, otpauth_uri=build_totp_uri(secret, user.email))


@router.post("/totp/enable", response_model=TotpEnableResponse)
def enable_totp(
    payload: TotpEnableRequest, db: Session = Depends(get_db), user: User = Depends(require_admin)
) -> TotpEnableResponse:
    if not verify_totp_code(payload.secret, payload.code):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid authenticator code")
    backup_codes = generate_backup_codes()
    set_totp_secret(db, user, payload.secret)
    set_backup_codes(db, user, backup_codes)
    return TotpEnableResponse(enabled=True, backup_codes=backup_codes)


@router.post("/totp/disable", response_model=TotpStatusResponse)
def disable_totp(db: Session = Depends(get_db), user: User = Depends(require_admin_password)) -> TotpStatusResponse:
    set_totp_secret(db, user, None)
    set_backup_codes(db, user, None)
    return TotpStatusResponse(enabled=False)
