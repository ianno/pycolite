'''
This module contains all the symbol sets used to interface with external tools

Author: Antonio Iannopollo
'''

class Ltl3baSymbolSet(object):
    '''
    Spin symbol class
    All literals MUST be lowercase strings
    Make sure to include spaces before and after each symbols,
    you can trim later
    '''

    symbols = {
        'AND' : r'&&',
        'OR' : r'||',
        'GLOBALLY' : r'G',
        'EVENTUALLY' : r'F',
        'NEXT' : r'X',
        'UNTIL' : r'U',
        'RELEASE' : r'R',
        'WEAK_UNTIL' : r'W',
        'IMPLICATION' : r'->',
        'EQUALITY' : r'=',
        'NOT' : r'!',
        'TRUE' : r'true',
        'FALSE' : r'false',
        'LPAREN' : '(',
        'RPAREN' : ')',
        'GE' : r'>',
        'GEQ' : r'>=',
        'LE' : r'<',
        'LEQ' : r'<=',
        'ADD' : r'+',
        'SUB' : r'-',
        'MUL' : r'*',
        'DIV' : r'/'
        }

class NusmvSymbolSet(object):
    '''
    Spin symbol class
    All literals MUST be lowercase strings
    Make sure to include spaces before and after each symbols,
    you can trim later
    '''

    symbols = {
        'AND' : r'&',
        'OR' : r'|',
        'GLOBALLY' : r'G',
        'EVENTUALLY' : r'F',
        'NEXT' : r'X',
        'UNTIL' : r'U',
        'RELEASE' : r'V',
        'WEAK_UNTIL' : r'W',
        'IMPLICATION' : r'->',
        'EQUALITY' : r'<->',
        'NOT' : r'!',
        'TRUE' : r'TRUE',
        'FALSE' : r'FALSE',
        'LPAREN' : '(',
        'RPAREN' : ')',
        'GE' : '>',
        'GEQ' : '>=',
        'LE' : '<',
        'LEQ' : '<=',
        'ADD' : '+',
        'SUB' : '-',
        'MUL' : '*',
        'DIV' : '/'
        }
