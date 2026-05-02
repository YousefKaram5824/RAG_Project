# =============================================================================
# controllers/DataController.py — File Validation Controller
# =============================================================================
# PURPOSE:
#   Validates incoming file uploads BEFORE writing anything to disk.
#   Enforces two rules from config:
#     1. FILE_ALLOWED_EXTENSIONS — only PDF and plain text accepted
#     2. FILE_MAX_SIZE_MB        — reject files that are too large
#
# CALLED BY: routes/data.py → POST /api/data/upload/{project_id}
#
# TEAM NOTE (Pair A — Member 2):
#   This is the first line of defence for bad uploads.
#   Return a clear HTTPException with status 400 so the client knows why
#   the upload was rejected. Do NOT silently drop the file.
# =============================================================================

from fastapi import UploadFile, HTTPException
from controllers.BaseController import BaseController


class DataController(BaseController):
    """
    Handles all validation logic for uploaded files.
    Inherits path utilities and settings from BaseController.
    """

    def __init__(self):
        super().__init__()

    def validate_file(self, file: UploadFile) -> bool:
        """
        Validates that the uploaded file:
          - Has an allowed MIME type (e.g. "application/pdf", "text/plain")
          - Does not exceed the configured max size in MB

        Args:
            file: The FastAPI UploadFile object from the request

        Returns:
            True if valid

        Raises:
            HTTPException 400 if the MIME type is not allowed
            HTTPException 413 if the file is too large

        TODO (Pair A):
            - Implement MIME type check against self.app_settings.FILE_ALLOWED_EXTENSIONS
            - Implement size check against self.app_settings.FILE_MAX_SIZE_MB
            - Raise appropriate HTTPExceptions with descriptive messages
        """
        # ── Step 1: Check MIME type ────────────────────────────────────────
        # file.content_type gives the MIME type string e.g. "application/pdf"
        # Compare against self.app_settings.FILE_ALLOWED_EXTENSIONS list
        # Raise HTTPException(status_code=400, detail="File type not allowed") if invalid

        # TODO: implement MIME type validation here
        pass

        # ── Step 2: Check file size ────────────────────────────────────────
        # file.size gives the byte count (may be None for streaming uploads)
        # Convert FILE_MAX_SIZE_MB to bytes: max_bytes = MB * 1024 * 1024
        # Raise HTTPException(status_code=413, detail="File too large") if exceeded

        # TODO: implement size validation here
        pass

        return True
