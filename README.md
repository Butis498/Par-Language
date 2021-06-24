# Par-language

### Desctiption and main features of the language

Our programming language has the basic functions of any other language, that is, it only supports variables of type int, float, char and bool. Can be declared arrays and arrays, in which we use pointers as support within these to memory allocation. You can use void and variable types functions already previously mentioned, although it is a basic language, the functions support recursion and the use of parameters if required. Unlike other languages the declaration of variables is done before starting the function blocks and is written "Var" before you start declaring. Par ++ supports the use of conditionals, for and while loops with slight syntax changes. It can be read and written within our language as well than to perform basic arithmetic operations such as multiplication, addition, subtraction, and divisions.

### Possible Errors

#### System Errors:
● ("Syntax error in input!") 
#### Key Errors:
● ("Wrong usage of modifier") 
● ("Wrong usage of modifier in a not matrix variable")
● ('No return for function given')('Not int type in loop’)
● ('Variable ' + var + ' already exists')
● ('Can not insert variable, ' + str(err))
● ('Not function found ' , str(err))
● ("Function " + function_name + " already exists")
● (str(err) + ' does not exists')
● (f"No variable '{var_name}' found on scope")
● ('Array not found',str(err))
● ('modifier not found')
● ('Matrix not found')
#### Type Errors:
● ('No memory type found, ' + str(err)) 
● (str(err))● (f'Incompatible Types {validation_type_1} and {validation_type_2}')
● ('Can not update function, ' + str(err))
● ('Incompatible operation')
● ('Not compatible operation with matrix or array')
● (f'Incompatible operation "{operand_1}" and "{operand_2}"')
● ('Not supported type for operands '+ var1[0] + ' and ' + var2[0])
● (f'No type recognized for "{var}"')
● (f'{operand_1} Not bool variable')
● (f'Not supported operation "{operation}" for {mat_1} and {mat_2}')
● (f'Not compatible types for "{mat1_type}" and "{mat2_type}"')
#### Memory Errors:
● ('Out of memory variables')
● ('Segmentation fault')
● ('Repeated memory value')
● (f'Not address found {addr}')
#### Value Errors:
● ('No last temp value')
● ('No last temp value')
● ('Array not found',str(err)
● ('Cant get var scope '+ str(var[0]))
● ('No last temp value for action type')
● ('Missing Params in function '+ str(self.func_call_stack[-1]) )
● ('Too many arguments in function '+func)
● ('Wrong index in array' + str(err))
● ('Matrix must be n x n dims')
● ("Not compatible matrix")
● ('Out of index')


### Used tools for the development

Language: Python 3.8.3 was used for the development of the compiler and the virtual machine
Utilities: PLY was used for the lexicon and syntax, JSON library simply for printing orderly, and Pickle library to export the obj.


### Lexical

1. t_MINUS = r'-'
2. t_PLUS = r'\+'
3. t_TIMES = r'\*'
4. t_DIVIDE = r'/'
5. t_LPAREN = r'\('
6. t_RPAREN = r'\)'
7. t_SEMICOLONS = r'\;'
8. t_COMA = r'\,'
9. t_RBRACKET = r'\]'
10. t_LBRACKET = r'\['
11. t_RCURLYBRACKET = r'\}'
12. t_LCURLYBRACKET = r'\{'
13. t_GREATERTHAN = r'\>'
14. t_MINORTHAN = r'\<'
15. t_EQUAL = r'\='
16. t_EQUALS = r'\=\='
17. t_AND = r'\&'
18. t_OR = r'\|'
19. t_TRANSPOSE = r'\!'
20. t_DETERMINANT = r'\$'
21. t_INVERSE = r'\?'
22. t_CCHAR = r"'([A-Za-z]|[0-9])'"
23. t_STRING= r'"([A-Za-z]|[0-9])*"'
24. t_FNUM = r'[0-9]+(\.([0-9]+)?([eE][-+]?[0-9]+)?|[eE][-+]?[0-9]+)'25. t_ID = r'[A-Za-z]([A-Za-z]|[0-9])*'
26. t_INUM = r'\d+'
27. t_newline = r'\n+'
28. t_ignore = ' \t'
29. t_error = raise KeyError("Illegal character '%s'" % t.value[0])
