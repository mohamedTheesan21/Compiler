from AST_.ASTNode import ASTNode
from AST_.ASTNodeType import ASTNodeType

class Beta(ASTNode):
    def __init__(self):
        super().__init__()
        self.type = ASTNodeType.BETA
        self.then_body = []
        self.else_body = []

    def get_then_body(self):
        return self.then_body

    def get_else_body(self):
        return self.else_body

    def set_then_body(self, then_body):
        self.then_body = then_body

    def set_else_body(self, else_body):
        self.else_body = else_body

    def accept(self, node_copier):
        return node_copier.copy_beta(self)
