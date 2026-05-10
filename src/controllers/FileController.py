# =============================================================================
# controllers/FileController.py — File System Controller
# =============================================================================
# PURPOSE:
#   Manages the on-disk storage of uploaded project documents.
#   Creates per-project directories under src/assets/files/<project_id>/
#   and returns the full path where a specific file should be saved.
#
# CALLED BY:
#   routes/data.py → upload endpoint (to get the save path)
#   ProcessController → to find the file when loading it for chunking
#
# TEAM NOTE (Pair A — Member 2):
#   Keep this controller thin — it only manages paths and directories.
#   Actual file writing is done in the route using aiofiles.
#   Actual file reading is done in ProcessController using LangChain loaders.
# =============================================================================

import os
from controllers.BaseController import BaseController


class FileController(BaseController):
    """
    Provides path resolution and directory management for project files.
    """

    def __init__(self):
        super().__init__()

    def get_file_path(self, project_id: str, filename: str) -> str:
        project_dir = self.get_files_dir(project_id)
        return os.path.join(project_dir, filename)

        """
        Returns the full absolute path where an uploaded file should be stored.
        Creates the project directory if it does not exist.

        Args:
            project_id: The project slug (e.g. "demoproject")
            filename:   The original filename (e.g. "cv.pdf")

        Returns:
            Full path string: .../src/assets/files/<project_id>/<filename>

        Example:
            path = FileController().get_file_path("hr_project", "resume.pdf")
            # → /path/to/src/assets/files/hr_project/resume.pdf

        TODO (Pair A):
            - Use self.get_files_dir(project_id) from BaseController to get the folder
            - Join with filename using os.path.join
            - Return the complete path
        """
        # TODO: implement path resolution
        pass

    def list_project_files(self, project_id: str) -> list:
        project_dir = self.get_files_dir(project_id)
        if not os.path.exists(project_dir):
            return []
        return os.listdir(project_dir)
        """
        Returns a list of filenames in a project's upload folder.
        Useful for debugging or displaying available documents.

        TODO (Pair A — optional enhancement):
            - Get the project directory
            - Return os.listdir() of that directory
            - Handle the case where the directory does not exist yet
        """
        # TODO: implement directory listing
        pass