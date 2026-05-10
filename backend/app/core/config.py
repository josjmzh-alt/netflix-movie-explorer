import os


def _bool_from_env(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


def _int_from_env(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


class Settings:
    google_drive_scopes = ["https://www.googleapis.com/auth/drive.readonly"]

    credentials_file = os.getenv("CREDENTIALS_PATH", "credentials/credentials.json")
    token_file = os.getenv("TOKEN_PATH", "credentials/token.json")

    backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")

    drive_root_folder_id = os.getenv(
        "DRIVE_ROOT_FOLDER_ID",
        "1Z-Bqt69UgrGkwo0ArjHaNrA7uUmUm2r6",
    )
    debug_drive_logs = _bool_from_env("DEBUG_DRIVE_LOGS", default=False)
    drive_worker_count = max(1, _int_from_env("DRIVE_WORKER_COUNT", default=8))
    drive_page_size = min(1000, max(1, _int_from_env("DRIVE_PAGE_SIZE", default=1000)))

    @property
    def redirect_uri(self) -> str:
        return f"{self.backend_url}/auth/callback"


settings = Settings()
