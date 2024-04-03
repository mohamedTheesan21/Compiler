import Lexical_Analyzer

# Define ASTNodeType enumeration


class ASTNodeType:
    # General
    IDENTIFIER = "<ID:%s>"
    STRING = "<STR:'%s>"
    INTEGER = "<INT:%s>"

    # Expressions
    LET = "let"
    LAMBDA = "lambda"
    WHERE = "where"

    # Tuple expressions
    TAU = "tau"
    AUG = "aug"
    CONDITIONAL = "->"

    # Boolean Expressions
    OR = "or"
    AND = "&"
    NOT = "not"
    GR = "gr"
    GE = "ge"
    LS = "ls"
    LE = "le"
    EQ = "eq"
    NE = "ne"

    # Arithmetic Expressions
    PLUS = "+"
    MINUS = "-"
    NEG = "neg"
    MULT = "*"
    DIV = "/"
    EXP = "**"
    AT = "@"

    # Rators and Rands
    GAMMA = "gamma"
    TRUE = "<true>"
    FALSE = "<false>"
    NIL = "<nil>"
    DUMMY = "<dummy>"

    # Definitions
    WITHIN = "within"
    SIMULTDEF = "and"
    REC = "rec"
    EQUAL = "="
    FCNFORM = "function_form"

    # Variables
    PAREN = "<()>"
    COMMA = ","

    # Post-standardize
    YSTAR = "<Y*>"
    BETA = ""
    DELTA = ""
    ETA = ""
    TUPLE = ""


class TokenType:
    IDENTIFIER = "IDENTIFIER"
    STRING = "STRING"
    INTEGER = "INTEGER"
    RESERVED = "RESERVED"
    OPERATOR = "OPERATOR"
    L_PAREN = "L_PAREN"
    R_PAREN = "R_PAREN"
    DELETE = "DELETE"


# Define ASTNode class
class ASTNode:
    def __init__(self, type=None, value=None, child=None, sibling=None, line_number=None):
        self.type = type
        self.value = value
        self.child = child
        self.sibling = sibling
        self.line_number = line_number


# Define AST class
class AST:
    def __init__(self, root):
        self.root = root


