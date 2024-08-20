from AST_.ASTNode import ASTNode
from AST_.ASTNodeType import ASTNodeType

class Eta(ASTNode):
    def __init__(self):
        super().__init__()
        self.type = ASTNodeType.ETA
        self.delta = None

    def accept(self, node_copier):
        return node_copier.copy_eta(self)

    def get_value(self):
        return "[eta closure: " + self.delta.get_bound_vars()[0] + ": " + str(self.delta.get_index()) + "]"

    def get_delta(self):
        return self.delta

    def set_delta(self, delta):
        self.delta = delta
