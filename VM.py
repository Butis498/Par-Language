import pickle
from memory import Memory
import json
from time import sleep
import ast

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

    def start_data_segment(self):
        func = self.functions_dict[self.main_id]
        self.memory = Memory()
        self.memory.set_memory(func,self.base_memory_dict,self.variables_dict)


    def add_stack_segment(self,func_name):
        func = self.functions_dict[func_name]
        self.memory.add_memeory_call(func)

    def get_value_type(self,var):
        t = getattr(__builtins__, var)
        if isinstance(t, type):
            return t
        raise ValueError(var)


    def run_code(self):
        self.open_dicts()
        self.start_data_segment()
    
        while self.quadruples[self.instruction_pointer]['operation'] != 'end':

            # print(json.dumps(self.memory.stack_segment,sort_keys=False,indent=4, separators=(',', ': ')))

            self.make_action(self.quadruples[self.instruction_pointer])

            
            if len(self.quadruples) <= self.instruction_pointer:
                break
        

    def dataType(self, str):
        str=str.strip()
        if len(str) == 0: return 'BLANK'
        try:
            t=ast.literal_eval(str)

        except ValueError:
            return 'TEXT'
        except SyntaxError:
            return 'TEXT'

        else:
            if type(t) in [int, float, bool]:
                if type(t) is int or type(t) is int:
                    return 'INT'
                if t in set((True,False,"true", "false")):
                    return 'BOOL'
                if type(t) is float:
                    return 'FLOAT'
            else:
                return 'TEXT' 


    
    def str2bool(self, v):
        return v.lower() in ("yes", "true", "t", "1")
        


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


    def make_action(self,quadruple:dict):

        operation = quadruple['operation']
        operand_1 = quadruple['operand_1']
        operand_2 = quadruple['operand_2'] 
        save_loc = quadruple['save_loc']

        #print(operation,operand_1,operand_2,save_loc)


        if operation == 'goto':
            self.instruction_pointer = save_loc
        elif operation == 'gotof':

            if self.memory.get_mememory_value(operand_1) == "False" or False:
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

            temp = self.memory.get_mememory_value(operand_1) == 'True' or self.memory.get_mememory_value(operand_2) == 'True'
            # print('result: ',temp,type(temp))
            if temp == 'True' or temp:
                temp = 'True'
            else:
                temp = 'False'


            self.memory.set_memory_value(save_loc,temp)
            self.instruction_pointer += 1


        elif operation == '&':
            temp = self.memory.get_mememory_value(operand_1) and self.memory.get_mememory_value(operand_2)
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
            temp = self.memory.get_mememory_value(operand_2) <= self.memory.get_mememory_value(operand_1) <= self.memory.get_mememory_value(save_loc)
            if not temp:
                raise IndexError('Out of index')
            self.instruction_pointer += 1

        elif operation == 'ver_dim':
            equal = self.memory.get_mememory_value(operand_1) == self.memory.get_mememory_value(operand_1)
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
            print(self.memory.get_mememory_value(operand_1))
            self.instruction_pointer += 1
        
        elif operation == 'read':
            temp = input()
            temp2 = self.dataType(temp)
            print(temp2)
            if temp2 == 'INT':
                temp = int(temp)
            elif  temp2 == 'FLOAT':
                temp = float(temp)
            elif temp2 == 'BOOL':
                temp = self.str2bool(temp)
                print(type(temp))
                print(temp)

            self.memory.set_memory_value(operand_1,temp)
            self.instruction_pointer += 1

        elif operation == 'return':

            temp = self.memory.get_mememory_value(operand_1)
            if self.memory.is_pointer(save_loc):
                save_loc = self.memory.data_segment[save_loc]
            self.memory.data_segment[save_loc] = temp
            self.instruction_pointer += 1
            

            

        elif operation == '+mat':
            pass
         
        elif operation == '*mat':
            pass

        elif operation == '-mat':
            pass

        elif operation == '=mat':
            pass

        elif operation == '+arr':
            pass
         
        elif operation == '*arr':
            pass

        elif operation == '-arr':
            pass

        elif operation == '=arr':
            pass

        elif operation == 'transpose':
            pass

        elif operation == 'inverse':
            pass

