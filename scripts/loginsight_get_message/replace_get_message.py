# -*- coding: utf-8 -*-
'''
Created on 2017年6月9日

@author: ghou
'''

from abc import ABCMeta, abstractmethod
import codecs
import re
import sys
from  xml.dom import  minidom
from xml.sax.saxutils import *


class Parser(object):
    '''
    super class for resx_old ,property and vmsg l10nparser
    '''
    encoding = 'utf-8'
    need_escaped = False
    STRING = 0
    LAYOUTINFO = 1
    OTHER = 2

    __metaclass__ = ABCMeta
    def __init__(self, file_path, sep_char_re, ver_char_re, value_splitor):

        self._file_path = file_path
        self._sep_char_re = sep_char_re
        self._ver_char_re = ver_char_re
        self._value_splitor = value_splitor
        self._string_item_list = []


    @classmethod
    def store(cls, targ_string_items, targ_file_path, entities = {}):
        out = codecs.open(targ_file_path, 'w', cls.encoding)
        if out.mode[0] != 'w':
            raise ValueError, 'Steam should be opened in write mode!'

        try:
            for item in targ_string_items:
                value = item.value
                if cls.need_escaped and value.strip():
                    value = escape(value, entities)
                out.write(''.join((item.block, value)))
            out.close()
        except IOError, e:
            raise

    @classmethod
    def compose(cls, targ_string_items, entities = {}):
        strList = []
        for item in targ_string_items:
            value = item.value
            if cls.need_escaped and value.strip():
                value = escape(value, entities)
            strList.append(''.join((item.block, value)))
        block = ''.join(strList)
        return block

    def load(self):
        """ Load properties_old from an open file stream """
        stream = self._open_resource_file()
        lines = stream.readlines()
        self._parse(lines)

    @abstractmethod
    def _parse(self, lines):
        return

    def _generate_item(self, comment, key, value, block, hashcode = None, type=STRING, **kwargs):
        """
        generate the object contains key, value, comment,block
        kwargs:Extended parameter for special parser type, as 'keytrunk for rc parser'
        """
        stringItemsDic = {}
        stringItemsDic.update(comment = comment,
                              key = key,
                              value = value,
                              block = block,
                              hashcode = hashcode,
                              type = type)
        stringItemsDic.update(kwargs)
        sitem = StringItems(stringItemsDic)
        self._string_item_list.append(sitem)
        return sitem

    def _open_resource_file(self):
        try:
            file_stream = codecs.open(self._file_path, 'r', self.encoding)
        except IOError:
            print "No such file or directory!"
            sys.exit(0)
        else:
            return file_stream

    def _add_prev_next_hashcode(self):
        for i in xrange(len(self._string_item_list)):
            if i > 0:
                prevhashcode = self._string_item_list[i - 1].hashcode
            else:
                prevhashcode = 0
            if i < len(self._string_item_list) - 1:
                nexthashcode = self._string_item_list[i + 1].hashcode
            else:
                nexthashcode = 0
            self._string_item_list[i].prevhashcode = prevhashcode
            self._string_item_list[i].nexthashcode = nexthashcode


def c_mul(a, b):
    return eval(hex((long(a) * b) & 0xFFFFFFFFL)[:-1])

       
def getHashCode(s):
    if not s:
        return 0 # empty
    value = ord(s[0]) << 7
    for char in s:
        value = c_mul(1000003, value) ^ ord(char)
    value = value ^ len(s)
    if value == -1:
        value = -2
    return value


class StringItems(object):
    __slots__ = ['key',
                 'keytrunk',
                 'value',
                 'comment',
                 'block',
                 'globalid',
                 'hashcode',
                 'type',
                 'prevhashcode',
                 'nexthashcode',
                 'filepath',
                 'fileid']
    
    def __init__(self, *args, **kwargs):
        """
        Initialize attributes with parameters and set default value, if None. 
        """
        for dic in args:
            for key in dic:
                setattr(self, key, dic[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])

        for s in self.__slots__:
            if getattr(self, s, None) is None:
                setattr(self, s, "")

    def __unicode__(self):
        return u'%s********%s' % (self.key, self.value)

    def to_dic(self):
        return {s: getattr(self, s, None) for s in self.__slots__}


class PropertiesParser(Parser):
    encoding='utf-8'
    def __init__(self,file_path):
        sep_char_re=re.compile(r'(?<!\\)(\s*\=)|(?<!\\)(\s*\:)')
        ver_char_re=re.compile(r'(\s*\=)|(\s*\:)')
        value_splitor = re.compile(r'\r\n|\r|\n')
        self.__whitespace_re = re.compile(r'(?<![\\\=\:])(\s)')
        self.__whitespace_re_no_sep = re.compile(r'(?<![\\])(\s)')
        Parser.__init__(self,file_path,sep_char_re,ver_char_re,value_splitor)

    def _parse(self, lines):
        line_no=0
        i = iter(lines)
        comment=""
        block=""
        for line in i:
            line_no += 1
            line_after_strip = line.strip()
            # Skip null lines
            if not line_after_strip:
                block+=line
                continue

            # Skip lines which are comments
            if line[0] == '#':
                comment+=line
                block+=line
                continue
            if line[0]=="[" and line[-1]=="]":
                comment+=line
                block+=line
                continue
            sep_id_x = -1
            m = self._sep_char_re.search(line)
            if m:
                first, last = m.span()
                start, end = 0, first
                whitespace_re = self.__whitespace_re
            else:
                if self._ver_char_re.search(line):
                    whitespace_re = self.__whitespace_re_no_sep
                else:
                    comment+=line
                    block+=line
                    continue
                start, end = 0, len(line)

            m2 = whitespace_re.search(line, start, end)
            if m2:
                first, last = m2.span()
                if first!=0:
                    sep_id_x = first
                elif m:
                    first, last = m.span()
                    sep_id_x = last - 1
            elif m:
                first, last = m.span()
                sep_id_x = last - 1

            while line.strip()[-1] == '\\':
                next_line = i.next()
                line_no += 1
                line = line+next_line
                if next_line == '\n' or next_line == '\r' or next_line == '\r\n' or next_line == '\n\r':
                    break
            if sep_id_x != -1:
                key, value = line[:sep_id_x], line[sep_id_x+1:]
                block+=line[:sep_id_x+1]
            else:
                key,value = line,''
                block+=key

            s_block=""
            v_range_list=[]
            v_range_iter=self._value_splitor.finditer(value)
            for match in v_range_iter:
                v_range_list.append(match)

            if v_range_list:
                v_range_first, v_range_last = v_range_list[-1].span()
                if v_range_last == len(value):# means newline symbol is the last char.
                    s_block=value[v_range_first:]
                    value = value[:v_range_first]

            comment=comment.strip()
            key=key.strip()
            hashcode=getHashCode(value)
            self._generate_item(comment,key,value,block,hashcode)
            comment=""
            block=s_block
        if block : self._generate_item(comment,"","",block,"")


