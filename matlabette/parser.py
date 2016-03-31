"""
Takes a list tokens and converts them to a parse tree
Uses recursive-descent parsing algorithm

Grammar
=======
expr          : array_expr
              | atom
statement     : identifier '=' array_expr
              | identifier '=' atom
              | identifier

array_expr    : '[' array_list ']'

array_list    : atom_list  ';' atom_list
              | atom_list

atom_list     : atom ',' atom_list
              | atom atom_list
              | atom

atom          : NUMERIC_LITERAL
              | '-' NUMERIC_LITERAL

identifier    : IDENTIFIER

"""

from __future__ import unicode_literals
from lexer import Token
from errors import MatlabetteSyntaxError


class Parser(object):
    """
    Takes a list tokens and converts them to a parse tree
    """
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0

    @property
    def token(self):
        return self.tokens[self.position]

    @property
    def token_type(self):
        return self.token[0]

    @property
    def token_value(self):
        return self.token[1]

    def match(self, token):
        return token == self.token_type

    def consume(self):
        self.position += 1

    def expect(self, token):
        if self.match(token):
            self.consume()
            return True
        raise MatlabetteSyntaxError(self.token_value, token)

    def parse(self):
        if self.match(Token.END_OF_LINE):
            return ParseTreeNode()
        parse_tree = self.statement()
        if parse_tree is None:
            parse_tree = ParseTreeNode(
                operator=u'=',
                left_child=ParseTreeNode(value='ans'),
                right_child=self.expression()
            )
        self.expect(Token.END_OF_LINE)
        return parse_tree

    def statement(self):
        """
        Implements the rule:
            assign_stmt   : identifier '=' array_expr
                           | identifier
        """
        if self.match(Token.VARIABLE_NAME) or self.match(Token.BUILTIN_NAME):
            token = self.token_value
            self.consume()
            if self.match(Token.END_OF_LINE):
                node = ParseTreeNode(
                    operator=u'show',
                    value=token
                )
                return node
            elif self.match(Token.ASSIGN_OPERATOR):
                self.consume()
                node = ParseTreeNode(
                    left_child=ParseTreeNode(value=token),
                    operator=u'=',
                    right_child=self.expression()
                )
                return node
            else:
                raise MatlabetteSyntaxError(self.token_value, Token.ASSIGN_OPERATOR)
        return None

    def expression(self):
        atom = self.atom()
        if atom is not None:
            return ParseTreeNode(
                value=atom,
            )
        return self.array_expression()

    def array_expression(self):
        """
        Implements the rule:
            array_expression : '[' array_list ']'
        """
        if self.match(Token.LEFT_SQUARE_BRACKET):
            self.consume()
            node = self.array_list()
            self.expect(Token.RIGHT_SQUARE_BRACKET)
        else:
            raise MatlabetteSyntaxError(
                self.token_value,
                Token.LEFT_SQUARE_BRACKET
            )
        return node

    def array_list(self):
        """
        Implements the rule:
            array_list : atom_list  ';' atom_list
                       | atom_list
        """
        node = ParseTreeNode(value=[])
        while True:
            if self.match(Token.SEMI_COLON):
                self.consume()
            atoms = self.atom_list()
            if atoms:
                if len(node.value) and len(node.value[-1]) != len(atoms):
                    raise MatlabetteSyntaxError(self.token_value, "End of list not")
                node.value.append(atoms)
            else:
                break
        return node

    def atom_list(self):
        """
        Implements the rule:
            atom_list  : atom ',' atom_list
                          | atom atom_list
                          | atom

        """
        atoms = []
        while True:
            if self.match(Token.COMMA):
                self.consume()
            atom = self.atom()
            if atom is not None:
                atoms.append(atom)
            else:
                break
        return atoms

    def atom(self):
        """
        Implements the rule:
            atom : NUMERIC_LITERAL
                 | '-' NUMERIC_LITERAL
        """
        value = None
        if self.match(Token.INTEGER_LITERAL)\
                or self.match(Token.FLOAT_LITERAL):
            value = float(self.token_value)
            self.consume()
        elif self.match(Token.SUBTRACT_OPERATOR):
            self.consume()
            value = -self.atom()
        return value


class ParseTreeNode(object):
    """
    One node of the parse tree
    This defines the parse tree recursively
    """
    def __init__(self, **kwargs):
        self.operator = kwargs.get("operator")
        self.left_child = kwargs.get("left_child")
        self.right_child = kwargs.get("right_child")
        self.value = kwargs.get("value")
