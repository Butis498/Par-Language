import pickle
from memory import Memory
from time import sleep
class VirtualMachine():

    def __init__(self,main_id):
        self.functions_dict = None
        self.quadruples = None
        self.base_memory_dict = None
        self.variables_dict = None
        self.instruction_pointer = 0
        self.DataSegment = None
        self.main_id = main_id

    def start_data_segment(self):
        func = self.functions_dict[self.main_id]
        self.memory = Memory()
        self.memory.set_memory(func,self.base_memory_dict,self.variables_dict)


    def add_stack_segment(self,func_name):
        func = self.functions_dict[func_name]
        self.memory.add_memeory_call(func)


    def run_code(self):
        self.open_dicts()
        self.start_data_segment()
        while self.quadruples[self.instruction_pointer]['operation'] != 'end':
            self.make_action(self.quadruples[self.instruction_pointer])



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

  
        print(operation,operand_1,operand_2,save_loc)



    if operation == 'goto':
            self.instruction_pointer = save_loc
        elif operation == 'gotof':

            if get_mememory_value(operand_1) == "False":
                self.instruction_pointer = save_loc
            else:
                self.instruction_pointer += 1

        elif operation == '+':
            temp = get_mememory_value(operand_1) + get_mememory_value(operand_2)
            set_memory(save_loc,temp)
            self.instruction_pointer += 1

        elif operation == '-':
            temp = get_mememory_value(operand_1) - get_mememory_value(operand_2)
            set_memory(save_loc,temp)
            self.instruction_pointer += 1

         elif operation == '/':
            temp = get_mememory_value(operand_1) / get_mememory_value(operand_2)
            set_memory(save_loc,temp)
            self.instruction_pointer += 1

         elif operation == '*':
            temp = get_mememory_value(operand_1) * get_mememory_value(operand_2)
            set_memory(save_loc,temp)
            self.instruction_pointer += 1

         elif operation == '<':
            temp = get_mememory_value(operand_1) < get_mememory_value(operand_2)
            set_memory(save_loc,temp)
            self.instruction_pointer += 1
         
         elif operation == '>':
            temp = get_mememory_value(operand_1) > get_mememory_value(operand_2)
            set_memory(save_loc,temp)
            self.instruction_pointer += 1

         elif operation == '<=':
            temp = get_mememory_value(operand_1) <= get_mememory_value(operand_2)
            set_memory(save_loc,temp)
            self.instruction_pointer += 1

         elif operation == '>=':
            temp = get_mememory_value(operand_1) >= get_mememory_value(operand_2)
            set_memory(save_loc,temp)
            self.instruction_pointer += 1

         elif operation == '=':
            temp = get_mememory_value(operand_1)
            set_memory(save_loc,temp)
            self.instruction_pointer += 1

         elif operation == '==':
             temp = get_mememory_value(operand_1) == get_mememory_value(operand_2)
            set_memory(save_loc,temp)
            self.instruction_pointer += 1

         elif operation == 'gosub':
            temp = get_mememory_value(operand_1) >= get_mememory_value(operand_2)
            set_memory(save_loc,temp)
            self.instruction_pointer += 1

         elif operation == 'param':
            temp = get_mememory_value(operand_1) >= get_mememory_value(operand_2)
            set_memory(save_loc,temp)
            self.instruction_pointer += 1

         elif operation == 'ver':
            temp = get_mememory_value(operand_1) >= get_mememory_value(operand_2)
            set_memory(save_loc,temp)
            self.instruction_pointer += 1

         elif operation == 'ver_dim':
            temp = get_mememory_value(operand_1) >= get_mememory_value(operand_2)
            set_memory(save_loc,temp)
            self.instruction_pointer += 1

         elif operation == 'era':
            temp = get_mememory_value(operand_1) >= get_mememory_value(operand_2)
            set_memory(save_loc,temp)
            self.instruction_pointer += 1
        
         elif operation == 'end':
            temp = get_mememory_value(operand_1) >= get_mememory_value(operand_2)
            set_memory(save_loc,temp)
            self.instruction_pointer += 1

         elif operation == 'endfunc':
            temp = get_mememory_value(operand_1) >= get_mememory_value(operand_2)
            set_memory(save_loc,temp)
            self.instruction_pointer += 1

         elif operation == 'write':
            print(get_mememory_value(operand_1))
            self.instruction_pointer += 1
        
         elif operation == 'read':
            temp = input()
            set_memory(save_loc,temp)
            self.instruction_pointer += 1

         elif operation == '+mat':
            temp = get_mememory_value(operand_1) >= get_mememory_value(operand_2)
            set_memory(save_loc,temp)
            self.instruction_pointer += 1
         
         elif operation == '*mat':
            temp = get_mememory_value(operand_1) >= get_mememory_value(operand_2)
            set_memory(save_loc,temp)
            self.instruction_pointer += 1

         elif operation == '-mat':
            temp = get_mememory_value(operand_1) >= get_mememory_value(operand_2)
            set_memory(save_loc,temp)
            self.instruction_pointer += 1

         elif operation == '=mat':
            temp = get_mememory_value(operand_1) >= get_mememory_value(operand_2)
            set_memory(save_loc,temp)
            self.instruction_pointer += 1

         elif operation == '+arr':
            temp = get_mememory_value(operand_1) >= get_mememory_value(operand_2)
            set_memory(save_loc,temp)
            self.instruction_pointer += 1
         
         elif operation == '*arr':
            temp = get_mememory_value(operand_1) >= get_mememory_value(operand_2)
            set_memory(save_loc,temp)
            self.instruction_pointer += 1

         elif operation == '-arr':
            temp = get_mememory_value(operand_1) >= get_mememory_value(operand_2)
            set_memory(save_loc,temp)
            self.instruction_pointer += 1

         elif operation == '=arr':
            temp = get_mememory_value(operand_1) >= get_mememory_value(operand_2)
            set_memory(save_loc,temp)
            self.instruction_pointer += 1

         elif operation == 'transpose':
            temp = get_mememory_value(operand_1) >= get_mememory_value(operand_2)
            set_memory(save_loc,temp)
            self.instruction_pointer += 1

         elif operation == 'inverse':
            temp = get_mememory_value(operand_1) >= get_mememory_value(operand_2)
            set_memory(save_loc,temp)
            self.instruction_pointer += 1

