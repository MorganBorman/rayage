from sqlalchemy import and_

#converts:
# { name: "*pepper*", aisle: "Spices" }

#into:
# and_(name.like("%pepper%"), aisle.like("Spices"))

def even(num):
    return num % 2 == 0

def count_preceeding_slashes(string, pos):
    count = 0
    while string[pos] == "\\" and pos >= 0:
        count += 1
        pos -= 1
    return count
    
replacements = {"*": "%", "?": "_"}

def apply_simple_reg_exp(column_map, column_name, reg_exp):
    if reg_exp == {} or reg_exp == "*" or reg_exp == "":
        return None

    column = column_map[column_name]
    
    reg_exp = list(reg_exp)
    
    for ci in range(len(reg_exp)):
        if reg_exp[ci] in replacements.keys() and even(count_preceeding_slashes(reg_exp, ci-1)):
            reg_exp[ci] = replacements[reg_exp[ci]]
    
    reg_exp = "".join(reg_exp)
    
    return column.like(reg_exp)
    
################################################################################
################################################################################

class SimpleDojoQuery(object):
    def __init__(self, query_dict):  
        self.query_dict = query_dict
    
    def apply_to_sqla_query(self, sqla_query, column_map):
        "Takes an sql alchemy query, applies this dojo query to it, and returns the resulting query."
        
        and_args = map(lambda k: apply_simple_reg_exp(column_map, k, self.query_dict[k]), self.query_dict.keys())
        
        and_args = filter(lambda v: v is not None, and_args)
        
        return sqla_query.filter(and_(*and_args))
