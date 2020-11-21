
import json
class Memory():

    def __init__(self):
        self.memory = {}


    def set_memory(self,func:dict,memory_dict:dict,const_vars:dict):

        var_cont = func['memory_usage']
        params_cont = func['param_cont']
        variables = func['params']

        for const,addr in const_vars.keys():
            if addr not in self.memory.keys():
                var_set = {addr:const_vars[(const,addr)]['value']}
                self.memory.update(var_set)
            else:
                raise MemoryError('Repeated memory value')

        for var,addr in list(variables.keys()):

            key = (var,addr)
            arr_size = 1
            if 'index_1' in variables[key].keys():
                if 'index_2' in variables[key].keys():
                    arr_size = self.memory[variables[key]['index_1']] * self.memory[variables[key]['index_2']]
                else:
                
                    arr_size = self.memory[variables[key]['index_1']]

            for _ in range(arr_size):

                if addr not in self.memory.keys():
                    var_set = {addr:None}
                    self.memory.update(var_set)
                else:
                    raise MemoryError('Repeated memory value')

                addr += 1

        print(json.dumps(self.memory,sort_keys=True,indent=4, separators=(',', ': ')))

    def add_memeory_call(self,func:dict,memory_dict:dict):

        var_cont = func['memory_usage']
        params_cont = func['param_cont']
        variables = func['params']


        for var,addr in list(variables.keys()):

            key = (var,addr)
            arr_size = 1
            if 'index_1' in variables[key].keys():
                if 'index_2' in variables[key].keys():
                    arr_size = self.memory[variables[key]['index_1']] * self.memory[variables[key]['index_2']]
                else:
                
                    arr_size = self.memory[variables[key]['index_1']]

            for _ in range(arr_size):

                if addr not in self.memory.keys():
                    var_set = {addr:None}
                    self.memory.update(var_set)
                else:
                    raise MemoryError('Repeated memory value')

                addr += 1

        
        for scope in var_cont.keys():
            for type_var in scope.keys():
                for i in range(scope[type_var]):

                    pass



        print(json.dumps(self.memory,sort_keys=True,indent=4, separators=(',', ': ')))


        



        


    