class Node(object):
    def __init__(self, children=None):
        self._children_list = [] if children is None else children

    def __iter__(self):
        for child in self.children():
            if child is not None:
                yield child

    def children(self):
        return self._children_list

    def to_ecma(self):
        from slimit.visitors.ecmavisitor import ECMAVisitor
        visitor = ECMAVisitor()
        return visitor.visit(self)

class Program(Node):
    pass

class Block(Node):
    pass

class Boolean(Node):
    def __init__(self, value):
        self.value = value

    def children(self):
        return []

class Null(Node):
    def __init__(self, value):
        self.value = value

    def children(self):
        return []

class Number(Node):
    def __init__(self, value):
        self.value = value

    def children(self):
        return []

class Identifier(Node):
    def __init__(self, value):
        self.value = value

    def children(self):
        return []

class String(Node):
    def __init__(self, value,oppos):
        self.value = value
        self.oppos=oppos

    def children(self):
        return []

class Regex(Node):
    def __init__(self, value):
        self.value = value

    def children(self):
        return []

class Array(Node):
    def __init__(self, items):
        self.items = items

    def children(self):
        return self.items

class Object(Node):
    def __init__(self, properties=None):
        self.properties = [] if properties is None else properties

    def children(self):
        return self.properties

class NewExpr(Node):
    def __init__(self, identifier, args=None):
        self.identifier = identifier
        self.args = [] if args is None else args

    def children(self):
        return [self.identifier, self.args]

class FunctionCall(Node):
    def __init__(self, identifier, args=None):
        self.identifier = identifier
        self.args = [] if args is None else args

    def children(self):
        return [self.identifier] + self.args

class BracketAccessor(Node):
    def __init__(self, node, expr):
        self.node = node
        self.expr = expr

    def children(self):
        return [self.node, self.expr]

class DotAccessor(Node):
    def __init__(self, node, identifier):
        self.node = node
        self.identifier = identifier

    def children(self):
        return [self.node, self.identifier]


# modify the return from yacc from locate translated string
class Assign(Node):
    def __init__(self, op, left, right,oppos):
        self.op = op
        self.left = left
        self.right = right
        self.oppos=oppos

    def children(self):
        return [self.left, self.right]

class GetPropAssign(Node):
    def __init__(self, prop_name, elements):
        """elements - function body"""
        self.prop_name = prop_name
        self.elements = elements

    def children(self):
        return [self.prop_name] + self.elements

class SetPropAssign(Node):
    def __init__(self, prop_name, parameters, elements):
        """elements - function body"""
        self.prop_name = prop_name
        self.parameters = parameters
        self.elements = elements

    def children(self):
        return [self.prop_name] + self.parameters + self.elements

class VarStatement(Node):
    pass

class VarDecl(Node):
    def __init__(self, identifier, initializer=None):
        self.identifier = identifier
        self.identifier._mangle_candidate = True
        self.initializer = initializer

    def children(self):
        return [self.identifier, self.initializer]

class UnaryOp(Node):
    def __init__(self, op, value, postfix=False):
        self.op = op
        self.value = value
        self.postfix = postfix

    def children(self):
        return [self.value]

class BinOp(Node):
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

    def children(self):
        return [self.left, self.right]

class Conditional(Node):
    """Conditional Operator ( ? : )"""
    def __init__(self, predicate, consequent, alternative):
        self.predicate = predicate
        self.consequent = consequent
        self.alternative = alternative

    def children(self):
        return [self.predicate, self.consequent, self.alternative]

class If(Node):
    def __init__(self, predicate, consequent, alternative=None):
        self.predicate = predicate
        self.consequent = consequent
        self.alternative = alternative

    def children(self):
        return [self.predicate, self.consequent, self.alternative]

class DoWhile(Node):
    def __init__(self, predicate, statement):
        self.predicate = predicate
        self.statement = statement

    def children(self):
        return [self.predicate, self.statement]

class While(Node):
    def __init__(self, predicate, statement):
        self.predicate = predicate
        self.statement = statement

    def children(self):
        return [self.predicate, self.statement]

class For(Node):
    def __init__(self, init, cond, count, statement):
        self.init = init
        self.cond = cond
        self.count = count
        self.statement = statement

    def children(self):
        return [self.init, self.cond, self.count, self.statement]

class ForIn(Node):
    def __init__(self, item, iterable, statement):
        self.item = item
        self.iterable = iterable
        self.statement = statement

    def children(self):
        return [self.item, self.iterable, self.statement]

class Continue(Node):
    def __init__(self, identifier=None):
        self.identifier = identifier

    def children(self):
        return [self.identifier]

class Break(Node):
    def __init__(self, identifier=None):
        self.identifier = identifier

    def children(self):
        return [self.identifier]

class Return(Node):
    def __init__(self, expr=None):
        self.expr = expr

    def children(self):
        return [self.expr]

class With(Node):
    def __init__(self, expr, statement):
        self.expr = expr
        self.statement = statement

    def children(self):
        return [self.expr, self.statement]

class Switch(Node):
    def __init__(self, expr, cases, default=None):
        self.expr = expr
        self.cases = cases
        self.default = default

    def children(self):
        return [self.expr] + self.cases + [self.default]

class Case(Node):
    def __init__(self, expr, elements):
        self.expr = expr
        self.elements = elements if elements is not None else []

    def children(self):
        return [self.expr] + self.elements

class Default(Node):
    def __init__(self, elements):
        self.elements = elements if elements is not None else []

    def children(self):
        return self.elements

class Label(Node):
    def __init__(self, identifier, statement):
        self.identifier = identifier
        self.statement = statement

    def children(self):
        return [self.identifier, self.statement]

class Throw(Node):
    def __init__(self, expr):
        self.expr = expr

    def children(self):
        return [self.expr]

class Try(Node):
    def __init__(self, statements, catch=None, fin=None):
        self.statements = statements
        self.catch = catch
        self.fin = fin

    def children(self):
        return [self.statements] + [self.catch, self.fin]

class Catch(Node):
    def __init__(self, identifier, elements):
        self.identifier = identifier
        self.identifier._mangle_candidate = True
        self.elements = elements

    def children(self):
        return [self.identifier, self.elements]

