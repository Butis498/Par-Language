import pickle
from memory import Memory
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
        self.add_stack_segment('Arreglos')


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

        