import re

# Define an enumeration for different token types
class TokenType:
    RESERVED = "RESERVED"
    OPERATOR = "OPERATOR"
    IDENTIFIER = "IDENTIFIER"
    INTEGER = "INTEGER"
    STRING = "STRING"
    L_PAREN = "L_PAREN"
    R_PAREN = "R_PAREN"
    DELETE = "DELETE"
    COMMA = "COMMA"

# Class representing a token with type, value, and line number
class Token:
    def __init__(self, type, value, line_number):
        self.type = type
        self.value = value
        self.line_number = line_number

# Lexical analyzer class to tokenize the input string
class LexicalAnalyzer:
    def __init__(self, input_string):
        self.input_string = input_string  # The input string to be tokenized
        self.current_position = 0  # Current position in the input string
        self.line_number = 1  # Current line number (for error reporting)
        # List of token types and their corresponding regex patterns
        self.token_regex = [
            (TokenType.DELETE, r'//.*?\n'),  # Comments
            (TokenType.RESERVED, r'(let|in|lambda|within|where|tau|aug|or|&|not|gr|ge|ls|le|eq|ne|true|false|nil|rec|fn|dummy)'),  # Reserved keywords
            (TokenType.OPERATOR, r'[+\-*<>&.@/:=~|$\#!%^_,\[\]{}"‘?]+'),  # Operators and punctuation
            (TokenType.IDENTIFIER, r'[a-zA-Z_][a-zA-Z0-9_]*'),  # Identifiers (variable names)
            (TokenType.INTEGER, r'\d+'),  # Integer literals
            (TokenType.STRING, r"'((\\t)|(\\n)|(\\\\)|(\\')|[^'\\])*'"),  # String literals
            (TokenType.L_PAREN, r'\('),  # Left parenthesis
            (TokenType.R_PAREN, r'\)'),  # Right parenthesis
            (TokenType.DELETE, r'[\s\n\t]+'),
        ]
        # Tokenize the input string
        self.tokens = self.tokenize()

    def tokenize(self):
        tokens = []
        # Loop until the end of the input string is reached
        while self.current_position < len(self.input_string):
            match_pattern = None
            # Try to match each token type in the regex list
            for token_type, pattern in self.token_regex:
                regex = re.compile(pattern)
                match_pattern = regex.match(self.input_string, self.current_position)
                if match_pattern:
                    value = match_pattern.group(0)
                    # Only add the token if it's not a DELETE type (whitespace or comment)
                    if token_type != TokenType.DELETE:
                        tokens.append(Token(token_type, value, self.line_number))
                    # If it's a DELETE type and contains new lines, update the line number
                    if token_type == TokenType.DELETE and '\n' in value:
                        self.line_number += value.count('\n')
                    # Update the current position to the end of the matched pattern
                    self.current_position = match_pattern.end()
                    break
            # If no pattern matches, raise an error indicating an invalid token
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