class Finally(Node):
    def __init__(self, elements):
        self.elements = elements

    def children(self):
        return self.elements

class Debugger(Node):
    def __init__(self, value):
        self.value = value

    def children(self):
        return []


class FuncBase(Node):
    def __init__(self, identifier, parameters, elements):
        self.identifier = identifier
        self.parameters = parameters if parameters is not None else []
        self.elements = elements if elements is not None else []
        self._init_ids()

    def _init_ids(self):
        if self.identifier is not None:
            self.identifier._mangle_candidate = True
        for param in self.parameters:
            param._mangle_candidate = True

    def children(self):
        return [self.identifier] + self.parameters + self.elements

class FuncDecl(FuncBase):
    pass

class FuncExpr(FuncBase):
    pass


class Comma(Node):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def children(self):
        return [self.left, self.right]

class EmptyStatement(Node):
    def __init__(self, value):
        self.value = value

    def children(self):
        return []

class ExprStatement(Node):
    def __init__(self, expr):
        self.expr = expr

    def children(self):
        return [self.expr]

class Elision(Node):
    def __init__(self, value):
        self.value = value

    def children(self):
        return []

class This(Node):
    def __init__(self):
        pass

    def children(self):
        return [] 
        

import ply.yacc

import ast
from l10nparser.js.handler.lexer import Lexer


try:
    from slimit import lextab, yacctab
except ImportError:
    lextab, yacctab = 'lextab', 'yacctab'


