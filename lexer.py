import ply.lex as lex


class MyLexer(object):


    def __init__(self):
        self.reserved = {
            'write' : 'WRITE',
            'if':'IF',
            'else':'ELSE',
            'int' : 'INT',
            'float': 'FLOAT',
            'char': 'CHAR',
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
            'return' : 'RETURN'
            }

    tokens = (
        'NUMBER','PLUS','MINUS','TIMES','DIVIDE','LPAREN','RPAREN','ID','SEMICOLONS','COMA',
        'RBRACKET','LBRACKET','GREATERTHAN','MINORTHAN','IF','ELSE', 'EQUAL','INT','FLOAT',
        'VAR','PROGRAM','STRING','CHAR','RCURLYBRACKET','LCURLYBRACKET','MAIN', 'WRITE','MODULE','READ',
        'DO' , 'WHILE', 'FOR','TO','RETURN', 'VOID','AND','OR', 'EQUALS'
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
    t_RBRACKET = r'\}'
    t_LBRACKET = r'\{'
    t_RCURLYBRACKET = r'\]'
    t_LCURLYBRACKET = r'\['
    t_GREATERTHAN = r'\>'
    t_MINORTHAN =  r'\<'
    t_EQUAL = r'\='
    t_EQUALS = r'\=='
    t_AND = r'\&'
    t_OR = r'\|'
    t_STRING = r'"([A-Za-z]|[0-9])*"'

    
    # A regular expression rule with some action code
    def t_NUMBER(self, t):
        r'[0-9]+'
        t.value = int(t.value)    
        return t

    def t_ID(self, t):
        r'[A-Za-z]([A-Za-z]|[0-9])*'
        if t.value in self.reserved:
            t.type = self.reserved[ t.value ]
        return t
    
    # Define a rule so we can track line numbers
    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)
    
    # A string containing ignored characters (spaces and tabs)
    t_ignore  = ' \t'
    
    # Error handling rule
    def t_error(self, t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

       # Build the lexer
    
    def build(self,**kwargs):
        return lex.lex(module=self, **kwargs)
        


