class ASTNode:
    def __init__(self, type=None, value=None, child=None, sibling=None, line_number=None):
        self.type = type
        self.value = value
        self.child = child
        self.sibling = sibling
        self.line_number = line_number
    
    def accept(self, node_copier):
        return node_copier.copy(self)