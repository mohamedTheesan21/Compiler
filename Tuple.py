from Parser import ASTNode, ASTNodeType

class Tuple(ASTNode):
    def __init__(self):
        super().__init__()
        self.type = ASTNodeType.TUPLE

    def get_value(self):
        child_node = self.child
        if child_node is None:
            return "nil"

        print_value = "("
        while child_node.sibling is not None:
            print_value += child_node.value + ", "
            child_node = child_node.sibling
        print_value += child_node.value + ")"
        return print_value

    def accept(self, node_copier):
        return node_copier.copy_tuple(self)
