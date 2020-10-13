from yacc import MyParser

if __name__ == "__main__":
    
    correct_code = r'''
            program programID;
            var varTest,varTest2, varTest3:int;
            {
                variableTest = Num;
                if (variable > varTest){
                    asignTest = Num;
                }else{
                    asignTest = Num;
                };
            }
            '''


    print(correct_code)
    parser = MyParser()
    parser.parse(correct_code)
