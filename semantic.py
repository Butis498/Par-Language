from semantic_cube import semantic_cube
import copy


class Semantic():
    def __init__(self):

        self.MEMORY_SPACE = 1000
        self.next_memory_block = self.MEMORY_SPACE
        self.variables_table = {}
        self.functions_table = {}
        self.jumps_stack = [0]
        self.quadruples = []
        self.last_temp = {}
        self.temp_count = 0
        self.const_var_count = 0
        self.goto_quadruples_stack = []
        self.operand_stack = []
        self.current_func = None
        self.variables_table_func = {}
        self.param_count = 0
        self.func_call_stack = []
        self.pointer_count = 0
        
    
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

    def insert_variable(self, variable_name, variable_type, scope, param=False, dim1=None,dim2=None,value=None):

        dims = {}

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

                dims.update({'m1':m1_addr,'index_1':index_1_addr})
                
            else:
                index_1 = 'const'+str(self.const_var_count)
                self.insert_variable(index_1,'int','const',value = dim1)
                self.const_var_count += 1

                m1_value = dim1 * dim2
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

                dims.update({'m1':m1_addr,'m2':m2_addr,'index_1':index_1_addr,'index_2':index_2_addr})

        
        try:
            new_variable = (variable_name, self.memory_count[scope][variable_type])
            base ,top = self.get_range(scope)

            for var,addr in list(self.variables_table.keys()):
                if base <= addr <= top and var == variable_name:
                    raise KeyError('Variable ' + var + ' already exists')

            variable = {new_variable: {'type': variable_type}}

            
            self.variables_table.update(variable)
            self.variables_table[new_variable].update(dims)

            if scope == 'const' and value != None:
                value_const = {'value':value}
                self.variables_table[new_variable].update(value_const)

            if param:
                self.variables_table_func.update(variable)

            if self.memory_count[scope][variable_type] >= top:
                raise MemoryError('Out of memory variables')
            
            if dim1 == None:
                self.memory_count[scope][variable_type] += 1
            else:
                if dim2 != None:
                    self.memory_count[scope][variable_type] += dim1 * dim2
                else:
                    self.memory_count[scope][variable_type] += dim1

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
                        res['temp'][self.variables_table[var]['type']] += 1

                    if var[1] in range(base_local,top_local):
                        res['local'][self.variables_table[var]['type']] += 1


        return res

    def insert_func_quadruple(self,operation,func=None):

        quadruple = {'operation': operation, 'operand_1': None,
                    'operand_2': None, 'save_loc': func}

        self.quadruples.append(quadruple)

    def insert_param_quadruple(self,operand_1,save_loc):

        if operand_1 == None:
            try:
                operand_1 = list(self.last_temp.keys())[0][0] # first item of dict and firt item of tuple which is var name
                operand_1_addr = list(self.last_temp.keys())[0][1]
            except:
                raise ValueError('No last temp value')
        
        try:
            if self.get_value_type(operand_1) != 'var':
                
                type_1 = self.get_value_type(operand_1)
                operand_1 = 'const'+str(self.const_var_count)
                self.insert_variable(operand_1,type_1,'const')
                self.const_var_count += 1

        except TypeError as err:

            raise TypeError(str(err))


        operand_1_addr = self.get_var_addr(operand_1)
        save_loc_addr = save_loc

        
        validation_type_1 = self.variables_table[(operand_1,operand_1_addr)]['type']
        validation_type_2 = self.get_addr_type(save_loc_addr)

        if validation_type_1 != validation_type_2:
            raise TypeError(f'Incompatible Types {validation_type_1} and {validation_type_2}')

        quadruple = {'operation': 'param', 'operand_1': operand_1_addr,
                    'operand_2': None, 'save_loc': save_loc_addr}

        self.quadruples.append(quadruple)

    def verify_params_num(self):
        params_number = len(self.get_era(self.func_call_stack[-1]))
        params_give = self.param_count
        if params_number != params_give:
            raise IndexError('Missing Params in function '+ str(self.func_call_stack[-1]) )

    def get_era(self,func):
        try:
            params =  list(reversed(list(self.functions_table[func]['params'])))

        except KeyError as err:

            raise KeyError('Not function found ' , str(err))

        return params

    def get_curr_param_addr(self,func):


        era = self.get_era(func)
        try:
            curret_param  = era[self.param_count]
        except IndexError:
            raise IndexError('Too many arguments in function '+func)
        var = curret_param[1]
        return var


    def insert_gosub_quadruple(self,subfunc):

        quadruple = {'operation': 'gosub', 'operand_1': None,
                    'operand_2': None, 'save_loc': subfunc}

        self.quadruples.append(quadruple)


    def insert_func(self,function_name,function_type):
        
        if function_name in self.functions_table.keys():
            raise KeyError("Function " + function_name + " already exists")
        if function_type != 'void':
            self.insert_variable(function_name,function_type,'global')
        function = {function_name: {'type': function_type,'memory_usage':None ,'params':None}}
        self.functions_table.update(function)


    def update_func(self, function_name):


        try:

            memory_usage = self.get_func_memory_usage()
            params_table = copy.deepcopy(self.variables_table_func)
            self.functions_table[function_name]['params']= params_table
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
                
                value = operand_1
                type_1 = self.get_value_type(operand_1)
                operand_1 = 'const'+str(self.const_var_count)
                self.insert_variable(operand_1,type_1,'const',value=value)
                self.const_var_count += 1

            if self.get_value_type(operand_2) != 'var':
                value = operand_2
                type_2 = self.get_value_type(operand_2)
                operand_2 = 'const'+str(self.const_var_count)
                self.insert_variable(operand_2,type_2,'const',value=value)
                self.const_var_count += 1

        except TypeError as err:

            raise TypeError(str(err))

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
                        index1 = self.variables_table[key1]['index_1']
                        index2 = self.variables_table[key2]['index_1']

                        index1_comp =  {'operation': 'ver_dim', 'operand_1': index1,
                                        'operand_2': index2, 'save_loc': None}

                        self.quadruples.append(index1_comp)

                except KeyError as err:

                    raise ValueError('Array not found',str(err))
                
            else:

                raise TypeError('Not compatible operation with matrix or array')
            
        
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
                    raise ValueError('No last temp value for action type ')
            else:

                try:
                    if self.get_value_type(operand_1) != 'var':
                        value = operand_1
                        type_1 = self.get_value_type(operand_1)
                        operand_1 = 'const'+str(self.const_var_count)
                        self.insert_variable(operand_1,type_1,'const',value = value)
                        self.const_var_count += 1

                except TypeError as err:

                    raise TypeError(str(err))


                operand_1_addr = self.get_var_addr(operand_1)

            quadruple = {'operation': action, 'operand_1': operand_1_addr,
                            'operand_2': None, 'save_loc': None}

            self.quadruples.append(quadruple)
    
    def insert_quadruple_asignation(self,save_loc,operand_1=None):
        
        if operand_1 == None:
            try:
                operand_1 = list(self.last_temp.keys())[0][0] # first item of dict and firt item of tuple which is var name
                operand_1_addr = list(self.last_temp.keys())[0][1]
            except:
                raise ValueError('No last tmep value')
        
        try:
            if self.get_value_type(operand_1) != 'var':
                value = operand_1
                type_1 = self.get_value_type(operand_1)
                operand_1 = 'const'+str(self.const_var_count)
                self.insert_variable(operand_1,type_1,'const',value = value)
                self.const_var_count += 1


        except TypeError as err:

            raise TypeError(str(err))

        operand_1_addr = self.get_var_addr(operand_1)

        validation_type_1 = self.variables_table[(operand_1,operand_1_addr)]['type']
        

        if save_loc == None:
  
            save_loc = 'temp'+str(self.temp_count)
            temp_type = validation_type_1
            self.insert_variable(save_loc,temp_type,'temp')
            new_var = (save_loc , self.memory_count['temp'][temp_type]-1)#the variable count has increase so take one from the memory count
            newTemp = {new_var:{'type':temp_type}}
            self.last_temp = newTemp
            self.temp_count += 1

        save_loc_addr = self.get_var_addr(save_loc)
        validation_type_2 = self.variables_table[(save_loc,save_loc_addr)]['type']

        if validation_type_1 != validation_type_2:
            raise TypeError(f'Incompatible Types {validation_type_1} and {validation_type_2}')

        quadruple = {'operation': '=', 'operand_1': operand_1_addr,
                        'operand_2': None, 'save_loc': save_loc_addr}

        self.quadruples.append(quadruple)


    def insert_quadruple_goto(self,quadruple_num=None,operand_1=None,goto_type=None):

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

    def get_addr_type(self, addr):


        for scope in self.variables_base_memory.keys():
            for type_var in self.variables_base_memory[scope].keys():
                base = self.variables_base_memory[scope][type_var]
                top = base + self.MEMORY_SPACE -1
                if base <= addr <= top:
                    return type_var

    def print_quadruples(self):

        print('============ Quadruples table =============')
        for cont,quadruple in zip(range(0,len(self.quadruples)),self.quadruples):
            print(cont,quadruple)
            cont += 1

        print('============ Variables table =============')
        for var in self.variables_table.keys():
            print(var,self.variables_table[var])

        print('============ Functions table =============')
        for func in self.functions_table.keys():
            print(func,self.functions_table[func])





    def insert_ver_quadruple(self,arr_name,operand_1=None,dim1=True):

        if operand_1 == None:
            try:
                operand_1 = list(self.last_temp.keys())[0][0] # first item of dict and firt item of tuple which is var name
                operand_1_addr = list(self.last_temp.keys())[0][1]
            except:
                raise ValueError('No last temp value')
        
        try:
            if self.get_value_type(operand_1) != 'var':
                value = operand_1
                type_1 = self.get_value_type(operand_1)
                operand_1 = 'const'+str(self.const_var_count)
                self.insert_variable(operand_1,type_1,'const',value = value)
                self.const_var_count += 1


        except TypeError as err:

            raise TypeError(str(err))

        operand_1_addr = self.get_var_addr(operand_1)
        var_addr = self.get_var_addr(arr_name)
        var = (arr_name,var_addr)

        try:
            base = self.get_var_addr(arr_name)
            curr_var = (arr_name,base)
            m1 = self.variables_table[curr_var]['m1']
            if dim1 == True:
                
                index = self.variables_table[var]['index_1']
                
            else:
                index = self.variables_table[var]['index_2']
                m2 = self.variables_table[curr_var]['m2']
        except KeyError as err:

            raise IndexError('Wrong index in array' + str(err))

        base_0 = 'const0'
        base_0_addr = self.get_var_addr(base_0)

        quadruple = {'operation':'ver','operand_1':operand_1_addr,'operand_2':base_0_addr,'save_loc':index}
        self.quadruples.append(quadruple)


    def insert_plus_quadruple(self,arr,operand_1=None):

        if operand_1 == None:
            try:
                operand_1 = list(self.last_temp.keys())[0][0] # first item of dict and firt item of tuple which is var name
                operand_1_addr = list(self.last_temp.keys())[0][1]
            except:
                raise ValueError('No last tmep value')
        
        operand_1_addr = self.get_var_addr(operand_1)

        save_loc = 'temp'+str(self.pointer_count)
        temp_type = 'pointer'
        self.insert_variable(save_loc,temp_type,'temp',value=operand_1_addr)
        new_var = (save_loc , self.memory_count['temp'][temp_type]-1)#the variable count has increase so take one from the memory count
        newTemp = {new_var:{'type':temp_type}}
        self.last_temp = newTemp
        self.pointer_count += 1
        save_loc_addr = self.get_var_addr(save_loc)
        
        base_name = 'base_'+arr 
        base = self.get_var_addr(arr)
        try: 
            self.insert_variable('base_'+arr ,temp_type,'const',value=base)
            base_addr = self.get_var_addr(base_name)
        except KeyError:
            pass

        base_addr = self.get_var_addr(base_name)
            
        quadruple = {'operation':'+','operand_1':base_addr,'operand_2':operand_1_addr,'save_loc':save_loc_addr}

        
        self.quadruples.append(quadruple)
    
    def insert_times_quadruple(self,arr,operand_1=None):

        if operand_1 == None:
            try:
                operand_1 = list(self.last_temp.keys())[0][0] # first item of dict and firt item of tuple which is var name
                operand_1_addr = list(self.last_temp.keys())[0][1]
            except:
                raise ValueError('No last tmep value')
        
        operand_1_addr = self.get_var_addr(operand_1)

        save_loc = 'temp'+str(self.temp_count)
        temp_type = 'int'
        self.insert_variable(save_loc,temp_type,'temp',value=operand_1_addr)
        new_var = (save_loc , self.memory_count['temp'][temp_type]-1)#the variable count has increase so take one from the memory count
        newTemp = {new_var:{'type':temp_type}}
        self.last_temp = newTemp
        self.temp_count += 1
        save_loc_addr = self.get_var_addr(save_loc)


        base = self.get_var_addr(arr)
        var = (arr,base)
        m1 = self.variables_table[var]['m1']
        quadruple = {'operation':'*','operand_1':m1,'operand_2':operand_1_addr,'save_loc':save_loc_addr}
        self.quadruples.append(quadruple)    


    def insert_plus_quadruple_dim2(self,arr,operand_1=None,dim1=None):

        if operand_1 == None:
            try:
                operand_1 = list(self.last_temp.keys())[0][0] # first item of dict and firt item of tuple which is var name
                operand_1_addr = list(self.last_temp.keys())[0][1]
            except:
                raise ValueError('No last tmep value')
        
        operand_1_addr = self.get_var_addr(operand_1)
        dim1_addr = self.get_var_addr(dim1)

        save_loc = 'temp'+str(self.temp_count)
        temp_type = 'int'
        self.insert_variable(save_loc,temp_type,'temp',value=operand_1_addr)
        new_var = (save_loc , self.memory_count['temp'][temp_type]-1)#the variable count has increase so take one from the memory count
        newTemp = {new_var:{'type':temp_type}}
        self.last_temp = newTemp
        self.temp_count += 1
        save_loc_addr = self.get_var_addr(save_loc)


        quadruple = {'operation':'+','operand_1':dim1_addr,'operand_2':operand_1_addr,'save_loc':save_loc_addr}

        
        self.quadruples.append(quadruple)           


    def is_arr(self,arr_name):

        arr_addr = self.get_var_addr(arr_name)
        key = (arr_name,arr_addr)
        m1 = 'm1'

        if m1 in list(self.variables_table[key].keys()) :

            return True
        else :

            return False

    def is_mat(self,mat_name):

        arr_addr = self.get_var_addr(mat_name)
        key = (mat_name,arr_addr)
        m1 = 'm1'
        m2 = 'm2'

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