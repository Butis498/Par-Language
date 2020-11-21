from yacc import MyParser
from VM import VirtualMachine

if __name__ == "__main__":
    
    with open('program_test.txt',encoding='utf8') as file:
        test_code = file.read()
        print(test_code)
        parser = MyParser()
        parser.parse(test_code)

    vm = VirtualMachine()
    vm.open_dicts()
    vm.start_data_segment()
