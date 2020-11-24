from semantic_cube import semantic_cube
import copy
import json
import pickle
import os


class Semantic():
    def __init__(self):

        self.MEMORY_SPACE = 5000
        self.next_memory_block = self.MEMORY_SPACE
        self.variables_table = {}
        self.functions_table = {}
        self.jumps_stack = [0]
        self.quadruples = []
        self.last_temp = []
        self.temp_count = 0
        self.const_var_count = 0
        self.goto_quadruples_stack = []
        self.operand_stack = []
        self.current_func = None
        self.variables_table_func = {}
        self.param_count = 0
        self.func_call_stack = []
        self.pointer_count = 0
        self.supported_arr_op = ['+','-','*']
        self.program_id = ''
        self.param_dec_count = 0
        self.param_stack = []
        self.current_arr = []
        
    
        self.variables_base_memory = {

            'global': {'int': self.asign_memory_base(),
                       'float': self.asign_memory_base(),
                       'char': self.asign_memory_base(),
                       'bool': self.asign_memory_base(),
                       'pointer':self.asign_memory_base()},

            'local': {'int': self.asign_memory_base(),
                      'float': self.asign_memory_base(),
                      'char': self.asign_memory_base(),
                      'bool': self.asign_memory_base(),
                      'pointer':self.asign_memory_base()},

            'temp': {'int': self.asign_memory_base(),
                     'float': self.asign_memory_base(),
                     'char': self.asign_memory_base(),
                     'bool': self.asign_memory_base(),
                     'pointer':self.asign_memory_base()},

            'const': {'int': self.asign_memory_base(),
                      'float': self.asign_memory_base(),
                      'char': self.asign_memory_base(),
                      'bool': self.asign_memory_base(),
                      'pointer':self.asign_memory_base()}

        }
        self.memory_count = copy.deepcopy(self.variables_base_memory)
        self.insert_variable('const'+str(self.const_var_count),'int','const',value=0)
        self.const_var_count += 1


    # Function to assing a memory base value,each time it is called the value returned by the fuction is 
    # Increased by the MEMORY_SIZE constant
    def asign_memory_base(self):

        self.next_memory_block += self.MEMORY_SPACE
        return self.next_memory_block


    # Clears the variables table from local and temp variables, it means that when this fucntion is called
    # the memory remains only with constant variable, it requires the memmory type as parameters, it does not have a return value.
    def reset_memory(self, memory_type):

        
        try:
            self.memory_count[memory_type] = copy.deepcopy(self.variables_base_memory[memory_type])
            base,top = self.get_range(memory_type)
            for var,addr in list(self.variables_table.keys()):
                if base <= addr <= top:
                    del self.variables_table[(var,addr)]

            self.current_func = None

        except KeyError as err:

            raise TypeError('No memory type found, ' + str(err))


    # This function inserts variables in the variables table the process of insertion deffers depending on the 
    # data type if the var is an array it will insert a variable with other attributes types
    # after the insertion the variable is set to the last_temp stack for future use
    # it needs the variable name the variable type, the varible scope , as optional parametres it is requires to send 
    # the dimension of the array in case it is an array, the dimensions of the second index of it is a matrix
    # in case it is a constant the value of the constant, and last but not least the array configuration, in case the you need to send 
    # a configuratrion manualy of the array 

    def insert_variable(self, variable_name, variable_type, scope, param=False, dim1=None,dim2=None,value=None,arr_conf=None):

        dims = {}

        if arr_conf != None:# if there is a pre set configuratio for an array
            dims.update(arr_conf)
        else:# if there is not a pre configures array 

            if dim1 != None: # if it is not an array or a matrix
                
                if dim2 == None: # it is not a matrix

                    index_1 = 'const'+str(self.const_var_count)
                    self.insert_variable(index_1,'int','const',value=dim1)
                    self.const_var_count += 1
                    
                    m1_value = 1
                    m1 = 'const'+str(self.const_var_count)
                    self.insert_variable(m1,'int','const',value = m1_value)
                    self.const_var_count += 1

                    index_1_addr = self.get_var_addr(index_1)
                    m1_addr = self.get_var_addr(m1)

                    size = dim1

                    dims.update({'m1':m1_addr,'index_1':index_1_addr,'size':size})
                    
                else: # its a matrix
                    index_1 = 'const'+str(self.const_var_count)
                    self.insert_variable(index_1,'int','const',value = dim1)
                    self.const_var_count += 1

                    m1_value = dim2
                    m1 = 'const'+str(self.const_var_count)
                    self.insert_variable(m1,'int','const',value = m1_value)
                    self.const_var_count += 1

                    index_2 = 'const'+str(self.const_var_count)
                    self.insert_variable(index_2,'int','const',value = dim2)
                    self.const_var_count += 1

                    m2_value = 1
                    m2 = 'const'+str(self.const_var_count)
                    self.insert_variable(m2,'int','const',value = m2_value)
                    self.const_var_count += 1

                    index_1_addr = self.get_var_addr(index_1)
                    m1_addr = self.get_var_addr(m1)

                    index_2_addr = self.get_var_addr(index_2)
                    m2_addr = self.get_var_addr(m2)

                    size = dim1 * dim2
                    
                    
                    dims.update({'m1':m1_addr,'m2':m2_addr,'index_1':index_1_addr,'index_2':index_2_addr,'size':size})

        
        try:
            if variable_type == 'string': 
                variable_type = 'char'
            new_variable = (variable_name, self.memory_count[scope][variable_type])
            base ,top = self.get_range(scope)

            # check if the variable exists in the variables table
            for var,addr in list(self.variables_table.keys()):
                if base <= addr <= top and var == variable_name:
                    raise KeyError('Variable ' + var + ' already exists')

            variable = {new_variable: {'type': variable_type}}


            if variable_type == 'pointer':# variable is a pointer
                
                arr_base_addr = self.get_var_addr(self.current_arr[-1])
                last_temp_type = self.get_addr_type(arr_base_addr)
                pointer_type = {'pointer_type':last_temp_type}
                variable[new_variable].update(pointer_type)

            
            self.last_temp.append(variable)
            self.variables_table.update(variable)
            self.variables_table[new_variable].update(dims)

            if scope == 'const' and value != None:
                if variable_type == 'char':
                    value = value.replace('"','')
                    value = value.replace("'",'')

                value_const = {'value':value}
                self.variables_table[new_variable].update(value_const)

            base_temp,top_temp = self.get_range('temp')
            base_const,top_const = self.get_range('const')
            #base_glob,top_glob = self.get_range('global')

            if param or new_variable[1] not in range(base_temp,top_temp) and new_variable[1] not in range(base_const,top_const):
                self.variables_table_func.update(variable)

            if self.memory_count[scope][variable_type] >= top:
                raise MemoryError('Out of memory variables')
            
            if dim1 == None: # it is not an array or a matrix
                self.memory_count[scope][variable_type] += 1
            else:
                if dim2 != None: # it is a matrix
                    if arr_conf == None: # it has not a pre set conf for the array
                        self.memory_count[scope][variable_type] += dim1 * dim2
                    else:
                        key1 = self.get_const_value(arr_conf['index_1'])
                        key2 = self.get_const_value(arr_conf['index_2'])

                        value1 = self.variables_table[key1]['value']
                        value2 = self.variables_table[key2]['value']

                        self.memory_count[scope][variable_type] += value1 * value2

                else:
                    if arr_conf == None:
                        self.memory_count[scope][variable_type] += dim1
                    else:
                        key1 = self.get_const_value(arr_conf['index_1'])
                        value1 = self.variables_table[key1]['value']

                        self.memory_count[scope][variable_type] += value1

        except KeyError as err:

            raise KeyError('Can not insert variable, ' + str(err))


    # Returns a dictionary of the memory that has been used between the last call of the same fuction
    # this function has to be called in order to pass the memory usage to the obj. file
    # it does not need a parameter, it takes the current array from the object
    def get_func_memory_usage(self):
        res = {'temp':{'int':0,'float':0,'char':0,'bool':0,'pointer':0},
                'local':{'int':0,'float':0,'char':0,'bool':0,'pointer':0}}

        

        for var in self.variables_table.keys():
            if var not in self.variables_table_func:
                
                base_glob,top_glob = self.get_range('global')
                base_const,top_const = self.get_range('const')
                base_temp,top_temp = self.get_range('temp')
                base_local,top_local = self.get_range('local')
                if var[1] not in range(base_glob,top_glob) and var[1] not in range(base_const,top_const): # if the variable is not a global or const 
                    
                    if var[1] in range(base_temp,top_temp): # the variable is a temp
                        if 'size' in self.variables_table[var].keys(): # if it is an array or a matrix
                            res['temp'][self.variables_table[var]['type']] += self.variables_table[var]['size']
                        else:
                            res['temp'][self.variables_table[var]['type']] += 1

                    if var[1] in range(base_local,top_local): # the variable is a local
                        if 'size' in self.variables_table[var].keys():# it is a array or a matrix
                            res['local'][self.variables_table[var]['type']] += self.variables_table[var]['size']
                        else:
                            res['local'][self.variables_table[var]['type']] += 1


        return res

    # the main purpose of this function is to insert simple quadruples such as write or ends
    # it takes as parameters the operation to be done and the func in case it has one
    # it does not have a return value
    def insert_func_quadruple(self,operation,func=None):

        quadruple = {'operation': operation, 'operand_1': None,
                    'operand_2': None, 'save_loc': func}

        self.quadruples.append(quadruple)
    

    # Inserts a quadruple to assing a value to a function global variable , it has two parameters the operand_1 which is the value to be asing in 
    # and the save_loc parameter which is the name of the saving location in case it is none it will get the last temp value
    # it takes two parameters: the operand1 which is the expression to be saved , and the save_loc which refers to the 
    # global varible to be set
    def insert_param_quadruple(self,operand_1,save_loc):

        if operand_1 == None:# if the operand 1 is a temporal value 
            try: # get the last temporal value
                operand_1 = list(self.last_temp[-1].keys())[0][0] # first item of dict and firt item of tuple which is var name
                operand_1_addr = list(self.last_temp[-1].keys())[0][1]
                self.last_temp.pop(-1)

            except:
                raise ValueError('No last temp value')
        
        try:
            if self.get_value_type(operand_1) != 'var': # if the value pased is not a variable
                
                value = operand_1
                type_1 = self.get_value_type(operand_1)
                operand_1 = 'const'+str(self.const_var_count)
                self.insert_variable(operand_1,type_1,'const',value=value)
                self.const_var_count += 1
                self.last_temp.pop(-1)

        except TypeError as err:

            raise TypeError(str(err))


        operand_1_addr = self.get_var_addr(operand_1)
        save_loc_addr = save_loc

        
        validation_type_1 = self.variables_table[(operand_1,operand_1_addr)]['type']

        if validation_type_1 == 'pointer': # if the type is a pointer get the pointer type
            validation_type_1 = self.variables_table[(operand_1,operand_1_addr)]['pointer_type']

        validation_type_2 = self.get_addr_type(save_loc_addr)

        try:
            semantic_cube[validation_type_1]['='][validation_type_2]
        except:
             raise TypeError(f'Incompatible Types {validation_type_1} and {validation_type_2}')

        quadruple = {'operation': 'param', 'operand_1': operand_1_addr,
                    'operand_2': None, 'save_loc': save_loc_addr}

        self.quadruples.append(quadruple)
    
    # returns a list of tuples of the parameters of a function
    # it takes as a parameter the function name and its main use is when 
    # calling a era quadruple
    def get_era(self,func):
        try:
            
            params =  []
            keys = []

            for key in self.functions_table[func]['params'].keys():
                keys.append(key)

            for key in range(0,self.functions_table[func]['param_cont']):
                params.append(keys[key])

        except KeyError as err:

            raise KeyError('Not function found ' , str(err))

        return params


    # Verify id the current fucntion has the correct numbers of parameters    
    # it does not take any parameters, it takes the object current function
    # and it does not return any value
    def verify_params_num(self):
        params_number = len(self.get_era(self.func_call_stack[-1]))
        params_give = self.param_count
        if params_number != params_give: # if the stack of params is empty menas you have too much parameters
            raise IndexError('Missing Params in function '+ str(self.func_call_stack[-1]) )


    # returns the current param memeory address 
    # it takas as a parameter the fucntion name
    def get_curr_param_addr(self,func):


        era = list(reversed(self.get_era(func)))
        try:
            current_param  = era[self.param_count]
        except IndexError:
            raise IndexError('Too many arguments in function '+func)
        var = current_param[1]
        return var


    # inserts a gosub quadruple
    # it requires the function that has been called
    # it does not have a return value
    def insert_gosub_quadruple(self,subfunc):

        quadruple = {'operation': 'gosub', 'operand_1': None,
                    'operand_2': None, 'save_loc': subfunc}

        self.quadruples.append(quadruple)

    # inserts a function to the the functions table, it requieres a fuction name the function type and the quadruple
    # in which it starts. It will also insert a global variable in case it is no a void function 
    def insert_func(self,function_name,function_type,init):
        
        if function_name in self.functions_table.keys():
            raise KeyError("Function " + function_name + " already exists")

        if function_type != 'void':
            self.insert_variable(function_name,function_type,'global')
            self.last_temp.pop(-1)
            
            glob_var_key =(function_name,self.get_var_addr(function_name))
            new_glob_var = self.variables_table[glob_var_key]
            
            self.functions_table[self.program_id]['params'].update({glob_var_key:new_glob_var})

        function = {function_name: {'type': function_type,'memory_usage':None ,'params':None,'init':init}}
        self.functions_table.update(function)


    # update func will update the parameters and the variables used for this function after the expresion for the arguments 
    # are decalred 
    def update_func(self, function_name,param_count):


        try:
            #base_glob,top_glob = self.get_range('global')

            #memory_usage = self.get_func_memory_usage()

            params_table = copy.deepcopy(self.variables_table_func)
            self.functions_table[function_name]['params']= params_table
            self.functions_table[function_name]['param_cont']= param_count

            func_variables = []

            for func in list(self.functions_table.keys()):
                func_variables.append(func)

            for var,addr in list(self.functions_table[function_name]['params'].keys()):

                if var in func_variables:

                    addr = self.get_var_addr(func)
                    del self.functions_table[function_name]['params'][(var,addr)]
                

            self.variables_table_func.clear()
        except KeyError as err:

            raise TypeError('Can not update function, ' + str(err))

    
    # this function will set the memory usage for each function after the quadruples of the functions have ended
    # it takes as parameter the function to update the mnemory usage 
    def update_func_memory(self, function_name):


        try:

            memory_usage = self.get_func_memory_usage()
            self.functions_table[function_name]['memory_usage']= memory_usage
            self.variables_table_func.clear()
        except KeyError as err:

            raise TypeError('Can not update function, ' + str(err))

    
    # this function inserts a operetaion to the quadruples, it can be an aritmetic operation or a boolean operation
    # it takes four arguments, operation which is the operartion to inserted, operand_1 the first operand of the operation in case
    # it is a None it will get the last temporal value, the operand_2 is the second value to execute the operation if the value is null 
    # it will get the last temporal value, and save loc is the location to save the operation result in case it is null it will genreate
    # a temporal value that will be inserted into the last_temp stack

    def insert_quadruple_operation(self, operation, operand_1=None, operand_2=None, save_loc=None):



        if operand_1 == None: # if none get last temp value
            try:

                operand_1 = list(self.last_temp[-1].keys())[0][0] # first item of dict and firt item of tuple which is var name
                operand_1_addr = list(self.last_temp[-1].keys())[0][1]
                self.last_temp.pop(-1) # pop last temp value
                              
            except:
                raise ValueError('No last temp value')
        
        
        if operand_2 == None: # if non get last temp value and pop the temporal value
            try:
                operand_2 = list(self.last_temp[-1].keys())[0][0] # first item of dict and firt item of tuple which is var name
                operand_2_addr = list(self.last_temp[-1].keys())[0][1]
                self.last_temp.pop(-1)
            except:
                raise ValueError('No last temp value')
        

        try:
            if self.get_value_type(operand_1) != 'var': # if the operand is not a varible
                
                value = operand_1
                type_1 = self.get_value_type(operand_1)
                operand_1 = 'const'+str(self.const_var_count)
                self.insert_variable(operand_1,type_1,'const',value=value)
                self.const_var_count += 1
                self.last_temp.pop(-1)

            if self.get_value_type(operand_2) != 'var': # if the operand is not a varible
                value = operand_2
                type_2 = self.get_value_type(operand_2)
                operand_2 = 'const'+str(self.const_var_count)
                self.insert_variable(operand_2,type_2,'const',value=value)
                self.const_var_count += 1
                self.last_temp.pop(-1)

        except TypeError as err:

            raise TypeError(str(err))

        self.verify_arr_operation(operand_1,operand_2)

        if self.is_arr(operand_1) and self.is_arr(operand_2):
            if self.is_mat(operand_1) and self.is_mat(operand_2):
               self.matrix_operation(operation,operand_1,operand_2)
            else:
                self.matrix_operation(operation,operand_1,operand_2,True)
            
        else:
        

            operand_1_addr = self.get_var_addr(operand_1)
            operand_2_addr = self.get_var_addr(operand_2)

            
            if save_loc == None: # if there is not a save locarion inset a temporal value to save the result

                #operand_1_scope = self.get_var_scope((operand_1,operand_1_addr))
                #operand_2_scope = self.get_var_scope((operand_2,operand_2_addr))
                save_loc = 'temp'+str(self.temp_count)
            
                temp_type,_ = self.get_var_type(operation,(operand_1,operand_1_addr),(operand_2,operand_2_addr))
                self.insert_variable(save_loc,temp_type,'temp')
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

    

    # Verify if an operation between arrays or matrixes are compatible if it is not compatible
    # it wil end the compilation and if they are compatible it will continue the compilation
    # it takes as parameter the two array or matrixes which are gonna be evaluated
    def verify_arr_operation(self,operand_1,operand_2):

        if operand_1 == None or operand_2 == None:
            return
        
        operand_1_addr = self.get_var_addr(operand_1)
        operand_2_addr = self.get_var_addr(operand_2)



        if self.is_arr(operand_1) and self.is_arr(operand_2): # if both operand are arrays or matrix

            
            if self.same_dims(operand_1,operand_2): # check if the matrix or array has the same dimension

                key1 = (operand_1,operand_1_addr)
                key2 = (operand_2,operand_2_addr)

                try:
                    if self.is_mat(operand_1) and self.is_mat(operand_2): # if both operands are matrixes
                        index1 = self.variables_table[key1]['index_1']
                        index2 = self.variables_table[key2]['index_1']

                        index1_2 = self.variables_table[key1]['index_2']
                        index2_2 = self.variables_table[key2]['index_2']

                        index1_comp =  {'operation': 'ver_dim', 'operand_1': index1,
                                        'operand_2': index2, 'save_loc': None}

                        index2_comp =  {'operation': 'ver_dim', 'operand_1': index1_2,
                                        'operand_2': index2_2, 'save_loc': None}

                        self.quadruples.append(index1_comp)
                        self.quadruples.append(index2_comp)
                    else:

                        # In this section we check that bouth of them have compatible strutures

                        if self.is_mat(operand_1) and self.is_arr(operand_2):
                            raise TypeError('Incompatible operation')

                        if self.is_arr(operand_1) and self.is_mat(operand_2):
                            raise TypeError('Incompatible operation')
                        index1 = self.variables_table[key1]['index_1']
                        index2 = self.variables_table[key2]['index_1']

                        index1_comp =  {'operation': 'ver_dim', 'operand_1': index1,
                                        'operand_2': index2, 'save_loc': None}

                        self.quadruples.append(index1_comp)

                except KeyError as err:

                    raise ValueError('Array not found',str(err))
                
            else:

                raise TypeError('Not compatible operation with matrix or array')
        
        else:

            if self.is_arr(operand_1) and not self.is_arr(operand_2):
                raise TypeError(f'Incompatible operation "{operand_1}" and "{operand_2}"')

            if not self.is_arr(operand_1) and self.is_arr(operand_2):
                raise TypeError(f'Incompatible operation "{operand_1}" and "{operand_2}"')


    # returns a string with the type result of two operand with certain operation 
    # based in the sematic cube
    # it requeires three parameters , the operation to be done, and the two operand 
    def get_var_type(self,operation, var1,var2):
        is_pointer = False

        try:
            type_1 = self.variables_table[var1]['type']

            if type_1 == 'pointer': # if it is a pointer get the pointer type
                type_1 = self.variables_table[var1]['pointer_type']
                is_pointer = True

            type_2 = self.variables_table[var2]['type']

            if type_2 == 'pointer': # if it is a pointer get the pointer type
                type_2 = self.variables_table[var2]['pointer_type']
                is_pointer = True
        except KeyError as err:
            raise KeyError(str(err) + ' does not exists')

        try:
            type_res_var = semantic_cube[type_1][operation][type_2] # check in the semantic cube if the operartion is possible
                                                                    # and return the data type of the result
            return type_res_var,is_pointer
        except KeyError :
            raise TypeError('Not supported type for operands '+ var1[0] + ' and ' + var2[0])


    # returns the range of addresses of a certain scope 
    # it takes as parameter the scope that will be evaluated to get the range
    def get_range(self,scope):
        base = list(self.variables_base_memory[scope].values())[0]
        top = base + self.MEMORY_SPACE * len(self.variables_base_memory[scope]) -1
        return base,top



    # returns the variable address it will take first the local varibles if it is not defined in the local scope 
    # it will search in the global scope if it is not in the global scope 
    # it requires the variable name as a parameter
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


    # this function will reset the temp memory and will set the temp counter to 0 again 
    # it does not requiere any argument 
    # and it does not returns any value 

    def end_expression(self):

        self.temp_count = 0
        self.reset_memory('temp')


    # the main purpose of this function is to reste the memory count in case a function ends 
    # it does not require any parameters 
    # and it does not returns any values 

    def end_function(self):

        self.temp_count = 0
        self.reset_memory('temp')
        self.reset_memory('local')

    # Returns the value type of a constatn in form a string , it requieres the the constant value
    # if it is a varible it wil return the word var 
    
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


    # This fuction inserts an action quadruple such as write or write, it requeires 
    # tha action to be done, the first operand, if it is None it will recibe the last temporal value
    # and it will requiere the return id in case of a param asignation to a temporal value
    def insert_quadruple_action(self,action,operand_1=None,return_id=None):

        if type(action) == str:
            if operand_1 == None: # if operand is a temporal value
                try:
                    operand_1 = list(self.last_temp[-1].keys())[0][0] # first item of dict and firt item of tuple which is var name
                    operand_1_addr = list(self.last_temp[-1].keys())[0][1]

                
                except:
                    raise ValueError('No last temp value for action type')
            else:

                try: 
                    if self.get_value_type(operand_1) != 'var': # if varible is a constant
                        value = operand_1
                        type_1 = self.get_value_type(operand_1)
                        operand_1 = 'const'+str(self.const_var_count)
                        self.insert_variable(operand_1,type_1,'const',value = value)
                        self.const_var_count += 1
                        self.last_temp.pop(-1)

                except TypeError as err:

                    raise TypeError(str(err))


                operand_1_addr = self.get_var_addr(operand_1)

            if return_id != None: # if it is param igualation to a global variable of a fucntion 
                return_id = self.get_var_addr(return_id)

            quadruple = {'operation': action, 'operand_1': operand_1_addr,
                            'operand_2': None, 'save_loc': return_id}

            self.quadruples.append(quadruple)
            
    # This fucntion asings the a value to a varible by a quadruple, it takes saving location where the value will be stpred
    #  the second argument is the value to be stores in case it is None it will take the last temporal value
    # it does not have a return value
    def insert_quadruple_asignation(self,save_loc,operand_1=None,return_val=False):
        
        if operand_1 == None: # if operand is a temp value
            try:
                operand_1 = list(self.last_temp[-1].keys())[0][0] # first item of dict and firt item of tuple which is var name
                operand_1_addr = list(self.last_temp[-1].keys())[0][1]
                self.last_temp.pop(-1)
                
            except:
                raise ValueError('No last temp value')
        
        try:
            if self.get_value_type(operand_1) != 'var': # if operand is a constant
                value = operand_1
                type_1 = self.get_value_type(operand_1)
                operand_1 = 'const'+str(self.const_var_count)
                self.insert_variable(operand_1,type_1,'const',value = value)
                self.const_var_count += 1
                self.last_temp.pop(-1)
        except TypeError as err:

            raise TypeError(str(err))
        
        

        self.verify_arr_operation(save_loc,operand_1)

        if self.is_arr(save_loc) and self.is_arr(operand_1): # if operands are arrays or matrix
            if self.is_mat(save_loc) and self.is_mat(operand_1): # if operand are matrixes
               self.matrix_asignation(save_loc,operand_1)
            else:
                self.matrix_asignation(save_loc,operand_1,True)

