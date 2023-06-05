from constants import *
from exceptions import CalculatorException
from lexer import tokenize 
from parser import Environment, Parser
import math

def main():
	env = Environment()
	env.setFunc('ln', math.log)
	env.setFunc('sqrt', math.sqrt)
	env.setFunc('atan', math.atan)
	env.setFunc('asin', math.asin)
	env.setFunc('acos', math.acos)
	env.setFunc('cos', math.cos)
	env.setFunc('sin', math.sin)
	env.setFunc('tan', math.tan)
	env.setFunc('log10', math.log10)
	env.setFunc('exp', math.exp)

	while True:
		expression = input('-> ')
		if expression == 'q()' or expression == 'quit()':
			break
		try:
			tokens = tokenize(expression)
			expressions = Parser(tokens, env).parse()
			results = [expr.evaluate() for expr in expressions]
			print(*results)
		except CalculatorException as ex:
			print(ex)

if __name__ == '__main__':
	main()
