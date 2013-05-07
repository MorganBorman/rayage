from sqlalchemy import and_, or_

statement_types = {}

class MalformedDojoQuery(Exception):
    '''A dojo sort dictionary is missing fields or fields are invalid.'''
    def __init__(self, value=''):
        Exception.__init__(self, value)

def validate_statement_dict(statement_dict):
    if not u'data' in statement_dict:
        raise MalformedDojoQuery("Missing 'data' key in statement dictionary.")
        
    if not statement_dict[u'op'] in statement_types:
        raise MalformedDojoQuery("Unknown statement type.")
        
    if statement_dict[u'op'] == u'string' and not u'isCol' in statement_dict:
        raise MalformedDojoQuery("Missing 'isCol' key in string statement dictionary.")

################################################################################
################################################################################

class DojoQuery(object):
    def __init__(self, query_dict):
        "Validate that this query conforms to the expected syntax."
        
        #Check that u'op' is a key here so we can index based on it
        if not u'op' in query_dict:
            raise MalformedDojoQuery("Missing 'op' key in statement dictionary.")
            
        self.query = statement_types[query_dict[u'op']](query_dict)
    
    def apply_to_sqla_query(self, sqla_query, column_map):
        "Takes an sql alchemy query, applies this dojo query to it, and returns the resulting query."
        return self.query.apply_to_sqla_query(sqla_query, column_map)
        
################################################################################
################################################################################

class DojoAnyStatement(object):
    def __init__(self, statement_dict):
        validate_statement_dict(statement_dict)
        
        self.substatements = []
        
        for substatement_dict in statement_dict[u'data']:
            
            if not u'op' in statement_dict:
                raise MalformedDojoQuery("Missing 'op' key in statement dictionary.")
                
            self.substatements.append(statement_types[substatement_dict[u'op']](substatement_dict))
    
    def apply_to_sqla_query(self, sqla_query, column_map):
        "Takes an sql alchemy query, applies this dojo query to it, and returns the resulting query."
        args = map(lambda ds: ds.apply_to_sqla_query(sqla_query, column_map), self.substatements)
        return sqla_query.filter(or_(*args))

class DojoAllStatement(object):
    def __init__(self, statement_dict):
        validate_statement_dict(statement_dict)
        
        self.substatements = []
        
        for substatement_dict in statement_dict[u'data']:
            
            if not u'op' in statement_dict:
                raise MalformedDojoQuery("Missing 'op' key in statement dictionary.")
                
            self.substatements.append(statement_types[substatement_dict[u'op']](substatement_dict))
    
    def apply_to_sqla_query(self, sqla_query, column_map):
        "Takes an sql alchemy query, applies this dojo query to it, and returns the resulting query."
        args = map(lambda ds: ds.apply_to_sqla_query(sqla_query, column_map), self.substatements)
        return sqla_query.filter(and_(*args))

class DojoContainsStatement(object):
    def __init__(self, statement_dict):
        validate_statement_dict(statement_dict)
        
        data = statement_dict[u'data']
        
        if len(data) != 2:
            raise MalformedDojoQuery("Contains statement expects exactly two datum.")
            
        self.args = []
        
        for substatement_dict in statement_dict[u'data']:
            
            if not u'op' in statement_dict:
                raise MalformedDojoQuery("Missing 'op' key in statement dictionary.")
                
            if substatement_dict[u'op'] != u'string':
                raise MalformedDojoQuery("Arguments to contains statement must be strings.")
                
            self.args.append(statement_types[substatement_dict[u'op']](substatement_dict))
    
    def apply_to_sqla_query(self, sqla_query, column_map):
        "Takes an sql alchemy query, applies this dojo query to it, and returns the resulting query."
        
        if self.args[0].isCol and not self.args[1].isCol:
            column = self.args[0].string
            value = self.args[1].string
        elif not self.args[0].isCol and self.args[1].isCol:
            column = self.args[1].string
            value = self.args[0].string
        else:
            raise MalformedDojoQuery("Arguments to contains statement must be (Column, String) or (String, Column).")
        
        return column_map[column].like("%"+value+"%")

class DojoStringStatement(object):
    def __init__(self, statement_dict):
        validate_statement_dict(statement_dict)
        
        self.string = statement_dict[u'data']
        self.isCol = statement_dict[u'isCol']
    
    def apply_to_sqla_query(self, sqla_query, column_map):
        raise MalformedDojoQuery("String statement type may not be applied to an sql alchemy query.")

statement_types[u'any'] = DojoAnyStatement
statement_types[u'all'] = DojoAllStatement
statement_types[u'contains'] = DojoContainsStatement
statement_types[u'string'] = DojoStringStatement
        
################################################################################
################################################################################
