import ply.lex as lex


class MyLexer(object):


    def __init__(self):
        self.line_cont = 0
        self.reserved = {
            'write' : 'WRITE',
            'if':'IF',
            'else':'ELSE',
            'int' : 'INT',
            'float': 'FLOAT',
            'char': 'CHAR',
            'bool': 'BOOL',
            'var' : 'VAR',
            'program':'PROGRAM',
            'void' : 'VOID',
            'string':'STRING',
            'main' : 'MAIN',
            'module' : 'MODULE',
            'read' : 'READ',
            'do' : 'DO',
            'while' : 'WHILE',
            'for' : 'FOR',
            'to' : 'TO',
            'return' : 'RETURN',
            'then' : 'THEN',
            'True' : 'TRUE',
            'False' : 'FALSE'
            }

    tokens = (
        'FNUM','INUM','PLUS','MINUS','TIMES','DIVIDE','LPAREN','RPAREN','ID','SEMICOLONS','COMA',
        'RBRACKET','LBRACKET','GREATERTHAN','MINORTHAN','IF','ELSE', 'EQUAL','INT','FLOAT',
        'VAR','PROGRAM','STRING','CHAR','RCURLYBRACKET','LCURLYBRACKET','MAIN', 'WRITE','MODULE','READ',
        'DO' , 'WHILE', 'FOR','TO','RETURN', 'VOID','AND','OR', 'EQUALS','THEN','CCHAR','BOOL','TRUE','FALSE','TRANSPOSE',
        'INVERSE','DETERMINANT' 
    ) 

        
    # Regular expression rules for simple tokens
    #t_OP   = r'(\+ | \- | \* |\/)'
    t_MINUS   = r'-'
    t_PLUS = r'\+'
    t_TIMES   = r'\*'
    t_DIVIDE  = r'/'
    t_LPAREN  = r'\('
    t_RPAREN  = r'\)'
    t_SEMICOLONS = r'\;'
    t_COMA = r'\,'
    t_RBRACKET = r'\]'
    t_LBRACKET = r'\['
    t_RCURLYBRACKET = r'\}'
    t_LCURLYBRACKET = r'\{'
    t_GREATERTHAN = r'\>'
    t_MINORTHAN =  r'\<'
    t_EQUAL = r'\='
    t_EQUALS = r'\=\='
    t_AND = r'\&'
    t_OR = r'\|'
    t_TRANSPOSE = r'\!'
    t_DETERMINANT = r'\$'
    t_INVERSE = r'\?'
    t_CCHAR = r"'([A-Za-z]|[0-9])'"
    t_STRING= r'"([A-Za-z]|[0-9]|\ |\?|\+|\-|\*|\_|\-|\:|\,)*"'

    
    # A regular expression rule with some action code
    

    def t_FNUM(self, t):
        r'[0-9]+(\.([0-9]+)?([eE][-+]?[0-9]+)?|[eE][-+]?[0-9]+)'
        t.value = float(t.value)
        return t

    def t_ID(self, t):
        r'[A-Za-z]([A-Za-z]|[0-9])*'
        if t.value in self.reserved:
            t.type = self.reserved[ t.value ]
        return t

    def t_INUM(self, t):
        r'\d+'
        t.value = int(t.value)    
        return t
    
    # Define a rule so we can track line numbers
    def t_newline(self, t):
        r'\n+'
        self.line_cont += 1
        t.lexer.lineno += len(t.value)
    
    # A string containing ignored characters (spaces and tabs)
    t_ignore  = ' \t'
    
    # Error handling rule
    def t_error(self, t):
        raise KeyError("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

       # Build the lexer
    
    def build(self,**kwargs):
        return lex.lex(module=self, **kwargs)
        

    def printTokens(self,code):

        lexer = self.build()
        lexer.input(code)
        while True:
            
            tok = lexer.token()
            if not tok: 
                break      # No more input
            print(tok)
 