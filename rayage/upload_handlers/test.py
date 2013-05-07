from constants import *
import json

import tempfile
import zipfile

from ..UploadHandler import uploadHandler
from ..WebSocketHandler import WebSocketHandler

from ..websocket_message_handlers.TestStore import TestStoreHandler

@uploadHandler('test', PERMISSION_LEVEL_PROF)
def test_upload_handler(request_handler):
    if u'uploadedfiles[]' in request_handler.request.files.keys():
        file_info = request_handler.request.files[u'uploadedfiles[]'][0]
        response_data = {'file': file_info[u'filename'], 'type': file_info[u'content_type'], 'size': len(file_info[u'body'])}
        
        try:
            uploaded_files = request_handler.request.files[u'uploadedfiles[]']
            
            for uploaded_file in uploaded_files:
                
                with tempfile.TemporaryFile(mode='w+b') as tfile:
                    filename = uploaded_file['filename']
                    content_type = uploaded_file['content_type']
                    
                    # Write the test archive (hopefully an archive) to the temp file
                    tfile.write(uploaded_file['body'])
                    # Reset the file position
                    tfile.seek(0)
                    
                    if zipfile.is_zipfile(tfile):
                        zfile = zipfile.ZipFile(tfile)
                        
                        namelist = zfile.namelist()
                        
                        if len(namelist) == 0:
                            raise Exception("Cannot install empty project test.")
                        
                        if not '/' in namelist[0]:
                            raise Exception("All test files must be contained in a single directory within the zip file.")
                        
                        test_dir_prefix = namelist[0].split('/')[0]
                        
                        for name in namelist:
                            if namelist[0].split('/')[0] != test_dir_prefix:
                                raise Exception("All test files must be contained in a single directory within the zip file.")
                        
                        zfile.extractall(TEMPLATES_DIR)
                        
                        TestStoreHandler.on_change(test_dir_prefix, 'create')
        except Exception, e:
            username = request_handler.get_current_user()
            WebSocketHandler.notify_username(username, e.message, "error")
            
        print response_data
        request_handler.finish(json.dumps(response_data))
