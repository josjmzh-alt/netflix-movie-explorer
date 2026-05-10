import io
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import List

from googleapiclient.http import MediaIoBaseDownload

from app.core.config import settings
from app.core.structured_log import log_event
from app.services.drive_auth import get_drive_service, log_authenticated_user
from app.services.movie_parser import parse_json_file

FOLDER_MIME_TYPE = "application/vnd.google-apps.folder"
JSON_MIME_TYPE = "application/json"
_thread_local = threading.local()


@dataclass(frozen=True)
class DriveJsonFile:
    id: str
    name: str
    parent_folder_id: str
    depth: int


@dataclass(frozen=True)
class DriveFolder:
    id: str
    name: str
    depth: int


def _worker_drive_service():
    service = getattr(_thread_local, "drive_service", None)
    if service is None:
        service = get_drive_service()
        _thread_local.drive_service = service
    return service


def _download_file(service, file_id: str, file_name: str) -> str:
    """Download a Drive file and return its contents as a UTF-8 string."""
    log_event("drive_file_download_start", debug=True, file_id=file_id, file_name=file_name)
    request = service.files().get_media(fileId=file_id, supportsAllDrives=True)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    content = fh.getvalue().decode("utf-8", errors="ignore")
    log_event(
        "drive_file_download_complete",
        debug=True,
        file_id=file_id,
        file_name=file_name,
        byte_count=len(content.encode("utf-8")),
    )
    return content


def _list_folder(folder: DriveFolder) -> tuple[List[DriveJsonFile], List[DriveFolder]]:
    service = _worker_drive_service()
    files: List[DriveJsonFile] = []
    folders: List[DriveFolder] = []
    page_token = None
    page_number = 0

    log_event(
        "drive_folder_list_start",
        debug=True,
        folder_id=folder.id,
        folder_name=folder.name,
        depth=folder.depth,
    )

    while True:
        page_number += 1
        response = (
            service.files()
            .list(
                q=f"'{folder.id}' in parents and trashed=false",
                fields="nextPageToken, files(id, name, mimeType)",
                pageToken=page_token,
                pageSize=settings.drive_page_size,
                includeItemsFromAllDrives=True,
                supportsAllDrives=True,
            )
            .execute()
        )
        items = response.get("files", [])
        log_event(
            "drive_folder_page",
            debug=True,
            folder_id=folder.id,
            depth=folder.depth,
            page_number=page_number,
            item_count=len(items),
            has_next_page=bool(response.get("nextPageToken")),
        )

        for item in items:
            mime = item.get("mimeType", "")
            name = item.get("name", "")
            item_id = item.get("id", "")

            log_event(
                "drive_item_seen",
                debug=True,
                parent_folder_id=folder.id,
                depth=folder.depth,
                item_id=item_id,
                item_name=name,
                mime_type=mime,
            )

            if mime == FOLDER_MIME_TYPE:
                log_event(
                    "drive_folder_recurse",
                    debug=True,
                    parent_folder_id=folder.id,
                    folder_id=item_id,
                    folder_name=name,
                    depth=folder.depth,
                )
                folders.append(DriveFolder(id=item_id, name=name, depth=folder.depth + 1))
            elif name.lower().endswith(".json") or mime == JSON_MIME_TYPE:
                log_event(
                    "drive_json_candidate",
                    debug=True,
                    parent_folder_id=folder.id,
                    depth=folder.depth,
                    file_id=item_id,
                    file_name=name,
                    mime_type=mime,
                )
                files.append(
                    DriveJsonFile(
                        id=item_id,
                        name=name,
                        parent_folder_id=folder.id,
                        depth=folder.depth,
                    )
                )
            else:
                log_event(
                    "drive_item_skipped",
                    debug=True,
                    parent_folder_id=folder.id,
                    depth=folder.depth,
                    item_id=item_id,
                    item_name=name,
                    mime_type=mime,
                    reason="not_folder_or_json",
                )

        page_token = response.get("nextPageToken")
        if not page_token:
            break

    log_event(
        "drive_folder_list_complete",
        debug=True,
        folder_id=folder.id,
        folder_name=folder.name,
        depth=folder.depth,
        child_folder_count=len(folders),
        json_file_count=len(files),
    )
    return files, folders


def discover_json_files(root_folder_id: str) -> List[DriveJsonFile]:
    """Walk a Drive folder tree concurrently and collect JSON file references."""
    root = DriveFolder(id=root_folder_id, name="root", depth=0)
    discovered_files: List[DriveJsonFile] = []

    log_event(
        "drive_discovery_start",
        root_folder_id=root_folder_id,
        worker_count=settings.drive_worker_count,
        page_size=settings.drive_page_size,
    )

    with ThreadPoolExecutor(max_workers=settings.drive_worker_count) as executor:
        pending = [executor.submit(_list_folder, root)]
        while pending:
            next_pending = []
            for future in as_completed(pending):
                files, folders = future.result()
                discovered_files.extend(files)
                for folder in folders:
                    next_pending.append(executor.submit(_list_folder, folder))
            pending = next_pending

    log_event(
        "drive_discovery_complete",
        json_file_count=len(discovered_files),
    )
    return discovered_files


def _process_json_file(file: DriveJsonFile) -> List[dict]:
    service = _worker_drive_service()
    try:
        content = _download_file(service, file.id, file.name)
        movies = parse_json_file(content, file.name)
        log_event(
            "drive_json_parsed",
            debug=True,
            file_id=file.id,
            file_name=file.name,
            movie_count=len(movies),
        )
        return movies
    except Exception as exc:
        log_event(
            "drive_json_failed",
            file_id=file.id,
            file_name=file.name,
            error=str(exc),
        )
        return []


def load_json_files(files: List[DriveJsonFile]) -> List[dict]:
    if not files:
        return []

    worker_count = min(settings.drive_worker_count, len(files))
    movies: List[dict] = []
    log_event(
        "drive_json_processing_start",
        file_count=len(files),
        worker_count=worker_count,
    )

    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        futures = [executor.submit(_process_json_file, file) for file in files]
        for future in as_completed(futures):
            movies.extend(future.result())

    log_event(
        "drive_json_processing_complete",
        file_count=len(files),
        movie_count=len(movies),
    )
    return movies


def log_root_folder_metadata(service, folder_id: str) -> None:
    """Log metadata for the configured root folder before traversal."""
    try:
        folder = (
            service.files()
            .get(
                fileId=folder_id,
                fields="id, name, mimeType, driveId, parents, trashed",
                supportsAllDrives=True,
            )
            .execute()
        )
        log_event("drive_root_metadata", debug=True, **folder)
    except Exception as exc:
        log_event("drive_root_metadata_error", debug=True, folder_id=folder_id, error=str(exc))


def load_movies_from_drive() -> List[dict]:
    """Authenticate, traverse the root Drive folder, and return parsed movies."""
    log_event("drive_load_start", root_folder_id=settings.drive_root_folder_id)
    print("Authenticating with Google Drive...")
    service = get_drive_service()
    log_authenticated_user(service)
    log_root_folder_metadata(service, settings.drive_root_folder_id)
    print(f"Traversing folder: {settings.drive_root_folder_id}")
    files = discover_json_files(settings.drive_root_folder_id)
    movies = load_json_files(files)
    log_event("drive_load_complete", root_folder_id=settings.drive_root_folder_id, movie_count=len(movies))
    print(f"Done. {len(movies)} movies loaded")
    return movies
