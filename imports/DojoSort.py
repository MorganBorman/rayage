from sqlalchemy.sql.expression import asc, desc

class MalformedDojoSort(Exception):
    '''A dojo sort dictionary is missing fields or fields are invalid.'''
    def __init__(self, value=''):
        Exception.__init__(self, value)

class DojoSort(object):
    def __init__(self, sort_data):
        "Validate that this query conforms to the expected syntax."
        
        self.sort_data = sort_data
    
    def apply_to_sqla_query(self, sqla_query, column_map):
        "Takes an sql alchemy query, applies this dojo query to it, and returns the resulting query."
        
        if len(self.sort_data) <= 0:
            return sqla_query
        
        sorts = []
        
        for sort_dict in self.sort_data:
        
            if not u'attribute' in sort_dict.keys():
                raise MalformedDojoSort("Missing 'attribute' key in sort dictionary.")
                
            attribute = sort_dict[u'attribute']
                
            direction = asc
            if u'descending' in sort_dict.keys():
                direction = desc if sort_dict[u'descending'] else asc
            
            sorts.append(direction(column_map[attribute]))
        
        return sqla_query.order_by(*sorts)
