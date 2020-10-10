from spark_parser import GenericParser, GenericASTTraversal
from spark_parser import AST
from spark_parser.scanner import GenericScanner, GenericToken


class ExprScanner(GenericScanner):
    """
    基于GenericScanner实现的词法分析器
    """

    def __init__(self):
        GenericScanner.__init__(self)

    def tokenize(self, input):
        self.rv = []
        GenericScanner.tokenize(self, input)
        return self.rv

    def add_token(self, name, s):
        t = GenericToken(kind=name, attr=s)
        self.rv.append(t)

    # 遇到空格则跳过
    def t_whitespace(self, s):
        r""" \s+ """
        pass

    # 词法分析，用正则表达式匹配数字和符号，并用token标记
    def t_add_op(self, s):
        r"""[+-]"""
        self.add_token('ADD_OP', s)

    def t_mult_op(self, s):
        r"""[/*]"""
        self.add_token('MULT_OP', s)

    def t_integer(self, s):
        r"""\d+"""
        self.add_token('INTEGER', s)

    # 识别括号
    def t_lpar(self, s):
        r"""[(]"""
        self.add_token('LPAREN', s)

    def t_rpar(self, s):
        r"""[)]"""
        self.add_token('RPAREN', s)


class ExprParser(GenericParser):
    """
    基于GenericParser构造的语法分析器，p_开头的是特殊方法，分析器会读取其中的__doc__内容，并根据该内容制定解析规则
    """

    def __init__(self, start='expr'):
        GenericParser.__init__(self, start)

    def p_expr_add_term(self, args):
        ' expr ::= expr ADD_OP expr '
        op = 'add' if args[1].attr == '+' else 'subtract'
        return AST(op, [args[0], args[2]])

    def p_term_mult_factor(self, args):
        ' expr ::= expr MULT_OP expr '
        op = 'multiply' if args[1].attr == '*' else 'divide'
        return AST(op, [args[0], args[2]])

    # 从expr到整数
    def p_expr2integer(self, args):
        ' expr ::= INTEGER '
        return AST('single', [args[0]])

    # 从表达式推导到加括号的表达式
    def p_expr2paren(self, args):
        'expr ::= LPAREN expr RPAREN'
        return AST('single', [args[1]])


class Interpret(GenericASTTraversal):
    """
    基于GenericASTTraversal构造的解释执行器，能遍历抽象语法树，并得到最终的计算结果
    """

    def __init__(self, ast):
        GenericASTTraversal.__init__(self, ast)
        self.postorder(ast)
        self.attr = int(ast.attr)

    def n_single(self, node):
        node.attr = node.data[0].attr

    def n_multiply(self, node):
        node.attr = int(node[0].attr) * int(node[1].attr)

    def n_divide(self, node):
        node.attr = int(node[0].attr) / int(node[1].attr)

    def n_add(self, node):
        node.attr = int(node[0].attr) + int(node[1].attr)

    def n_subtract(self, node):
        node.attr = int(node[0].attr) - int(node[1].attr)

    def default(self, node):
        pass


def scan_expression(data):
    """
    Tokenize *filename* into integers, numbers, and operators
    """
    scanner = ExprScanner()
    return scanner.tokenize(data)


def parse_expression(tokens):
    parser = ExprParser()
    return parser.parse(tokens)


if __name__ == '__main__':
    filename = 'expr.txt'
    data = open(filename).read()
    print(data)
    tokens = scan_expression(data)
    # 打印符号列表
    print(tokens)
    # 打印抽象语法树
    tree = parse_expression(tokens)
    print(tree)
    i = Interpret(tree)
    print("Final value is: %d" % i.attr)