class Handler(object):
    """JavaScript and json handler.

    base on the lex and yacc. call all content. 
    """

    def __init__(self, lex_optimize=True, lextab=lextab,
                 yacc_optimize=True, yacctab=yacctab, yacc_debug=False):
        self.lex_optimize = lex_optimize
        self.lextab = lextab
        self.yacc_optimize = yacc_optimize
        self.yacctab = yacctab
        self.yacc_debug = yacc_debug

        self.lexer = Lexer()
        self.lexer.build(optimize=lex_optimize, lextab=lextab)
        self.tokens = self.lexer.tokens

        self.parser = ply.yacc.yacc(
            module=self, optimize=yacc_optimize,
            debug=yacc_debug, tabmodule=yacctab, start='program')

        self._error_tokens = {}

    def _has_been_seen_before(self, token):
        if token is None:
            return False
        key = token.type, token.value, token.lineno, token.lexpos
        return key in self._error_tokens

    def _mark_as_seen(self, token):
        if token is None:
            return
        key = token.type, token.value, token.lineno, token.lexpos
        self._error_tokens[key] = True

    def _raise_syntax_error(self, token):
        raise SyntaxError(
            'Unexpected token (%s, %r) at %s:%s between %s and %s' % (
                token.type, token.value, token.lineno, token.lexpos,
                self.lexer.prev_token, self.lexer.token())
            )

    def parse(self, text, debug=False):
        return self.parser.parse(text, lexer=self.lexer, debug=debug)

    def p_empty(self, p):
        """empty :"""
        pass

    def p_auto_semi(self, p):
        """auto_semi : error"""
        pass

    def p_error(self, token):
        if self._has_been_seen_before(token):
            self._raise_syntax_error(token)

        if token is None or token.type != 'SEMI':
            next_token = self.lexer.auto_semi(token)
            if next_token is not None:
                self._mark_as_seen(token)
                self.parser.errok()
                return next_token

        self._raise_syntax_error(token)

    # Comment rules
    # def p_single_line_comment(self, p):
    #     """single_line_comment : LINE_COMMENT"""
    #     pass

    # def p_multi_line_comment(self, p):
    #     """multi_line_comment : BLOCK_COMMENT"""
    #     pass

    # Main rules

    def p_program(self, p):
        """program : source_elements"""
        p[0] = Program(p[1])


    def p_source_elements(self, p):
        """source_elements : empty
                           | source_element_list
        """
        p[0] = p[1]

    def p_source_element_list(self, p):
        """source_element_list : source_element
                               | source_element_list source_element
        """
        if len(p) == 2: # single source element
            p[0] = [p[1]]
        else:
            p[1].append(p[2])
            p[0] = p[1]

    def p_source_element(self, p):
        """source_element : statement
                          | function_declaration
        """
        p[0] = p[1]

    def p_statement(self, p):
        """statement : block
                     | variable_statement
                     | empty_statement
                     | expr_statement
                     | if_statement
                     | iteration_statement
                     | continue_statement
                     | break_statement
                     | return_statement
                     | with_statement
                     | switch_statement
                     | labelled_statement
                     | throw_statement
                     | try_statement
                     | debugger_statement
                     | function_declaration
        """
        p[0] = p[1]

    # By having source_elements in the production we support
    # also function_declaration inside blocks
    def p_block(self, p):
        """block : LBRACE source_elements RBRACE"""
        p[0] = Block(p[2])

    def p_literal(self, p):
        """literal : null_literal
                   | boolean_literal
                   | numeric_literal
                   | string_literal
                   | regex_literal
        """
        p[0] = p[1]

    def p_boolean_literal(self, p):
        """boolean_literal : TRUE
                           | FALSE
        """
        p[0] = Boolean(p[1])

    def p_null_literal(self, p):
        """null_literal : NULL"""
        p[0] = Null(p[1])

    def p_numeric_literal(self, p):
        """numeric_literal : NUMBER"""
        p[0] = Number(p[1])

    def p_string_literal(self, p):
        """string_literal : STRING"""
        p[0] = String(p[1],oppos=getattr(p.slice[1], 'lexpos', ''))

    def p_regex_literal(self, p):
        """regex_literal : REGEX"""
        p[0] = Regex(p[1])

    def p_identifier(self, p):
        """identifier : ID"""
        p[0] = Identifier(p[1])

    ###########################################
    # Expressions
    ###########################################
    def p_primary_expr(self, p):
        """primary_expr : primary_expr_no_brace
                        | object_literal
        """
        p[0] = p[1]

    def p_primary_expr_no_brace_1(self, p):
        """primary_expr_no_brace : identifier"""
        p[1]._mangle_candidate = True
        p[1]._in_expression = True
        p[0] = p[1]

    def p_primary_expr_no_brace_2(self, p):
        """primary_expr_no_brace : THIS"""
        p[0] = This()

    def p_primary_expr_no_brace_3(self, p):
        """primary_expr_no_brace : literal
                                 | array_literal
        """
        p[0] = p[1]

    def p_primary_expr_no_brace_4(self, p):
        """primary_expr_no_brace : LPAREN expr RPAREN"""
        p[2]._parens = True
        p[0] = p[2]

    def p_array_literal_1(self, p):
        """array_literal : LBRACKET elision_opt RBRACKET"""
        p[0] = Array(items=p[2])

    def p_array_literal_2(self, p):
        """array_literal : LBRACKET element_list RBRACKET
                         | LBRACKET element_list COMMA elision_opt RBRACKET
        """
        items = p[2]
        if len(p) == 6:
            items.extend(p[4])
        p[0] = Array(items=items)


    def p_element_list(self, p):
        """element_list : elision_opt assignment_expr
                        | element_list COMMA elision_opt assignment_expr
        """
        if len(p) == 3:
            p[0] = p[1] + [p[2]]
        else:
            p[1].extend(p[3])
            p[1].append(p[4])
            p[0] = p[1]

    def p_elision_opt_1(self, p):
        """elision_opt : empty"""
        p[0] = []

    def p_elision_opt_2(self, p):
        """elision_opt : elision"""
        p[0] = p[1]

    def p_elision(self, p):
        """elision : COMMA
                   | elision COMMA
        """
        if len(p) == 2:
            p[0] = [Elision(p[1])]
        else:
            p[1].append(Elision(p[2]))
            p[0] = p[1]

    def p_object_literal(self, p):
        """object_literal : LBRACE RBRACE
                          | LBRACE property_list RBRACE
                          | LBRACE property_list COMMA RBRACE
        """
        if len(p) == 3:
            p[0] = Object()
        else:
            p[0] = Object(properties=p[2])

    def p_property_list(self, p):
        """property_list : property_assignment
                         | property_list COMMA property_assignment
        """
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[1].append(p[3])
            p[0] = p[1]

    # XXX: GET / SET
    def p_property_assignment(self, p):
        """property_assignment \
             : property_name COLON assignment_expr
             | GETPROP property_name LPAREN RPAREN LBRACE function_body RBRACE
             | SETPROP property_name LPAREN formal_parameter_list RPAREN \
                   LBRACE function_body RBRACE
        """
        if len(p) == 4:
            p[0] = Assign(left=p[1], op=p[2], right=p[3],oppos=getattr(p.slice[2], 'lexpos', ''))
        elif len(p) == 8:
            p[0] = GetPropAssign(prop_name=p[2], elements=p[6])
        else:
            p[0] = SetPropAssign(
                prop_name=p[2], parameters=p[4], elements=p[7])

    def p_property_name(self, p):
        """property_name : identifier
                         | string_literal
                         | numeric_literal
        """
        p[0] = p[1]

    # 11.2 Left-Hand-Side Expressions
    def p_member_expr(self, p):
        """member_expr : primary_expr
                       | function_expr
                       | member_expr LBRACKET expr RBRACKET
                       | member_expr PERIOD identifier
                       | NEW member_expr arguments
        """
        if len(p) == 2:
            p[0] = p[1]
        elif p[1] == 'new':
            p[0] = NewExpr(p[2], p[3])
        elif p[2] == '.':
            p[0] = DotAccessor(p[1], p[3])
        else:
            p[0] = BracketAccessor(p[1], p[3])

    def p_member_expr_nobf(self, p):
        """member_expr_nobf : primary_expr_no_brace
                            | function_expr
                            | member_expr_nobf LBRACKET expr RBRACKET
                            | member_expr_nobf PERIOD identifier
                            | NEW member_expr arguments
        """
        if len(p) == 2:
            p[0] = p[1]
        elif p[1] == 'new':
            p[0] = NewExpr(p[2], p[3])
        elif p[2] == '.':
            p[0] = DotAccessor(p[1], p[3])
        else:
            p[0] = BracketAccessor(p[1], p[3])

    def p_new_expr(self, p):
        """new_expr : member_expr
                    | NEW new_expr
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = NewExpr(p[2])

    def p_new_expr_nobf(self, p):
        """new_expr_nobf : member_expr_nobf
                         | NEW new_expr
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = NewExpr(p[2])

    def p_call_expr(self, p):
        """call_expr : member_expr arguments
                     | call_expr arguments
                     | call_expr LBRACKET expr RBRACKET
                     | call_expr PERIOD identifier
        """
        if len(p) == 3:
            p[0] = FunctionCall(p[1], p[2])
        elif len(p) == 4:
            p[0] = DotAccessor(p[1], p[3])
        else:
            p[0] = BracketAccessor(p[1], p[3])

    def p_call_expr_nobf(self, p):
        """call_expr_nobf : member_expr_nobf arguments
                          | call_expr_nobf arguments
                          | call_expr_nobf LBRACKET expr RBRACKET
                          | call_expr_nobf PERIOD identifier
        """
        if len(p) == 3:
            p[0] = FunctionCall(p[1], p[2])
        elif len(p) == 4:
            p[0] = DotAccessor(p[1], p[3])
        else:
            p[0] = BracketAccessor(p[1], p[3])

    def p_arguments(self, p):
        """arguments : LPAREN RPAREN
                     | LPAREN argument_list RPAREN
        """
        if len(p) == 4:
            p[0] = p[2]

    def p_argument_list(self, p):
        """argument_list : assignment_expr
                         | argument_list COMMA assignment_expr
        """
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[1].append(p[3])
            p[0] = p[1]

    def p_lef_hand_side_expr(self, p):
        """left_hand_side_expr : new_expr
                               | call_expr
        """
        p[0] = p[1]

    def p_lef_hand_side_expr_nobf(self, p):
        """left_hand_side_expr_nobf : new_expr_nobf
                                    | call_expr_nobf
        """
        p[0] = p[1]

    # 11.3 Postfix Expressions
    def p_postfix_expr(self, p):
        """postfix_expr : left_hand_side_expr
                        | left_hand_side_expr PLUSPLUS
                        | left_hand_side_expr MINUSMINUS
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = UnaryOp(op=p[2], value=p[1], postfix=True)

    def p_postfix_expr_nobf(self, p):
        """postfix_expr_nobf : left_hand_side_expr_nobf
                             | left_hand_side_expr_nobf PLUSPLUS
                             | left_hand_side_expr_nobf MINUSMINUS
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = UnaryOp(op=p[2], value=p[1], postfix=True)

    # 11.4 Unary Operators
    def p_unary_expr(self, p):
        """unary_expr : postfix_expr
                      | unary_expr_common
        """
        p[0] = p[1]

    def p_unary_expr_nobf(self, p):
        """unary_expr_nobf : postfix_expr_nobf
                           | unary_expr_common
        """
        p[0] = p[1]

    def p_unary_expr_common(self, p):
        """unary_expr_common : DELETE unary_expr
                             | VOID unary_expr
                             | TYPEOF unary_expr
                             | PLUSPLUS unary_expr
                             | MINUSMINUS unary_expr
                             | PLUS unary_expr
                             | MINUS unary_expr
                             | BNOT unary_expr
                             | NOT unary_expr
        """
        p[0] = UnaryOp(p[1], p[2])

    # 11.5 Multiplicative Operators
    def p_multiplicative_expr(self, p):
        """multiplicative_expr : unary_expr
                               | multiplicative_expr MULT unary_expr
                               | multiplicative_expr DIV unary_expr
                               | multiplicative_expr MOD unary_expr
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = BinOp(op=p[2], left=p[1], right=p[3])

    def p_multiplicative_expr_nobf(self, p):
        """multiplicative_expr_nobf : unary_expr_nobf
                                    | multiplicative_expr_nobf MULT unary_expr
                                    | multiplicative_expr_nobf DIV unary_expr
                                    | multiplicative_expr_nobf MOD unary_expr
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = BinOp(op=p[2], left=p[1], right=p[3])

    # 11.6 Additive Operators
    def p_additive_expr(self, p):
        """additive_expr : multiplicative_expr
                         | additive_expr PLUS multiplicative_expr
                         | additive_expr MINUS multiplicative_expr
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = BinOp(op=p[2], left=p[1], right=p[3])

    def p_additive_expr_nobf(self, p):
        """additive_expr_nobf : multiplicative_expr_nobf
                              | additive_expr_nobf PLUS multiplicative_expr
                              | additive_expr_nobf MINUS multiplicative_expr
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = BinOp(op=p[2], left=p[1], right=p[3])

    # 11.7 Bitwise Shift Operators
    def p_shift_expr(self, p):
        """shift_expr : additive_expr
                      | shift_expr LSHIFT additive_expr
                      | shift_expr RSHIFT additive_expr
                      | shift_expr URSHIFT additive_expr
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = BinOp(op=p[2], left=p[1], right=p[3])

    def p_shift_expr_nobf(self, p):
        """shift_expr_nobf : additive_expr_nobf
                           | shift_expr_nobf LSHIFT additive_expr
                           | shift_expr_nobf RSHIFT additive_expr
                           | shift_expr_nobf URSHIFT additive_expr
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = BinOp(op=p[2], left=p[1], right=p[3])


    # 11.8 Relational Operators
    def p_relational_expr(self, p):
        """relational_expr : shift_expr
                           | relational_expr LT shift_expr
                           | relational_expr GT shift_expr
                           | relational_expr LE shift_expr
                           | relational_expr GE shift_expr
                           | relational_expr INSTANCEOF shift_expr
                           | relational_expr IN shift_expr
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = BinOp(op=p[2], left=p[1], right=p[3])

    def p_relational_expr_noin(self, p):
        """relational_expr_noin : shift_expr
                                | relational_expr_noin LT shift_expr
                                | relational_expr_noin GT shift_expr
                                | relational_expr_noin LE shift_expr
                                | relational_expr_noin GE shift_expr
                                | relational_expr_noin INSTANCEOF shift_expr
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = BinOp(op=p[2], left=p[1], right=p[3])

    def p_relational_expr_nobf(self, p):
        """relational_expr_nobf : shift_expr_nobf
                                | relational_expr_nobf LT shift_expr
                                | relational_expr_nobf GT shift_expr
                                | relational_expr_nobf LE shift_expr
                                | relational_expr_nobf GE shift_expr
                                | relational_expr_nobf INSTANCEOF shift_expr
                                | relational_expr_nobf IN shift_expr
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = BinOp(op=p[2], left=p[1], right=p[3])

    # 11.9 Equality Operators
    def p_equality_expr(self, p):
        """equality_expr : relational_expr
                         | equality_expr EQEQ relational_expr
                         | equality_expr NE relational_expr
                         | equality_expr STREQ relational_expr
                         | equality_expr STRNEQ relational_expr
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = BinOp(op=p[2], left=p[1], right=p[3])

    def p_equality_expr_noin(self, p):
        """equality_expr_noin : relational_expr_noin
                              | equality_expr_noin EQEQ relational_expr
                              | equality_expr_noin NE relational_expr
                              | equality_expr_noin STREQ relational_expr
                              | equality_expr_noin STRNEQ relational_expr
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = BinOp(op=p[2], left=p[1], right=p[3])

    def p_equality_expr_nobf(self, p):
        """equality_expr_nobf : relational_expr_nobf
                              | equality_expr_nobf EQEQ relational_expr
                              | equality_expr_nobf NE relational_expr
                              | equality_expr_nobf STREQ relational_expr
                              | equality_expr_nobf STRNEQ relational_expr
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = BinOp(op=p[2], left=p[1], right=p[3])

    # 11.10 Binary Bitwise Operators
    def p_bitwise_and_expr(self, p):
        """bitwise_and_expr : equality_expr
                            | bitwise_and_expr BAND equality_expr
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = BinOp(op=p[2], left=p[1], right=p[3])

    def p_bitwise_and_expr_noin(self, p):
        """bitwise_and_expr_noin \
            : equality_expr_noin
            | bitwise_and_expr_noin BAND equality_expr_noin
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = BinOp(op=p[2], left=p[1], right=p[3])

    def p_bitwise_and_expr_nobf(self, p):
        """bitwise_and_expr_nobf \
            : equality_expr_nobf
            | bitwise_and_expr_nobf BAND equality_expr_nobf
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = BinOp(op=p[2], left=p[1], right=p[3])

    def p_bitwise_xor_expr(self, p):
        """bitwise_xor_expr : bitwise_and_expr
                            | bitwise_xor_expr BXOR bitwise_and_expr
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = BinOp(op=p[2], left=p[1], right=p[3])

    def p_bitwise_xor_expr_noin(self, p):
        """
        bitwise_xor_expr_noin \
            : bitwise_and_expr_noin
            | bitwise_xor_expr_noin BXOR bitwise_and_expr_noin
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = BinOp(op=p[2], left=p[1], right=p[3])

    def p_bitwise_xor_expr_nobf(self, p):
        """
        bitwise_xor_expr_nobf \
            : bitwise_and_expr_nobf
            | bitwise_xor_expr_nobf BXOR bitwise_and_expr_nobf
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = BinOp(op=p[2], left=p[1], right=p[3])

    def p_bitwise_or_expr(self, p):
        """bitwise_or_expr : bitwise_xor_expr
                           | bitwise_or_expr BOR bitwise_xor_expr
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = BinOp(op=p[2], left=p[1], right=p[3])

    def p_bitwise_or_expr_noin(self, p):
        """
        bitwise_or_expr_noin \
            : bitwise_xor_expr_noin
            | bitwise_or_expr_noin BOR bitwise_xor_expr_noin
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = BinOp(op=p[2], left=p[1], right=p[3])

    def p_bitwise_or_expr_nobf(self, p):
        """
        bitwise_or_expr_nobf \
            : bitwise_xor_expr_nobf
            | bitwise_or_expr_nobf BOR bitwise_xor_expr_nobf
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = BinOp(op=p[2], left=p[1], right=p[3])

    # 11.11 Binary Logical Operators
    def p_logical_and_expr(self, p):
        """logical_and_expr : bitwise_or_expr
                            | logical_and_expr AND bitwise_or_expr
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = BinOp(op=p[2], left=p[1], right=p[3])

    def p_logical_and_expr_noin(self, p):
        """
        logical_and_expr_noin : bitwise_or_expr_noin
                              | logical_and_expr_noin AND bitwise_or_expr_noin
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = BinOp(op=p[2], left=p[1], right=p[3])

    def p_logical_and_expr_nobf(self, p):
        """
        logical_and_expr_nobf : bitwise_or_expr_nobf
                              | logical_and_expr_nobf AND bitwise_or_expr_nobf
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = BinOp(op=p[2], left=p[1], right=p[3])

    def p_logical_or_expr(self, p):
        """logical_or_expr : logical_and_expr
                           | logical_or_expr OR logical_and_expr
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = BinOp(op=p[2], left=p[1], right=p[3])

    def p_logical_or_expr_noin(self, p):
        """logical_or_expr_noin : logical_and_expr_noin
                                | logical_or_expr_noin OR logical_and_expr_noin
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = BinOp(op=p[2], left=p[1], right=p[3])

    def p_logical_or_expr_nobf(self, p):
        """logical_or_expr_nobf : logical_and_expr_nobf
                                | logical_or_expr_nobf OR logical_and_expr_nobf
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = BinOp(op=p[2], left=p[1], right=p[3])

    # 11.12 Conditional Operator ( ? : )
    def p_conditional_expr(self, p):
        """
        conditional_expr \
            : logical_or_expr
            | logical_or_expr CONDOP assignment_expr COLON assignment_expr
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = Conditional(
                predicate=p[1], consequent=p[3], alternative=p[5])

    def p_conditional_expr_noin(self, p):
        """
        conditional_expr_noin \
            : logical_or_expr_noin
            | logical_or_expr_noin CONDOP assignment_expr_noin COLON \
                  assignment_expr_noin
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = Conditional(
                predicate=p[1], consequent=p[3], alternative=p[5])

    def p_conditional_expr_nobf(self, p):
        """
        conditional_expr_nobf \
            : logical_or_expr_nobf
            | logical_or_expr_nobf CONDOP assignment_expr COLON assignment_expr
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = Conditional(
                predicate=p[1], consequent=p[3], alternative=p[5])

    # 11.13 Assignment Operators
    def p_assignment_expr(self, p):
        """
        assignment_expr \
            : conditional_expr
            | left_hand_side_expr assignment_operator assignment_expr
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = Assign(left=p[1], op=p[2], right=p[3],oppos=getattr(p.slice[2], 'lexpos', ''))

    def p_assignment_expr_noin(self, p):
        """
        assignment_expr_noin \
            : conditional_expr_noin
            | left_hand_side_expr assignment_operator assignment_expr_noin
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = Assign(left=p[1], op=p[2], right=p[3],oppos=getattr(p.slice[2], 'lexpos', ''))

    def p_assignment_expr_nobf(self, p):
        """
        assignment_expr_nobf \
            : conditional_expr_nobf
            | left_hand_side_expr_nobf assignment_operator assignment_expr
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
#             if isinstance(p.slice[2], ply.yacc.YaccSymbol):
#                 pass
            oppos=getattr(p.slice[2], 'lexpos', '')
            print oppos

            p[0] = Assign(left=p[1], op=p[2], right=p[3],oppos=getattr(p.slice[2], 'lexpos', ''))

    def p_assignment_operator(self, p):
        """assignment_operator : EQ
                               | MULTEQUAL
                               | DIVEQUAL
                               | MODEQUAL
                               | PLUSEQUAL
                               | MINUSEQUAL
                               | LSHIFTEQUAL
                               | RSHIFTEQUAL
                               | URSHIFTEQUAL
                               | ANDEQUAL
                               | XOREQUAL
                               | OREQUAL
        """
        p[0] = p[1]

    # 11.4 Comma Operator
    def p_expr(self, p):
        """expr : assignment_expr
                | expr COMMA assignment_expr
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = Comma(left=p[1], right=p[3])

    def p_expr_noin(self, p):
        """expr_noin : assignment_expr_noin
                     | expr_noin COMMA assignment_expr_noin
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = Comma(left=p[1], right=p[3])

    def p_expr_nobf(self, p):
        """expr_nobf : assignment_expr_nobf
                     | expr_nobf COMMA assignment_expr
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = Comma(left=p[1], right=p[3])

    # 12.2 Variable Statement
    def p_variable_statement(self, p):
        """variable_statement : VAR variable_declaration_list SEMI
                              | VAR variable_declaration_list auto_semi
        """
        p[0] = VarStatement(p[2])

    def p_variable_declaration_list(self, p):
        """
        variable_declaration_list \
            : variable_declaration
            | variable_declaration_list COMMA variable_declaration
        """
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[1].append(p[3])
            p[0] = p[1]

    def p_variable_declaration_list_noin(self, p):
        """
        variable_declaration_list_noin \
            : variable_declaration_noin
            | variable_declaration_list_noin COMMA variable_declaration_noin
        """
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[1].append(p[3])
            p[0] = p[1]

    def p_variable_declaration(self, p):
        """variable_declaration : identifier
                                | identifier initializer
        """
        if len(p) == 2:
            p[0] = VarDecl(p[1])
        else:
            p[0] = VarDecl(p[1], p[2])

    def p_variable_declaration_noin(self, p):
        """variable_declaration_noin : identifier
                                     | identifier initializer_noin
        """
        if len(p) == 2:
            p[0] = VarDecl(p[1])
        else:
            p[0] = VarDecl(p[1], p[2])

    def p_initializer(self, p):
        """initializer : EQ assignment_expr"""
        p[0] = p[2]

    def p_initializer_noin(self, p):
        """initializer_noin : EQ assignment_expr_noin"""
        p[0] = p[2]

    # 12.3 Empty Statement
    def p_empty_statement(self, p):
        """empty_statement : SEMI"""
        p[0] = EmptyStatement(p[1])

    # 12.4 Expression Statement
    def p_expr_statement(self, p):
        """expr_statement : expr_nobf SEMI
                          | expr_nobf auto_semi
        """
        p[0] = ExprStatement(p[1])

    # 12.5 The if Statement
    def p_if_statement_1(self, p):
        """if_statement : IF LPAREN expr RPAREN statement"""
        p[0] = If(predicate=p[3], consequent=p[5])

    def p_if_statement_2(self, p):
        """if_statement : IF LPAREN expr RPAREN statement ELSE statement"""
        p[0] = If(predicate=p[3], consequent=p[5], alternative=p[7])

    # 12.6 Iteration Statements
    def p_iteration_statement_1(self, p):
        """
        iteration_statement \
            : DO statement WHILE LPAREN expr RPAREN SEMI
            | DO statement WHILE LPAREN expr RPAREN auto_semi
        """
        p[0] = DoWhile(predicate=p[5], statement=p[2])

    def p_iteration_statement_2(self, p):
        """iteration_statement : WHILE LPAREN expr RPAREN statement"""
        p[0] = While(predicate=p[3], statement=p[5])

    def p_iteration_statement_3(self, p):
        """
        iteration_statement \
            : FOR LPAREN expr_noin_opt SEMI expr_opt SEMI expr_opt RPAREN \
                  statement
            | FOR LPAREN VAR variable_declaration_list_noin SEMI expr_opt SEMI\
                  expr_opt RPAREN statement
        """
        if len(p) == 10:
            p[0] = For(init=p[3], cond=p[5], count=p[7], statement=p[9])
        else:
            init = VarStatement(p[4])
            p[0] = For(init=init, cond=p[6], count=p[8], statement=p[10])

    def p_iteration_statement_4(self, p):
        """
        iteration_statement \
            : FOR LPAREN left_hand_side_expr IN expr RPAREN statement
        """
        p[0] = ForIn(item=p[3], iterable=p[5], statement=p[7])

    def p_iteration_statement_5(self, p):
        """
        iteration_statement : \
            FOR LPAREN VAR identifier IN expr RPAREN statement
        """
        p[0] = ForIn(item=VarDecl(p[4]), iterable=p[6], statement=p[8])

    def p_iteration_statement_6(self, p):
        """
        iteration_statement \
          : FOR LPAREN VAR identifier initializer_noin IN expr RPAREN statement
        """
        p[0] = ForIn(item=VarDecl(identifier=p[4], initializer=p[5]),
                         iterable=p[7], statement=p[9])

    def p_expr_opt(self, p):
        """expr_opt : empty
                    | expr
        """
        p[0] = p[1]

    def p_expr_noin_opt(self, p):
        """expr_noin_opt : empty
                         | expr_noin
        """
        p[0] = p[1]

    # 12.7 The continue Statement
    def p_continue_statement_1(self, p):
        """continue_statement : CONTINUE SEMI
                              | CONTINUE auto_semi
        """
        p[0] = Continue()

    def p_continue_statement_2(self, p):
        """continue_statement : CONTINUE identifier SEMI
                              | CONTINUE identifier auto_semi
        """
        p[0] = Continue(p[2])

    # 12.8 The break Statement
    def p_break_statement_1(self, p):
        """break_statement : BREAK SEMI
                           | BREAK auto_semi
        """
        p[0] = Break()

    def p_break_statement_2(self, p):
        """break_statement : BREAK identifier SEMI
                           | BREAK identifier auto_semi
        """
        p[0] = Break(p[2])


    # 12.9 The return Statement
    def p_return_statement_1(self, p):
        """return_statement : RETURN SEMI
                            | RETURN auto_semi
        """
        p[0] = Return()

    def p_return_statement_2(self, p):
        """return_statement : RETURN expr SEMI
                            | RETURN expr auto_semi
        """
        p[0] = Return(expr=p[2])

    # 12.10 The with Statement
    def p_with_statement(self, p):
        """with_statement : WITH LPAREN expr RPAREN statement"""
        p[0] = With(expr=p[3], statement=p[5])

    # 12.11 The switch Statement
    def p_switch_statement(self, p):
        """switch_statement : SWITCH LPAREN expr RPAREN case_block"""
        cases = []
        default = None
        # iterate over return values from case_block
        for item in p[5]:
            if isinstance(item, Default):
                default = item
            elif isinstance(item, list):
                cases.extend(item)

        p[0] = Switch(expr=p[3], cases=cases, default=default)

    def p_case_block(self, p):
        """
        case_block \
            : LBRACE case_clauses_opt RBRACE
            | LBRACE case_clauses_opt default_clause case_clauses_opt RBRACE
        """
        p[0] = p[2:-1]

    def p_case_clauses_opt(self, p):
        """case_clauses_opt : empty
                            | case_clauses
        """
        p[0] = p[1]

    def p_case_clauses(self, p):
        """case_clauses : case_clause
                        | case_clauses case_clause
        """
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[1].append(p[2])
            p[0] = p[1]

    def p_case_clause(self, p):
        """case_clause : CASE expr COLON source_elements"""
        p[0] = Case(expr=p[2], elements=p[4])

    def p_default_clause(self, p):
        """default_clause : DEFAULT COLON source_elements"""
        p[0] = Default(elements=p[3])

    # 12.12 Labelled Statements
    def p_labelled_statement(self, p):
        """labelled_statement : identifier COLON statement"""
        p[0] = Label(identifier=p[1], statement=p[3])

    # 12.13 The throw Statement
    def p_throw_statement(self, p):
        """throw_statement : THROW expr SEMI
                           | THROW expr auto_semi
        """
        p[0] = Throw(expr=p[2])

    # 12.14 The try Statement
    def p_try_statement_1(self, p):
        """try_statement : TRY block catch"""
        p[0] = Try(statements=p[2], catch=p[3])

    def p_try_statement_2(self, p):
        """try_statement : TRY block finally"""
        p[0] = Try(statements=p[2], fin=p[3])

    def p_try_statement_3(self, p):
        """try_statement : TRY block catch finally"""
        p[0] = Try(statements=p[2], catch=p[3], fin=p[4])

    def p_catch(self, p):
        """catch : CATCH LPAREN identifier RPAREN block"""
        p[0] = Catch(identifier=p[3], elements=p[5])

    def p_finally(self, p):
        """finally : FINALLY block"""
        p[0] = Finally(elements=p[2])

    # 12.15 The debugger statement
    def p_debugger_statement(self, p):
        """debugger_statement : DEBUGGER SEMI
                              | DEBUGGER auto_semi
        """
        p[0] = Debugger(p[1])

    # 13 Function Definition
    def p_function_declaration(self, p):
        """
        function_declaration \
            : FUNCTION identifier LPAREN RPAREN LBRACE function_body RBRACE
            | FUNCTION identifier LPAREN formal_parameter_list RPAREN LBRACE \
                 function_body RBRACE
        """
        if len(p) == 8:
            p[0] = FuncDecl(
                identifier=p[2], parameters=None, elements=p[6])
        else:
            p[0] = FuncDecl(
                identifier=p[2], parameters=p[4], elements=p[7])

    def p_function_expr_1(self, p):
        """
        function_expr \
            : FUNCTION LPAREN RPAREN LBRACE function_body RBRACE
            | FUNCTION LPAREN formal_parameter_list RPAREN \
                LBRACE function_body RBRACE
        """
        if len(p) == 7:
            p[0] = FuncExpr(
                identifier=None, parameters=None, elements=p[5])
        else:
            p[0] = FuncExpr(
                identifier=None, parameters=p[3], elements=p[6])

    def p_function_expr_2(self, p):
        """
        function_expr \
            : FUNCTION identifier LPAREN RPAREN LBRACE function_body RBRACE
            | FUNCTION identifier LPAREN formal_parameter_list RPAREN \
                LBRACE function_body RBRACE
        """
        if len(p) == 8:
            p[0] = FuncExpr(
                identifier=p[2], parameters=None, elements=p[6])
        else:
            p[0] = FuncExpr(
                identifier=p[2], parameters=p[4], elements=p[7])


    def p_formal_parameter_list(self, p):
        """formal_parameter_list : identifier
                                 | formal_parameter_list COMMA identifier
        """
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[1].append(p[3])
            p[0] = p[1]

    def p_function_body(self, p):
        """function_body : source_elements"""
        p[0] = p[1]


