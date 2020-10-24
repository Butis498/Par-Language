
class Semantic():
    def __init__(self):

        self.semantic_cube = {
            'int': {
                '+': {
                    'int': 'int',
                    'float': 'float'
                },
                '-': {
                    'int': 'int',
                    'float': 'float'
                },
                '=': {
                    'int': 'int',
                    'float': 'int'
                },
                '*': {
                    'int': 'int',
                    'float': 'float'
                },
                '/': {
                    'int': 'int',
                    'float': 'float'
                },
    
                '<': {
                    'int': 'bool',
                    'float': 'bool'
                },
                '>': {
                    'int': 'bool',
                    'float': 'bool'
                },
                '<=': {
                    'int': 'bool',
                    'float': 'bool'
                },
                '>=': {
                    'int': 'bool',
                    'float': 'bool'
                },
                '==': {
                    'int': 'bool',
                    'float': 'bool'
                },
                '!=': {
                    'int': 'bool',
                    'float': 'bool'
                }
            },

            'float': {
                '+': {
                    'int': 'float',
                    'float': 'float'
                },
                '-': {
                    'int': 'float',
                    'float': 'float'
                },
                '=': {
                    'int': 'float',
                    'float': 'float'
                },
                '*': {
                    'int': 'float',
                    'float': 'float'
                },
                '/': {
                    'int': 'float',
                    'float': 'float'
                },
                
                '<': {
                    'int': 'bool',
                    'float': 'bool'
                },
                '>': {
                    'int': 'bool',
                    'float': 'bool'
                },
                '<=': {
                    'int': 'bool',
                    'float': 'bool'
                },
                '>=': {
                    'int': 'bool',
                    'float': 'bool'
                },
                '==': {
                    'int': 'bool',
                    'float': 'bool'
                },
                '!=': {
                    'int': 'bool',
                    'float': 'bool'
                }
            },

            'bool': {
                '=': {
                    'bool': 'bool'
                },
                '==': {
                    'bool': 'bool'
                },
                '!=': {
                    'bool': 'bool'
                },
                '&': {
                    'bool': 'bool'
                },
                '|': {
                    'bool': 'bool'
                }
            },

            'char': {
                '=': {
                    'char': 'char'
                },
                '==': {
                    'char': 'bool'
                },
                '!=': {
                    'char': 'bool'
                }
            }
        }
        self.MEMORY_SPACE = 1000
        self.next_memory_block = self.MEMORY_SPACE
        self.variables_table = {}
        self.functions_table = {}
        self.jumps_stack = []
        
        self.variables_base_memory = {

            'global':{'int':self.asign_memory_base(),
                    'float':self.asign_memory_base(),
                    'char':self.asign_memory_base()},

            'local':{'int':self.asign_memory_base(),
                    'float':self.asign_memory_base(),
                    'char':self.asign_memory_base()},

            'temp':{'int':self.asign_memory_base(),
                    'float':self.asign_memory_base(),
                    'char':self.asign_memory_base()},

            'const':{'int':self.asign_memory_base(),
                    'float':self.asign_memory_base(),
                    'char':self.asign_memory_base()}
            }

    def asign_memory_base(self):

        self.next_memory_block += self.MEMORY_SPACE
        return self.next_memory_block

    def remove_variable(self,variable_name):

        if variable_name not in self.variables_table.keys():
            raise KeyError("Variable "+ variable_name  +" already exists")
        
        del self.variables_table[variable_name]

    def insert_variable(self,variable_name,variable_type,socope):

        if variable_name in self.variables_table.keys():

            raise KeyError("Variable "+ variable_name  +" already exists")
        
        variable = {variable_name:{'type': variable_type,'memory_addr':self.variables_base_memory[socope][variable_type]}}
        self.variables_table.update(variable)
        self.variables_base_memory[socope][variable_type] += 1

    def insert_function(self,function_name,function_type):

        if function_name in self.functions_table.keys():

            raise KeyError("Function "+ function_name +" already exists")
        
        function = {function_name:{'type': function_type}}
        self.functions_table.update(function) 

    def function_call(self,function_name):

        if function_name not in self.functions_table.keys():

            raise KeyError("Function " + str(function_name) +" not declared")


