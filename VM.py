import pickle
from memory import Memory
import json
from time import sleep
import ast
import numpy as np 
import sys



class VirtualMachine():

    def __init__(self,main_id):
        self.functions_dict = None
        self.quadruples = None
        self.base_memory_dict = None
        self.variables_dict = None
        self.instruction_pointer = 0
        self.DataSegment = None
        self.main_id = main_id
        self.jump_stack = []


    # Functino to start the data sectment base on the obj binary files created on the class
    # it does not takes any parameters and does not have a return value
    def start_data_segment(self):
        func = self.functions_dict[self.main_id]
        self.memory = Memory()
        self.memory.set_memory(func,self.base_memory_dict,self.variables_dict)


    # add memory dictionary to the stack segment based on the function name
    # this fucntion name is stored in the fucntion table from the class dictionary
    # it is called when a function is called in the execution
    def add_stack_segment(self,func_name):
        func = self.functions_dict[func_name]
        self.memory.add_memeory_call(func)


    
    def get_value_type(self,var):
        t = getattr(__builtins__, var)
        if isinstance(t, type):
            return t
        raise ValueError(var)

    

    # returns the type of the address of a variable in case it does not exists it will retuen error
    # as a parameter it requieres the address to serch in the ranges 
    def get_addr_type(self, addr):


        for scope in self.base_memory_dict.keys():
            for type_var in self.base_memory_dict[scope].keys():
                base = self.base_memory_dict[scope][type_var]
                top = base + self.memory.MEMORY_SIZE -1
                if base <= addr <= top:

                    return type_var

    # this fucntion starts the code execuion by reading the quadruples until the it detects a end operation
    # it has no return value and it no parameters 
    def run_code(self):
        self.open_dicts()
        self.start_data_segment()
    
        while self.quadruples[self.instruction_pointer]['operation'] != 'end':

            # print(json.dumps(self.memory.stack_segment,sort_keys=False,indent=4, separators=(',', ': ')))

            self.make_action(self.quadruples[self.instruction_pointer])

            
            if len(self.quadruples) <= self.instruction_pointer:
                break
        

    def dataType(self, str_in):
        str_in=str_in.strip()
        if len(str_in) == 0: return 'BLANK'
        try:
            t=ast.literal_eval(str_in)

        except ValueError:
            if len(str_in) == 1:
                return 'char'
            else:   
                return 'string'
        except SyntaxError:
            if len(str_in) == 1:
                return 'char'
            else:   
                return 'string'

        else:
            if type(t) in [int, float, bool]:
                if type(t) is int or type(t) is int:
                    return 'int'
                if t in set((True,False,"true", "false")):
                    return 'bool'
                if type(t) is float:
                    return 'float'
            else:
                if len(str_in) == 1:
                    return 'char'
                else:
                   
                    return 'string' 


    # converts string to a bool
    # as a parameter it take a string which will be converted into a python bool
    def str2bool(self, v):
        return v.lower() in ("yes", "true", "t", "1")
        

    # Opens the binary dictionarys located in the obj folder and asing the values in
    # the object attributes, it does not have a return value and does not have any parameters
    def open_dicts(self):
        
        try:

            with open('obj/quadruples.dictionary', 'rb') as config_dictionary_file:
    
                self.quadruples = pickle.load(config_dictionary_file)

            with open('obj/functions.dictionary', 'rb') as config_dictionary_file:
    
                self.functions_dict = pickle.load(config_dictionary_file)

            with open('obj/variables.dictionary', 'rb') as config_dictionary_file:
    
                self.variables_dict = pickle.load(config_dictionary_file)

            with open('obj/base_memory.dictionary', 'rb') as config_dictionary_file:
    
                self.base_memory_dict = pickle.load(config_dictionary_file)
        except:

            raise SystemError('Can not open files to execute')

    

    # This fucntion is a big switch that will execute the quadruples depending on the operatino 
    # It takes as a paramerter the quadruple to be executes, after each action is taken it will move the instruction pointer 
    def make_action(self,quadruple:dict):

        operation = quadruple['operation']
        operand_1 = quadruple['operand_1']
        operand_2 = quadruple['operand_2'] 
        save_loc = quadruple['save_loc']


        if operation == 'goto':
            self.instruction_pointer = save_loc
        elif operation == 'gotof':

            if self.memory.get_mememory_value(operand_1) == "False" or self.memory.get_mememory_value(operand_1) == False:
                self.instruction_pointer = save_loc
            else:
                self.instruction_pointer += 1

        elif operation == '+':

            temp = self.memory.get_mememory_value(operand_1) + self.memory.get_mememory_value(operand_2)
            self.memory.set_memory_value(save_loc,temp)
            self.instruction_pointer += 1

        elif operation == '-':
            temp = self.memory.get_mememory_value(operand_1) - self.memory.get_mememory_value(operand_2)
            self.memory.set_memory_value(save_loc,temp)
            self.instruction_pointer += 1

        elif operation == '/':
            temp = self.memory.get_mememory_value(operand_1) / self.memory.get_mememory_value(operand_2)
            self.memory.set_memory_value(save_loc,temp)
            self.instruction_pointer += 1

        elif operation == '*':
            temp = self.memory.get_mememory_value(operand_1) * self.memory.get_mememory_value(operand_2)
            self.memory.set_memory_value(save_loc,temp)
            self.instruction_pointer += 1


        elif operation == '<':
            temp = self.memory.get_mememory_value(operand_1) < self.memory.get_mememory_value(operand_2)
            if temp == 'True' or temp:
                temp = 'True'
            else:
                temp = 'False'
            self.memory.set_memory_value(save_loc,temp)
            self.instruction_pointer += 1

        elif operation == '|':
            # print(self.memory.get_mememory_value(operand_1) , self.memory.get_mememory_value(operand_2))
            # print(type(self.memory.get_mememory_value(operand_1)),type(self.memory.get_mememory_value(operand_2)))

            temp = self.memory.get_mememory_value(operand_1) == 'True'  or self.memory.get_mememory_value(operand_2) == 'True'
            # print('result: ',temp,type(temp))
            if temp == 'True' or temp:
                temp = 'True'
            else:
                temp = 'False'


            self.memory.set_memory_value(save_loc,temp)
            self.instruction_pointer += 1


        elif operation == '&':
            temp = self.memory.get_mememory_value(operand_1) == 'True'  and self.memory.get_mememory_value(operand_2) == 'True'
            # print('result: ',temp,type(temp))
            if temp == 'True' or temp:
                temp = 'True'
            else:
                temp = 'False'
            self.memory.set_memory_value(save_loc,temp)
            self.instruction_pointer += 1
         
        elif operation == '>':
            temp = self.memory.get_mememory_value(operand_1) > self.memory.get_mememory_value(operand_2)
            if temp == 'True' or temp:
                temp = 'True'
            else:
                temp = 'False'
            self.memory.set_memory_value(save_loc,temp)
            self.instruction_pointer += 1

        elif operation == '<=':
            temp = self.memory.get_mememory_value(operand_1) <= self.memory.get_mememory_value(operand_2)
            if temp == 'True' or temp:
                temp = 'True'
            else:
                temp = 'False'
            self.memory.set_memory_value(save_loc,temp)
            self.instruction_pointer += 1

        elif operation == '>=':
            temp = self.memory.get_mememory_value(operand_1) >= self.memory.get_mememory_value(operand_2)
            if temp == 'True' or temp:
                temp = 'True'
            else:
                temp = 'False'
            self.memory.set_memory_value(save_loc,temp)
            self.instruction_pointer += 1

        elif operation == '=':
            temp = self.memory.get_mememory_value(operand_1)
            if self.memory.is_pointer(save_loc):
                save_loc = self.memory.get_raw_memory_value(save_loc)
            self.memory.set_memory_value(save_loc,temp)
            self.instruction_pointer += 1

        elif operation == '==':
            # print(self.memory.get_mememory_value(operand_1), self.memory.get_mememory_value(operand_2))
            # print(type(self.memory.get_mememory_value(operand_1)),type(self.memory.get_mememory_value(operand_2)))
            temp = self.memory.get_mememory_value(operand_1) == self.memory.get_mememory_value(operand_2)
            # print('result: ',temp,type(temp))

            if temp == 'True' or temp:
                temp = 'True'
            else:
                temp = 'False'

            # print('curr segement: ',self.memory.curr_segment)
            self.memory.set_memory_value(save_loc,temp)
            # print('changed_result: ',self.memory.stack_segment[self.memory.curr_segment][save_loc])

            self.instruction_pointer += 1

        elif operation == 'gosub':
            if len(self.memory.stack_segment) > 1:
                self.memory.curr_segment += 1
            self.jump_stack.append(self.instruction_pointer + 1)
            self.instruction_pointer = self.functions_dict[save_loc]['init']
            
            

        elif operation == 'param':
            
            temp = self.memory.get_mememory_value(operand_1)
            if self.memory.is_pointer(save_loc):
                save_loc = self.memory.get_raw_memory_value(save_loc)
            self.memory.set_memory_value(save_loc,temp,param=True)
            self.instruction_pointer += 1


        elif operation == 'ver':
            #print(self.memory.get_mememory_value(operand_2) , self.memory.get_mememory_value(operand_1) , self.memory.get_mememory_value(save_loc),'veeeeeeeeeeeeeeeeer')
            temp = self.memory.get_mememory_value(operand_2) <= self.memory.get_mememory_value(operand_1) < self.memory.get_mememory_value(save_loc)
            if not temp:
                raise IndexError('Out of index')
            self.instruction_pointer += 1

        elif operation == 'ver_dim':
            equal = self.memory.get_mememory_value(operand_1) == self.memory.get_mememory_value(operand_2)
            if not equal:
                raise IndexError("Not compatible matrix")
            self.instruction_pointer += 1

        elif operation == 'era':
            self.add_stack_segment(save_loc)
            self.instruction_pointer += 1
        

        elif operation == 'endfunc':
            self.memory.end_func()
            self.instruction_pointer = self.jump_stack[-1]
            self.jump_stack.pop(-1)

        elif operation == 'write':
            sys.stdout.write(str(self.memory.get_mememory_value(operand_1)))
            sys.stdout.write(' ')
            self.instruction_pointer += 1

        elif operation == 'end_write':
            sys.stdout.write('\n')
            self.instruction_pointer += 1
        
        elif operation == 'read':
            temp = input()
            temp2 = self.dataType(temp)
            if temp2 == 'int':
                temp = int(temp)
            elif  temp2 == 'flaot':
                temp = float(temp)
            elif temp2 == 'bool':
                temp = str(temp)
            elif temp2 == 'char':
                temp = str(temp)

           # print(temp2,self.get_addr_type(operand_1))
            if temp2 != self.get_addr_type(operand_1):
                raise TypeError('Not compatible input')


            self.memory.set_memory_value(operand_1,temp)
            self.instruction_pointer += 1

        elif operation == 'return':

            temp = self.memory.get_mememory_value(operand_1)
            if self.memory.is_pointer(save_loc):
                save_loc = self.memory.data_segment[save_loc]
            self.memory.data_segment[save_loc] = temp
            self.instruction_pointer += 1
            

            

        elif operation == '+mat':

            size1 = self.memory.get_arr_size(operand_1)
            
            
            
            for i in range(size1):
                value1 = self.memory.get_mememory_value(operand_1)
                if value1 == None:
                    value1 = 0
                
                value2 = self.memory.get_mememory_value(operand_2)
                if value2 == None:
                    value2 = 0
                
                temp = value1 + value2
                self.memory.set_memory_value(save_loc,temp)
                
                operand_1 += 1
                operand_2 += 1
                save_loc += 1
            
            self.instruction_pointer += 1

         
        elif operation == '*mat':
            size1 = self.memory.get_arr_size(operand_1)
            

            
            for i in range(size1):
                value1 = self.memory.get_mememory_value(operand_1)
                if value1 == None:
                    value1 = 0
                
                value2 = self.memory.get_mememory_value(operand_2)
                if value2 == None:
                    value2 = 0
                
                temp = value1 * value2
                self.memory.set_memory_value(save_loc,temp)
                
                operand_1 += 1
                operand_2 += 1
                save_loc += 1
            
            self.instruction_pointer += 1


        elif operation == '-mat':
            size1 = self.memory.get_arr_size(operand_1)
            
    
            
            for i in range(size1):
                value1 = self.memory.get_mememory_value(operand_1)
                if value1 == None:
                    value1 = 0
                
                value2 = self.memory.get_mememory_value(operand_2)
                if value2 == None:
                    value2 = 0
                
                temp = value1 - value2
                self.memory.set_memory_value(save_loc,temp)
                
                operand_1 += 1
                operand_2 += 1
                save_loc += 1
            
            self.instruction_pointer += 1


        elif operation == '=mat':
            size1 = self.memory.get_arr_size(save_loc)
               
            for i in range(size1):
                value1 = self.memory.get_mememory_value(operand_1)

                self.memory.set_memory_value(save_loc,value1)
                
                operand_1 += 1
                save_loc += 1
            
            self.instruction_pointer += 1


        elif operation == '+arr':
            size1 = self.memory.get_arr_size(operand_1)
            
        
            
            for i in range(size1):
                value1 = self.memory.get_mememory_value(operand_1)
                if value1 == None:
                    value1 = 0
                
                value2 = self.memory.get_mememory_value(operand_2)
                if value2 == None:
                    value2 = 0
                
                temp = value1 + value2
                self.memory.set_memory_value(save_loc,temp)
                
                operand_1 += 1
                operand_2 += 1
                save_loc += 1
            
            self.instruction_pointer += 1

         
        elif operation == '*arr':
            size1 = self.memory.get_arr_size(operand_1)

            
            for i in range(size1):
                value1 = self.memory.get_mememory_value(operand_1)
                if value1 == None:
                    value1 = 0
                
                value2 = self.memory.get_mememory_value(operand_2)
                if value2 == None:
                    value2 = 0
                
                temp = value1 * value2
                self.memory.set_memory_value(save_loc,temp)
                
                operand_1 += 1
                operand_2 += 1
                save_loc += 1
            
            self.instruction_pointer += 1

        elif operation == '-arr':
            size1 = self.memory.get_arr_size(operand_1)
            
            

            
            for i in range(size1):
                value1 = self.memory.get_mememory_value(operand_1)
                if value1 == None:
                    value1 = 0
                
                value2 = self.memory.get_mememory_value(operand_2)
                if value2 == None:
                    value2 = 0
                
                temp = value1 - value2
                self.memory.set_memory_value(save_loc,temp)
                
                operand_1 += 1
                operand_2 += 1
                save_loc += 1
            
            self.instruction_pointer += 1

        elif operation == '=arr':
            size1 = self.memory.get_arr_size(save_loc)
            
            
            for i in range(size1):
                value1 = self.memory.get_mememory_value(operand_1)

                self.memory.set_memory_value(save_loc,value1)
                
                operand_1 += 1
                save_loc += 1
            
            self.instruction_pointer += 1

        elif operation == 'transpose':
            size_dict = self.memory.get_arr_indexes(operand_1)
            index1 = size_dict['index_1']
            index2 = size_dict['index_2']


            Matrix = [[0 for x in range(index2)] for y in range(index1)]

            for i in range(index2):
                for j in range(index1):
                    value = self.memory.get_mememory_value(operand_1)
                    Matrix[j][i] = value
                    operand_1 += 1

            for i in range(index2):
                for j in range(index1):

                    self.memory.set_memory_value(save_loc,Matrix[i][j])
                    save_loc += 1

            self.instruction_pointer += 1

            
                    



        elif operation == 'inverse':
            
            size_dict = self.memory.get_arr_indexes(operand_1)
            index1 = size_dict['index_1']
            index2 = size_dict['index_2']
            start_mem = operand_1
            save_loc_start  = save_loc 

            Matrix = [[0 for x in range(index2)] for y in range(index1)] 

            for i in range(index2):
                for j in range(index1):
                    value = self.memory.get_mememory_value(operand_1)
                    Matrix[j][i] = value
                    operand_1 += 1



            NpMatrix = np.matrix(Matrix,dtype='float')

            inverse_mat = np.linalg.inv(NpMatrix)

            inverse_py = inverse_mat.tolist()

            for i in range(index2):
                for j in range(index1):

                    self.memory.set_memory_value(save_loc,inverse_py[j][i])
                    save_loc += 1

            self.instruction_pointer += 1

        elif operation == 'determinant':
            
            size_dict = self.memory.get_arr_indexes(operand_1)
            index1 = size_dict['index_1']
            index2 = size_dict['index_2']
            start_mem = operand_1
            save_loc_start  = save_loc 

            Matrix = [[0 for x in range(index2)] for y in range(index1)] 

            for i in range(index2):
                for j in range(index1):
                    value = self.memory.get_mememory_value(operand_1)
                    Matrix[j][i] = value
                    operand_1 += 1



            NpMatrix = np.matrix(Matrix,dtype='float')

            determinant_mat = np.linalg.det(NpMatrix)

            determinant_mat = float(determinant_mat)

            self.memory.set_memory_value(save_loc,determinant_mat)

            self.instruction_pointer += 1