__author__ = 'Ruslan Spivak <ruslan.spivak@gmail.com>'


class ASTVisitor(object):
    """Base class for custom AST node visitors.

    Example:

    >>> from slimit.parser import Parser
    >>> from slimit.visitors.nodevisitor import ASTVisitor
    >>>
    >>> text = '''
    ... var x = {
    ...     "key1": "value1",
    ...     "key2": "value2"
    ... };
    ... '''
    >>>
    >>> class MyVisitor(ASTVisitor):
    ...     def visit_Object(self, node):
    ...         '''Visit object literal.'''
    ...         for prop in node:
    ...             left, right = prop.left, prop.right
    ...             print 'Property value: %s' % right.value
    ...             # visit all children in turn
    ...             self.visit(prop)
    ...
    >>>
    >>> parser = Parser()
    >>> tree = parser.parse(text)
    >>> visitor = MyVisitor()
    >>> visitor.visit(tree)
    Property value: "value1"
    Property value: "value2"

    """

    def visit(self, node):
        method = 'visit_%s' % node.__class__.__name__
        return getattr(self, method, self.generic_visit)(node)

    def generic_visit(self, node):
        for child in node:
            self.visit(child)


class NodeVisitor(object):
    """Simple node visitor."""

    def visit(self, node):
        """Returns a generator that walks all children recursively."""
        for child in node:
            yield child
            for subchild in self.visit(child):
                yield subchild


