import re

class TokenType:
    RESERVED = "RESERVED"
    OPERATOR = "OPERATOR"
    IDENTIFIER = "IDENTIFIER"
    INTEGER = "INTEGER"
    STRING = "STRING"
    L_PAREN = "L_PAREN"
    R_PAREN = "R_PAREN"
    DELETE = "DELETE"

class Token:
    def __init__(self, type, value, line_number):
        self.type = type
        self.value = value
        self.line_number = line_number

class LexicalAnalyzer:
    def __init__(self, input_string):
        self.input_string = input_string
        self.current_position = 0
        self.line_number = 1
        self.token_regex = [
            (TokenType.DELETE, r'//.*?\n'),
            (TokenType.RESERVED, r'(let|in|lambda|within|where|tau|aug|or|&|not|gr|ge|ls|le|eq|ne|true|false|nil|rec|fn|dummy)'),
            (TokenType.OPERATOR, r'[+\-*<>&.@/:=~|$\#!%^_,\[\]{}"‘?]+'),
            (TokenType.IDENTIFIER, r'[a-zA-Z_][a-zA-Z0-9_]*'),
            (TokenType.INTEGER, r'\d+'),
            (TokenType.STRING, r"'((\\t)|(\\n)|(\\\\)|(\\')|[^'\\])*'"),
            (TokenType.L_PAREN, r'\('),
            (TokenType.R_PAREN, r'\)'),
            (TokenType.DELETE, r'[\s\n\t]+'),
        ]
        self.tokens = self.tokenize()

    def tokenize(self):
        tokens = []
        while self.current_position < len(self.input_string):
            match_pattern = None
            for token_type, pattern in self.token_regex:
                regex = re.compile(pattern)
                match_pattern = regex.match(self.input_string, self.current_position)
                if match_pattern:
                    value = match_pattern.group(0)
                    if token_type != TokenType.DELETE:
                        tokens.append(Token(token_type, value, self.line_number))
                    if token_type == TokenType.DELETE and '\n' in value:
                        self.line_number += value.count('\n')
                    self.current_position = match_pattern.end()
                    break
            if not match_pattern:
                raise ValueError(f"Invalid token at position {self.current_position}")
        return tokens

# def main():
#     file = open("input.txt", "r")
#     input_string = file.read()

#     lexer = LexicalAnalyzer(input_string)
#     for token in lexer.tokens:
#         print(token.type, token.value, token.line_number)


# if __name__ == "__main__":
#     main()
