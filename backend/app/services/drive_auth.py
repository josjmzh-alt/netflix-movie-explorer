import os
from glob import glob
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

from app.core.config import settings
from app.core.structured_log import log_event

_pending_flow: Optional[Flow] = None


def _credentials_file() -> str:
    """Return the OAuth client-secret file path, supporting Google's default filename."""
    if os.path.exists(settings.credentials_file):
        return settings.credentials_file

    credentials_dir = os.path.dirname(settings.credentials_file) or "."
    candidates = sorted(glob(os.path.join(credentials_dir, "client_secret*.json")))
    if candidates:
        return candidates[0]

    raise FileNotFoundError(
        f"Google OAuth credentials file not found. Expected {settings.credentials_file} "
        f"or a client_secret*.json file in {credentials_dir}."
    )


def is_authenticated() -> bool:
    """Return True if a valid or refreshable token exists."""
    if not os.path.exists(settings.token_file):
        log_event("google_auth_status", debug=True, authenticated=False, reason="missing_token_file")
        return False
    try:
        creds = Credentials.from_authorized_user_file(
            settings.token_file,
            settings.google_drive_scopes,
        )
        if creds.valid:
            log_event("google_auth_status", debug=True, authenticated=True, reason="valid_token")
            return True
        if creds.expired and creds.refresh_token:
            log_event("google_auth_refresh_start", debug=True)
            creds.refresh(Request())
            _save_token(creds)
            log_event("google_auth_status", debug=True, authenticated=True, reason="refreshed_token")
            return True
    except Exception as exc:
        log_event("google_auth_status", debug=True, authenticated=False, reason="token_error", error=str(exc))
        pass
    log_event("google_auth_status", debug=True, authenticated=False, reason="invalid_token")
    return False


def get_auth_url() -> str:
    """Build and cache the Google OAuth consent URL."""
    global _pending_flow
    credentials_file = _credentials_file()
    log_event("google_auth_url_start", debug=True, credentials_file=credentials_file, redirect_uri=settings.redirect_uri)
    _pending_flow = Flow.from_client_secrets_file(
        credentials_file,
        scopes=settings.google_drive_scopes,
        redirect_uri=settings.redirect_uri,
    )
    auth_url, _ = _pending_flow.authorization_url(
        access_type="offline",
        prompt="consent",
    )
    log_event("google_auth_url_created", debug=True, redirect_uri=settings.redirect_uri)
    return auth_url


def complete_auth(code: str) -> None:
    """Exchange the OAuth code for tokens and persist them."""
    global _pending_flow
    log_event("google_auth_complete_start", debug=True, has_pending_flow=_pending_flow is not None)
    if _pending_flow is None:
        _pending_flow = Flow.from_client_secrets_file(
            _credentials_file(),
            scopes=settings.google_drive_scopes,
            redirect_uri=settings.redirect_uri,
        )
    _pending_flow.fetch_token(code=code)
    _save_token(_pending_flow.credentials)
    _pending_flow = None
    log_event("google_auth_complete_success", token_file=settings.token_file)


def _save_token(creds: Credentials) -> None:
    os.makedirs(os.path.dirname(settings.token_file), exist_ok=True)
    with open(settings.token_file, "w") as fh:
        fh.write(creds.to_json())
    log_event("google_auth_token_saved", debug=True, token_file=settings.token_file)


def get_drive_service():
    """Return an authenticated Drive v3 service, refreshing token if needed."""
    log_event("google_drive_service_start", debug=True, token_file=settings.token_file)
    creds = Credentials.from_authorized_user_file(
        settings.token_file,
        settings.google_drive_scopes,
    )
    if not creds.valid and creds.expired and creds.refresh_token:
        log_event("google_drive_service_refresh_start", debug=True)
        creds.refresh(Request())
        _save_token(creds)
    service = build("drive", "v3", credentials=creds)
    log_event("google_drive_service_ready", debug=True)
    return service


def log_authenticated_user(service) -> None:
    """Log the Drive user associated with the current OAuth token."""
    try:
        about = service.about().get(fields="user(emailAddress,displayName)").execute()
        user = about.get("user") or {}
        log_event(
            "google_drive_user",
            debug=True,
            email=user.get("emailAddress"),
            display_name=user.get("displayName"),
        )
    except Exception as exc:
        log_event("google_drive_user_error", debug=True, error=str(exc))
