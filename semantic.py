from semantic_cube import semantic_cube
import copy


class Semantic():
    def __init__(self):

        self.MEMORY_SPACE = 1000
        self.next_memory_block = self.MEMORY_SPACE
        self.variables_table = {}
        self.functions_table = {}
        self.jumps_stack = []
        self.quadruples = []
        self.last_temp = {}
        self.temp_count = 0
        self.const_var_count = 0

        self.variables_base_memory = {

            'global': {'int': self.asign_memory_base(),
                       'float': self.asign_memory_base(),
                       'char': self.asign_memory_base(),
                       'bool': self.asign_memory_base()},

            'local': {'int': self.asign_memory_base(),
                      'float': self.asign_memory_base(),
                      'char': self.asign_memory_base(),
                      'bool': self.asign_memory_base()},

            'temp': {'int': self.asign_memory_base(),
                     'float': self.asign_memory_base(),
                     'char': self.asign_memory_base(),
                     'bool': self.asign_memory_base()},

            'const': {'int': self.asign_memory_base(),
                      'float': self.asign_memory_base(),
                      'char': self.asign_memory_base(),
                      'bool': self.asign_memory_base()}
        }
        self.memory_count = copy.deepcopy(self.variables_base_memory)

    def asign_memory_base(self):

        self.next_memory_block += self.MEMORY_SPACE
        return self.next_memory_block

    def reset_memory(self, memory_type):


        try:
            self.memory_count[memory_type] = copy.deepcopy(self.variables_base_memory[memory_type])
            base,top = self.get_range(memory_type)
            for var,addr in list(self.variables_table.keys()):
                if base <= addr <= top:
                    del self.variables_table[(var,addr)]

        except KeyError as err:

            print('No memory type found, ' + str(err))

    def insert_variable(self, variable_name, variable_type, scope):

        try:
            new_variable = (variable_name, self.memory_count[scope][variable_type])
            base ,top = self.get_range(scope)

            for var,addr in list(self.variables_table.keys()):
                if base <= addr <= top and var == variable_name:
                    raise KeyError('Variable ' + var + ' already exists')

            variable = {new_variable: {'type': variable_type}}
            self.variables_table.update(variable)

            if self.memory_count[scope][variable_type] >= top:
                raise MemoryError('Out of memory variables')

            self.memory_count[scope][variable_type] += 1

        except KeyError as err:

            raise KeyError('Can not insert variable, ' + str(err))



    def insert_function(self, function_name, function_type):

        if function_name in self.functions_table.keys():

            raise KeyError("Function " + function_name + " already exists")

        try:
            function = {function_name: {'type': function_type}}
            self.functions_table.update(function)
        except KeyError as err:

            print('Can not declare function, ' + str(err))

    def function_call(self, function_name):

        if function_name not in self.functions_table.keys():

            raise KeyError("Function " + str(function_name) + " not declared")

    def insert_quadruple_operation(self, operation, operand_1=None, operand_2=None, save_loc=None):

        print(operation,operand_1,operand_2,save_loc)
        if operand_1 == None:
            try:
                operand_1 = list(self.last_temp.keys())[0][0] # first item of dict and firt item of tuple which is var name
                operand_1_addr = list(self.last_temp.keys())[0][1]
            except:
                raise ValueError('No last tmep value')

        if operand_2 == None:
            try:
                operand_2 = list(self.last_temp.keys())[0][0] # first item of dict and firt item of tuple which is var name
                operand_2_addr = list(self.last_temp.keys())[0][1]
            except:
                raise ValueError('No last tmep value')

        try:
            if self.get_value_type(operand_1) != 'var':
                
                type_1 = self.get_value_type(operand_1)
                operand_1 = 'const'+str(self.const_var_count)
                self.insert_variable(operand_1,type_1,'const')
                self.const_var_count += 1

            if self.get_value_type(operand_2) != 'var':
                
                type_2 = self.get_value_type(operand_2)
                operand_2 = 'const'+str(self.const_var_count)
                self.insert_variable(operand_2,type_2,'const')
                self.const_var_count += 1

        except TypeError as err:

            raise TypeError(str(err))

        operand_1_addr = self.get_var_addr(operand_1)
        operand_2_addr = self.get_var_addr(operand_2)
            
        
        if save_loc == None:

            #operand_1_scope = self.get_var_scope((operand_1,operand_1_addr))
            #operand_2_scope = self.get_var_scope((operand_2,operand_2_addr))
            save_loc = 'temp'+str(self.temp_count)
            temp_type = self.get_var_type(operation,(operand_1,operand_1_addr),(operand_2,operand_2_addr))
            self.insert_variable(save_loc,temp_type,'temp')
            new_var = (save_loc , self.memory_count['temp'][temp_type])
            newTemp = {new_var:{'type':temp_type}}
            self.last_temp = newTemp
            self.temp_count += 1
   
        save_loc_addr = self.get_var_addr(save_loc)

        try:
            operand1_mem = operand_1_addr
            operand2_mem = operand_2_addr
            save_loc_mem = save_loc_addr
            quadruple = {'operation': operation, 'operand_1': operand1_mem,
                         'operand_2': operand2_mem, 'save_loc': save_loc_mem}
            self.quadruples.append(quadruple)
        except KeyError as err:
            raise KeyError('Var  does not exists in table, ' + str(err))

        print(quadruple)



    def get_var_type(self,operation, var1,var2):
        try:
            type_1 = self.variables_table[var1]['type']
            type_2 = self.variables_table[var2]['type']
        except KeyError as err:
            raise KeyError(str(err) + ' does not exists')

        try:
            type_res_var = semantic_cube[type_1][operation][type_2]
            return type_res_var
        except KeyError :
            raise TypeError('Not supported type for operands '+ var1[0] + ' and ' + var2[0])

    def get_range(self,scope):
        base = list(self.variables_base_memory[scope].values())[0]
        top = base + self.MEMORY_SPACE * len(self.variables_base_memory[scope]) -1
        return base,top


    def get_var_scope(self,var:tuple):

        try:
            if var in self.variables_table.keys():
                for scope in self.variables_base_memory.keys():
                    base,top = self.get_range(scope)
                    if base <= var[1] <= top:
                        return scope

        except KeyError:
            raise ValueError('Cant get var scope '+ str(var[0]))


    def get_var_addr(self,var_name):

        for var,addr in self.variables_table.keys():
                if var == var_name:
                    return addr

    def end_expression(self):

        self.temp_count = 0
        self.reset_memory('temp')

    def end_function(self):

        self.temp_count = 0
        self.reset_memory('temp')
        self.reset_memory('local')

    def get_value_type(self,var):

        if type(var) == int:
            return 'int'
        elif type(var) == float:
            return 'float'
        elif type(var) == str and var[0] == '"' and var[-1] == '"' and len(var) == 3:
            return 'char'
        elif type(var) == bool:
            return 'bool'
        elif type(var) == str:
            return 'var'
        else:
            raise TypeError(f'No type recognized for "{var}"')
            



                
                
