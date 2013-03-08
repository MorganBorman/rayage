from constants import *
import json

import tempfile
import zipfile
import os.path
import shutil

from rayage.database.Assignment import Assignment

from ..DownloadHandler import downloadHandler
from ..WebSocketHandler import WebSocketHandler

@downloadHandler('assignment', PERMISSION_LEVEL_PROF)
def assignment_download_handler(request_handler, download_selector):
    assignment_id = int(download_selector)
    
    assignment = Assignment.by_id(assignment_id)
    
    tfileno, tfilename = tempfile.mkstemp(".zip")
    
    basename, ext = os.path.splitext(tfilename)
    
    temp_zip_file_path = shutil.make_archive(basename, 'zip', '{}/{}'.format(ASSIGNMENTS_DIR, assignment_id))
    
    with open(temp_zip_file_path, 'rb') as f:
    
        request_handler.set_header ('Content-Type', 'application/zip')
        request_handler.set_header ('Content-Disposition', 'attachment; filename={}.zip'.format(assignment.name))
    
        request_handler.flush()
    
        request_handler.write(f.read())
        
    request_handler.finish()
