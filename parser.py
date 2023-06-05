from exceptions import EnvironmentException, FunctionException, MathException, ParsingException

class Operand:
	def __init__(self, value):
		self.value = value

	def evaluate(self):
		return self.value

class Atom:
	def __init__(self, left, operator, right):
		self.left = left
		self.operator = operator
		self.right = right

	def evaluate(self):
		result_left = self.left.evaluate()
		result_right = self.right.evaluate()
		if self.operator.lexeme == '*':
			return result_left * result_right
		elif self.operator.lexeme == '/':
			if result_right == 0:
				raise MathException("error: cannot divide by 0.")
			return result_left / result_right
		elif self.operator.lexeme == '%':
			if int(result_right) != result_right or result_right <= 0:
				raise MathException("error: invalid dividend for modulo operator `{:d}`.".format(result_right))
			return result_left % result_right
		raise MathException("error: invalid operator `{:s}`.".format(self.operator.lexeme))

class Expression:
	def __init__(self, atom_left, operator, atom_right):
		self.atom_left = atom_left
		self.operator = operator
		self.atom_right = atom_right

	def evaluate(self):
		result_left = self.atom_left.evaluate()
		result_right = self.atom_right.evaluate()
		if self.operator.lexeme == '+':
			return result_left + result_right
		elif self.operator.lexeme == '-':
			return result_left - result_right
		raise MathException("error: invalid operator `{:s}`.".format(self.operator.lexeme))

class Function:
	def __init__(self, name, varNames, tokens, env):
		self.name = name
		self.varNames = varNames
		self.tokens = tokens
		self.env = env.extend()

	def evaluate(self):
		return 0

	def construct(self, *args):
		if len(args) != len(self.varNames):
			raise FunctionException("error: incorrect number of arguments for function `{:s}`.".format(self.name))
		for idx, arg in enumerate(args):
			self.env.set(self.varNames[idx], arg)
		expressions = Parser(self.tokens, self.env).parse()
		results = [expr.evaluate() for expr in expressions]
		if len(results) == 0:
			return 0
		return results[-1]

class FunctionCall:
	def __init__(self, function, expressions):
		self.function = function
		self.expressions = expressions

	def evaluate(self):
		# TODO: surround with a try-except to return a MathException
		try:
			return self.function(*[expr.evaluate() for expr in self.expressions])
		except:
			# TODO: finish this
			raise MathException("error: math error in evaluation of function `{:s}`.".format())

class Environment:
	def __init__(self):
		self.mapping = {}
		self.functions = {}

	def get(self, index):
		if index in self.mapping:
			return self.mapping[index]
		raise EnvironmentException("error: unknown variable `{:s}`.".format(index))

	def set(self, index, value):
		self.mapping[index] = value

	def isFunc(self, index):
		return index in self.functions

	def getFunc(self, index):
		if self.isFunc(index):
			return self.functions[index]
		raise EnvironmentException("error: unknown function `{:s}`.".format(index))

	def setFunc(self, index, func):
		self.functions[index] = func

	def extend(self):
		envNew = Environment()
		for index in self.mapping:
			envNew.mapping[index] = self.mapping[index]
		for index in self.functions:
			envNew.functions[index] = self.functions[index]
		return envNew

