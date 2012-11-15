class MalformedMessage(Exception):
    '''A message is missing fields or fields are invalid.'''
    def __init__(self, value=''):
        Exception.__init__(self, value)
        
class InsufficientPermissions(Exception):
    '''A message is issued without sufficient permissions.'''
    def __init__(self, value=''):
        Exception.__init__(self, value)
