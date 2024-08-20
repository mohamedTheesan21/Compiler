from Parser import ASTNode
from Delta import Delta
from Beta import Beta
from Eta import Eta
from Tuple import Tuple

class NodeCopier:
    def copy(self, ast_node):
        copy = ASTNode()

        if ast_node.child is not None:
            copy.child = self.copy(ast_node.child)

        if ast_node.sibling is not None:
            copy.sibling = self.copy(ast_node.sibling)

        copy.type = ast_node.type
        copy.value = ast_node.value
        copy.line_number = ast_node.line_number

        return copy

    def copy_beta(self, beta):
        copy = Beta()

        if beta.child is not None:
            copy.child = self.copy(beta.child)

        if beta.sibling is not None:
            copy.sibling = self.copy(beta.sibling)

        copy.type = beta.type
        copy.value = beta.value
        copy.line_number = beta.line_number

        then_body_copy = [element.accept(self) for element in beta.then_body]
        copy.then_body = then_body_copy

        else_body_copy = [element.accept(self) for element in beta.else_body]
        copy.else_body = else_body_copy

        return copy

    def copy_delta(self, delta):
        copy = Delta()

        if delta.child is not None:
            copy.child = self.copy(delta.child)

        if delta.sibling is not None:
            copy.sibling = self.copy(delta.sibling)

        copy.type = delta.type
        copy.value = delta.value
        copy.index = delta.index
        copy.line_number = delta.line_number

        body_copy = [element.accept(self) for element in delta.body]
        copy.body = body_copy

        bound_vars_copy = delta.bound_vars.copy()
        copy.bound_vars = bound_vars_copy

        copy.linked_env = delta.linked_env

        return copy

    def copy_eta(self, eta):
        copy = Eta()

        if eta.child is not None:
            copy.child = self.copy(eta.child)

        if eta.sibling is not None:
            copy.sibling = self.copy(eta.sibling)

        copy.type = eta.type
        copy.value = eta.value
        copy.line_number = eta.line_number

        copy.delta = eta.delta.accept(self)

        return copy

    def copy_tuple(self, tuple):
        copy = Tuple()

        if tuple.child is not None:
            copy.child = self.copy(tuple.child)

        if tuple.sibling is not None:
            copy.sibling = self.copy(tuple.sibling)

        copy.type = tuple.type
        copy.value = tuple.value
        copy.line_number = tuple.line_number

        return copy