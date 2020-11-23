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

            self.current_func = None

        except KeyError as err:

            raise TypeError('No memory type found, ' + str(err))

    def insert_variable(self, variable_name, variable_type, scope, param=False, dim1=None,dim2=None,value=None,arr_conf=None):

        dims = {}

        if arr_conf != None:
            dims.update(arr_conf)
        else:

            if dim1 != None:
                
                if dim2 == None:

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
                    
                else:
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

            for var,addr in list(self.variables_table.keys()):
                if base <= addr <= top and var == variable_name:
                    raise KeyError('Variable ' + var + ' already exists')

            variable = {new_variable: {'type': variable_type}}

            if variable_type == 'pointer':
                
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
            
            if dim1 == None:
                self.memory_count[scope][variable_type] += 1
            else:
                if dim2 != None:
                    if arr_conf == None:
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

    def get_func_memory_usage(self):
        res = {'temp':{'int':0,'float':0,'char':0,'bool':0,'pointer':0},
                'local':{'int':0,'float':0,'char':0,'bool':0,'pointer':0}}

        

        for var in self.variables_table.keys():
            if var not in self.variables_table_func:
                
                base_glob,top_glob = self.get_range('global')
                base_const,top_const = self.get_range('const')
                base_temp,top_temp = self.get_range('temp')
                base_local,top_local = self.get_range('local')
                if var[1] not in range(base_glob,top_glob) and var[1] not in range(base_const,top_const):
                    
                    if var[1] in range(base_temp,top_temp):
                        if 'size' in self.variables_table[var].keys():
                            res['temp'][self.variables_table[var]['type']] += self.variables_table[var]['size']
                        else:
                            res['temp'][self.variables_table[var]['type']] += 1

                    if var[1] in range(base_local,top_local):
                        if 'size' in self.variables_table[var].keys():
                            res['local'][self.variables_table[var]['type']] += self.variables_table[var]['size']
                        else:
                            res['local'][self.variables_table[var]['type']] += 1


        return res

    def insert_func_quadruple(self,operation,func=None):

        quadruple = {'operation': operation, 'operand_1': None,
                    'operand_2': None, 'save_loc': func}

        self.quadruples.append(quadruple)
        print(self.last_temp)
        print(quadruple)

    def insert_param_quadruple(self,operand_1,save_loc):

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
        save_loc_addr = save_loc

        
        validation_type_1 = self.variables_table[(operand_1,operand_1_addr)]['type']

        if validation_type_1 == 'pointer':
            validation_type_1 = self.variables_table[(operand_1,operand_1_addr)]['pointer_type']

        validation_type_2 = self.get_addr_type(save_loc_addr)

        try:
            semantic_cube[validation_type_1]['='][validation_type_2]
        except:
             raise TypeError(f'Incompatible Types {validation_type_1} and {validation_type_2}')

        quadruple = {'operation': 'param', 'operand_1': operand_1_addr,
                    'operand_2': None, 'save_loc': save_loc_addr}

        self.quadruples.append(quadruple)
        print(self.last_temp)
        print(quadruple)

    
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

    def verify_params_num(self):
        params_number = len(self.get_era(self.func_call_stack[-1]))
        params_give = self.param_count
        if params_number != params_give:
            raise IndexError('Missing Params in function '+ str(self.func_call_stack[-1]) )

    def get_curr_param_addr(self,func):


        era = list(reversed(self.get_era(func)))
        try:
            current_param  = era[self.param_count]
        except IndexError:
            raise IndexError('Too many arguments in function '+func)
        var = current_param[1]
        return var


    def insert_gosub_quadruple(self,subfunc):

        quadruple = {'operation': 'gosub', 'operand_1': None,
                    'operand_2': None, 'save_loc': subfunc}

        self.quadruples.append(quadruple)
        # print(self.last_temp)
        print(quadruple)


    def insert_func(self,function_name,function_type,init):
        
        if function_name in self.functions_table.keys():
            raise KeyError("Function " + function_name + " already exists")

        if function_type != 'void':
            self.insert_variable(function_name,function_type,'global')
            self.last_temp.pop(-1)
            print(self.last_temp)
            
            glob_var_key =(function_name,self.get_var_addr(function_name))
            new_glob_var = self.variables_table[glob_var_key]
            
            self.functions_table[self.program_id]['params'].update({glob_var_key:new_glob_var})

        function = {function_name: {'type': function_type,'memory_usage':None ,'params':None,'init':init}}
        self.functions_table.update(function)


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


    def update_func_memory(self, function_name):


        try:

            memory_usage = self.get_func_memory_usage()
            self.functions_table[function_name]['memory_usage']= memory_usage
            self.variables_table_func.clear()
        except KeyError as err:

            raise TypeError('Can not update function, ' + str(err))


    def insert_quadruple_operation(self, operation, operand_1=None, operand_2=None, save_loc=None):



        print(self.last_temp,operation)
        if operand_1 == None:
            try:

                operand_1 = list(self.last_temp[-1].keys())[0][0] # first item of dict and firt item of tuple which is var name
                operand_1_addr = list(self.last_temp[-1].keys())[0][1]
                self.last_temp.pop(-1)
                              
            except:
                raise ValueError('No last temp value')
        
        
        if operand_2 == None:
            try:
                operand_2 = list(self.last_temp[-1].keys())[0][0] # first item of dict and firt item of tuple which is var name
                operand_2_addr = list(self.last_temp[-1].keys())[0][1]
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

            if self.get_value_type(operand_2) != 'var':
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

            
            if save_loc == None:

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
                # print(self.last_temp)
                print(quadruple)
            except KeyError as err:
                raise KeyError('Var  does not exists in table, ' + str(err))

    
    def verify_arr_operation(self,operand_1,operand_2):

        if operand_1 == None or operand_2 == None:
            return
        
        operand_1_addr = self.get_var_addr(operand_1)
        operand_2_addr = self.get_var_addr(operand_2)



        if self.is_arr(operand_1) and self.is_arr(operand_2):

            
            if self.same_dims(operand_1,operand_2):

                key1 = (operand_1,operand_1_addr)
                key2 = (operand_2,operand_2_addr)

                try:
                    if self.is_mat(operand_1) and self.is_mat(operand_2):
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


    def get_var_type(self,operation, var1,var2):
        is_pointer = False

        try:
            type_1 = self.variables_table[var1]['type']

            if type_1 == 'pointer':
                type_1 = self.variables_table[var1]['pointer_type']
                is_pointer = True

            type_2 = self.variables_table[var2]['type']

            if type_2 == 'pointer':
                type_2 = self.variables_table[var1]['pointer_type']
                is_pointer = True
        except KeyError as err:
            raise KeyError(str(err) + ' does not exists')

        try:
            type_res_var = semantic_cube[type_1][operation][type_2]
            return type_res_var,is_pointer
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

    def insert_quadruple_action(self,action,operand_1=None,return_id=None):

        if type(action) == str:
            if operand_1 == None:
                try:
                    operand_1 = list(self.last_temp[-1].keys())[0][0] # first item of dict and firt item of tuple which is var name
                    operand_1_addr = list(self.last_temp[-1].keys())[0][1]

                
                except:
                    raise ValueError('No last temp value for action type')
            else:

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

            if return_id != None:
                return_id = self.get_var_addr(return_id)

            quadruple = {'operation': action, 'operand_1': operand_1_addr,
                            'operand_2': None, 'save_loc': return_id}

            self.quadruples.append(quadruple)
            # print(self.last_temp)
            print(quadruple)
    
    def insert_quadruple_asignation(self,save_loc,operand_1=None,return_val=False):
        
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
        
        

        self.verify_arr_operation(save_loc,operand_1)

        if self.is_arr(save_loc) and self.is_arr(operand_1):
            if self.is_mat(save_loc) and self.is_mat(operand_1):
               self.matrix_asignation(save_loc,operand_1)
            else:
                self.matrix_asignation(save_loc,operand_1,True)

