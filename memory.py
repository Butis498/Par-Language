
import json
class Memory():

    def __init__(self):
        self.MEMORY_SIZE = 1000
        self.data_segment = {}
        self.base_memory = None
        self.stack_segment = []
        self.ranges = []
        self.max_call_stack = 300
        self.curr_segment = 0


    def set_memory_value(self,addr,value,param=False):

        off_set = 0
        if param and len(self.stack_segment) > 1:
            off_set = 1

        if len(self.stack_segment) > 0:

            if addr in self.stack_segment[self.curr_segment+off_set].keys():
                self.stack_segment[self.curr_segment+off_set][addr] = value

            if addr in self.data_segment.keys():
                self.data_segment[addr] = value

        elif addr in self.data_segment.keys():
            self.data_segment[addr] = value
        else:
            raise MemoryError(f'Not address found {addr}')




    def get_range(self,scope):
        base = list(self.base_memory[scope].values())[0]
        top = base + self.MEMORY_SIZE * len(self.base_memory[scope]) -1
        return range(base,top)

    def get_raw_memory_value(self,addr):

        
        if len(self.stack_segment) > 0:
            if addr in self.stack_segment[self.curr_segment].keys():
                return self.stack_segment[self.curr_segment][addr]

            if addr in self.data_segment.keys():
                return self.data_segment[addr]

        elif addr in self.data_segment.keys():
            return self.data_segment[addr]
        else:
            raise MemoryError(f'Not address found {addr}')   


    def get_mememory_value(self,addr):

        
        if self.is_pointer(addr) and addr not in self.get_range('const'):
            value_mem = self.get_raw_memory_value(addr)
            value = self.get_raw_memory_value(value_mem)
        else:
            value = self.get_raw_memory_value(addr)

        return value

    def is_pointer(self,addr):

        for interval in self.ranges:
            if addr in interval:
                return True
            
        return False


    def set_memory(self,func:dict,memory_dict:dict,const_vars:dict):

        var_cont = func['memory_usage']
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

        
        for scope in self.base_memory.keys():
            for type_var in self.base_memory[scope].keys():
                if type_var == "pointer":
                    base = self.base_memory[scope][type_var]
                    top = base + self.MEMORY_SIZE -1
                    self.ranges.append(range(base,top))

        for scope in var_cont.keys():
            for type_var in var_cont[scope].keys():
                var_base = self.base_memory[scope][type_var]
                for _ in range(var_cont[scope][type_var]):
                    var_set = {var_base:None}
                    var_base += 1
                    self.data_segment.update(var_set)  

        #print(json.dumps(self.data_segment,sort_keys=True,indent=4, separators=(',', ': ')))


    def end_func(self):

        self.stack_segment.pop(-1)
        self.curr_segment -= 1

    

    def add_memeory_call(self,func:dict):

        if len(self.stack_segment) >= self.max_call_stack:
            raise MemoryError('Segmentation fault')

        new_func = {}
        var_cont = func['memory_usage']
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

        
        self.stack_segment.append(new_func)
        

        #print(json.dumps(new_func,sort_keys=True,indent=4, separators=(',', ': ')))


        



        


    
