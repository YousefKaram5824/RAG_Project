import os
from controllers.BaseController import BaseController

class FileController(BaseController):

    def __init__(self):
        super().__init__()

    def get_file_path(self, project_id: str, filename: str) -> str:
        project_dir = self.get_files_dir(project_id)
        return os.path.join(project_dir, filename)

    def list_project_files(self, project_id: str) -> list:
        project_dir = self.get_files_dir(project_id)
        if not os.path.exists(project_dir):
            return []
        return os.listdir(project_dir)