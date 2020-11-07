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
        self.goto_quadruples_stack = []
        self.operand_stack = []

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
                raise ValueError('No last temp value')

        if operand_2 == None:
            try:
                operand_2 = list(self.last_temp.keys())[0][0] # first item of dict and firt item of tuple which is var name
                operand_2_addr = list(self.last_temp.keys())[0][1]
            except:
                raise ValueError('No last temp value')

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
            new_var = (save_loc , self.memory_count['temp'][temp_type]-1)#the variable count has increase so take one from the memory count
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

        base_local,top_local = self.get_range('local')
        base_global,top_global = self.get_range('global')

        for var,addr in self.variables_table.keys():

            if var == var_name and base_local <= addr <=top_local:
                return addr

        for var,addr in self.variables_table.keys():
            
            if var == var_name and base_global <= addr <=top_global:
                return addr

        for var,addr in self.variables_table.keys():
            
            if var == var_name:
                return addr
        
        raise KeyError(f"No variable '{var_name}' found on scope")
                

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
        elif type(var) == str and var[0] == "'" and var[-1] == "'" and len(var) == 3:
            return 'char'
        elif type(var) == str and var[0] == '"' and var[-1] == '"':
            return 'string'
        elif type(var) == str:
            if var == 'True' or var == 'False':
                return 'bool'

            return 'var'
        else:
            raise TypeError(f'No type recognized for "{var}"')

    def insert_quadruple_action(self,action,operand_1=None):

        if type(action) == str:
            if operand_1 == None:
                try:
                    operand_1 = list(self.last_temp.keys())[0][0] # first item of dict and firt item of tuple which is var name
                    operand_1_addr = list(self.last_temp.keys())[0][1]

                except:
                    raise ValueError('No last tmep value for action type ')
            else:

                operand_1_addr = self.get_var_addr(operand_1)

            quadruple = {'operation': action, 'operand_1': operand_1_addr,
                            'operand_2': None, 'save_loc': None}

            print(quadruple)
            self.quadruples.append(quadruple)
    
    def insert_quadruple_asignation(self,save_loc,operand_1=None):
        
        print('=',operand_1,save_loc)
        if operand_1 == None:
            try:
                operand_1 = list(self.last_temp.keys())[0][0] # first item of dict and firt item of tuple which is var name
                operand_1_addr = list(self.last_temp.keys())[0][1]
            except:
                raise ValueError('No last tmep value')
        
        try:
            if self.get_value_type(operand_1) != 'var':
                
                type_1 = self.get_value_type(operand_1)
                operand_1 = 'const'+str(self.const_var_count)
                self.insert_variable(operand_1,type_1,'const')
                self.const_var_count += 1


        except TypeError as err:

            raise TypeError(str(err))

        operand_1_addr = self.get_var_addr(operand_1)
        save_loc_addr = self.get_var_addr(save_loc)

        validation_type_1 = self.variables_table[(operand_1,operand_1_addr)]['type']
        validation_type_2 = self.variables_table[(save_loc,save_loc_addr)]['type']

        if validation_type_1 != validation_type_2:
            raise TypeError(f'Incompatible Types {validation_type_1} and {validation_type_2}')

        quadruple = {'operation': '=', 'operand_1': operand_1_addr,
                        'operand_2': None, 'save_loc': save_loc_addr}

        print(quadruple)
        self.quadruples.append(quadruple)


    def insert_quadruple_goto(self,quadruple_num=None,operand_1=None,goto_type=None):

        print(quadruple_num,operand_1,goto_type)
        if operand_1 == None and goto_type != None:
            try:
                operand_1 = list(self.last_temp.keys())[0][0] # first item of dict and firt item of tuple which is var name
                operand_1_addr = list(self.last_temp.keys())[0][1]
                           
            except:
                raise ValueError('No last temp value')
        
        else:
            if operand_1 != None:
                operand_1_addr = self.get_var_addr(operand_1) 

                if self.get_variable_type(operand_1) != 'bool':
                    raise TypeError(f'{operand_1} Not bool variable')
            

        goto = 'goto'
        if goto_type == True:
            goto = 'gotot'
        elif goto_type == False:
            goto = 'gotof'
        elif goto_type == None:
            operand_1 = None
            operand_1_addr = None

        
        quadruple = {'operation':goto,'operand_1':operand_1_addr,'operand_2':None,'save_loc':quadruple_num}
        print(quadruple) 
        self.quadruples.append(quadruple)
        self.goto_quadruples_stack.append(self.quadruples[-1])


    def get_variable_type(self, var):

        addr = self.get_var_addr(var)

        for scope in self.variables_base_memory.keys():
            for type_var in self.variables_base_memory[scope].keys():
                base = self.variables_base_memory[scope][type_var]
                top = base + self.MEMORY_SPACE -1
                if base <= addr <= top:
                    return type_var

    def print_quadruples(self):
        cont = 0
        for quadruple in self.quadruples:
            print(cont,quadruple)
            cont += 1

        

                
                
