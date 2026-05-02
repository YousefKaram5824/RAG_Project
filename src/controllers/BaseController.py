# =============================================================================
# controllers/BaseController.py — Base Controller (Parent Class)
# =============================================================================
# PURPOSE:
#   Root class for ALL controllers in the project.
#   Provides shared utilities that every controller needs:
#     - Access to app settings (config values)
#     - Resolved file system paths (where uploads live, where DB lives)
#
# PATTERN USED: Template Method
#   Common setup (settings, paths) lives here.
#   Child controllers (Data, File, Process, Nlp) add their own behaviour.
#
# CHILDREN:
#   DataController, FileController, ProcessController, NlpController
#   All inherit from BaseController and gain its attributes for free.
#
# TEAM NOTE (Ahmed — Phase 0):
#   Build this FIRST before any other controller. Every teammate's file
#   imports from here, so breaking changes here break everything.
# =============================================================================

import os
from helpers.config import Settings, get_settings


class BaseController:
    """
    Parent controller. Instantiated once per request via FastAPI Depends().
    """

    def __init__(self, app_settings: Settings = None):
        # If no settings are injected (e.g. in unit tests), create defaults
        self.app_settings = app_settings or get_settings()

        # ── Path resolution ────────────────────────────────────────────────
        # __file__ = .../src/controllers/BaseController.py
        # base_dir = .../src/
        self.base_dir = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )

        # Where uploaded project files are stored: src/assets/files/<project_id>/
        self.files_dir = os.path.join(self.base_dir, "assets", "files")

        # Where Qdrant persists its data on disk
        self.db_dir = os.path.join(self.base_dir, self.app_settings.VECTOR_DB_PATH)

    def get_files_dir(self, project_id: str) -> str:
        """
        Returns the absolute path for a specific project's upload folder.
        Creates the folder if it doesn't exist yet.

        Called by: FileController.get_file_path()
        """
        project_dir = os.path.join(self.files_dir, project_id)
        os.makedirs(project_dir, exist_ok=True)
        return project_dir

    def get_db_path(self) -> str:
        """
        Returns the absolute path for Qdrant's local storage directory.
        Called by: VectorDBFactory when initialising QDrantDB.
        """
        os.makedirs(self.db_dir, exist_ok=True)
        return self.db_dir
