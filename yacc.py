from lexer import MyLexer
import ply.yacc as yacc
from semantic import Semantic

class MyParser(object):

    tokens = MyLexer.tokens


    def p_expression_program(self,p):
        '''
        program : start_goto PROGRAM ID SEMICOLONS program2 program3 main
        '''
        
        quadruple_end =  {'operation':'end','operand_1':None,'operand_2':None,'save_loc':None}
        self.semantic.quadruples.append(quadruple_end)
        self.semantic.print_quadruples()
        
    def p_expression_start_goto(self,p):
        '''
        start_goto : empty
        '''
        self.semantic.insert_quadruple_goto(None,None,None)

    def p_expression_program2(self,p):
        '''
        program2 : vars
                 | empty
        '''
        self.current_scope = 'local'

    def p_expression_program3(self,p):
        '''
        program3 : functions
                 | empty
        '''

    def p_expression_vars(self,p):
        '''
        vars : VAR vars1
        vars3 : COMA vars2
              | SEMICOLONS vars4
        vars4 : vars1
              | empty
        '''
    
    def p_expression_vars1(self,p):
        '''
        vars1 : type vars2
        '''
        for var in self.variables_stack:
            dim_1 = self.dims_stack[-1]
            self.dims_stack.pop(-1)
            dim_2 = self.dims_stack[-1]
            self.dims_stack.pop(-1)
            self.semantic.insert_variable(var,p[1],self.current_scope,dim1=dim_1,dim2=dim_2)
        self.variables_stack.clear()

    def p_expression_vars2(self,p):
        '''
        vars2 : var vars3
        '''
        self.variables_stack.append(p[1])

    def p_expression_functions(self,p):
        '''
        functions : end_func erase_mem functions3
        '''
       

    def p_expression_end_func(self,p):
        '''
        end_func : MODULE func_dec LPAREN functions2 RPAREN functions5 update_params block
        '''
        
        self.semantic.update_func_memory(self.semantic.current_func)
        self.semantic.insert_func_quadruple(operation='endfunc')


    def p_asignation_update_params(self,p):
        '''
        update_params : empty
        '''
        self.semantic.update_func(self.semantic.current_func)

    def p_asignation_func_dec(self,p):
        '''
        func_dec : functions1 func_name
        '''
        self.semantic.insert_func(p[2],p[1])

    def p_expression_functions1(self,p):
        '''
        functions1 : type
                   | VOID
        '''
        p[0] = p[1]

    def p_expression_functions3(self,p):
        '''
        functions3 : functions
                   | empty
        functions4 : COMA functions2
                   | empty
        functions5 : vars
                   | empty

        '''

    def p_expression_func_name(self,p):
        '''
        func_name : ID
        '''
        self.semantic.current_func = p[1]
        
        p[0] = p[1]


    def p_expression_functions2(self,p):
        '''
        functions2 : type var functions4
                   | empty functions4
        '''
        if p[1] != None:
            self.semantic.insert_variable(p[2],p[1],'local',True)

    
        
    def p_expression_erase_mem(self,p):
        '''
        erase_mem : empty
        '''
        self.semantic.reset_memory('temp')
        self.semantic.reset_memory('local')


    def p_term_type(self,p):
        
        '''
        type : INT 
             | FLOAT
             | CHAR
             | BOOL
        '''
        p[0] = p[1]

    def p_factor_block(self,p):
        
        '''
        block : LCURLYBRACKET block1 RCURLYBRACKET 
        block1 : statute block1
                | empty
        '''
    

    def p_expression_statute(self,p):
        '''
        statute : asignation 
                 | condition 
                 | writing
                 | repetitionstatute
                 | return
                 | call SEMICOLONS
                 | read
        '''
        
       # p[0] = p[1]

    
    def p_expression_condition(self,p):
        '''
        condition : IF condition2 THEN block condition1 
        '''
        self.semantic.quadruples[self.semantic.jumps_stack[-1]]['save_loc'] = len(self.semantic.quadruples)
        self.semantic.jumps_stack.pop(-1)

    def p_expression_condition2(self,p):
        '''
        condition2 : LPAREN expression RPAREN
        '''
        self.semantic.insert_quadruple_goto(None,p[2],False)
        self.semantic.jumps_stack.append(len(self.semantic.quadruples)-1)


    def p_expression_condition1(self,p):
        '''
        condition1 : empty 
                   | ELSE else_detect block 
        '''

    def p_expression_else_detect(self,p):
        '''
        else_detect : empty  
        '''
        salto = self.semantic.jumps_stack[-1]
        self.semantic.jumps_stack.pop(-1)
        self.semantic.insert_quadruple_goto(None)
        self.semantic.jumps_stack.append(len(self.semantic.quadruples)-1)
        self.semantic.quadruples[salto]['save_loc'] = len(self.semantic.quadruples)



    def p_expression_writing(self,p):
        '''
        writing : WRITE LPAREN  writing1 RPAREN SEMICOLONS
        '''

        

    def p_expression_writing1(self,p):
        '''
        writing1 : writing2 writing3
        writing3 : COMA writing1
                 | empty
        '''

    def p_expression_writing2(self,p):
        '''
        writing2 : expression
                 | STRING
        '''
        self.semantic.insert_quadruple_action('write',p[1])
    
    def p_expression_read(self,p):
        '''
        read : READ LPAREN read1 RPAREN SEMICOLONS
        '''

    

    def p_expression_read1(self,p):
        '''
        read1 : param read2
        '''
        self.semantic.insert_quadruple_action('read',p[1])


    def p_expression_read2(self,p):
        
        '''
        read2 : COMA read1
              | empty
        '''

    def p_expression_repetitionstatute(self,p):
        '''
        repetitionstatute : repetitionstatute1 DO block
        '''
        
        falso = self.semantic.jumps_stack[-1]
        self.semantic.jumps_stack.pop(-1)
        ret = self.semantic.jumps_stack[-1]
        self.semantic.jumps_stack.pop(-1)
        self.semantic.insert_quadruple_goto(quadruple_num=ret)
        self.semantic.quadruples[falso]['save_loc'] = len(self.semantic.quadruples)




    def p_expression_repetitionstatute1(self,p):
        '''
        repetitionstatute1 : FOR for_asign end_for
                           | WHILE while_start while_end
        '''

    def p_expression_end_for(self,p):
        '''
        end_for : TO expression
        '''
        
        if p[2] == None:
            last_temp = list(self.semantic.last_temp.keys())[0][0]
        else:
            last_temp = p[2]

        
        comp = self.semantic.operand_stack[-1]
        self.semantic.operand_stack.pop(-1)
        self.semantic.insert_quadruple_operation('<=',comp,last_temp)
        self.semantic.insert_quadruple_goto(None,goto_type=False)
        self.semantic.jumps_stack.append(len(self.semantic.quadruples)-1)

    def p_expression_for_asign(self,p):
        '''
        for_asign : param EQUAL expression
        '''
        if self.semantic.get_variable_type(p[1]) != 'int':
            raise TypeError('Not int type in loop')
        
       
        if p[3] == None:
            last_temp = list(self.semantic.last_temp.keys())[0][0]
        else:
            last_temp = p[3]
        

        self.semantic.insert_quadruple_asignation(p[1],last_temp)
        self.semantic.operand_stack.append(p[1])
        self.semantic.jumps_stack.append(len(self.semantic.quadruples))



    def p_expression_while_end(self,p):
        '''
        while_end : LPAREN expression RPAREN
        '''
        self.semantic.insert_quadruple_goto(None,p[2],False)
        self.semantic.jumps_stack.append(len(self.semantic.quadruples)-1)

    def p_expression_while_start(self,p):
        '''
        while_start : empty
        '''
        self.semantic.jumps_stack.append(len(self.semantic.quadruples))

        

    def p_asignation_factor(self,p):
        '''
        asignation : param EQUAL expression SEMICOLONS
        '''
        self.semantic.insert_quadruple_asignation(p[1],p[3])

    def p_asignation_return(self,p):
        '''
        return : RETURN  LPAREN expression detect_asignation RPAREN SEMICOLONS
        '''
        self.semantic.insert_quadruple_action(p[1],p[3])
        try:
            self.semantic.insert_quadruple_asignation(self.semantic.current_func,p[3])
        except KeyError:

            raise KeyError('No return for function given')
        

    def p_asignation_detect_asignation(self,p):
        '''
        detect_asignation : empty
        '''
        

    def p_expression_var(self,p):
        '''
        var : ID var1
        '''
        p[0] = p[1]

    def p_expression_var1(self,p):
        '''
        var1 : LBRACKET INUM RBRACKET var2
             | empty
        '''
        if p[1] != None:
            self.dims_stack.append(p[2])
        else:
            self.dims_stack.append(None)
            self.dims_stack.append(None)
            p[0] = None

    def p_expression_var2(self,p):
        '''
        var2 : LBRACKET INUM RBRACKET
             | empty
        '''
        if p[1] != None:
            self.dims_stack.append(p[2])
        else:
            self.dims_stack.append(None)
            p[0] = None

    def p_expression_call(self,p):
        '''
        call : era LPAREN call1 end_params RPAREN 
        '''
        self.semantic.verify_params_num()
        self.semantic.func_call_stack.pop(-1)
        self.semantic.param_count = 0
        p[0] = None

        

    def p_expression_end_params(self,p):
        '''
        end_params : empty
        '''
        self.semantic.insert_gosub_quadruple(self.semantic.func_call_stack[-1])
        try:
            self.semantic.insert_quadruple_asignation(None,self.semantic.func_call_stack[-1])
        except KeyError:
            pass
        
    def p_expression_call1(self,p):
        '''
        call1 : param_exp call2
              | empty
        call2 : COMA call1
              | empty
        '''

    def p_expression_param_exp(self,p):
        '''
        param_exp : expression
        '''
        self.semantic.insert_param_quadruple(p[1],self.semantic.get_curr_param_addr(self.semantic.func_call_stack[-1]))
        self.semantic.param_count += 1

    def p_expression_era(self,p):
        '''
        era : ID
        '''
        self.semantic.insert_func_quadruple(operation='era',func=p[1])
        self.semantic.func_call_stack.append(p[1])
    def p_expression_comparison(self,p):
        '''
        comparison : exp comparison1 exp
                   | exp empty
        '''
        if p[2] == None:
            p[0] = p[1]
        else:
            self.semantic.insert_quadruple_operation(p[2],p[1],p[3])

    def p_expression_comparison1(self,p):
        '''
        comparison1 : GREATERTHAN 
                    | MINORTHAN
                    | EQUALS
        '''
        p[0] = p[1]
    
    def p_expression_main(self,p):
        '''
        main : MAIN insert_jump LPAREN RPAREN main2 block
        '''
        self.semantic.reset_memory('temp')
        self.semantic.reset_memory('local')

    def p_expression_insert_jump(self,p):
        '''
        insert_jump : empty
        '''
        self.semantic.quadruples[self.semantic.jumps_stack[-1]]['save_loc'] = len(self.semantic.quadruples)

    def p_expression_main2(self,p):
        '''
        main2 : vars
              | empty
        '''

    def p_expression_param(self,p):
        '''
        param : param_id param_mod param1
        '''
        if p[3] == None: # is a single element

            if not self.semantic.is_arr(p[1]) and p[2] != None:
                raise KeyError("Wrong usage of modifier")

            p[0] = p[1]
        else:
            if p[2] != None:
                raise KeyError("Wrong usage of modifier")
            p[0] = list(self.semantic.last_temp.keys())[0][0]
        self.current_arr.pop(-1)

    def p_expression_param_mod(self,p):
        '''
        param_mod : modifier
                  | empty
        '''
        p[0] = p[1]

    def p_expression_param_id(self,p):
        '''
        param_id : ID
        '''
        p[0] = p[1]
        self.current_arr.append(p[1])

    def p_expression_param1(self,p):
        '''
        param1 : LBRACKET ver_dim1 RBRACKET param2
               | empty
        '''
        if p[1] != None:
            if p[4] == None:
                self.semantic.insert_plus_quadruple(self.current_arr[-1],p[2])

        p[0] = p[1]

    def p_expression_param2(self,p):
        '''
        param2 : LBRACKET two_detect ver_dim2 RBRACKET
               | empty
        '''
        if p[1] != None:
            s1_times_m1 = self.dims_stack[-1]
            self.dims_stack.pop(-1)
            self.semantic.insert_plus_quadruple_dim2(self.current_arr[-1],p[3],s1_times_m1)
            self.semantic.insert_plus_quadruple(self.current_arr[-1])
            p[0] = p[1]
            

    def p_expression_two_detect(self,p):
        '''
        two_detect : empty
        '''
        
        self.semantic.insert_times_quadruple(self.current_arr[-1],p[1])
        self.dims_stack.append('temp'+str(self.semantic.temp_count-1))


    def p_expression_ver_dim1(self,p):
        '''
        ver_dim1 : expression 
        '''
        curr_arr_name = self.current_arr[-1]
        self.semantic.insert_ver_quadruple(curr_arr_name,p[1])
        p[0] = p[1]
            

    def p_expression_ver_dim2(self,p):
        '''
        ver_dim2 : expression 
        '''
        curr_arr_name = self.current_arr[-1]
        self.semantic.insert_ver_quadruple(curr_arr_name,p[1],False)
        p[0] = p[1]
      

    def p_expression_expression(self,p):
        '''
        expression : comparison expression1 comparison
                   | comparison empty
        '''
        if p[2] == None:
            p[0] = p[1]
            
        else:
            self.semantic.insert_quadruple_operation(p[2],p[1],p[3])
        
        

    def p_expression_expression1(self,p):
        '''
        expression1 : AND 
                    | OR
        '''
        p[0] = p[1]

    def p_term_exp(self,p):
        '''
        exp : term exp1 exp
            | term empty
        '''
        if p[2] == None:
            p[0] = p[1]
        else:
            self.semantic.insert_quadruple_operation(p[2],p[1],p[3])

    def p_term_exp1(self,p):
        '''
        exp1 : PLUS 
             | MINUS
        '''
        p[0] = p[1]

    def p_empty(self,p):
        'empty :'
        p[0] = None
        pass



    def p_term_term(self,p):
        '''
        term : factor term1 term  
             | factor empty
        '''
        if p[2] == None:
            p[0] = p[1]
        else:
            self.semantic.insert_quadruple_operation(p[2],p[1],p[3])

    def p_term_term1(self,p):
        '''
        term1 : TIMES 
              | DIVIDE
        '''
        p[0] = p[1]


    def p_factor_factor(self,p):
        '''
        factor : factor1
        '''
        p[0] = p[1]

    def p_factor_factor1(self,p):
        '''
        factor1 : LPAREN expression RPAREN 
                | factor2
        '''
        if p[1] != '(':
            p[0] = p[1]

    def p_factor_factor2(self,p):
        '''
        factor2 : factor3 varcte 
                | varcte 
        '''
        if p[1] == '+' or p[1] == '-':
            if p[1] == '-':
                p[0] = -p[2]
            else:
                p[0] = p[2]
        else:
            p[0] = p[1]
    def p_factor_factor3(self,p):
        '''
        factor3 : PLUS 
                | MINUS 
        ''' 
        p[0] = p[1]  
    
    def p_expression_varcte(self,p):
        '''
        varcte : param
               | INUM
               | FNUM
               | TRUE
               | FALSE
               | CCHAR
               | call
        '''
        p[0] = p[1]

    def p_expression_modifier(self,p):
        '''
        modifier : TRANSPOSE
                 | DETERMINANT
                 | INVERSE
        '''
        p[0] = p[1]

    def parse(self,inputString):
        #r = MyLexer()
        #r.printTokens(inputString)
        self.parser.parse(input=inputString,lexer=self.lexer,debug=False)
        

    # Error rule for syntax errors
    def p_error(self,p):
        raise SystemError("Syntax error in input!")

    def __init__(self):
        self.lexer = MyLexer().build()
        self.parser = yacc.yacc(module=self)
        self.semantic = Semantic()
        self.current_type =''
        self.current_scope = 'global'
        self.variables_stack  = []
        self.dims_stack = []
        self.current_arr = []


