semantic_cube = {
    'int': {
        '+': {
            'int': 'int',
            'float': 'float'
        },
        '-': {
            'int': 'int',
            'float': 'float'
        },
        '=': {
            'int': 'int',
            'float': 'int'
        },
        '*': {
            'int': 'int',
            'float': 'float'
        },
        '/': {
            'int': 'int',
            'float': 'float'
        },

        '<': {
            'int': 'bool',
            'float': 'bool'
        },
        '>': {
            'int': 'bool',
            'float': 'bool'
        },
        '<=': {
            'int': 'bool',
            'float': 'bool'
        },
        '>=': {
            'int': 'bool',
            'float': 'bool'
        },
        '==': {
            'int': 'bool',
            'float': 'bool'
        },
        '!=': {
            'int': 'bool',
            'float': 'bool'
        }
    },

    'float': {
        '+': {
            'int': 'float',
            'float': 'float'
        },
        '-': {
            'int': 'float',
            'float': 'float'
        },
        '=': {
            'int': 'float',
            'float': 'float'
        },
        '*': {
            'int': 'float',
            'float': 'float'
        },
        '/': {
            'int': 'float',
            'float': 'float'
        },

        '<': {
            'int': 'bool',
            'float': 'bool'
        },
        '>': {
            'int': 'bool',
            'float': 'bool'
        },
        '<=': {
            'int': 'bool',
            'float': 'bool'
        },
        '>=': {
            'int': 'bool',
            'float': 'bool'
        },
        '==': {
            'int': 'bool',
            'float': 'bool'
        },
        '!=': {
            'int': 'bool',
            'float': 'bool'
        }
    },

    'bool': {
        '=': {
            'bool': 'bool'
        },
        '==': {
            'bool': 'bool'
        },
        '!=': {
            'bool': 'bool'
        },
        '&': {
            'bool': 'bool'
        },
        '|': {
            'bool': 'bool'
        }
    },

    'char': {
        '=': {
            'char': 'char'
        },
        '==': {
            'char': 'bool'
        },
        '!=': {
            'char': 'bool'
        }
    },

    'pointer':{
        '=':{
            'pointer':'pointer'
        },
        '+':{
            'int':'pointer',
            'pointer':'pointer'
        },
        '-':{
            'int':'pointer',
        },
        '*':{
            'int':'pointer',
            'pointer':'pointer'
        }
    }
}
