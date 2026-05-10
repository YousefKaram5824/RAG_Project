from fastapi import UploadFile, HTTPException
from controllers.BaseController import BaseController
from models import ResponseSignal

class DataController(BaseController):
    
    def __init__(self):
        super().__init__()

    def validate_file(self, file: UploadFile):

        # validate type
        if file.content_type not in self.app_settings.FILE_ALLOWED_EXTENSIONS:
            return False, ResponseSignal.FILE_TYPE_NOT_SUPPORTED    
        
        # validate size
        if file.size is not None:
           max_bytes = self.app_settings.FILE_MAX_SIZE_MB * 1024 * 1024
           if file.size > max_bytes:
                return False, ResponseSignal.FILE_SIZE_EXCEEDED    
        

        return True, ResponseSignal.FILE_UPLOAD_SUCCESS    