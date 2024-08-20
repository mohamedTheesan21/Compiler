from LexicalAnalyzer import LexicalAnalyzer
from AST_.AST import AST
from Parser import Parser
from CSEMachine import CSEMachine


def main():

    file = open("input2.txt", "r")
    input_string = file.read()

    input = LexicalAnalyzer(input_string)
    parser = Parser(input)
    ast = parser.build_ast()
    ast.standardize()

    csem = CSEMachine(ast)
    csem.evaluate_program()

if __name__ == "__main__":
    main()