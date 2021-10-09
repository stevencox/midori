import sys
from typing import List
from dataclasses import dataclass

from lark import Lark, ast_utils, Transformer, v_args
from lark.tree import Meta

this_module = sys.modules[__name__]

#
#   Define AST
#
class _Ast(ast_utils.Ast):
    # This will be skipped by create_transformer(), because it starts with an underscore
    pass

class _Statement(_Ast):
    # This will be skipped by create_transformer(), because it starts with an underscore
    pass

@dataclass
class Value(_Ast, ast_utils.WithMeta):
    "Uses WithMeta to include line-number metadata in the meta attribute"
    meta: Meta
    value: object

@dataclass
class Name(_Ast):
    name: str

@dataclass
class Program(_Ast, ast_utils.AsList):
    # Corresponds to code_block in the grammar
    statements: List[_Statement]

@dataclass
class If(_Statement):
    cond: Value
    then: Program

@dataclass
class SetVar(_Statement):
    # Corresponds to set_var in the grammar
    name: str
    value: Value

@dataclass
class Print(_Statement):
    value: Value


class ToAst(Transformer):
    # Define extra transformation functions, for rules that don't correspond to an AST class.

    def STRING(self, s):
        # Remove quotation marks
        return s[1:-1]

    def DEC_NUMBER(self, n):
        return int(n)

    @v_args(inline=True)
    def start(self, x):
        return x

#
#   Define Parser
#

parser = Lark("""
    start: program

    program: statement+

    ?statement: controller | node | switch | link | start 
              | ping | stop

    controller: value
    node: "node" NAME "ip" value "image" value
    switch: "switch" name+
    link: "link" NAME value+
    start: "start"
    ping: value+
    stop: "stop"

    value: name | STRING | DEC_NUMBER
    name: NAME
    ip_addr: NAME
    image: NAME

    %import python (NAME, STRING, DEC_NUMBER)
    %import common.WS
    %ignore WS
    """,
    parser="lalr",
)

transformer = ast_utils.create_transformer(this_module, ToAst())

class Parser:
    def parse(self, text: str) -> Program:
        tree = parser.parse(text)
        return transformer.transform(tree)


#
#   Test
#

if __name__ == '__main__':
    ast = parse("""
        a = 1;
        if a {
            print "a is 1";
            a = 2;
        }
    """)
    for statement in ast.statements:
        print (statement)