# Define Parser class
class Parser:
    def __init__(self, scanner):
        self.scanner = scanner
        self.tokens = scanner.tokens
        self.current_token = None
        self.stack = []

    def build_ast(self):
        print("Building AST")
        self.start_parse()
        ast = AST(self.stack.pop())
        return ast

    def start_parse(self):
        self.read_non_terminal()
        self.read_e()
        if self.current_token is not None:
            raise Exception()
        else:
            print("Parsing complete, no errors found.")

    def read_non_terminal(self):
        if len(self.tokens) > 0:
            self.current_token = self.tokens.pop(0)
            # print(self.current_token.type, self.current_token.value)

        else:
            self.current_token = None

        if self.current_token is not None:
            if self.current_token.type == TokenType.IDENTIFIER:
                self.create_terminal_ast_node(
                    ASTNodeType.IDENTIFIER, self.current_token.value)
            elif self.current_token.type == TokenType.INTEGER:
                self.create_terminal_ast_node(
                    ASTNodeType.INTEGER, self.current_token.value)
            elif self.current_token.type == TokenType.STRING:
                self.create_terminal_ast_node(
                    ASTNodeType.STRING, self.current_token.value)

    def is_current_token(self, type, value=None):
        return self.current_token is not None and self.current_token.type == type and (
            value is None or self.current_token.value == value)

    def is_current_token_type(self, type):
        return self.current_token is not None and self.current_token.type == type

    def build_nary_ast_node(self, type, ary_value):
        # print("from build_nary_ast_node", type, ary_value)
        # for x in self.stack:
        #     print(x.type, end=" ")
        # print()
        node = ASTNode(type=type)
        while ary_value > 0:
            child = self.stack.pop()
            if node.child is not None:
                child.sibling = node.child
            node.child = child
            node.line_number = child.line_number
            ary_value -= 1
        self.stack.append(node)

    def create_terminal_ast_node(self, terminal_type, terminal_value):
        node = ASTNode(type=terminal_type, value=terminal_value, line_number=self.current_token.line_number)
        self.stack.append(node)

    # EXPRESSIONS

    # NON TERMINAL -> E
    def read_e(self):
        # E -> 'let' D 'in' E => 'let'
        if self.is_current_token(TokenType.RESERVED, "let"):
            self.read_non_terminal()
            self.read_d()
            if not self.is_current_token(TokenType.RESERVED, "in"):
                raise Exception()
            self.read_non_terminal()
            self.read_e()
            self.build_nary_ast_node(ASTNodeType.LET, 2)
            self.read_non_terminal()
        # E -> 'fn' Vb+ '.' E => 'lambda'
        elif self.is_current_token(TokenType.RESERVED, "fn"):
            trees_to_pop = 0
            self.read_non_terminal()
            while self.is_current_token_type(TokenType.IDENTIFIER) or self.is_current_token_type(TokenType.L_PAREN):
                self.read_vb()
                trees_to_pop += 1
            if trees_to_pop == 0:
                raise Exception()
            if not self.is_current_token(TokenType.OPERATOR, "."):
                raise Exception()
            self.read_non_terminal()
            self.read_e()
            self.build_nary_ast_node(ASTNodeType.LAMBDA, trees_to_pop + 1)
        else:  # E -> Ew
            self.read_ew()

    # NON TERMINAL -> EW
    def read_ew(self):
        self.read_t()  # Ew -> T
        # Ew -> T 'where' Dr => 'where'
        if self.is_current_token(TokenType.RESERVED, "where"):
            self.read_non_terminal()
            self.read_dr()
            self.build_nary_ast_node(ASTNodeType.WHERE, 2)

    # Tuple Expressions

    # NON TERMINAL -> T
    def read_t(self):
        self.read_ta()  # T -> Ta
        trees_to_pop = 0
        # T -> Ta (',' Ta )+ => 'tau'
        while self.is_current_token(TokenType.OPERATOR, ","):
            self.read_non_terminal()
            self.read_ta()
            trees_to_pop += 1
        if trees_to_pop > 0:
            self.build_nary_ast_node(ASTNodeType.TAU, trees_to_pop + 1)

    # NON TERMINAL -> TA
    def read_ta(self):
        self.read_tc()  # Ta -> Tc
        # Ta -> Ta 'aug' Tc => 'aug'
        while self.is_current_token(TokenType.RESERVED, "aug"):
            self.read_non_terminal()
            self.read_tc()
            self.build_nary_ast_node(ASTNodeType.AUG, 2)

    # NON TERMINAL -> TC
    def read_tc(self):
        self.read_b()  # Tc -> B
        # Tc -> B '->' Tc '|' Tc => '->'
        if self.is_current_token(TokenType.OPERATOR, "->"):
            self.read_non_terminal()
            self.read_tc()
            if not self.is_current_token(TokenType.OPERATOR, "|"):
                raise Exception()
            self.read_non_terminal()
            self.read_tc()
            self.build_nary_ast_node(ASTNodeType.CONDITIONAL, 3)

    # Boolean Expressions

    # NON TERMINAL -> B
    def read_b(self):
        self.read_bt()  # B -> Bt
        # B -> B 'or' Bt => 'or'
        while self.is_current_token(TokenType.RESERVED, "or"):
            self.read_non_terminal()
            self.read_bt()
            self.build_nary_ast_node(ASTNodeType.OR, 2)

    # NON TERMINAL -> BT
    def read_bt(self):
        self.read_bs()  # Bt -> Bs;
        # Bt -> Bt '&' Bs => '&'
        while self.is_current_token(TokenType.OPERATOR, "&"):
            self.read_non_terminal()
            self.read_bs()
            self.build_nary_ast_node(ASTNodeType.AND, 2)

    # NON TERMINAL -> BS
    def read_bs(self):
        if self.is_current_token(TokenType.RESERVED, "not"):  # Bs -> 'not' Bp => 'not'
            self.read_non_terminal()
            self.read_bp()
            self.build_nary_ast_node(ASTNodeType.NOT, 1)
        else:
            self.read_bp()  # Bs -> Bp

    # NON TERMINAL -> BP
    def read_bp(self):
        self.read_a()  # Bp -> A
        # Bp -> A('gr' | '>' ) A => 'gr'
        if self.is_current_token(TokenType.RESERVED, "gr") or self.is_current_token(TokenType.OPERATOR, ">"):
            self.read_non_terminal()
            self.read_a()
            self.build_nary_ast_node(ASTNodeType.GR, 2)
        # Bp -> A ('ge' | '>=') A => 'ge'
        elif self.is_current_token(TokenType.RESERVED, "ge") or self.is_current_token(TokenType.OPERATOR, ">="):
            self.read_non_terminal()
            self.read_a()
            self.build_nary_ast_node(ASTNodeType.GE, 2)
        # Bp -> A ('ls' | '<' ) A => 'ls'
        elif self.is_current_token(TokenType.RESERVED, "ls") or self.is_current_token(TokenType.OPERATOR, "<"):
            self.read_non_terminal()
            self.read_a()
            self.build_nary_ast_node(ASTNodeType.LS, 2)
        # Bp -> A ('le' | '<=') A => 'le'
        elif self.is_current_token(TokenType.RESERVED, "le") or self.is_current_token(TokenType.OPERATOR, "<="):
            self.read_non_terminal()
            self.read_a()
            self.build_nary_ast_node(ASTNodeType.LE, 2)
        # Bp -> A 'eq' A => 'eq'
        elif self.is_current_token(TokenType.RESERVED, "eq"):
            self.read_non_terminal()
            self.read_a()
            self.build_nary_ast_node(ASTNodeType.EQ, 2)
        # Bp -> A 'ne' A => 'ne'
        elif self.is_current_token(TokenType.RESERVED, "ne"):
            self.read_non_terminal()
            self.read_a()
            self.build_nary_ast_node(ASTNodeType.NE, 2)
    # Arithmetic Expressions

    # NON TERMINAL -> A
    def read_a(self):
        if self.is_current_token(TokenType.OPERATOR, "+"):  # A -> '+' At
            self.read_non_terminal()
            self.read_at()
        elif self.is_current_token(TokenType.OPERATOR, "-"):  # A -> '-' At => 'neg'
            self.read_non_terminal()
            self.read_at()
            self.build_nary_ast_node(ASTNodeType.NEG, 1)
        else:
            self.read_at()

        plus = True
        while self.is_current_token(TokenType.OPERATOR, "+") or self.is_current_token(TokenType.OPERATOR, "-"):
            if self.current_token.value == "+":
                plus = True
            elif self.current_token.value == "-":
                plus = False
            self.read_non_terminal()
            self.read_at()
            if plus:  # A -> A '+' At => '+'
                self.build_nary_ast_node(ASTNodeType.PLUS, 2)
            else:  # A -> A '-' At => '-'
                self.build_nary_ast_node(ASTNodeType.MINUS, 2)

    # NON TERMINAL -> AT
    def read_at(self):
        self.read_af()  # At -> Af;
        mult = True
        while self.is_current_token(TokenType.OPERATOR, "*") or self.is_current_token(TokenType.OPERATOR, "/"):
            if self.current_token.value == "*":
                mult = True
            elif self.current_token.value == "/":
                mult = False
            self.read_non_terminal()
            self.read_af()
            if mult:  # At -> At '*' Af => '*'
                self.build_nary_ast_node(ASTNodeType.MULT, 2)
            else:  # At -> At '/' Af => '/'
                self.build_nary_ast_node(ASTNodeType.DIV, 2)

    # NON TERMINAL -> AF
    def read_af(self):
        self.read_ap()
        if self.is_current_token(TokenType.OPERATOR, "**"):  # Af -> Ap '**' Af => '**'
            self.read_non_terminal()
            self.read_af()
            self.build_nary_ast_node(ASTNodeType.EXP, 2)

    # NON TERMINAL -> AP
    def read_ap(self):
        self.read_r()
        # Ap -> Ap '@' '<IDENTIFIER>' R => '@'
        while self.is_current_token(TokenType.OPERATOR, "@"):
            self.read_non_terminal()
            if not self.is_current_token(TokenType.IDENTIFIER):
                raise Exception()
            self.read_non_terminal()
            self.read_r()
            self.build_nary_ast_node(ASTNodeType.AT, 3)

    # Rators and Rands

    # NON TERMINAL -> R
    def read_r(self):

        self.read_rn()

        self.read_non_terminal()
        while self.is_current_token(TokenType.INTEGER) or self.is_current_token(TokenType.STRING) or \
                self.is_current_token(TokenType.IDENTIFIER) or self.is_current_token(TokenType.RESERVED, "true") \
                or self.is_current_token(TokenType.RESERVED, "false") or self.is_current_token(TokenType.RESERVED, "nil") \
                or self.is_current_token(TokenType.RESERVED, "dummy") or self.is_current_token(TokenType.L_PAREN):
            self.read_rn()
            self.build_nary_ast_node(ASTNodeType.GAMMA, 2)
            self.read_non_terminal()

    # NON TERMINAL -> RN
    def read_rn(self):

        if self.is_current_token(TokenType.IDENTIFIER) or self.is_current_token(TokenType.INTEGER) or \
                self.is_current_token(TokenType.STRING):
            pass
        elif self.is_current_token(TokenType.RESERVED, "true"):
            self.create_terminal_ast_node(ASTNodeType.TRUE, "true")
        elif self.is_current_token(TokenType.RESERVED, "false"):
            self.create_terminal_ast_node(ASTNodeType.FALSE, "false")
        elif self.is_current_token(TokenType.RESERVED, "nil"):
            self.create_terminal_ast_node(ASTNodeType.NIL, "nil")
        elif self.is_current_token(TokenType.L_PAREN):
            self.read_non_terminal()
            self.read_e()

            if not self.is_current_token(TokenType.R_PAREN):
                raise Exception()
        elif self.is_current_token(TokenType.RESERVED, "dummy"):
            self.create_terminal_ast_node(ASTNodeType.DUMMY, "dummy")

    # Definitions

    # NON TERMINAL -> D
    def read_d(self):

        self.read_da()
        # D -> Da 'within' D => 'within'
        if self.is_current_token(TokenType.RESERVED, "within"):
            self.read_non_terminal()
            self.read_d()
            self.build_nary_ast_node(ASTNodeType.WITHIN, 2)

    # NON TERMINAL -> DA
    def read_da(self):

        self.read_dr()
        trees_to_pop = 0
        # Da -> Dr ( 'and' Dr )+ => 'and'
        while self.is_current_token(TokenType.RESERVED, "and"):
            self.read_non_terminal()
            self.read_dr()
            trees_to_pop += 1
        if trees_to_pop > 0:
            self.build_nary_ast_node(ASTNodeType.SIMULTDEF, trees_to_pop + 1)

    # NON TERMINAL -> DR
    def read_dr(self):
        if self.is_current_token(TokenType.RESERVED, "rec"):  # Dr -> 'rec' Db => 'rec'
            self.read_non_terminal()
            self.read_db()
            self.build_nary_ast_node(ASTNodeType.REC, 1)
        else:
            self.read_db()

    # NON TERMINAL -> DB
    def read_db(self):

        if self.is_current_token(TokenType.L_PAREN):  # Db -> '(' D ')'
            self.read_d()
            self.read_non_terminal()
            if not self.is_current_token(TokenType.R_PAREN):
                raise Exception()
            self.read_non_terminal()
        elif self.is_current_token(TokenType.IDENTIFIER):
            self.read_non_terminal()
            if self.is_current_token(TokenType.OPERATOR, ","):  # Db -> Vl '=' E => '='
                self.read_non_terminal()
                self.read_vl()
                if not self.is_current_token(TokenType.OPERATOR, "="):
                    raise Exception()
                self.build_nary_ast_node(ASTNodeType.COMMA, 2)
                self.read_non_terminal()
                self.read_e()
                self.build_nary_ast_node(ASTNodeType.EQUAL, 2)
            else:  # Db -> '<IDENTIFIER>' Vb+ '=' E => 'fcn_form'
                # Db -> Vl '=' E => '='; if Vl had only one IDENTIFIER (no commas)
                if self.is_current_token(TokenType.OPERATOR, "="):
                    self.read_non_terminal()
                    self.read_e()
                    self.build_nary_ast_node(ASTNodeType.EQUAL, 2)
                else:  # Db -> '<IDENTIFIER>' Vb+ '=' E => 'fcn_form'
                    trees_to_pop = 0
                    while self.is_current_token(TokenType.IDENTIFIER) or self.is_current_token(TokenType.L_PAREN):
                        self.read_vb()
                        trees_to_pop += 1
                    if trees_to_pop == 0:
                        raise Exception()
                    if not self.is_current_token(TokenType.OPERATOR, "="):
                        raise Exception()
                    self.read_non_terminal()
                    self.read_e()
                    self.build_nary_ast_node(
                        ASTNodeType.FCNFORM, trees_to_pop + 2)

    # Variables

    # NON TERMINAL -> VB
    def read_vb(self):

        if self.is_current_token(TokenType.IDENTIFIER):  # Vb -> '<IDENTIFIER>'
            self.read_non_terminal()
        elif self.is_current_token(TokenType.L_PAREN):
            self.read_non_terminal()
            if self.is_current_token(TokenType.R_PAREN):  # Vb -> '(' ')' => '()'
                self.create_terminal_ast_node(ASTNodeType.PAREN, "")
                self.read_non_terminal()
            else:  # Vb -> '(' Vl ')'
                self.read_vl()
                if not self.is_current_token(TokenType.R_PAREN):
                    raise Exception()
                self.read_non_terminal()

    # NON TERMINAL -> VL
    def read_vl(self):
        if not self.is_current_token(TokenType.IDENTIFIER):
            raise Exception()
        else:
            self.read_non_terminal()
            trees_to_pop = 0
            # Vl -> '<IDENTIFIER>' list ',' => ','?;
            while self.is_current_token(TokenType.OPERATOR, ","):
                self.read_non_terminal()
                if not self.is_current_token(TokenType.IDENTIFIER):
                    raise Exception()
                self.read_non_terminal()
                trees_to_pop += 1
            if trees_to_pop > 0:
                # +1 for the first identifier
                self.build_nary_ast_node(ASTNodeType.COMMA, trees_to_pop + 1)


def main():
    file = open("input.txt", "r")
    input_string = file.read()

    scanner = Lexical_Analyzer.LexicalAnalyzer(input_string)
    parser = Parser(scanner)
    ast = parser.build_ast()

if __name__ == "__main__":
    main()
