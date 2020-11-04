from lexer import MyLexer
import ply.yacc as yacc
from semantic import Semantic

class MyParser(object):

    tokens = MyLexer.tokens


    def p_expression_program(self,p):
        '''
        program : PROGRAM ID SEMICOLONS program2 main
        program2 : program4
                 | program9
        program4 : VAR program5
        program7 : COMA program6
                 | SEMICOLONS program8
        program8 : program5
                 | program9
        program9 : functions
                 | empty
        '''


    def p_expression_program5(self,p):
        '''
        program5 : type program6
        '''
        for var in self.variables_stack:
            self.semantic.insert_variable(var,p[1],'global')


    def p_expression_program6(self,p):
        '''
        program6 : var program7
        '''
        self.variables_stack.append(p[1])
    
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
            self.semantic.insert_variable(var,p[1],'global')

    def p_expression_vars2(self,p):
        '''
        vars2 : var vars3
        '''
        self.variables_stack.append(p[1])

    def p_expression_functions(self,p):
        '''
        functions : functions1 MODULE ID LPAREN functions2 RPAREN functions5 block functions3
        functions1 : type
                   | VOID
        functions2 : type param functions4
        functions3 : functions
                   | empty
        functions4 : COMA functions2
                   | empty
        functions5 : vars
                   | empty
        '''

    

    def p_term_type(self,p):
        
        '''
        type : INT 
             | FLOAT
             | CHAR
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
        condition : IF LPAREN expression RPAREN THEN block condition1
        condition1 : empty 
                   | ELSE block
        '''

    def p_expression_writing(self,p):
        '''
        writing : WRITE LPAREN  writing1 RPAREN SEMICOLONS
        writing1 : writing2 writing3
        writing2 : expression
                 | STRING
        writing3 : COMA writing1
                 | empty
        '''
    
    def p_expression_read(self,p):
        '''
        read : READ LPAREN read1 RPAREN SEMICOLONS
        read1 : param read2
        read2 : COMA read1
              | empty
        '''
    def p_expression_repetitionstatute(self,p):
        '''
        repetitionstatute : repetitionstatute1 DO block
        repetitionstatute1 : FOR param EQUAL expression TO expression
                           | WHILE LPAREN expression RPAREN
        '''
    def p_asignation_factor(self,p):
        '''
        asignation : param EQUAL expression SEMICOLONS
        '''
        

    def p_asignation_return(self,p):
        '''
        return : RETURN LPAREN expression RPAREN SEMICOLONS
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
        var2 : LBRACKET INUM RBRACKET
             | empty
        '''

    def p_expression_call(self,p):
        '''
        call : ID LPAREN call1 RPAREN 
        call1 : expression call2
        call2 : COMA call1
              | empty
        '''

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
        main : MAIN LPAREN RPAREN block
        '''

    def p_expression_param(self,p):
        '''
        param : ID param1
        '''
        p[0] = p[1]

    def p_expression_param1(self,p):
        '''
        param1 : LBRACKET expression RBRACKET param2
               | empty
        param2 : LBRACKET expression RBRACKET
               | empty
        '''

    def p_expression_expression(self,p):
        '''
        expression : comparison expression1 comparison
                   | comparison empty
        '''
        if p[2] == None:
            p[0] = p[1]
        else:
            self.semantic.insert_quadruple_operation(p[2],p[1],p[3])
        self.semantic.end_expression()

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
               | call
        '''
        p[0] = p[1]

    def parse(self,inputString):
        #r = MyLexer()
        #r.printTokens(inputString)
        self.parser.parse(input=inputString,lexer=self.lexer,debug=False)

    # Error rule for syntax errors
    def p_error(self,p):
        print("Syntax error in input!")

    def __init__(self):
        self.lexer = MyLexer().build()
        self.parser = yacc.yacc(module=self)
        self.semantic = Semantic()
        self.current_type =''
        self.variables_stack  = []


