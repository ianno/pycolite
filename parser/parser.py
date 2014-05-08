import ply.lex as lex
import ply.yacc as yacc
import lexer

tokens = lexer.tokens

def p_expr(p):
		'''expr : expr AND expr
				| expr OR expr
				| NOT expr
				| expr IMPLICATION expr
				| expr EQUALS expr
				| GLOBAL expr
				| FUTURE expr
				| NEXT expr
				| expr UNTIL expr
				| expr RELEASE expr
				| expr WEAK_UNTIL expr
				| LITERAL'''

yacc.yacc()

if __name__ == '__main__':
		yacc.parse("h | b")

