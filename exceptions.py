class CalculatorException(Exception):
	pass

class TokenizationException(CalculatorException):
	pass

class MathException(CalculatorException):
	pass

class ParsingException(CalculatorException):
	pass

class EnvironmentException(CalculatorException):
	pass

class FunctionException(CalculatorException):
	pass