class Parser:
	def __init__(self, tokens, env):
		self.tokens = tokens
		self.index = 0
		self.env = env

	def end(self):
		return 0 > self.index or self.index >= len(self.tokens)

	def next(self):
		if self.end():
			raise ParsingException("error: index out of range for parser (next).")
		return self.tokens[self.index]

	def consume(self):
		if self.end():
			raise ParsingException("error: index out of range for parser (consume).")
		token = self.tokens[self.index]
		self.index += 1
		return token

	def matchType(self, tokentype):
		return not self.end() and self.next().tokentype == tokentype

	def matchToken(self, tokentype, lexeme):
		return self.matchType(tokentype) and self.next().lexeme == lexeme

	def matchTokens(self, tokentypes, lexemes):
		return not self.end() and self.next().tokentype in tokentypes and self.next().lexeme in lexemes

	def parseUnit(self):
		if self.matchType('NUM'):
			return Operand(float(self.consume().lexeme))
		elif self.matchType('VAR'):
			name = self.consume().lexeme
			if name == 'macro':
				name = self.consume().lexeme
				if self.matchToken('PUNC', '('):
					self.consume()
					varNames = []
					while not self.matchToken('PUNC', ')'):
						if self.matchType('VAR'):
							varNames.append(self.consume().lexeme)
						else:
							raise ParsingException("error: expected VAR, got `{:s}`.".format('EOF' if self.end() else self.next().tokentype))
						if self.matchToken('PUNC', ')'):
							break
						elif self.matchTokens(['PUNC'], [',', '\n']):
							self.consume()
						else:
							raise ParsingException("error: expected `)`, `,`, or `\\n`, got `{:s}`.".format('EOF' if self.end() else self.next().lexeme))
					if self.end():
						raise ParsingException("error: expected `)`, got `EOF`.")
					self.consume()
					if self.matchToken('PUNC', '('):
						self.consume()
						tokens = []	
						parensCount = 1
						while not self.end():
							if self.matchToken('PUNC', '('):
								parensCount += 1
							elif self.matchToken('PUNC', ')'):
								parensCount -= 1
							if parensCount == 0:
								break
							tokens.append(self.consume())
						if self.matchToken('PUNC', ')'):
							self.consume()
							self.env.setFunc(name, Function(name, varNames, tokens, self.env).construct)
							return Operand(0)
						else:
							raise ParsingException("error: expected `)`, got `EOF`.")
					else:
						raise ParsingException("error: expected `)`, got `{:s}`.".format('EOF' if self.end() else self.next().lexeme))
				else:
					raise ParsingException("error: expected `)`, got `{:s}`.".format('EOF' if self.end() else self.next().lexeme))
			elif self.matchToken('PUNC', '('):
				if not self.env.isFunc(name):
					raise ParsingException("error: unknown function `{:s}`.".format(name))
				self.consume()
				expressions = self.parseExpressions(lambda this: this.matchToken('PUNC', ')'))
				if self.matchToken('PUNC', ')'):
					self.consume()
					return FunctionCall(self.env.getFunc(name), expressions)
				else:
					raise ParsingException("error: expected `)`, got `{:s}`.".format('EOF' if self.end() else self.next().lexeme))
			elif self.matchToken('OPERATOR', '='):
				self.consume()
				expression = self.parseExpression()
				self.env.set(name, expression.evaluate())
				return expression
			else:
				return Operand(self.env.get(name))
		elif self.matchToken('PUNC', '('):
			self.consume()
			expression = self.parseExpression()
			if self.matchToken('PUNC', ')'):
				self.consume()
				return expression
			raise ParsingException("error: expected `)`, got `{:s}`.".format('EOF' if self.end() else self.next().lexeme))
		raise ParsingException("error: expected operand, got `EOF`.")

	def parseAtom(self):
		unit_left = self.parseUnit()
		while self.matchTokens(['OPERATOR'], ['*', '/', '%']):
			operator = self.consume()
			unit_right = self.parseUnit()
			unit_left = Atom(unit_left, operator, unit_right)
		return unit_left

	def parseExpression(self):
		atom_left = self.parseAtom()
		while self.matchTokens(['OPERATOR'], ['+', '-']):
			operator = self.consume()
			atom_right = self.parseAtom()
			atom_left = Expression(atom_left, operator, atom_right)
		return atom_left

	def parseExpressions(self, endCondition):
		expressions = []
		while not endCondition(self):
			expressions.append(self.parseExpression())
			if endCondition(self):
				break
			elif self.matchTokens(['PUNC'], [',', '\n']):
				self.consume()
			else:
				raise ParsingException("error: expected `,` or `\\n`, got `{:s}`.".format('EOF' if self.end() else self.next().lexeme))
		return expressions

	def parse(self):
		return self.parseExpressions(lambda this: this.end())