#            self.last_temp.pop(-1)
        else:
            operand_1_addr = self.get_var_addr(operand_1)

            validation_type_1 = self.variables_table[(operand_1,operand_1_addr)]['type']
            
            if validation_type_1 == 'pointer':
                validation_type_1 = self.variables_table[(operand_1,operand_1_addr)]['pointer_type']
            
            

            if save_loc == None:
    
                save_loc = 'temp'+str(self.temp_count)
                temp_type = validation_type_1
                self.insert_variable(save_loc,temp_type,'temp')
                self.temp_count += 1

            
            save_loc_addr = self.get_var_addr(save_loc)
            validation_type_2 = self.variables_table[(save_loc,save_loc_addr)]['type']

            if validation_type_2 == 'pointer':
                validation_type_2 = self.variables_table[(save_loc,save_loc_addr)]['pointer_type']

            try:
                
                semantic_cube[validation_type_1]['='][validation_type_2]
            except:
                raise TypeError(f'Incompatible Types {validation_type_1} and {validation_type_2}')



            quadruple = {'operation': '=', 'operand_1': operand_1_addr,
                            'operand_2': None, 'save_loc': save_loc_addr}

            #self.last_temp.pop(-1)

            self.quadruples.append(quadruple)
            print(self.last_temp)
            print(quadruple)


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
        print(self.last_temp)
        print(quadruple)
        self.goto_quadruples_stack.append(self.quadruples[-1])


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




    def insert_ver_quadruple(self,arr_name,operand_1=None,dim1=True):


        if operand_1 == None:
            try:
                operand_1 = list(self.last_temp[-1].keys())[0][0] # first item of dict and firt item of tuple which is var name
                operand_1_addr = list(self.last_temp[-1].keys())[0][1]
                
            except:
                raise ValueError('No last temp value')
        
        try:
            if self.get_value_type(operand_1) != 'var':
                value = operand_1
                type_1 = self.get_value_type(operand_1)
                operand_1 = 'const'+str(self.const_var_count)
                self.insert_variable(operand_1,type_1,'const',value = value)
                self.const_var_count += 1
            else:
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
        print(self.last_temp)
        print(quadruple)


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
        print(self.last_temp)
        print(quadruple)
    
    def insert_times_quadruple(self,arr,operand_1=None):

        print(arr,operand_1)
        print(self.last_temp)

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
        print(quadruple) 
        print(self.last_temp)
           


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
        print(self.last_temp) 
        print(quadruple)
               


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

    def apply_modifier(self,mat,mod):
        
        if mod == '?':
            self.inverse_modify(mat)
        elif mod == '!':
            self.transpose_modify(mat)
        elif mod == '$':
            self.determinant_modify(mat)
        else:
            raise KeyError('modifier not found')

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
        print(self.last_temp)
        print(quadruple)
        


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


    

        temp_mat_key  = self.insert_temp_mat(mat_type,index1,index2,var_obj)
        quadruple = {'operation':'inverse','operand_1':mat_addr,'operand_2':None,'save_loc':temp_mat_key[1]}
        self.last_temp.append({temp_mat_key:self.variables_table[temp_mat_key]})
        self.quadruples.append(quadruple)
        print(self.last_temp)
        print(quadruple)



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
        print(self.last_temp)
        print(quadruple)




    def insert_temp_mat(self,mat_type,dim1=None, dim2=None,arr_conf=None):

        temp_mat = 'temp'+str(self.temp_count)
        self.insert_variable(temp_mat,mat_type,'temp',param=False,dim1=dim1,dim2=dim2,arr_conf=arr_conf)
        temp_mat_addr = self.get_var_addr(temp_mat)
        newVar = (temp_mat,temp_mat_addr)
        self.temp_count += 1

        return newVar
    

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
        print(self.last_temp)
        print(quadruple)


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
        print(self.last_temp)
        print(quadruple)


    
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
            print(res_type)
        
        return res_type


    def get_const_value(self,addr):

        for name,addr_ in list(self.variables_table.keys()):

            if addr_ == addr:
                return (name,addr_)
        
        return None

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