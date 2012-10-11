

class Project(object):
    def __init__(self, path):
        self.path = path
        
    @classmethod
    def from_template(self, template, user):
        """
        Copies the template specified (relative to the template path) to the path for the specified user.
        Returns an instance of Project on success or None on failure.
        """
        pass
        
    def get_filenames(self):
        """
        Crawls the project path and returns a list of the filenames in the project. (relative to the project path)
        """
        pass
        
    def get_file(self, filename):
        """
        filename is the location of the file to retrieve. (relative to the project path)
        Returns the contents of the specified file.
        """
        pass
        
    def update_file(self, filename, contents):
        """
        filename is the location of the file to update. (relative to the project path)
        contents is the new contents of the file.
        Returns whether the update was successful.
        """
        pass
        
    def create_file(self, filename):
        """
        filename is the location of the file to create. (relative to the project path)
        Returns whether the file creation was successful.
        """
        pass
        
