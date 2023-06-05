from constants import OPERATORS, PUNCTUATION
from exceptions import TokenizationException

class Token:
	def __init__(self, tokentype, lexeme):
		self.tokentype = tokentype
		self.lexeme = lexeme

	def __str__(self):
		return "Token({:s}, {:s})".format(self.tokentype, self.lexeme)

def tokenize(expression):
	tokens = []
	i = 0
	while i < len(expression):
		if expression[i].isdigit() or expression[i] == '.':
			seen_decimal = (expression[i] == '.')
			seen_exp = False
			lexeme = ''
			while i < len(expression) and (expression[i].isdigit() or (not seen_decimal and expression[i] == '.') or \
			                                                          (not seen_exp and expression[i] in 'eE')):
				if expression[i] == '.':
					seen_decimal = True
				elif expression[i] in 'eE':
					seen_decimal = True
					seen_exp = True
				lexeme += expression[i]
				i += 1
			tokens.append(Token('NUM', lexeme))
		elif expression[i].isalpha() or expression[i] == '_':
			lexeme = ''
			while i < len(expression) and (expression[i].isalnum() or expression[i] == '_'):
				lexeme += expression[i]
				i += 1
			tokens.append(Token('VAR', lexeme))
		elif expression[i] in PUNCTUATION:
			tokens.append(Token('PUNC', expression[i]))
			i += 1
		elif expression[i] in OPERATORS:
			tokens.append(Token('OPERATOR', expression[i]))
			i += 1
		elif expression[i].isspace():
			i += 1
		else:
			raise TokenizationException("error: invalid token `{:s}`.".format(expression[i]))
	return tokens
