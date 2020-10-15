from yacc import MyParser

if __name__ == "__main__":
    
    with open('program_test.txt',encoding='utf8') as file:
        test_code = file.read()
        print(test_code)
        parser = MyParser()
        parser.parse(test_code)
