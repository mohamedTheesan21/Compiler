import re

class LexicalAnalyzer:
    # Constructor
    def __init__(self, input_string):
        self.input_string = input_string
        self.current_position = 0
        # Regular expressions for token types
        self.token_regex = [
            # r used to specify raw string
            ('<IDENTIFIER>', r'[a-zA-Z_][a-zA-Z0-9_]*'),
            ('<INTEGER>', r'\d+'),
            ('<OPERATOR>', r'[+\-*<>&.@/:=~|$\#!%^_\[\]{}"‘?]+'),
            ('<STRING>', r"'((\\t)|(\\n)|(\\\\)|(\\')|[^'\\])*'"),
            ('<DELETE>', r'[\s\n\t]+'),
            ('<DELETE>', r'//.*?\n'),  # Single line comment
            ('<PUNCTION>', r'[(),;]'),
        ]
        self.tokens = self.tokenize()

    def tokenize(self):
        tokens = []
        while self.current_position < len(self.input_string):
            match_pattern = None
            for token_type, pattern in self.token_regex:
                regex = re.compile(pattern)
                match_pattern = regex.match(
                    self.input_string, self.current_position)
                # print(match_pattern)
                if match_pattern:
                    # to get the matched string
                    value = match_pattern.group(0)
                    if token_type != '<DELETE>':
                        tokens.append((token_type, value))
                    self.current_position = match_pattern.end()
                    break
            if not match_pattern:
                raise ValueError(
                    f"Invalid token at position {self.current_position}")
        return tokens

    def get_tokens(self):
        return self.tokens


def main():
    input_string = ""
    # Take input from the user
    print("Enter your input (type 'end' on a new line to finish):")
    while True:
        line = input()
        if line.strip().lower() == "end":
            break
        input_string += line + "\n"

    lexer = LexicalAnalyzer(input_string)
    tokens = lexer.get_tokens()
    for token in tokens:
        print(token)


if __name__ == "__main__":
    main()