#            self.last_temp.pop(-1)
        else:
            operand_1_addr = self.get_var_addr(operand_1)

            validation_type_1 = self.variables_table[(operand_1,operand_1_addr)]['type']
            
            if validation_type_1 == 'pointer':
                validation_type_1 = self.variables_table[(operand_1,operand_1_addr)]['pointer_type']
            
            

            if save_loc == None: # if there is not a save value create a temporal value
    
                save_loc = 'temp'+str(self.temp_count)
                temp_type = validation_type_1
                self.insert_variable(save_loc,temp_type,'temp')
                self.temp_count += 1

            
            save_loc_addr = self.get_var_addr(save_loc)
            validation_type_2 = self.variables_table[(save_loc,save_loc_addr)]['type']

            if validation_type_2 == 'pointer':
                validation_type_2 = self.variables_table[(save_loc,save_loc_addr)]['pointer_type']

            try:
                semantic_cube[validation_type_2]['='][validation_type_1]
            except:
                raise TypeError(f'Incompatible Types {validation_type_1} and {validation_type_2}')



            quadruple = {'operation': '=', 'operand_1': operand_1_addr,
                            'operand_2': None, 'save_loc': save_loc_addr}

            #self.last_temp.pop(-1)

            self.quadruples.append(quadruple)
        
    # this function generates goto quadruple,it takes the quadruples to jump, it could be None and be set later on 
    # as the second parameter it takes the operand 1 which is a boolean expresion to be evaluates in the condition of 
    # the goto in case it exists , and the last parameter is the goto type in case it is a False it will insert a gotof
    # in case it is true it will insert a gotof and if it is none it will insert a goto
    # it does not have a return value

    def insert_quadruple_goto(self,quadruple_num=None,operand_1=None,goto_type=None):


        if operand_1 == None and goto_type != None:
            try:
                operand_1 = list(self.last_temp[-1].keys())[0][0] # first item of dict and firt item of tuple which is var name
                operand_1_addr = list(self.last_temp[-1].keys())[0][1]
                self.last_temp.pop(-1)
                           
            except:
                raise ValueError('No last temp value')
        
        else:
            if operand_1 != None:

                try:
                    if self.get_value_type(operand_1) != 'var':
                        value = operand_1
                        type_1 = self.get_value_type(operand_1)
                        operand_1 = 'const'+str(self.const_var_count)
                        self.insert_variable(operand_1,type_1,'const',value = value)
                        self.const_var_count += 1
                        self.last_temp.pop(-1)
                except TypeError as err:

                    raise TypeError(str(err))

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
        self.quadruples.append(quadruple)
        self.goto_quadruples_stack.append(self.quadruples[-1])


    # this function returns a variable type in form of a string, it searches the address value in the different ranges of the base 
    # memory for each type and scope, it requieres as a parameter the variable to be search

    def get_variable_type(self, var):

        addr = self.get_var_addr(var)


        for scope in self.variables_base_memory.keys():
            for type_var in self.variables_base_memory[scope].keys():
                base = self.variables_base_memory[scope][type_var]
                top = base + self.MEMORY_SPACE -1
                if base <= addr <= top:

                    if type_var  == 'pointer':
                        type_var = self.variables_table[(var,addr)]['pointer_type']
                    return type_var

    
    
    # returns the type of the address of a variable in case it does not exists it will return error
    # as a parameter it requieres the address to serch in the ranges 
    def get_addr_type(self, addr):


        for scope in self.variables_base_memory.keys():
            for type_var in self.variables_base_memory[scope].keys():
                base = self.variables_base_memory[scope][type_var]
                top = base + self.MEMORY_SPACE -1
                if base <= addr <= top:
                    if type_var  == 'pointer':
                        
                        for var_name,addr_saved in self.variables_table.keys():
                            if addr == addr_saved:
                                var = var_name 

                        type_var = self.variables_table[(var,addr)]['pointer_type']
                    return type_var


    # This is an auxiliar function to help as print formated the json data converting a tuple to a string
    # it takes as a parameter a the data to convert the keys into strings
    # it returns the data formated 
    def key_to_json(self,data):
        if data is None or isinstance(data, (bool, int, str)):
            return data
        if isinstance(data, (tuple, frozenset)):
            return str(data)
        raise TypeError

    
    def to_json(self,data):
        if data is None or isinstance(data, (bool, int, tuple, range, str, list)):
            return data
        if isinstance(data, (set, frozenset)):
            return sorted(data)
        if isinstance(data, dict):
            return {self.key_to_json(key): self.to_json(data[key]) for key in data}
        raise TypeError


    # simple function to print the quadruples the variables and the functions tables in thath order and formated
    # it does not take any arguments and it is call when the compiling ends
    def print_quadruples(self):

        print('============ Quadruples table =============')
        for cont,quadruple in zip(range(0,len(self.quadruples)),self.quadruples):
            print(cont,quadruple)
            cont += 1

        print('============ Variables table =============')
        for var in self.variables_table.keys():
            print(var,json.dumps(self.variables_table[var],sort_keys=True,
                                                            indent=4,
                                                            separators=(',', ': ')))

        print('============ Functions table =============')
        for func in self.functions_table.keys():
            print(func,json.dumps(self.to_json(self.functions_table[func]),sort_keys=True,
                                                            indent=4,
                                                            separators=(',', ': ')))

        print('============ Base Variables table =============')
        print(json.dumps(self.variables_base_memory,sort_keys=True,
                                                            indent=4,
                                                            separators=(',', ': ')))


    # function to insert a ver quadruple which compare a value if it is in a range of the index and the base
    # it takes as parameters the array name to get the the dimensions, as the second parameter it will take the value to evaluate 
    # if is inside the range, and the last parameter is the dimension in which is currently working, if it is true it means
    # that is currenty working on the first dimension, in case it is false it means it is working on the second dimension

    def insert_ver_quadruple(self,arr_name,operand_1=None,dim1=True):
        
        t = False

        if operand_1 == None: # if expression on the the array is None it will take the last value
            try:
                operand_1 = list(self.last_temp[-1].keys())[0][0] # first item of dict and firt item of tuple which is var name
                operand_1_addr = list(self.last_temp[-1].keys())[0][1]
                t = True
                
            except:
                raise ValueError('No last temp value')

        
        try:
            if self.get_value_type(operand_1) != 'var':
                value = operand_1
                type_1 = self.get_value_type(operand_1)
                operand_1 = 'const'+str(self.const_var_count)
                self.insert_variable(operand_1,type_1,'const',value = value)
                self.const_var_count += 1
                t = True

            if not t:
                operand_1_addr = self.get_var_addr(operand_1)
                self.last_temp.append({(operand_1,operand_1_addr):self.variables_table[(operand_1,operand_1_addr)]})      

        except TypeError as err:

            raise TypeError(str(err))

        operand_1_addr = self.get_var_addr(operand_1)
           

        var_addr = self.get_var_addr(arr_name)
        var = (arr_name,var_addr)


        try:
            #base = self.get_var_addr(arr_name)
            #curr_var = (arr_name,base)
            #m1 = self.variables_table[curr_var]['m1']
            if dim1 == True:
                
                index = self.variables_table[var]['index_1']
                
            else:
                index = self.variables_table[var]['index_2']
               # m2 = self.variables_table[curr_var]['m2']
        except KeyError as err:

            raise IndexError('Wrong index in array' + str(err))

        base_0 = 'const0'
        base_0_addr = self.get_var_addr(base_0)

        quadruple = {'operation':'ver','operand_1':operand_1_addr,'operand_2':base_0_addr,'save_loc':index}
        self.quadruples.append(quadruple)
    

    # this function inserts a sum quadruple, but is not a common sum quadruple it takes as parameter the array and the expresion
    # this plus fuction is meant to be used in to add the base address and the index expression
    # it does not return any value
    def insert_plus_quadruple(self,arr,operand_1=None):
        
        if operand_1 == None:
            try:
                operand_1 = list(self.last_temp[-1].keys())[0][0] # first item of dict and firt item of tuple which is var name
                operand_1_addr = list(self.last_temp[-1].keys())[0][1]
                self.last_temp.pop(-1)
            except:
                raise ValueError('No last tmep value')

        try:
            if self.get_value_type(operand_1) != 'var':
                
                value = operand_1
                type_1 = self.get_value_type(operand_1)
                operand_1 = 'const'+str(self.const_var_count)
                self.insert_variable(operand_1,type_1,'const',value=value)
                self.const_var_count += 1
                self.last_temp.pop(-1)


        except TypeError as err:

            raise TypeError(str(err))
        
        operand_1_addr = self.get_var_addr(operand_1)

        save_loc = 'temp'+str(self.temp_count)
        temp_type = 'pointer'
        self.insert_variable(save_loc,temp_type,'temp',value= operand_1_addr)
        #new_var = (save_loc , self.memory_count['temp'][temp_type]-1)#the variable count has increase so take one from the memory count
        #newTemp = {new_var:{'type':temp_type}}
        #self.last_temp.append(newTemp)
        self.temp_count += 1
        save_loc_addr = self.get_var_addr(save_loc)
        
        base_name = 'base_'+arr 
        base = self.get_var_addr(arr)
        try: 
            self.insert_variable('base_'+arr ,temp_type,'const',value=base)
            base_addr = self.get_var_addr(base_name)
            self.last_temp.pop(-1)
        except KeyError:
            pass

        base_addr = self.get_var_addr(base_name)
            
        quadruple = {'operation':'+','operand_1':base_addr,'operand_2':operand_1_addr,'save_loc':save_loc_addr}

        
        self.quadruples.append(quadruple)
  
    
    # Inserts a multiplication quadruple for the m value and the array expression, it takes as parameters two values 
    # the array that we are indexing and the expression to be multiply by the m values
    # it does not have return value
    def insert_times_quadruple(self,arr,operand_1=None):

 

        if operand_1 == None:
            try:
                operand_1 = list(self.last_temp[-1].keys())[0][0] # first item of dict and firt item of tuple which is var name
                operand_1_addr = list(self.last_temp[-1].keys())[0][1]
                self.last_temp.pop(-1)
            except:
                raise ValueError('No last temp value')


         
        try:
            if self.get_value_type(operand_1) != 'var':
                value = operand_1
                type_1 = self.get_value_type(operand_1)
                operand_1 = 'const'+str(self.const_var_count)
                self.insert_variable(operand_1,type_1,'const',value = value)
                self.const_var_count += 1
                self.last_temp.pop(-1)


        except TypeError as err:

            raise TypeError(str(err))


        operand_1_addr = self.get_var_addr(operand_1)

        save_loc = 'temp'+str(self.temp_count)
        temp_type = 'int'
        self.insert_variable(save_loc,temp_type,'temp',value=operand_1_addr)
        #new_var = (save_loc , self.memory_count['temp'][temp_type]-1)#the variable count has increase so take one from the memory count
        #newTemp = {new_var:{'type':temp_type}}
        #self.last_temp.append(newTemp)
        self.temp_count += 1
        save_loc_addr = self.get_var_addr(save_loc)


        base = self.get_var_addr(arr)
        var = (arr,base)
        m1 = self.variables_table[var]['m1']
        quadruple = {'operation':'*','operand_1':m1,'operand_2':operand_1_addr,'save_loc':save_loc_addr}
        self.quadruples.append(quadruple)
      
           
    # Inserts a sum quadruple, meant to use to sum the previous indexed value to the the second dimension value 
    # it takes as parameters the array to be indexed the expression of the second index of the matrix and the value of
    # the previos index, it does not have a return value

    def insert_plus_quadruple_dim2(self,arr,operand_1=None,dim1=None):

        if operand_1 == None:
            try:
                operand_1 = list(self.last_temp[-1].keys())[0][0] # first item of dict and firt item of tuple which is var name
                operand_1_addr = list(self.last_temp[-1].keys())[0][1]
                self.last_temp.pop(-1)


            except:
                raise ValueError('No last temp value')

        try:
            if self.get_value_type(operand_1) != 'var':
                
                value = operand_1
                type_1 = self.get_value_type(operand_1)
                operand_1 = 'const'+str(self.const_var_count)
                self.insert_variable(operand_1,type_1,'const',value=value)

                self.const_var_count += 1
                self.last_temp.pop(-1)



        except TypeError as err:

            raise TypeError(str(err))
        
        operand_1_addr = self.get_var_addr(operand_1)
        dim1_addr = self.get_var_addr(dim1)
        

        save_loc = 'temp'+str(self.temp_count)
        temp_type = 'int'
        self.insert_variable(save_loc,temp_type,'temp',value=operand_1_addr)
        self.temp_count += 1
        save_loc_addr = self.get_var_addr(save_loc)




        quadruple = {'operation':'+','operand_1':dim1_addr,'operand_2':operand_1_addr,'save_loc':save_loc_addr}

        
        self.quadruples.append(quadruple)
        # 
     
               
    # Determines if the variable is an array or matrix , it takes as parameter the the array name
    # it returns a true in case the variable is an array or matrix, false in case it not

    def is_arr(self,arr_name):

        try:

            arr_addr = self.get_var_addr(arr_name)
            key = (arr_name,arr_addr)
            m1 = 'm1'
        except:
            return False

        if m1 in list(self.variables_table[key].keys()) :

            return True
        else :

            return False


    #  Determines if the variable is a matrix , it takes as parameter the variable name
    # it returns a true if the variable is a matrix, false if its not


    def is_mat(self,mat_name):

        try:
            arr_addr = self.get_var_addr(mat_name)
            key = (mat_name,arr_addr)
            m1 = 'm1'
            m2 = 'm2'
        
        except:
            return False

        if m1 in list(self.variables_table[key].keys()) and m2 in list(self.variables_table[key].keys()) :

            return True
        else :

            return False


    # function to determine if the arrays or matrixes have the same dimension , it takes as parameters the name of the two variables to 
    # evaluate, in case they are the same dimension it would return true in case they have different dimension it would return false
    def same_dims(self,arr_1,arr_2):

        arr_1_addr = self.get_var_addr(arr_1)
        arr_2_addr = self.get_var_addr(arr_2)

        var1 = (arr_1,arr_1_addr)
        var2 = (arr_2,arr_2_addr)


        try:
            var1_obj = self.variables_table[var1]
            var2_obj = self.variables_table[var2]

        except KeyError as err:
            raise KeyError('Array not found',str(err))
        

        var1_keys = list(var1_obj.keys())
        var2_keys = list(var2_obj.keys())

        if len(var1_keys) != len(var2_keys):
            return False

        return True


    # this function will apply a modifier to a matrix in case it is one of the modifiers valids, inverse of a matrix , determinant of a matrix 
    # or the transpose of a matrix , it does not have a return value
    def apply_modifier(self,mat,mod):
        
        if mod == '?':
            self.inverse_modify(mat)
        elif mod == '!':
            self.transpose_modify(mat)
        elif mod == '$':
            self.determinant_modify(mat)
        else:
            raise KeyError('modifier not found')


    # This funciton has two main parts, first it wil generate a temporal matrix with the 
    # requierd dims for the modifier , after this it will insert a modifier quadruple
    # it does no have a return value 

    def transpose_modify(self,mat):
        
        mat_addr = self.get_var_addr(mat)
        mat_type = self.get_variable_type(mat)
        key = (mat,mat_addr)
        try:
            var_obj = copy.deepcopy(self.variables_table[key])

        except KeyError:
            raise KeyError('Matrix not found')

        index1 = var_obj['index_1']
        index2 = var_obj['index_2']

        if index1 != index1:
            raise IndexError('Matrix must be n x n dims')

        var_obj['index_1'] = index2
        var_obj['index_2'] = index1

        temp_mat_key  = self.insert_temp_mat(mat_type,index1,index2,var_obj)
        quadruple = {'operation':'transpose','operand_1':mat_addr,'operand_2':None,'save_loc':temp_mat_key[1]}
        self.last_temp.append({temp_mat_key:self.variables_table[temp_mat_key]})
        self.quadruples.append(quadruple)
 
        

    # This funciton has two main parts, first it wil generate a temporal matrix with the 
    # requierd dims for the modifier , after this it will insert a modifier quadruple
    # it does no have a return value 
    def inverse_modify(self,mat):
        mat_addr = self.get_var_addr(mat)
        mat_type = self.get_variable_type(mat)
        key = (mat,mat_addr)
        try:
            var_obj = copy.deepcopy(self.variables_table[key])
        except KeyError:
            raise KeyError('Matrix not found')

        index1 = var_obj['index_1']
        index2 = var_obj['index_2']


        if self.get_variable_type(mat) != 'float':
            raise TypeError('Can only inverse a float matrix')

        temp_mat_key  = self.insert_temp_mat(mat_type,index1,index2,var_obj)
        quadruple = {'operation':'inverse','operand_1':mat_addr,'operand_2':None,'save_loc':temp_mat_key[1]}
        self.last_temp.append({temp_mat_key:self.variables_table[temp_mat_key]})
        self.quadruples.append(quadruple)
       


    # This funciton has two main parts, first it wil generate a temporal matrix with the 
    # requierd dims for the modifier , after this it will insert a modifier quadruple
    # it does no have a return value 
    def determinant_modify(self,mat):
        mat_addr = self.get_var_addr(mat)
        mat_type = self.get_variable_type(mat)
        key = (mat,mat_addr)
        try:
            var_obj = copy.deepcopy(self.variables_table[key])
        except KeyError:
            raise KeyError('Matrix not found')

        index1 = var_obj['index_1']
        index2 = var_obj['index_2']

        if index1 != index1:
            raise IndexError('Matrix must be n x n dims')

        save_loc = 'temp'+str(self.temp_count)
        temp_type = 'float'
        self.insert_variable(save_loc,temp_type,'temp')
        self.temp_count += 1
        save_loc_addr = self.get_var_addr(save_loc)
    
        
        quadruple = {'operation':'determinant','operand_1':mat_addr,'operand_2':None,'save_loc':save_loc_addr}
        self.quadruples.append(quadruple)



    # Inserts a temporal matrix in the the variables table for usage in the modifiers 
    # it takes as parameters the matrix type , and as optional values the dimension of the matrix in case they are None
    # it is necesay to send the array or matrix configuration in the last parameter 

    def insert_temp_mat(self,mat_type,dim1=None, dim2=None,arr_conf=None):

        temp_mat = 'temp'+str(self.temp_count)
        self.insert_variable(temp_mat,mat_type,'temp',param=False,dim1=dim1,dim2=dim2,arr_conf=arr_conf)
        temp_mat_addr = self.get_var_addr(temp_mat)
        newVar = (temp_mat,temp_mat_addr)
        self.temp_count += 1

        return newVar
    


    # This function provides matrix and array operations quadruples meant to use in overloads operations
    # it takes as parameters the operation which has a limitation of +,-,* and the two matrixs or arrays 
    # to make the operation, and the last parameter takes in account if the operations are array as defaoult it is false

    def matrix_operation(self,operation, mat_1, mat_2, arr=False):
        
        mat_1_addr = self.get_var_addr(mat_1)
        mat2_addr  = self.get_var_addr(mat_2)
        mat1_type = self.get_variable_type(mat_1)
        mat2_type = self.get_variable_type(mat_2)

        

        if mat1_type == 'pointer':
            mat1_type_val = self.variables_table[(mat_1,mat_1_addr)]['pointer_type']

        if mat2_type == 'pointer':
            mat2_type_val = self.variables_table[(mat_2,mat2_addr)]['pointer_type']

        try:
            semantic_cube[mat1_type][operation][mat2_type]

        except KeyError:

            raise TypeError(f'Not compatible types for "{mat1_type_val}" and "{mat2_type_val}"')

        key1 = (mat_1,mat_1_addr)
        key2 = (mat_2,mat2_addr)
        if operation not in self.supported_arr_op:
            raise TypeError(f'Not supported operation "{operation}" for {mat_1} and {mat_2}')

        try:
            var_obj1 = copy.deepcopy(self.variables_table[key1])
            var_obj2 = copy.deepcopy(self.variables_table[key2])
        except KeyError:
            raise KeyError('Matrix not found')

        index1 = var_obj1['index_1']
        index2 = None
        if arr == False:
            index2 = var_obj2['index_2']

        type_op = 'mat'
        if arr == True:
            type_op = 'arr'

        temp_mat_key  = self.insert_temp_mat(mat1_type,index1,index2,var_obj1)
        quadruple =  {'operation':operation+ type_op,'operand_1':mat_1_addr,'operand_2':mat2_addr,'save_loc':temp_mat_key[1]}
        self.last_temp.append({temp_mat_key:self.variables_table[temp_mat_key]})
        self.quadruples.append(quadruple)
      

    # Function to asing one matrix or array to other arary or matrix respectebly menas tha you can only asing a mtrix to a 
    # matrix and an array to an array , it take 3 parameters , the first are  two matrixs or arrays 
    # which are the operators, and the last parameter takes in account if the operations are array as defaoult it is false

    def matrix_asignation(self, mat_1, mat_2,arr=False):
        
        mat_1_addr = self.get_var_addr(mat_1)
        mat2_addr  = self.get_var_addr(mat_2)
        mat1_type = self.get_variable_type(mat_1)
        mat2_type = self.get_variable_type(mat_2)
        

        try:
            semantic_cube[mat1_type]['='][mat2_type]

        except KeyError:

            raise TypeError(f'Not compatible types for "{mat1_type}" and "{mat2_type}"')

        key1 = (mat_1,mat_1_addr)
        key2 = (mat_2,mat2_addr)

        try:
            _ = copy.deepcopy(self.variables_table[key1])
            _ = copy.deepcopy(self.variables_table[key2])
        except KeyError:
            raise KeyError('Matrix not found')

        type_op = 'mat'
        if arr == True:
            type_op = 'arr'

        quadruple =  {'operation':'='+type_op,'operand_1':mat2_addr,'operand_2':None,'save_loc':mat_1_addr}
        self.quadruples.append(quadruple)
       


    # This function will return the value or variable type in form of string 
    # if it is a pointer it will return the pointer type, it takes the expression to be evaluated
    # if the expression is none it will get the last temporal value
    def check_exp_type(self, operand_1):
        
        if operand_1 == None:
            try:
                operand_1 = list(self.last_temp[-1].keys())[0][0] # first item of dict and firt item of tuple which is var name
                operand_1_addr = list(self.last_temp[-1].keys())[0][1]
            except:
                raise ValueError('No last temp value')

        try:
            if self.get_value_type(operand_1) != 'var':
                
                #value = operand_1
                type_1 = self.get_value_type(operand_1)
                return type_1


        except TypeError as err:

            raise TypeError(str(err))
        
        operand_1_addr = self.get_var_addr(operand_1)
        res_type = self.get_addr_type(operand_1_addr)
        if res_type == 'pointer':
            key = (operand_1,operand_1_addr)
            res_type = self.variables_table[key]['pointer_type']
     
        
        return res_type



    # This function returns the constant value of based on an address, if it does not exists it will 
    # return None other wise it will return the value saved on the constant table
    # it takes as parameter the address to search 
    def get_const_value(self,addr):

        for name,addr_ in list(self.variables_table.keys()):

            if addr_ == addr:
                return (name,addr_)
        
        return None


    # This fucntion exports the constants, the functions table the quadruples and the base memory table into 
    # binary object files in the obj folder if it does not exists it will create this directory
    # it does not have a return value and it is used when the compilation has ended
    def export_to_obj(self):
        if not os.path.exists('obj'):
            os.makedirs('obj')

        with open('obj/quadruples.dictionary', 'wb') as config_dictionary_file:
 
            pickle.dump(self.quadruples, config_dictionary_file)

        with open('obj/functions.dictionary', 'wb') as config_dictionary_file:
 
            pickle.dump(self.functions_table, config_dictionary_file)

        with open('obj/variables.dictionary', 'wb') as config_dictionary_file:
 
            pickle.dump(self.variables_table, config_dictionary_file)

        with open('obj/base_memory.dictionary', 'wb') as config_dictionary_file:
 
            pickle.dump(self.variables_base_memory, config_dictionary_file)