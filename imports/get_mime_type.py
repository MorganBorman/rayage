import mimetypes
mimetypes.init()

def get_mime_type(full_filename):
    "Returns the mimetype for a file given its fully qualified filename."
    mime, encoding = mimetypes.guess_type(full_filename)
    return mime
