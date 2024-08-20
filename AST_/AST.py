from Beta import Beta
from Delta import Delta
from collections import deque
from AST_.ASTNode import ASTNode
from AST_.ASTNodeType import ASTNodeType

class AST:
    def __init__(self, root):
        self.root = root
        self.pending_delta_body_queue = deque()
        self.standardized = False
        self.current_delta = None
        self.root_delta = None
        self.delta_index = 0

    def standardize(self):
        self._standardize(self.root)
        self.standardized = True

    def _standardize(self, node):
        if node.child is not None:
            child_node = node.child
            while child_node is not None:
                self._standardize(child_node)
                child_node = child_node.sibling

        if node.type == ASTNodeType.LET:
            equal_node = node.child
            if equal_node.type != ASTNodeType.EQUAL:
                raise Exception()
            e = equal_node.child.sibling
            equal_node.child.sibling = equal_node.sibling
            equal_node.sibling = e
            equal_node.type = ASTNodeType.LAMBDA
            node.type = ASTNodeType.GAMMA
        elif node.type == ASTNodeType.WHERE:
            equal_node = node.child.sibling
            node.child.sibling = None
            equal_node.sibling = node.child
            node.child = equal_node
            node.type = ASTNodeType.LET
            self._standardize(node)
        elif node.type == ASTNodeType.FCNFORM:
            child_sibling = node.child.sibling
            node.child.sibling = self._construct_lambda_chain(child_sibling)
            node.type = ASTNodeType.EQUAL
        elif node.type == ASTNodeType.AT:
            e1 = node.child
            n = e1.sibling
            e2 = n.sibling
            gamma_node = ASTNode()
            gamma_node.type = ASTNodeType.GAMMA
            gamma_node.child = n
            n.sibling = e1
            e1.sibling = None
            gamma_node.sibling = e2
            node.child = gamma_node
            node.type = ASTNodeType.GAMMA
        elif node.type == ASTNodeType.WITHIN:
            if node.child.type != ASTNodeType.EQUAL or node.child.sibling.type != ASTNodeType.EQUAL:
                raise Exception()
            x1 = node.child.child
            e1 = x1.sibling
            x2 = node.child.sibling.child
            e2 = x2.sibling
            lambda_node = ASTNode()
            lambda_node.type = ASTNodeType.LAMBDA
            x1.sibling = e2
            lambda_node.child = x1
            lambda_node.sibling = e1
            gamma_node = ASTNode()
            gamma_node.type = ASTNodeType.GAMMA
            gamma_node.child = lambda_node
            x2.sibling = gamma_node
            node.child = x2
            node.type = ASTNodeType.EQUAL
        elif node.type == ASTNodeType.SIMULTDEF:
            comma_node = ASTNode()
            comma_node.type = ASTNodeType.COMMA
            tau_node = ASTNode()
            tau_node.type = ASTNodeType.TAU
            child_node = node.child
            while child_node is not None:
                self._populate_comma_and_tau_node(
                    child_node, comma_node, tau_node)
                child_node = child_node.sibling
            comma_node.sibling = tau_node
            node.child = comma_node
            node.type = ASTNodeType.EQUAL
        elif node.type == ASTNodeType.REC:
            child_node = node.child
            if child_node.type != ASTNodeType.EQUAL:
                raise Exception()
            x = child_node.child
            lambda_node = ASTNode()
            lambda_node.type = ASTNodeType.LAMBDA
            lambda_node.child = x
            y_star_node = ASTNode()
            y_star_node.type = ASTNodeType.YSTAR
            y_star_node.sibling = lambda_node
            gamma_node = ASTNode()
            gamma_node.type = ASTNodeType.GAMMA
            gamma_node.child = y_star_node
            x_with_sibling_gamma = ASTNode()
            x_with_sibling_gamma.child = x.child
            x_with_sibling_gamma.sibling = gamma_node
            x_with_sibling_gamma.type = x.type
            x_with_sibling_gamma.value = x.value
            node.child = x_with_sibling_gamma
            node.type = ASTNodeType.EQUAL
        elif node.type == ASTNodeType.LAMBDA:
            child_sibling = node.child.sibling
            node.child.sibling = self._construct_lambda_chain(child_sibling)

    def _populate_comma_and_tau_node(self, equal_node, comma_node, tau_node):
        if equal_node.type != ASTNodeType.EQUAL:
            raise Exception()
        x = equal_node.child
        e = x.sibling
        comma_node.child = x
        tau_node.child = e

    def _construct_lambda_chain(self, node):
        if node.sibling is None:
            return node
        lambda_node = ASTNode()
        lambda_node.type = ASTNodeType.LAMBDA
        lambda_node.child = node
        next_node = node.sibling
        while next_node.sibling is not None:
            temp_node = ASTNode()
            temp_node.type = ASTNodeType.LAMBDA
            temp_node.child = next_node
            lambda_node.sibling = temp_node
            lambda_node = temp_node
            next_node = next_node.sibling
        lambda_node.sibling = next_node
        return lambda_node

    def create_deltas(self):

        self.delta_index = 0
        self.current_delta = self._create_delta(self.root)
        self._process_pending_delta_stack()
        return self.root_delta

    def _create_delta(self, start_body_node):
        pending_delta = self.PendingDeltaBody()
        pending_delta.start_node = start_body_node
        pending_delta.body = []
        self.pending_delta_body_queue.append(pending_delta)
        d = Delta()
        d.body = pending_delta.body
        d.index = self.delta_index
        self.current_delta = d
        if start_body_node == self.root:
            self.root_delta = self.current_delta
        return d

    def _process_pending_delta_stack(self):

        while self.pending_delta_body_queue:
            pending_delta_body = self.pending_delta_body_queue.popleft()
            body = pending_delta_body.body
            start_node = pending_delta_body.start_node
            self._build_delta_body(start_node, body)

    def _build_delta_body(self, node, body):
        if node.type == ASTNodeType.LAMBDA:
            d = self._create_delta(node.child.sibling)
            if node.child.type == ASTNodeType.COMMA:
                comma_node = node.child
                child_node = comma_node.child
                while child_node is not None:
                    d.bound_vars.append(child_node.value)
                    child_node = child_node.sibling
            else:
                d.bound_vars.append(node.child.value)
            body.append(d)
            return
        elif node.type == ASTNodeType.CONDITIONAL:

            condition_node = node.child
            then_node = condition_node.sibling
            else_node = then_node.sibling

            beta_node = Beta()
            self._build_delta_body(then_node, beta_node.then_body)
            self._build_delta_body(else_node, beta_node.else_body)
            body.append(beta_node)
            self._build_delta_body(condition_node, body)
            return
        else:
            body.append(node)

            child_node = node.child
            while child_node is not None:
                self._build_delta_body(child_node, body)
                child_node = child_node.sibling

    class PendingDeltaBody:
        def __init__(self):
            self.body = []
            self.start_node = None

    def is_standardized(self):
        return self.standardized
