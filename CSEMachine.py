from AST_.AST import AST
from AST_.ASTNode import ASTNode
from AST_.ASTNodeType import ASTNodeType

from Environment import Environment
from Delta import Delta
from Eta import Eta
from Tuple import Tuple


class CSEMachine:
    def __init__(self, ast):
        if not ast.is_standardized():
            raise RuntimeError("AST has NOT been standardized!")

        self.root_delta = ast.create_deltas()
        self.root_delta.set_linked_env(Environment())
        self.value_stack = []

    def evaluate_program(self):
        self.process_control_stack(self.root_delta, self.root_delta.get_linked_env())

    def process_control_stack(self, current_delta, current_env):
        control_stack = []
        control_stack.extend(current_delta.get_body())
        # print(control_stack)
        while control_stack:
            self.process_current_node(current_env, control_stack)

    def process_current_node(self, current_env, current_control_stack):
        node = current_control_stack.pop()
        # print("Node: "+ node.type)
        if self.apply_binary_operation(node):
            return
        elif self.apply_unary_operation(node):
            return
        else:
            node_type = node.type
            if node_type == ASTNodeType.IDENTIFIER:
                self.handle_identifiers(node, current_env)
            elif node_type in (ASTNodeType.NIL, ASTNodeType.TAU):
                self.create_tuple(node)
            elif node_type == ASTNodeType.BETA:
                self.handle_beta(node, current_control_stack)
            elif node_type == ASTNodeType.GAMMA:
                self.apply_gamma( node,
                                  current_control_stack)
            elif node_type == ASTNodeType.DELTA:
                node.set_linked_env(current_env)
                self.value_stack.append(node)
            else:
                self.value_stack.append(node)

    def apply_binary_operation(self, rator):
        node_type = rator.type
        if node_type in [ASTNodeType.PLUS, ASTNodeType.MINUS, ASTNodeType.MULT, ASTNodeType.DIV, ASTNodeType.EXP,
                         ASTNodeType.LS, ASTNodeType.LE, ASTNodeType.GR, ASTNodeType.GE]:
            self.binary_arithmetic_op(node_type)
            return True
        elif node_type in [ASTNodeType.EQ, ASTNodeType.NE]:
            self.binary_logical_eq_ne_op(node_type)
            return True
        elif node_type in [ASTNodeType.OR, ASTNodeType.AND]:
            self.binary_logical_or_and_op(node_type)
            return True
        elif node_type == ASTNodeType.AUG:
            self.aug_tuples()
            return True
        else:
            return False

    def binary_arithmetic_op(self, node_type):
        rand1 = self.value_stack.pop()
        rand2 = self.value_stack.pop()
        # print(rand1.value, rand2.value)
        if rand1.type != ASTNodeType.INTEGER or rand2.type != ASTNodeType.INTEGER:
            raise Exception()

        result = ASTNode()
        result.type = (ASTNodeType.INTEGER)

        if node_type == ASTNodeType.PLUS:
            result.value = (str(int(rand1.value) + int(rand2.value)))
            self.value_stack.append(result)
        elif node_type == ASTNodeType.MINUS:
            result.value = (str(int(rand1.value) - int(rand2.value)))
            self.value_stack.append(result)
        elif node_type == ASTNodeType.MULT:
            # print(rand2.value)
            result.value = (str(int(rand1.value) * int(rand2.value)))
            self.value_stack.append(result)
        elif node_type == ASTNodeType.DIV:
            result.value = (str(int(rand1.value) / int(rand2.value)))
            self.value_stack.append(result)
        elif node_type == ASTNodeType.EXP:
            result.value = (str(int(rand1.value) ** int(rand2.value)))
            self.value_stack.append(result)
        elif node_type in [ASTNodeType.LS, ASTNodeType.LE, ASTNodeType.GR, ASTNodeType.GE]:
            if node_type == ASTNodeType.LS:
                if int(rand1.value) < int(rand2.value):
                    self.push_true_node()
                else:
                    self.push_false_node()
            elif node_type == ASTNodeType.LE:
                if int(rand1.value) <= int(rand2.value):
                    self.push_true_node()
                else:
                    self.push_false_node()
            elif node_type == ASTNodeType.GR:
                if int(rand1.value) > int(rand2.value):
                    self.push_true_node()
                else:
                    self.push_false_node()
            elif node_type == ASTNodeType.GE:
                if int(rand1.value) >= int(rand2.value):
                    self.push_true_node()
                else:
                    self.push_false_node()
        else:
            raise Exception()

    def binary_logical_eq_ne_op(self, node_type):
        rand1 = self.value_stack.pop()
        rand2 = self.value_stack.pop()

        if rand1.type == ASTNodeType.TRUE or rand1.type == ASTNodeType.FALSE:
            if rand2.type != ASTNodeType.TRUE and rand2.type != ASTNodeType.FALSE:
                raise Exception()
            self.compare_truth_values(rand1, rand2, node_type)
            return

        if rand1.type != rand2.type:
            raise Exception()

        if rand1.type == ASTNodeType.STRING:
            self.compare_strings(rand1, rand2, node_type)
        elif rand1.type == ASTNodeType.INTEGER:
            self.compare_integers(rand1, rand2, node_type)
        else:
            raise Exception()

    def compare_truth_values(self, rand1, rand2, node_type):
        if rand1.type == rand2.type:
            if node_type == ASTNodeType.EQ:
                self.push_true_node()
            else:
                self.push_false_node()
        else:
            if node_type == ASTNodeType.EQ:
                self.push_false_node()
            else:
                self.push_true_node()

    def compare_strings(self, rand1, rand2, node_type):
        if rand1.value == rand2.value:
            if node_type == ASTNodeType.EQ:
                self.push_true_node()
            else:
                self.push_false_node()
        else:
            if node_type == ASTNodeType.EQ:
                self.push_false_node()
            else:
                self.push_true_node()

    def compare_integers(self, rand1, rand2, node_type):
        if int(rand1.value) == int(rand2.value):
            if node_type == ASTNodeType.EQ:
                self.push_true_node()
            else:
                self.push_false_node()
        else:
            if node_type == ASTNodeType.EQ:
                self.push_false_node()
            else:
                self.push_true_node()

    def binary_logical_or_and_op(self, node_type):
        rand1 = self.value_stack.pop()
        rand2 = self.value_stack.pop()

        if (rand1.type == ASTNodeType.TRUE or rand1.type == ASTNodeType.FALSE) and \
           (rand2.type == ASTNodeType.TRUE or rand2.type == ASTNodeType.FALSE):
            self.or_and_truth_values(rand1, rand2, node_type)
        else:
            raise Exception()

    def or_and_truth_values(self, rand1, rand2, node_type):
        if node_type == ASTNodeType.OR:
            if rand1.type == ASTNodeType.TRUE or rand2.type == ASTNodeType.TRUE:
                self.push_true_node()
            else:
                self.push_false_node()
        else:
            if rand1.type == ASTNodeType.TRUE and rand2.type == ASTNodeType.TRUE:
                self.push_true_node()
            else:
                self.push_false_node()

    def aug_tuples(self):
        rand1 = self.value_stack.pop()
        rand2 = self.value_stack.pop()
        # print()
        # print("rand1", rand1.value)
        # print("rand2", rand2.value)
        # print()

        if rand1.type != ASTNodeType.TUPLE:
            raise Exception()

        child_node = rand1.child
        if child_node is None:
            rand1.child = (rand2)
        else:
            while child_node.sibling is not None:
                child_node = child_node.sibling
            child_node.sibling = (rand2)
        rand2.sibling = (None)

        self.value_stack.append(rand1)

    def apply_unary_operation(self, rator):
        node_type = rator.type
        if node_type == ASTNodeType.NOT:
            self.not_()
            return True
        elif node_type == ASTNodeType.NEG:
            self.neg()
            return True
        else:
            return False

    def not_(self):
        rand = self.value_stack.pop()
        if rand.type != ASTNodeType.TRUE and rand.type != ASTNodeType.FALSE:
            raise Exception()

        if rand.type == ASTNodeType.TRUE:
            self.push_false_node()
        else:
            self.push_true_node()

    def neg(self):
        rand = self.value_stack.pop()
        if rand.type != ASTNodeType.INTEGER:
            raise Exception()

        result = ASTNode()
        result.type = (ASTNodeType.INTEGER)
        result.value = (str(-1 * int(rand.value)))
        self.value_stack.append(result)
        # print("value stack", self.value_stack)

    def apply_gamma(self, node, current_control_stack):
        # print(self.value_stack)
        rator = self.value_stack.pop()
        rand = self.value_stack.pop()
        if rator.type == ASTNodeType.DELTA:
            next_delta = rator

            new_env = Environment()
            new_env.set_parent(next_delta.get_linked_env())

            if len(next_delta.get_bound_vars()) == 1:
                # print("mapping", next_delta.get_bound_vars()[0])
                new_env.add_mapping(next_delta.get_bound_vars()[0], rand)
            else:
                if rand.type != ASTNodeType.TUPLE:
                    raise Exception()

                for i in range(len(next_delta.get_bound_vars())):
                    new_env.add_mapping(next_delta.get_bound_vars()[
                                        i], self.get_nth_tuple_child(rand, i + 1))

            self.process_control_stack(next_delta, new_env)
            return
        elif rator.type == ASTNodeType.YSTAR:
            if rand.type != ASTNodeType.DELTA:
                raise Exception()

            eta_node = Eta()
            eta_node.set_delta(rand)
            self.value_stack.append(eta_node)
            return
        elif rator.type == ASTNodeType.ETA:
            self.value_stack.append(rand)
            self.value_stack.append(rator)
            self.value_stack.append(rator.get_delta())
            current_control_stack.append(node)
            current_control_stack.append(node)
            return
        elif rator.type == ASTNodeType.TUPLE:
            self.tuple_selection(rator, rand)
            return
        elif self.evaluate_reserved_identifiers(rator, rand, current_control_stack):
            return
        else:
            raise Exception()

    def evaluate_reserved_identifiers(self, rator, rand, current_control_stack):
        value = rator.value
        if value == "Isinteger":
            self.check_type_and_push_true_or_false(rand, ASTNodeType.INTEGER)
            return True
        elif value == "Isstring":
            self.check_type_and_push_true_or_false(rand, ASTNodeType.STRING)
            return True
        elif value == "Isdummy":
            self.check_type_and_push_true_or_false(rand, ASTNodeType.DUMMY)
            return True
        elif value == "Isfunction":
            self.check_type_and_push_true_or_false(rand, ASTNodeType.DELTA)
            return True
        elif value == "Istuple":
            self.check_type_and_push_true_or_false(rand, ASTNodeType.TUPLE)
            return True
        elif value == "Istruthvalue":
            if rand.type == ASTNodeType.TRUE or rand.type == ASTNodeType.FALSE:
                self.push_true_node()
            else:
                self.push_false_node()
            return True
        elif value == "Stem":
            self.stem(rand)
            return True
        elif value == "Stern":
            self.stern(rand)
            return True
        elif value == "Conc" or value == "conc":  
            self.conc(rand, current_control_stack)
            return True
        elif value == "Print" or value == "print":
            self.print_node_value(rand)
            self.push_dummy_node()
            return True
        elif value == "ItoS":
            self.itos(rand)
            return True
        elif value == "Order":
            self.order(rand)
            return True
        elif value == "Null":
            self.is_null_tuple(rand)
            return True
        else:
            return False

    def check_type_and_push_true_or_false(self, rand, type):
        if rand.type == type:
            self.push_true_node()
        else:
            self.push_false_node()

    def push_true_node(self):
        true_node = ASTNode()
        true_node.type = (ASTNodeType.TRUE)
        true_node.value = ("true")
        self.value_stack.append(true_node)

    def push_false_node(self):
        false_node = ASTNode()
        false_node.type = (ASTNodeType.FALSE)
        false_node.value = ("false")
        self.value_stack.append(false_node)

    def push_dummy_node(self):
        dummy_node = ASTNode()
        dummy_node.type = (ASTNodeType.DUMMY)
        self.value_stack.append(dummy_node)

    def stem(self, rand):
        if rand.type != ASTNodeType.STRING:
            raise Exception()

        if rand.value == "":
            rand.value = ("")
        else:
            rand.value = (rand.value[0])

        self.value_stack.append(rand)

    def stern(self, rand):
        if rand.type != ASTNodeType.STRING:
            raise Exception()

        if rand.value == "" or len(rand.value) == 1:
            rand.value = ("")
        else:
            rand.value = (rand.value[1:])

        self.value_stack.append(rand)

    def conc(self, rand1, current_control_stack):
        current_control_stack.pop()
        rand2 = self.value_stack.pop()
        if rand1.type != ASTNodeType.STRING or rand2.type != ASTNodeType.STRING:
            raise Exception()

        result = ASTNode()
        result.type = (ASTNodeType.STRING)
        result.value = (rand1.value + rand2.value)

        self.value_stack.append(result)

    def itos(self, rand):
        if rand.type != ASTNodeType.INTEGER:
            raise Exception()

        rand.type = (ASTNodeType.STRING)
        self.value_stack.append(rand)

    def order(self, rand):
        if rand.type != ASTNodeType.TUPLE:
            raise Exception()

        result = ASTNode()
        result.type = (ASTNodeType.INTEGER)
        result.value = (str(self.get_num_children(rand)))

        self.value_stack.append(result)

    def is_null_tuple(self, rand):
        if rand.type != ASTNodeType.TUPLE:
            raise Exception()

        if self.get_num_children(rand) == 0:
            self.push_true_node()
        else:
            self.push_false_node()

    def tuple_selection(self, rator, rand):
        if rand.type != ASTNodeType.INTEGER:
            raise Exception()

        result = self.get_nth_tuple_child(rator, int(rand.value))
        if result is None:
            raise Exception()
        self.value_stack.append(result)

    def get_nth_tuple_child(self, tuple_node, n):
        child_node = tuple_node.child
        for i in range(n - 1): 
            if child_node is None:
                break
            child_node = child_node.sibling
        return child_node

    def handle_identifiers(self, node, current_env):
        value = node.value
        if current_env.lookup(value) is not None:
            self.value_stack.append(current_env.lookup(value))
        elif value in ["Isinteger", "Isstring", "Istuple", "Isdummy", "Istruthvalue",
                        "Isfunction", "ItoS", "Order", "Conc", "conc", "Stern", "Stem",
                        "Null", "Print", "print", "neg"]:
            self.value_stack.append(node)
        else:
            raise Exception()

    def create_tuple(self, node):
        num_children = self.get_num_children(node)
        tuple_node = Tuple()

        if num_children == 0:
            self.value_stack.append(tuple_node)
            return

        child_node = None
        temp_node = None
        for i in range(num_children):
            if child_node is None:
                child_node = self.value_stack.pop()
            elif temp_node is None:
                temp_node = self.value_stack.pop()
                child_node.sibling = (temp_node)
            else:
                temp_node.sibling = (self.value_stack.pop())
                temp_node = temp_node.sibling

        if temp_node:
            temp_node.sibling = (None)
        tuple_node.child = (child_node)
        self.value_stack.append(tuple_node)

    def handle_beta(self, node, current_control_stack):
        condition_result_node = self.value_stack.pop()

        if condition_result_node.type != ASTNodeType.TRUE and condition_result_node.type != ASTNodeType.FALSE:
            raise Exception()

        if condition_result_node.type == ASTNodeType.TRUE:
            current_control_stack.extend(node.get_then_body())
        else:
            current_control_stack.extend(node.get_else_body())

    def get_num_children(self,node):
        num_children = 0
        child_node = node.child
        while child_node is not None:
            num_children += 1
            child_node = child_node.sibling
        return num_children

    def print_node_value(self, rand):
        if rand.type == ASTNodeType.TUPLE:
            evaluation_result = rand.get_value()
        else:
            evaluation_result = rand.value
        evaluation_result = evaluation_result.replace("\\t", "\t")
        evaluation_result = evaluation_result.replace("\\n", "\n")
        print("Output of the above program is:")
        print(evaluation_result.strip("'"), end='')