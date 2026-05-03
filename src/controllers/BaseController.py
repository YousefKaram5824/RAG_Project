import os
from helpers.config import Settings, get_settings

class BaseController:

    def __init__(self, app_settings: Settings = None):

        self.app_settings = app_settings or get_settings()

        self.base_dir = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )
        self.files_dir = os.path.join(self.base_dir, "assets", "files")
        self.db_dir = os.path.join(self.base_dir, self.app_settings.VECTOR_DB_PATH)

    def get_files_dir(self, project_id: str) -> str:
        project_dir = os.path.join(self.files_dir, project_id)
        os.makedirs(project_dir, exist_ok=True)
        return project_dir

    def get_db_path(self) -> str:
        os.makedirs(self.db_dir, exist_ok=True)
        return self.db_dir
