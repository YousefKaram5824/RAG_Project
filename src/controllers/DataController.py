from fastapi import UploadFile, HTTPException
from controllers.BaseController import BaseController

class DataController(BaseController):
    
    def __init__(self):
        super().__init__()

    def validate_file(self, file: UploadFile) -> bool:

        # validate type
        if file.content_type not in self.app_settings.FILE_ALLOWED_EXTENSIONS:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"File type '{file.content_type}' is not allowed. "
                        f"Accepted types: {self.app_settings.FILE_ALLOWED_EXTENSIONS}"
                    ),
                )
        
        # validate size
        if file.size is not None:
           max_bytes = self.app_settings.FILE_MAX_SIZE_MB * 1024 * 1024
           if file.size > max_bytes:
                raise HTTPException(
                    status_code=413,
                    detail=(
                        f"File size {file.size / (1024 * 1024):.2f} MB exceeds "
                        f"the maximum allowed size of {self.app_settings.FILE_MAX_SIZE_MB} MB."
                    ),
                )

        return True       