def visit(node):
    visitor = NodeVisitor()
    for child in visitor.visit(node):
        yield child


class JsParser(Parser):
    encoding='utf-8'
    def __init__(self,file_path):
        ver_char_re=re.compile(r'^[\s]*?$')
        Parser.__init__(self,file_path,None,ver_char_re,None)
 
    def load(self):
        """ Load properties_old from an open file stream """
        stream=self._open_resource_file()
        lines = stream.read()
        self._parse(lines)
        self._add_prev_next_hashcode()

    def _parse(self, lines):
        curr_block=""
        curr_key=""
        curr_value=""
        curr_comment=""
        block_stat_op=0
        key_count = 0
        tree = Handler().parse(lines)
        for node in visit(tree):
            if isinstance(node, String):
                curr_key=key_count
                curr_value=node.value
                
                if curr_value[0]=="'" or curr_value[-1]=="'":
                    curr_value=curr_value.strip("'")
                    

                elif curr_value[0]=="\"" or curr_value[-1]=="\"":
                    curr_value=curr_value.strip("\"")
                    
                else:
                    print curr_value
                    raise Exception("Unhandled format. file name: %s format: %s" % (self._file_path,curr_value))
#                 print
                
                m2=self._ver_char_re.match(curr_value)
                if m2:
                    continue
                v_stat_op=int(node.oppos)
                curr_block=lines[block_stat_op:v_stat_op+1]
                block_stat_op=v_stat_op+len(curr_value)+1
                hashcode=getHashCode(curr_value)
                self._generate_item(curr_comment,str(curr_key),curr_value,curr_block,hashcode)
                key_count += 1 
                curr_block=""
                curr_key=""
                curr_value=""
                curr_comment=""
        last_block=lines[block_stat_op:]
        hashcode=getHashCode(curr_value)
        self._generate_item(curr_comment,str(curr_key),curr_value,last_block,hashcode)
        
        
if __name__ == '__main__':
    data = []
#     aaaa = r'D:\strata\loginsight\components\commons-lib\lib\src\com\vmware\loginsight\i18n\messages.properties'
#     parser = PropertiesParser(aaaa)
#     parser.load()
#     for i in parser._string_item_list:
#         data.append(i.key)
#     print len(data)
#     print len(list(set(data)))
    
#     aaaa = r'D:\strata\loginsight\components\ui\application\src\webui.properties'
#     parser = PropertiesParser(aaaa)
#     parser.load()
    data1 = {}
#     for i in parser._string_item_list:
#         data.append(i.key)
#         
#     print len(data)
#     print len(list(set(data)))    
    
    aaaa1 = r'D:\\strata\loginsight\components\ui\application\WebContent\js\pi-i18n\lang\pi-i18n.js'
    parser1 = PropertiesParser(aaaa1)
    parser1.load()
    for i in parser1._string_item_list:
        data.append(i.key)
        if i.key not in data1:
            data1[i.key] = i.value
        elif i.key in data1:
            print i.key, '11111111', i.value
            print data1.get(i.key)
    print len(data)
    print len(list(set(data)))