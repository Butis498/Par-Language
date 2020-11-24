from yacc import MyParser
from VM import VirtualMachine

if __name__ == "__main__":
    
    with open('program_test.ppp',encoding='utf8') as file:
        test_code = file.read()
        parser = MyParser()
        parser.parse(test_code)
        program_id = parser.program_id

    vm = VirtualMachine(program_id)
    vm.run_code()
