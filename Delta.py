from AST_.ASTNode import ASTNode
from AST_.ASTNodeType import ASTNodeType

class Delta(ASTNode):
    def __init__(self):
        super().__init__()
        self.type = ASTNodeType.DELTA
        self.bound_vars = []
        self.linked_env = None
        self.body = []
        self.index = 0

    def accept(self, node_copier):
        return node_copier.copy_delta(self)

    def get_value(self):
        return f"[lambda closure: {self.bound_vars[0]}: {self.index}]"

    def get_bound_vars(self):
        return self.bound_vars

    def add_bound_var(self, bound_var):
        self.bound_vars.append(bound_var)

    def set_bound_vars(self, bound_vars):
        self.bound_vars = bound_vars

    def get_body(self):
        return self.body

    def set_body(self, body):
        self.body = body

    def get_index(self):
        return self.index

    def set_index(self, index):
        self.index = index

    def get_linked_env(self):
        return self.linked_env

    def set_linked_env(self, linked_env):
        self.linked_env = linked_env
