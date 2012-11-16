from rayage_ws import StreamHandle

class RayageJsonStoreHandler(object):
    def __init__(self):
        pass
    
    def __call__(self, socket_connection, message):
        action = message[u'action']
        
        if action == u'QUERY':
            options = {}
            if u'options' in message.keys():
                options = message[u'options']
            
            count = 30
            if u'count' in options.keys():
                count = int(options[u'count'])
                
            start = 0
            if u'start' in options.keys():
                start = int(options[u'start'])
                
            sort = None
            if u'sort' in options.keys():
                sort = options[u'sort']
                
            query = None
            if u'query' in options.keys():
                query = options[u'query']
                
            self.query(socket_connection, message, count, start, sort, query)
            
        elif action == u'PUT':
            object_data = json.loads(message[u'objectData'])
            
            self.put(socket_connection, message, object_data)
            
        else:
            raise Exception("Unsupported RayageJsonStore action: {}".format(action))
            
    def query(self, socket_connection, message, count, start, sort, query):
        raise Exception("Not implemented RayageJsonStore action: {}".format(message[u'action']))
        
    def put(self, socket_connection, message, object_data):
        raise Exception("Not implemented RayageJsonStore action: {}".format(message[u'action']))
