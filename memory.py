
import json
class Memory():

    def __init__(self):
        self.data_segment = {}
        self.base_memory = None
        self.stck_segment = []


    def set_memory(self,func:dict,memory_dict:dict,const_vars:dict):

        _ = func['memory_usage']
        params_cont = func['param_cont']
        variables = func['params']
        self.base_memory = memory_dict
        for const,addr in const_vars.keys():
            if addr not in self.data_segment.keys():
                var_set = {addr:const_vars[(const,addr)]['value']}
                self.data_segment.update(var_set)
            else:
                raise MemoryError('Repeated memory value')

        for var,addr in list(variables.keys()):

            key = (var,addr)
            arr_size = 1
            if 'size' in variables[key].keys():
                arr_size = variables[key]['size']

            for _ in range(arr_size):

                if addr not in self.data_segment.keys():
                    var_set = {addr:None}
                    self.data_segment.update(var_set)
                else:
                    raise MemoryError('Repeated memory value')

                addr += 1

        print(json.dumps(self.data_segment,sort_keys=True,indent=4, separators=(',', ': ')))


    def end_func(self):

        self.stck_segment.pop(-1)

    

    def add_memeory_call(self,func:dict):

        new_func = {}
        var_cont = func['memory_usage']
        params_cont = func['param_cont']
        variables = func['params']


        for var,addr in list(variables.keys()):

            key = (var,addr)
            arr_size = 1
            if 'size' in variables[key].keys():
                arr_size = variables[key]['size']
      

            for _ in range(arr_size):

                if addr not in new_func.keys():
                    var_set = {addr:None}
                    new_func.update(var_set)
                else:
                    raise MemoryError('Repeated memory value')

                addr += 1

        
        for scope in var_cont.keys():
            for type_var in var_cont[scope].keys():
                var_base = self.base_memory[scope][type_var]
                for _ in range(var_cont[scope][type_var]):
                    var_set = {var_base:None}
                    var_base += 1
                    new_func.update(var_set)

        
        self.stck_segment.append(new_func)

        print(json.dumps(new_func,sort_keys=True,indent=4, separators=(',', ': ')))


        



        


    
