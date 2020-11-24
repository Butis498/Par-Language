
import json
class Memory():

    def __init__(self):
        self.MEMORY_SIZE = 5000
        self.data_segment = {}
        self.base_memory = None
        self.stack_segment = []
        self.ranges = []
        self.max_call_stack = 300
        self.curr_segment = 0
        self.arr_sizes = [{}]
        self.index_sizes = [{}]


    # This function asings a value to the memory address, it will search the memory address in the las stack segement memeory
    # in case it does not exists it will serach in the data sectment
    # as parameters it takes the addr value to set , the value to set into the address and the last parameter is if it is 
    # a parameter in case it is a parameter it will set the value in the next stack segemnt value for the parameter
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


       # print(json.dumps(self.data_segment,sort_keys=True,indent=4, separators=(',', ': ')))



    # Returns the value of the the array size in case it is not a temporal array
    # as a parameter it takes the array base address
    def get_arr_size(self,arr):

        return self.arr_sizes[self.curr_segment][arr]

    # Returns a dictrionary with the indexes of an array 
    # or matrix as a parameters it is a array or matrix address
    def get_arr_indexes(self,arr):

        return self.index_sizes[self.curr_segment][arr]


    # returns the range of addresses of a certain scope 
    # it takes as parameter the scope that will be evaluated to get the range
    def get_range(self,scope):
        base = list(self.base_memory[scope].values())[0]
        top = base + self.MEMORY_SIZE * len(self.base_memory[scope]) -1
        return range(base,top)


    # THis function returns the raw value of a memory address
    # as a parameter it takes the address
    # it returns the value inside of the memeory address
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

    

    # returns the value inside a memory address, if the memory address is  a pointer it will the value inside that pointer value
    # as a parameter it takes tha address to serch
    def get_mememory_value(self,addr):

        
        if self.is_pointer(addr) and addr not in self.get_range('const'):
            value_mem = self.get_raw_memory_value(addr)
            value = self.get_raw_memory_value(value_mem)
        else:
            value = self.get_raw_memory_value(addr)

        return value


    # Returns a boolean evaluating if the address is a pointer,
    # it takes as parameter the address to be evaluated
    # returns true if the value is a pointer false if it is a value
    def is_pointer(self,addr):

        for interval in self.ranges:
            if addr in interval:
                return True
            
        return False

    # this function inialize the memory data segment it will ,
    # it takes as parametes the fucntion ibject with all the information of the memory usage,
    # the memmory dictionary with the base address of each type and the constat variables tables

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
                size_arr = {addr:arr_size}
                self.arr_sizes[self.curr_segment].update(size_arr)


                if 'index_2' in variables[key].keys():
                    index_1 = self.get_mememory_value(variables[key]['index_1'])
                    index_2 = self.get_mememory_value(variables[key]['index_2'])
                    index_dict = {addr:{'index_1':index_1,'index_2':index_2}}
                    self.index_sizes[self.curr_segment].update(index_dict)
               

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


    # this function is called when a function has ended , it does not require any arguments and no return value
    def end_func(self):

        self.stack_segment.pop(-1)
        self.arr_sizes.pop(-1)
        self.index_sizes.pop(-1)
        self.curr_segment -= 1

    
    # this function adds a memory dictionary inside the stack segament 
    # as a parameter it takes the the fucntion dictionary with all the 
    # memeory information such as usage, init value , and variables used
    def add_memeory_call(self,func:dict):

        self.arr_sizes.append({})
        self.index_sizes.append({})

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
                size_arr = {addr:arr_size}
                self.arr_sizes[self.curr_segment].update(size_arr)

                if 'index_2' in variables[key].keys():
                    index_1 = self.get_mememory_value(variables[key]['index_1'])
                    index_2 = self.get_mememory_value(variables[key]['index_2'])
                    index_dict = {addr:{'index_1':index_1,'index_2':index_2}}
                    self.index_sizes[self.curr_segment].update(index_dict)
      

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


        



        


    
