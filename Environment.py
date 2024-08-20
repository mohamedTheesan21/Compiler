from NodeCopier import NodeCopier

class Environment:
    def __init__(self):
        self.parent = None
        self.name_value_map = {}

    def get_parent(self):
        return self.parent

    def set_parent(self, parent):
        self.parent = parent

    def lookup(self, key):
        return_value = self.name_value_map.get(key)

        if return_value is not None:
            return return_value.accept(NodeCopier())

        if self.parent is not None:
            return self.parent.lookup(key)
        else:
            return None

    def add_mapping(self, key, value):
        self.name_value_map[key] = value
