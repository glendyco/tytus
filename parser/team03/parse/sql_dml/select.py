from parse.ast_node import ASTNode
from jsonMode import *
from util import *


class Select(ASTNode):
    def __init__(self, is_distinct, col_names, tables, where, group_by, having, order_by, limit, offset, line, column, graph_ref):
        ASTNode.__init__(self, line, column)
        self.is_distinct = is_distinct  # true = distinct, false = not distinct, None = not specified
        self.col_names = col_names      # could be identifier or identifier.identifier
        self.tables = tables            # could be a string list and/or a list of node, not sure
        self.where = where              # could be a boolean and/or a node, not sure
        self.group_by = group_by        # is a list of col_names, like previous one
        self.having = having            # having is a logical expression, could be a node?
        self.order_by = order_by        # column name, could be identifier or identifier.identifier
        self.limit = limit              # integer
        self.offset = offset            # integer
        self.graph_ref = graph_ref

    def execute(self, table, tree):
        super().execute(table, tree)
        
        header = []
        megaunion = []
        #lets make the cartesiasn from all tables
        if self.tables:            
            
            for t in self.tables:
                #get all columnaes and add into header array
                columns = table.get_fields_from_table(t.name)
                columns.sort(key = lambda x: x.field_index)
                for c in columns:
                    if t.alias is None:
                        header.append(str(c.field_name))
                    else:
                        header.append(str((t.alias) + '.' + str(c.field_name)))
            
                data = extractTable(table.get_current_db().name, t.name)
                if len(megaunion) > 0 and len(data) > 0:
                    megaunion = doBinaryUnion(megaunion,data)
                elif len(megaunion) == 0:
                    megaunion = data
                else :
                    megaunion = megaunion
            #Appying filtering for each row by call the excute function if execute return true we kept the row else remove that
            if self.where:
                megaunion = self.where.execute(megaunion,header)
            #TODO:add agregate functions
            #TODO:filter columns...
            #TODO:apply group by execution...
            if self.group_by:
                pass
            #TODO:apply having by execution...
            if self.having:
                pass



        return [header, megaunion]
        


class Names(ASTNode):
    def __init__(self, is_asterisk, exp, alias, line, column, graph_ref):
        ASTNode.__init__(self, line, column)
        self.is_asterisk = is_asterisk
        self.exp = exp
        self.alias = alias
        self.graph_ref = graph_ref

    def execute(self, table, tree):
        super().execute(table, tree)
        return True


class TableReference(ASTNode):
    def __init__(self, table, natural_join, join_type, table_to_join, subquery, line, column, graph_ref):
        ASTNode.__init__(self, line, column)
        self.table = table                      # Unique field to be mandatory, others are None if no joins
        self.natural_join = natural_join        # Probably will be easier to add naturals to enum, dev must decide
        self.join_type = join_type              # join type reference, NOT string (maybe)
        self.table_to_join = table_to_join
        self.subquery = subquery                # Result of subquery or node, dev must decide
        self.graph_ref = graph_ref

    def execute(self, table, tree):
        super().execute(table, tree)
        return True


class Table(ASTNode):
    def __init__(self, name, alias, subquery, line, column, graph_ref):
        ASTNode.__init__(self, line, column)
        self.name = name
        self.alias = alias
        self.subquery = subquery
        self.graph_ref = graph_ref

    def execute(self, table, tree):
        super().execute(table, tree)
        return True


class Where(ASTNode):
    def __init__(self, exp, line, column, graph_ref):
        ASTNode.__init__(self, line, column)
        self.exp = exp
        self.graph_ref = graph_ref

    def execute(self, table, tree):
        super().execute(table, tree)
        result = []
        for row in table:
            #maybe I shouldn't do this... pass this paramas 
            keept_this_row = self.exp.execute(row, tree)
            if keept_this_row:
                result.append(row)
        return result


#  Probably not needed but added anyways
class Join(ASTNode):
    def __init__(self, name, line, column, graph_ref):
        ASTNode.__init__(self, line, column)
        self.name = name
        self.graph_ref = graph_ref

    def execute(self, table, tree):
        super().execute(table, tree)
        return True


# Probably needs to have a way to create a list from comma separated string
class GroupBy(ASTNode):
    def __init__(self, names, line, column, graph_ref):
        ASTNode.__init__(self, line, column)
        self.name = names
        self.graph_ref = graph_ref

    def execute(self, table, tree):
        super().execute(table, tree)
        return True


class Having(ASTNode):
    def __init__(self, exp, line, column, graph_ref):
        ASTNode.__init__(self, line, column)
        self.exp = exp
        self.graph_ref = graph_ref

    def execute(self, table, tree):
        super().execute(table, tree)
        return True


class TimeOps(ASTNode):
    def __init__(self, extract_opt, time_string, aux_string, line, column, graph_ref):
        ASTNode.__init__(self, line, column)
        self.extract_opt = extract_opt      # extract opt from Enum, if None then is date_part and needs aux_string
        self.time_string = time_string      # string used to parse date
        self.aux_string  = aux_string       # needed only if is date_part, ex. HOUR... would this be an enum?
        self.graph_ref = graph_ref
    def execute(self, table, tree):
        super().execute(table, tree)
        return True
