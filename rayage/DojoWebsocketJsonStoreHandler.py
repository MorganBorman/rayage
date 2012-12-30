from WebSocketHandler import StreamHandle
import json

class DojoWebsocketJsonStoreHandler(object):
    def __init__(self, message_type, required_fields, minimum_permission_level):
        self.message_type = message_type
        self.required_fields = required_fields
        self.stream_handle = StreamHandle(message_type, minimum_permission_level)
        
    def object_to_json(self, obj):
        return obj.__dict__
        
    def publish(self, message_data):
        self.stream_handle.publish(message_data)
        
    def on_update(self, updated_object):
        result_message = {'type': self.message_type,
                          'action': 'update',
                          'object': self.object_to_json(updated_object),
                         }
        
        self.publish(json.dumps(result_message))
        
    def on_delete(self, deleted_object_id):
        result_message = {'type': self.message_type,
                          'action': 'delete',
                          'object_id': deleted_object_id,
                         }
        
        self.publish(json.dumps(result_message))
    
    def __call__(self, socket_connection, message):
        action = message[u'action']
        
        if action == u'QUERY':
            options = {}
            if u'options' in message.keys():
                options = message[u'options']
            
            count = 30
            if u'count' in options.keys() and options[u'count'] is not None:
                count = int(options[u'count'])
                
            start = 0
            if u'start' in options.keys() and options[u'start'] is not None:
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
        elif action == u'GET':
            object_id = message[u'id']
            self.get(socket_connection, message, object_id)
            
        elif action == u'DELETE':
            object_id = message[u'id']
            self.delete(socket_connection, message, object_id)
            
        else:
            print message
            raise Exception("Unsupported DojoWebsocketJsonStoreHandler action: {}".format(action))
            
    def get(self, socket_connection, message, object_id):
        raise Exception("Not implemented DojoWebsocketJsonStoreHandler action: {}".format(message[u'action']))
        
    def delete(self, socket_connection, message, object_id):
        raise Exception("Not implemented DojoWebsocketJsonStoreHandler action: {}".format(message[u'action']))
            
    def query(self, socket_connection, message, count, start, sort, query):
        raise Exception("Not implemented DojoWebsocketJsonStoreHandler action: {}".format(message[u'action']))
        
    def put(self, socket_connection, message, object_data):
        raise Exception("Not implemented DojoWebsocketJsonStoreHandler action: {}".format(message[u'action']))
