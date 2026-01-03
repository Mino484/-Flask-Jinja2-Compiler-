import re
from enum import Enum
from typing import List, Optional, Dict, Any
from flask import Flask, request, jsonify
import json
import os
import uuid
from datetime import datetime

app = Flask(__name__, static_folder='static', template_folder='templates')

class TokenType(Enum):
    TAG_OPEN = "TAG_OPEN"
    TAG_CLOSE = "TAG_CLOSE"
    TAG_SELF_CLOSE = "TAG_SELF_CLOSE"
    TEXT = "TEXT"
    EXPR_OPEN = "EXPR_OPEN"
    EXPR_CLOSE = "EXPR_CLOSE"
    STMT_OPEN = "STMT_OPEN"
    STMT_CLOSE = "STMT_CLOSE"
    IDENTIFIER = "IDENTIFIER"
    STRING = "STRING"
    NUMBER = "NUMBER"
    BOOL = "BOOL"
    OPERATOR = "OPERATOR"
    ASSIGN = "ASSIGN"
    DOT = "DOT"
    COMMA = "COMMA"
    COLON = "COLON"
    PIPE = "PIPE"
    L_PAREN = "L_PAREN"
    R_PAREN = "R_PAREN"
    SLASH = "SLASH"  #  إضافة نوع جديد للمحرف /
    IF = "IF"
    ELSE = "ELSE"
    ELIF = "ELIF"
    ENDIF = "ENDIF"
    FOR = "FOR"
    IN = "IN"
    ENDFOR = "ENDFOR"
    SET = "SET"
    EOF = "EOF"

class Token:
    def __init__(self, type: TokenType, value: str, line: int, column: int):
        self.type = type
        self.value = value
        self.line = line
        self.column = column
    
    def to_dict(self):
        return {
            'type': self.type.name,
            'value': self.value,
            'line': self.line,
            'column': self.column
        }
    
    def __repr__(self):
        return f"Token({self.type}, '{self.value}', line={self.line})"

class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
        self.keywords = {
            'if': TokenType.IF,
            'else': TokenType.ELSE,
            'elif': TokenType.ELIF,
            'endif': TokenType.ENDIF,
            'for': TokenType.FOR,
            'in': TokenType.IN,
            'endfor': TokenType.ENDFOR,
            'set': TokenType.SET,
        }
    
    def tokenize(self) -> List[Token]:
        while self.position < len(self.source):
            if self.source[self.position].isspace():
                if self.source[self.position] == '\n':
                    self.line += 1
                    self.column = 1
                else:
                    self.column += 1
                self.position += 1
                continue
            
            # التحقق من الرموز المكونة من حرفين أولاً
            if self.position + 1 < len(self.source):
                two_char = self.source[self.position:self.position+2]
                if two_char == '{{':
                    token = Token(TokenType.EXPR_OPEN, two_char, self.line, self.column)
                    self.tokens.append(token)
                    self.position += 2
                    self.column += 2
                    continue
                elif two_char == '}}':
                    token = Token(TokenType.EXPR_CLOSE, two_char, self.line, self.column)
                    self.tokens.append(token)
                    self.position += 2
                    self.column += 2
                    continue
                elif two_char == '{%':
                    token = Token(TokenType.STMT_OPEN, two_char, self.line, self.column)
                    self.tokens.append(token)
                    self.position += 2
                    self.column += 2
                    continue
                elif two_char == '%}':
                    token = Token(TokenType.STMT_CLOSE, two_char, self.line, self.column)
                    self.tokens.append(token)
                    self.position += 2
                    self.column += 2
                    continue
                elif two_char == '/>':
                    token = Token(TokenType.TAG_SELF_CLOSE, two_char, self.line, self.column)
                    self.tokens.append(token)
                    self.position += 2
                    self.column += 2
                    continue
            
            char = self.source[self.position]
            
            # التعامل مع المحرف / بشكل منفصل
            if char == '/':
                # نتحقق إذا كان جزء من علامة إغلاق HTML مثل </div>
                if (self.position > 0 and 
                    self.source[self.position - 1] == '<' and 
                    self.position + 1 < len(self.source) and 
                    self.source[self.position + 1].isalpha()):
                    # في هذه الحالة، المحرف / هو جزء من علامة الإغلاق
                    token = Token(TokenType.SLASH, char, self.line, self.column)
                    self.tokens.append(token)
                    self.position += 1
                    self.column += 1
                    continue
                else:
                    # هون  نتعامل معه كعامل قسمة
                    token = Token(TokenType.OPERATOR, char, self.line, self.column)
                    self.tokens.append(token)
                    self.position += 1
                    self.column += 1
                    continue
            
            if char == '<':
                token = Token(TokenType.TAG_OPEN, char, self.line, self.column)
                self.tokens.append(token)
                self.position += 1
                self.column += 1
                continue
            elif char == '>':
                token = Token(TokenType.TAG_CLOSE, char, self.line, self.column)
                self.tokens.append(token)
                self.position += 1
                self.column += 1
                continue
            elif char == '|':
                token = Token(TokenType.PIPE, char, self.line, self.column)
                self.tokens.append(token)
                self.position += 1
                self.column += 1
                continue
            elif char == '(':
                token = Token(TokenType.L_PAREN, char, self.line, self.column)
                self.tokens.append(token)
                self.position += 1
                self.column += 1
                continue
            elif char == ')':
                token = Token(TokenType.R_PAREN, char, self.line, self.column)
                self.tokens.append(token)
                self.position += 1
                self.column += 1
                continue
            elif char == '=':
                token = Token(TokenType.ASSIGN, char, self.line, self.column)
                self.tokens.append(token)
                self.position += 1
                self.column += 1
                continue
            elif char == '.':
                token = Token(TokenType.DOT, char, self.line, self.column)
                self.tokens.append(token)
                self.position += 1
                self.column += 1
                continue
            elif char == ',':
                token = Token(TokenType.COMMA, char, self.line, self.column)
                self.tokens.append(token)
                self.position += 1
                self.column += 1
                continue
            elif char == ':':
                token = Token(TokenType.COLON, char, self.line, self.column)
                self.tokens.append(token)
                self.position += 1
                self.column += 1
                continue
            
            if char.isdigit():
                number = ''
                while self.position < len(self.source) and (self.source[self.position].isdigit() or 
                                                           (self.source[self.position] == '.' and 
                                                            self.position + 1 < len(self.source) and 
                                                            self.source[self.position + 1].isdigit())):
                    number += self.source[self.position]
                    self.position += 1
                token = Token(TokenType.NUMBER, number, self.line, self.column)
                self.tokens.append(token)
                self.column += len(number)
                continue
            
            if char.isalpha() or char == '_':
                identifier = ''
                while self.position < len(self.source) and (self.source[self.position].isalnum() or 
                                                           self.source[self.position] == '_'):
                    identifier += self.source[self.position]
                    self.position += 1
                token_type = TokenType.IDENTIFIER
                if identifier in self.keywords:
                    token_type = self.keywords[identifier]
                elif identifier in ['True', 'False']:
                    token_type = TokenType.BOOL
                token = Token(token_type, identifier, self.line, self.column)
                self.tokens.append(token)
                self.column += len(identifier)
                continue
            
            if char in ['"', "'"]:
                quote_char = char
                string_literal = quote_char
                self.position += 1
                self.column += 1
                while (self.position < len(self.source) and 
                       self.source[self.position] != quote_char):
                    if self.source[self.position] == '\\' and self.position + 1 < len(self.source):
                        string_literal += self.source[self.position]
                        self.position += 1
                        self.column += 1
                    string_literal += self.source[self.position]
                    self.position += 1
                    self.column += 1
                if self.position < len(self.source):
                    string_literal += self.source[self.position]
                    self.position += 1
                    self.column += 1
                token = Token(TokenType.STRING, string_literal, self.line, self.column)
                self.tokens.append(token)
                continue
            
            multi_char_operators = ['==', '!=', '<=', '>=', 'and', 'or', 'not']
            matched_operator = False
            for op in multi_char_operators:
                if self.source.startswith(op, self.position):
                    token = Token(TokenType.OPERATOR, op, self.line, self.column)
                    self.tokens.append(token)
                    self.position += len(op)
                    self.column += len(op)
                    matched_operator = True
                    break
            
            if matched_operator:
                continue
            
            
            single_char_operators = ['+', '-', '*', '<', '>']
            if char in single_char_operators:
                token = Token(TokenType.OPERATOR, char, self.line, self.column)
                self.tokens.append(token)
                self.position += 1
                self.column += 1
                continue
            
            # التعامل مع النص العادي
            text = ''
            while (self.position < len(self.source) and 
                   not self.source[self.position].isspace() and
                   self.position + 1 < len(self.source) and
                   not self.source.startswith('{{', self.position) and
                   not self.source.startswith('{%', self.position) and
                   not self.source.startswith('}}', self.position) and
                   not self.source.startswith('%}', self.position) and
                   self.source[self.position] not in ['<', '>', '|', '(', ')', '=', '.', ',', ':', '+', '-', '*', '/']):
                text += self.source[self.position]
                self.position += 1
            
            if text:
                token = Token(TokenType.TEXT, text, self.line, self.column)
                self.tokens.append(token)
                self.column += len(text)
            else:
                # إذا لم نتعرف على الحرف، نتعامل معه كنص
                char = self.source[self.position]
                token = Token(TokenType.TEXT, char, self.line, self.column)
                self.tokens.append(token)
                self.position += 1
                self.column += 1
        
        self.tokens.append(Token(TokenType.EOF, "", self.line, self.column))
        return self.tokens

class ASTNode:
    def __init__(self, node_type: str, line: int):
        self.node_type = node_type
        self.line = line
        self.children = []
        self.name = f"{node_type}_Node"
        self.id = str(uuid.uuid4())[:8]
    
    def add_child(self, child):
        self.children.append(child)
    
    def accept(self, visitor):
        return visitor.visit(self)
    
    def to_dict(self):
        children_data = []
        for child in self.children:
            if hasattr(child, 'to_dict'):
                children_data.append(child.to_dict())
            else:
                children_data.append(str(child))
        props = self._get_properties()
        for key, value in props.items():
            try:
                json.dumps(value)
            except:
                props[key] = str(value)
        return {
            'type': self.node_type,
            'name': self.name,
            'id': self.id,
            'line': self.line,
            'children': children_data,
            'properties': props
        }
    
    def _get_properties(self):
        props = {}
        for attr in dir(self):
            if not attr.startswith('_') and attr not in ['node_type', 'line', 'children', 'name', 'id',
                                                         'to_dict', 'accept', 'add_child', '_get_properties']:
                value = getattr(self, attr)
                if not callable(value):
                    props[attr] = value
        return props
    
    def __str__(self):
        return f"{self.name} (Line: {self.line})"

class HTMLNode(ASTNode):
    def __init__(self, tag: str, line: int, is_closing: bool = False):
        super().__init__("HTML", line)
        self.tag = tag
        self.attributes = {}
        self.is_closing = is_closing
        self.name = f"HTML_{'closing_' if is_closing else ''}{tag}_Node"
    
    def add_attribute(self, name: str, value: str):
        self.attributes[name] = value
    
    def _get_properties(self):
        props = super()._get_properties()
        props['attributes'] = self.attributes
        props['tag'] = self.tag
        props['is_closing'] = self.is_closing
        return props

class TextNode(ASTNode):
    def __init__(self, content: str, line: int):
        super().__init__("Text", line)
        self.content = content
        self.name = f"Text_Node"
    
    def _get_properties(self):
        props = super()._get_properties()
        if len(self.content) > 50:
            props['content_preview'] = self.content[:50] + "..."
        else:
            props['content_preview'] = self.content
        props['content'] = self.content
        props['length'] = len(self.content)
        return props

class ExpressionNode(ASTNode):
    def __init__(self, line: int):
        super().__init__("Expression", line)
        self.name = "Expression_Node"

class VariableNode(ASTNode):
    def __init__(self, name: str, line: int):
        super().__init__("Variable", line)
        self.var_name = name
        self.name = f"Variable_{name}_Node"
    
    def _get_properties(self):
        props = super()._get_properties()
        props['var_name'] = self.var_name
        return props

class LiteralNode(ASTNode):
    def __init__(self, value: Any, line: int):
        super().__init__("Literal", line)
        self.value = value
        self.value_type = type(value).__name__
        self.name = f"Literal_{self.value_type}_Node"
    
    def _get_properties(self):
        props = super()._get_properties()
        props['value'] = self.value
        props['value_type'] = self.value_type
        return props

class BinaryOpNode(ASTNode):
    def __init__(self, op: str, line: int):
        super().__init__("BinaryOp", line)
        self.operator = op
        self.name = f"BinaryOp_{op}_Node"
    
    def _get_properties(self):
        props = super()._get_properties()
        props['operator'] = self.operator
        return props

class FilterNode(ASTNode):
    def __init__(self, filter_name: str, line: int):
        super().__init__("Filter", line)
        self.filter_name = filter_name
        self.name = f"Filter_{filter_name}_Node"
        self.arguments = []
    
    def _get_properties(self):
        props = super()._get_properties()
        props['filter_name'] = self.filter_name
        return props

class IfNode(ASTNode):
    def __init__(self, line: int):
        super().__init__("If", line)
        self.name = "If_Node"

class ForNode(ASTNode):
    def __init__(self, line: int):
        super().__init__("For", line)
        self.name = "For_Node"

class SetNode(ASTNode):
    def __init__(self, line: int):
        super().__init__("Set", line)
        self.name = "Set_Node"

class RootNode(ASTNode):
    def __init__(self, line: int):
        super().__init__("Root", line)
        self.name = "Root_Node"

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.position = 0
        self.current_token = tokens[0] if tokens else Token(TokenType.EOF, "", 1, 1)
        self.html_stack = []  # لتتبع الـ HTML tags المفتوحة
    
    def advance(self):
        self.position += 1
        if self.position < len(self.tokens):
            self.current_token = self.tokens[self.position]
    
    def peek(self) -> Optional[Token]:
        if self.position + 1 < len(self.tokens):
            return self.tokens[self.position + 1]
        return None
    
    def consume(self, expected_type: TokenType) -> Token:
        if self.current_token.type == expected_type:
            token = self.current_token
            self.advance()
            return token
        raise SyntaxError(
            f"Expected {expected_type} but got {self.current_token.type} on line {self.current_token.line}"
        )
    
    def parse(self) -> ASTNode:
        root = RootNode(line=1)
        while self.current_token.type != TokenType.EOF:
            if self.current_token.type == TokenType.TAG_OPEN:
                node = self.parse_html()
                root.add_child(node)
            elif self.current_token.type == TokenType.STMT_OPEN:
                node = self.parse_statement()
                root.add_child(node)
            elif self.current_token.type == TokenType.EXPR_OPEN:
                node = self.parse_expression()
                root.add_child(node)
            else:
                node = self.parse_text()
                root.add_child(node)
        return root
    
    def parse_html(self) -> HTMLNode:
        line = self.current_token.line
        self.consume(TokenType.TAG_OPEN)
        
        # التحقق مما إذا كانت علامة إغلاق
        is_closing = False
        if self.current_token.type == TokenType.SLASH:
            is_closing = True
            self.consume(TokenType.SLASH)
            if self.current_token.type != TokenType.IDENTIFIER:
                raise SyntaxError(f"Expected tag name after /, got {self.current_token.type} on line {line}")
        
        tag_name = self.consume(TokenType.IDENTIFIER).value
        
        # إنشاء العقدة مع تحديد ما إذا كانت إغلاق أم لا
        html_node = HTMLNode(tag_name, line, is_closing=is_closing)
        
        # إذا كانت علامة فتح، نضيفها للمكدس
        if not is_closing:
            self.html_stack.append(tag_name)
        
        # إذا كانت علامة إغلاق، نتحقق من المطابقة
        if is_closing:
            if not self.html_stack:
                raise SyntaxError(f"Closing tag </{tag_name}> without opening tag on line {line}")
            last_tag = self.html_stack.pop()
            if last_tag != tag_name:
                raise SyntaxError(f"Mismatched tags: <{last_tag}> closed with </{tag_name}> on line {line}")
        
        # تحليل السمات (لعلامات الفتح فقط)
        if not is_closing:
            while (self.current_token.type not in [TokenType.TAG_CLOSE, TokenType.TAG_SELF_CLOSE, TokenType.EOF]):
                if self.current_token.type == TokenType.IDENTIFIER:
                    attr_name = self.current_token.value
                    self.advance()
                    if self.current_token.type == TokenType.ASSIGN:
                        self.advance()
                        if self.current_token.type == TokenType.STRING:
                            attr_value = self.current_token.value.strip('"\'')
                            html_node.add_attribute(attr_name, attr_value)
                            self.advance()
                self.advance()
        
        # التعامل مع نهاية العلامة
        if self.current_token.type == TokenType.TAG_SELF_CLOSE:
            self.consume(TokenType.TAG_SELF_CLOSE)
            # إذا كانت علامة ذاتية الإغلاق، لا نضيفها للمكدس ولا نزيلها
        else:
            self.consume(TokenType.TAG_CLOSE)
        
        return html_node
    
    def parse_text(self) -> TextNode:
        line = self.current_token.line
        content = self.current_token.value
        self.advance()
        return TextNode(content, line)
    
    def parse_expression(self) -> ExpressionNode:
        line = self.current_token.line
        self.consume(TokenType.EXPR_OPEN)
        expr_node = ExpressionNode(line)
        expr_content = self.parse_expression_content()
        expr_node.add_child(expr_content)
        self.consume(TokenType.EXPR_CLOSE)
        return expr_node
    
    def parse_expression_content(self) -> ASTNode:
        line = self.current_token.line
        base_node = self.parse_base_expression()
        
        # التعامل مع الفلاتر
        while self.current_token.type == TokenType.PIPE:
            self.advance()
            if self.current_token.type == TokenType.IDENTIFIER:
                filter_name = self.current_token.value
                self.advance()
                filter_node = FilterNode(filter_name, line)
                filter_node.add_child(base_node)
                if self.current_token.type == TokenType.L_PAREN:
                    self.advance()
                    if self.current_token.type != TokenType.R_PAREN:
                        arg = self.parse_expression_content()
                        filter_node.add_child(arg)
                    self.consume(TokenType.R_PAREN)
                base_node = filter_node
        
        # التعامل مع العمليات الثنائية (بما فيها القسمة)
        if self.current_token.type == TokenType.OPERATOR:
            op = self.current_token.value
            self.advance()
            binary_node = BinaryOpNode(op, line)
            binary_node.add_child(base_node)
            right_side = self.parse_expression_content()
            binary_node.add_child(right_side)
            return binary_node
        
        return base_node
    
    def parse_base_expression(self) -> ASTNode:
        line = self.current_token.line
        
        # التعامل مع الأقواس
        if self.current_token.type == TokenType.L_PAREN:
            self.advance()
            expr_node = self.parse_expression_content()
            self.consume(TokenType.R_PAREN)
            return expr_node
        
        if self.current_token.type == TokenType.IDENTIFIER:
            var_name = self.current_token.value
            self.advance()
            if self.current_token.type == TokenType.DOT:
                self.advance()
                if self.current_token.type == TokenType.IDENTIFIER:
                    attr_name = self.current_token.value
                    self.advance()
                    composite_var = VariableNode(f"{var_name}.{attr_name}", line)
                    return composite_var
            return VariableNode(var_name, line)
        elif self.current_token.type == TokenType.NUMBER:
            value = float(self.current_token.value) if '.' in self.current_token.value else int(self.current_token.value)
            self.advance()
            return LiteralNode(value, line)
        elif self.current_token.type == TokenType.STRING:
            value = self.current_token.value.strip('"\'')
            self.advance()
            return LiteralNode(value, line)
        elif self.current_token.type == TokenType.BOOL:
            value = self.current_token.value == 'True'
            self.advance()
            return LiteralNode(value, line)
        return TextNode("", line)
    
    def parse_statement(self) -> ASTNode:
        line = self.current_token.line
        self.consume(TokenType.STMT_OPEN)
        
        if self.current_token.type == TokenType.IF:
            return self.parse_if_statement(line)
        elif self.current_token.type == TokenType.FOR:
            return self.parse_for_statement(line)
        elif self.current_token.type == TokenType.SET:
            return self.parse_set_statement(line)
        elif self.current_token.type in [TokenType.ENDIF, TokenType.ELSE, TokenType.ELIF, TokenType.ENDFOR]:
            stmt_type = self.current_token.type.name.lower()
            self.advance()
            self.consume(TokenType.STMT_CLOSE)
            return ASTNode(f"End{stmt_type.capitalize()}", line)
        
        self.consume(TokenType.STMT_CLOSE)
        return ASTNode("Statement", line)
    
    def parse_if_statement(self, line: int) -> IfNode:
        self.consume(TokenType.IF)
        if_node = IfNode(line)
        condition = self.parse_expression_content()
        if_node.add_child(condition)
        self.consume(TokenType.STMT_CLOSE)
        return if_node
    
    def parse_for_statement(self, line: int) -> ForNode:
        self.consume(TokenType.FOR)
        for_node = ForNode(line)
        
        if self.current_token.type == TokenType.IDENTIFIER:
            loop_var = VariableNode(self.current_token.value, line)
            for_node.add_child(loop_var)
            self.advance()
        
        self.consume(TokenType.IN)
        
        if self.current_token.type == TokenType.IDENTIFIER:
            iter_var = VariableNode(self.current_token.value, line)
            for_node.add_child(iter_var)
            self.advance()
        
        self.consume(TokenType.STMT_CLOSE)
        return for_node
    
    def parse_set_statement(self, line: int) -> SetNode:
        self.consume(TokenType.SET)
        set_node = SetNode(line)
        
        if self.current_token.type == TokenType.IDENTIFIER:
            var_name = VariableNode(self.current_token.value, line)
            set_node.add_child(var_name)
            self.advance()
        
        if self.current_token.type == TokenType.ASSIGN:
            self.advance()
            value = self.parse_expression_content()
            set_node.add_child(value)
        
        self.consume(TokenType.STMT_CLOSE)
        return set_node

class SymbolTable:
    def __init__(self):
        self.symbols = {}
        self.scopes = [{}]
        self.current_scope = 0
    
    def enter_scope(self):
        self.scopes.append({})
        self.current_scope += 1
    
    def exit_scope(self):
        if self.current_scope > 0:
            self.scopes.pop()
            self.current_scope -= 1
    
    def add_symbol(self, name: str, symbol_type: str, value=None, line=None):
        symbol = {
            'name': name,
            'type': symbol_type,
            'value': value,
            'line': line,
            'scope': self.current_scope
        }
        if name in self.scopes[self.current_scope]:
            print(f"Warning: '{name}' already defined")
        self.scopes[self.current_scope][name] = symbol
        self.symbols[name] = symbol
        return symbol
    
    def get_symbol(self, name: str):
        for i in range(self.current_scope, -1, -1):
            if name in self.scopes[i]:
                return self.scopes[i][name]
        return None
    
    def update_symbol(self, name: str, value):
        symbol = self.get_symbol(name)
        if symbol:
            for i in range(self.current_scope, -1, -1):
                if name in self.scopes[i]:
                    self.scopes[i][name]['value'] = value
                    self.symbols[name]['value'] = value
                    return True
        return False
    
    def to_dict(self):
        result = {
            'scopes': [],
            'all_symbols': list(self.symbols.values())
        }
        for scope_idx, scope in enumerate(self.scopes):
            scope_data = {
                'id': scope_idx,
                'symbols': list(scope.values())
            }
            result['scopes'].append(scope_data)
        return result

class ASTDiagramGenerator:
    @staticmethod
    def generate_tree_diagram(node, show_ids=False, max_depth=10):
        lines = []
        ASTDiagramGenerator._add_tree_node(lines, node, "", "", show_ids, 0, max_depth)
        return "\n".join(lines)
    
    @staticmethod
    def _add_tree_node(lines, node, prefix, children_prefix, show_ids, depth, max_depth):
        if depth > max_depth:
            lines.append(prefix + "└── ... (hidden due to depth)")
            return
        if not node:
            return
        node_info = ASTDiagramGenerator._get_node_label(node, show_ids)
        lines.append(prefix + node_info)
        children = getattr(node, 'children', [])
        for i, child in enumerate(children):
            is_last = (i == len(children) - 1)
            if hasattr(child, 'children'):
                new_prefix = children_prefix + ("└── " if is_last else "├── ")
                new_children_prefix = children_prefix + ("    " if is_last else "│   ")
                ASTDiagramGenerator._add_tree_node(
                    lines, child, new_prefix, new_children_prefix, show_ids, depth + 1, max_depth
                )
            else:
                child_prefix = children_prefix + ("└── " if is_last else "├── ")
                lines.append(child_prefix + str(child)[:50])
    
    @staticmethod
    def _get_node_label(node, show_ids):
        node_type = getattr(node, 'node_type', 'Unknown')
        line = getattr(node, 'line', 0)
        node_id = getattr(node, 'id', '')[:4] if show_ids else ''
        icons = {
            'HTML': '',
            'Text': '',
            'Expression': '',
            'Variable': '',
            'Literal': '',
            'BinaryOp': '',
            'Filter': '',
            'If': '',
            'For': '',
            'Set': '',
            'Root': ''
        }
        icon = icons.get(node_type, '❓')
        extra_info = ""
        if node_type == 'HTML':
            tag = getattr(node, 'tag', '')
            is_closing = getattr(node, 'is_closing', False)
            if is_closing:
                extra_info = f" </{tag}>"
            else:
                extra_info = f" <{tag}>"
        elif node_type == 'Text':
            content = getattr(node, 'content', '')
            preview = content[:20] + "..." if len(content) > 20 else content
            extra_info = f" '{preview}'"
        elif node_type == 'Variable':
            var_name = getattr(node, 'var_name', '')
            extra_info = f" {var_name}"
        elif node_type == 'Literal':
            value = getattr(node, 'value', '')
            extra_info = f" {value}"
        elif node_type == 'BinaryOp':
            operator = getattr(node, 'operator', '')
            extra_info = f" {operator}"
        elif node_type == 'Filter':
            filter_name = getattr(node, 'filter_name', '')
            extra_info = f" {filter_name}"
        id_str = f" [{node_id}]" if node_id else ""
        line_str = f" (Line {line})" if line > 0 else ""
        return f"{icon} {node_type}{extra_info}{id_str}{line_str}"
    
    @staticmethod
    def generate_box_diagram(node):
        if not node:
            return {"nodes": [], "edges": []}
        nodes = []
        edges = []
        ASTDiagramGenerator._traverse_for_box_diagram(node, nodes, edges, None)
        return {
            "nodes": nodes,
            "edges": edges,
            "metadata": {
                "total_nodes": len(nodes),
                "total_edges": len(edges)
            }
        }
    
    @staticmethod
    def _traverse_for_box_diagram(node, nodes, edges, parent_id=None):
        if not node:
            return
        node_id = getattr(node, 'id', str(uuid.uuid4())[:8])
        node_type = getattr(node, 'node_type', 'Unknown')
        line = getattr(node, 'line', 0)
        colors = {
            'HTML': '#4CAF50',
            'Text': '#2196F3',
            'Expression': '#FF9800',
            'Variable': '#9C27B0',
            'Literal': '#F44336',
            'BinaryOp': '#607D8B',
            'Filter': '#00BCD4',
            'If': '#FF5722',
            'For': '#795548',
            'Set': '#3F51B5',
            'Root': '#000000'
        }
        node_data = {
            "id": node_id,
            "label": ASTDiagramGenerator._get_box_label(node),
            "type": node_type,
            "line": line,
            "color": colors.get(node_type, '#777777'),
            "properties": ASTDiagramGenerator._get_node_properties(node)
        }
        nodes.append(node_data)
        if parent_id:
            edges.append({
                "from": parent_id,
                "to": node_id,
                "label": f"child",
                "arrows": "to"
            })
        children = getattr(node, 'children', [])
        for child in children:
            if hasattr(child, 'children'):
                ASTDiagramGenerator._traverse_for_box_diagram(child, nodes, edges, node_id)
            else:
                child_id = str(uuid.uuid4())[:8]
                nodes.append({
                    "id": child_id,
                    "label": str(child)[:30],
                    "type": "Leaf",
                    "color": "#AAAAAA",
                    "properties": {"value": str(child)}
                })
                edges.append({
                    "from": node_id,
                    "to": child_id,
                    "label": "value",
                    "arrows": "to"
                })
    
    @staticmethod
    def _get_box_label(node):
        node_type = getattr(node, 'node_type', 'Unknown')
        if node_type == 'HTML':
            tag = getattr(node, 'tag', '')
            is_closing = getattr(node, 'is_closing', False)
            if is_closing:
                return f" HTML\n</{tag}>"
            else:
                return f" HTML\n<{tag}>"
        elif node_type == 'Text':
            content = getattr(node, 'content', '')
            preview = content[:15] + "..." if len(content) > 15 else content
            return f" Text\n'{preview}'"
        elif node_type == 'Variable':
            var_name = getattr(node, 'var_name', '')
            return f" Variable\n{var_name}"
        elif node_type == 'Literal':
            value = getattr(node, 'value', '')
            return f" Value\n{value}"
        elif node_type == 'BinaryOp':
            operator = getattr(node, 'operator', '')
            return f" Operation\n{operator}"
        elif node_type == 'Filter':
            filter_name = getattr(node, 'filter_name', '')
            return f" Filter\n{filter_name}"
        elif node_type == 'Expression':
            return f" Expression"
        elif node_type == 'If':
            return f" IF Condition"
        elif node_type == 'For':
            return f"FOR Loop"
        elif node_type == 'Set':
            return f" SET Assignment"
        elif node_type == 'Root':
            return f" Root"
        else:
            return f" {node_type}"
    
    @staticmethod
    def _get_node_properties(node):
        props = {}
        if hasattr(node, 'attributes'):
            props['attributes'] = getattr(node, 'attributes', {})
        if hasattr(node, 'tag'):
            props['tag'] = getattr(node, 'tag', '')
        if hasattr(node, 'is_closing'):
            props['is_closing'] = getattr(node, 'is_closing', False)
        if hasattr(node, 'var_name'):
            props['var_name'] = getattr(node, 'var_name', '')
        if hasattr(node, 'value'):
            props['value'] = getattr(node, 'value', '')
        if hasattr(node, 'operator'):
            props['operator'] = getattr(node, 'operator', '')
        if hasattr(node, 'filter_name'):
            props['filter_name'] = getattr(node, 'filter_name', '')
        if hasattr(node, 'content'):
            content = getattr(node, 'content', '')
            if len(content) > 30:
                props['content'] = content[:30] + "..."
            else:
                props['content'] = content
        return props
    
    @staticmethod
    def generate_summary_diagram(ast_root):
        if not ast_root:
            return ""
        summary_lines = []
        ASTDiagramGenerator._collect_summary(ast_root, summary_lines, 0)
        diagram = []
        max_depth = max(line[0] for line in summary_lines) if summary_lines else 0
        for depth, node_type, count in summary_lines:
            indent = "  " * depth
            bar_length = int((count / max(summary_lines, key=lambda x: x[2])[2]) * 20) if summary_lines else 0
            bar = "█" * bar_length + "░" * (20 - bar_length)
            diagram.append(f"{indent}{node_type}: {bar} {count}")
        return "\n".join(diagram)
    
    @staticmethod
    def _collect_summary(node, summary_lines, depth):
        if not node:
            return
        node_type = getattr(node, 'node_type', 'Unknown')
        found = False
        for i, (d, nt, count) in enumerate(summary_lines):
            if d == depth and nt == node_type:
                summary_lines[i] = (d, nt, count + 1)
                found = True
                break
        if not found:
            summary_lines.append((depth, node_type, 1))
        children = getattr(node, 'children', [])
        for child in children:
            if hasattr(child, 'children'):
                ASTDiagramGenerator._collect_summary(child, summary_lines, depth + 1)

class TreePrinter:
    def __init__(self, show_line_numbers=True):
        self.show_line_numbers = show_line_numbers
        self.node_counts = {}
        self.show_ids = False
    
    def print_tree(self, node, indent="", is_last=True):
        if not node:
            return
        prefix = indent
        if indent:
            prefix = prefix[:-2] + ("└── " if is_last else "├── ")
        node_info = self._get_node_info(node)
        print(f"{prefix}{node_info}")
        node_type = getattr(node, 'node_type', 'Unknown')
        self.node_counts[node_type] = self.node_counts.get(node_type, 0) + 1
        new_indent = indent + ("    " if is_last else "│   ")
        children = getattr(node, 'children', [])
        child_count = len(children)
        for i, child in enumerate(children):
            is_last_child = (i == child_count - 1)
            self.print_tree(child, new_indent, is_last_child)
    
    def _get_node_info(self, node):
        if not hasattr(node, 'node_type'):
            return str(node)
        node_type = getattr(node, 'node_type', 'Unknown')
        line_info = f" [Line: {node.line}]" if self.show_line_numbers and hasattr(node, 'line') else ""
        id_info = f" [{node.id[:4]}]" if self.show_ids and hasattr(node, 'id') else ""
        if node_type == 'HTML':
            tag = getattr(node, 'tag', '')
            is_closing = getattr(node, 'is_closing', False)
            if is_closing:
                tag_str = f"</{tag}>"
            else:
                attrs = getattr(node, 'attributes', {})
                attrs_str = f" ({len(attrs)} attributes)" if attrs else ""
                tag_str = f"<{tag}>{attrs_str}"
            return f" HTML {tag_str}{id_info}{line_info}"
        elif node_type == 'Text':
            content = getattr(node, 'content', '')
            preview = content[:30] + "..." if len(content) > 30 else content
            return f" Text: '{preview}'{id_info}{line_info}"
        elif node_type == 'Variable':
            var_name = getattr(node, 'var_name', '')
            return f" Variable: {var_name}{id_info}{line_info}"
        elif node_type == 'Literal':
            value = getattr(node, 'value', '')
            value_type = getattr(node, 'value_type', '')
            return f" Value ({value_type}): {value}{id_info}{line_info}"
        elif node_type == 'BinaryOp':
            operator = getattr(node, 'operator', '')
            return f" Operation: {operator}{id_info}{line_info}"
        elif node_type == 'Filter':
            filter_name = getattr(node, 'filter_name', '')
            return f" Filter: {filter_name}{id_info}{line_info}"
        elif node_type == 'Expression':
            return f" Expression{{...}}{id_info}{line_info}"
        elif node_type == 'If':
            return f" IF Condition{id_info}{line_info}"
        elif node_type == 'For':
            return f" FOR Loop{id_info}{line_info}"
        elif node_type == 'Set':
            return f" SET Assignment{id_info}{line_info}"
        elif node_type == 'Root':
            child_count = len(getattr(node, 'children', []))
            return f" Root ({child_count} children){id_info}{line_info}"
        else:
            return f" {node_type}{id_info}{line_info}"
    
    def print_summary(self):
        print("\n" + "="*80)
        print("📊 AST Tree Summary")
        print("="*80)
        if not self.node_counts:
            print("No nodes to print summary")
            return
        print("\n📈 Node Statistics:")
        print("-" * 40)
        sorted_counts = sorted(self.node_counts.items(), key=lambda x: x[1], reverse=True)
        for node_type, count in sorted_counts:
            print(f"  {node_type}: {count}")
        total_nodes = sum(self.node_counts.values())
        print(f"\n  Total: {total_nodes} nodes")
        print("="*80)

class VariableCounter:
    def __init__(self):
        self.variables = set()
        self.filters = set()
    
    def visit(self, node):
        method_name = f'visit_{node.node_type}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)
    
    def generic_visit(self, node):
        for child in node.children:
            if hasattr(child, 'accept'):
                child.accept(self)
            elif hasattr(child, 'children'):
                self.generic_visit(child)
    
    def visit_Variable(self, node):
        self.variables.add(node.var_name)
        return self.generic_visit(node)
    
    def visit_Filter(self, node):
        self.filters.add(node.filter_name)
        return self.generic_visit(node)
    
    def visit_Expression(self, node):
        return self.generic_visit(node)
    
    def visit_If(self, node):
        return self.generic_visit(node)
    
    def visit_For(self, node):
        return self.generic_visit(node)
    
    def visit_Set(self, node):
        return self.generic_visit(node)

class TemplateProcessor:
    @staticmethod
    def process_template(template_source: str, print_ast=False, generate_diagrams=True) -> dict:
        try:
            lexer = Lexer(template_source)
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            ast_root = parser.parse()
            variable_counter = VariableCounter()
            ast_root.accept(variable_counter)
            actual_variables = list(variable_counter.variables)
            actual_filters = list(variable_counter.filters)
            if print_ast:
                print("\n" + "="*80)
                print("🌳 AST Tree (Printed in Terminal)")
                print("="*80)
                printer = TreePrinter(show_line_numbers=True)
                printer.print_tree(ast_root)
                printer.print_summary()
                if actual_variables:
                    print("\n🔍 Variables found in template:")
                    print("-" * 40)
                    for var in actual_variables:
                        print(f"  • {var}")
                if actual_filters:
                    print("\n🔧 Filters found in template:")
                    print("-" * 40)
                    for filt in actual_filters:
                        print(f"  • {filt}")
                print("\n🔤 First 20 Tokens:")
                print("-" * 40)
                for i, token in enumerate(tokens[:20]):
                    print(f"  {i+1:2d}. {token}")
                print("="*80)
            tree_diagram = ""
            box_diagram = {}
            summary_diagram = ""
            if generate_diagrams:
                tree_diagram = ASTDiagramGenerator.generate_tree_diagram(ast_root, show_ids=True)
                box_diagram = ASTDiagramGenerator.generate_box_diagram(ast_root)
                summary_diagram = ASTDiagramGenerator.generate_summary_diagram(ast_root)
                if print_ast:
                    print("\n📊 AST Tree Diagram:")
                    print("="*80)
                    print(tree_diagram)
                    print("="*80)
                    print("\n📈 Tree Summary Diagram:")
                    print("="*80)
                    print(summary_diagram)
                    print("="*80)
            symbol_table = SymbolTable()
            symbol_table.enter_scope()
            for var_name in actual_variables:
                value = None
                if 'title' in var_name.lower():
                    value = 'My Page'
                elif 'user' in var_name.lower() and 'name' in var_name.lower():
                    value = 'Mohammed'
                elif 'logged' in var_name.lower():
                    value = True
                elif 'product' in var_name.lower() and 's' in var_name.lower():
                    value = [
                        {'name': 'Product 1', 'price': 100},
                        {'name': 'Product 2', 'price': 200},
                        {'name': 'Product 3', 'price': 150}
                    ]
                elif 'price' in var_name.lower():
                    value = 100.0
                elif 'name' in var_name.lower():
                    value = 'Sample Name'
                elif 'total' in var_name.lower() and 'price' in var_name.lower():
                    value = 450.0
                symbol_table.add_symbol(var_name, 'variable', value, 1)
            for filter_name in actual_filters:
                symbol_table.add_symbol(filter_name, 'filter', f'Filter: {filter_name}', 1)
            return {
                'success': True,
                'tokens': [token.to_dict() for token in tokens],
                'ast': ast_root.to_dict(),
                'symbol_table': symbol_table.to_dict(),
                'token_count': len(tokens),
                'ast_node_count': TemplateProcessor._count_ast_nodes(ast_root),
                'variables_count': len(actual_variables),
                'filters_count': len(actual_filters),
                'variables_found': actual_variables,
                'filters_found': actual_filters,
                'diagrams': {
                    'tree_diagram': tree_diagram,
                    'box_diagram': box_diagram,
                    'summary_diagram': summary_diagram
                },
                'lexer_debug': TemplateProcessor._debug_lexer(tokens[:20])
            }
        except Exception as e:
            import traceback
            return {
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc(),
                'tokens': [],
                'ast': {},
                'symbol_table': {},
                'variables_count': 0,
                'filters_count': 0,
                'variables_found': [],
                'filters_found': [],
                'diagrams': {
                    'tree_diagram': '',
                    'box_diagram': {},
                    'summary_diagram': ''
                }
            }
    
    @staticmethod
    def _count_ast_nodes(node):
        count = 1
        for child in node.children:
            if hasattr(child, 'children'):
                count += TemplateProcessor._count_ast_nodes(child)
            else:
                count += 1
        return count
    
    @staticmethod
    def _debug_lexer(tokens):
        return [str(token) for token in tokens]

class ProductManager:
    def __init__(self):
        self.products = []
        self.load_sample_products()
    
    def load_sample_products(self):
        sample_products = [
            {
                'id': str(uuid.uuid4()),
                'name': 'Dell Laptop',
                'price': 3500.00,
                'description': 'Powerful laptop for work and study',
                'category': 'Electronics',
                'stock': 15,
                'rating': 4.5,
                'image_url': 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400',
                'created_at': '2024-01-15'
            },
            {
                'id': str(uuid.uuid4()),
                'name': 'Samsung Phone',
                'price': 2500.00,
                'description': 'Smartphone with 6.5 inch screen',
                'category': 'Electronics',
                'stock': 25,
                'rating': 4.3,
                'image_url': 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400',
                'created_at': '2024-01-10'
            },
            {
                'id': str(uuid.uuid4()),
                'name': 'Bluetooth Headphones',
                'price': 300.00,
                'description': 'High quality wireless headphones',
                'category': 'Accessories',
                'stock': 50,
                'rating': 4.7,
                'image_url': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400',
                'created_at': '2024-01-05'
            },
            {
                'id': str(uuid.uuid4()),
                'name': 'Smart Watch',
                'price': 800.00,
                'description': 'Smart watch for fitness tracking',
                'category': 'Electronics',
                'stock': 30,
                'rating': 4.4,
                'image_url': 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400',
                'created_at': '2024-01-20'
            },
            {
                'id': str(uuid.uuid4()),
                'name': 'Canon Camera',
                'price': 4500.00,
                'description': 'Professional camera for photography',
                'category': 'Electronics',
                'stock': 10,
                'rating': 4.8,
                'image_url': 'https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=400',
                'created_at': '2024-01-18'
            },
            {
                'id': str(uuid.uuid4()),
                'name': 'Computer Bag',
                'price': 150.00,
                'description': 'Comfortable bag for laptop',
                'category': 'Accessories',
                'stock': 40,
                'rating': 4.2,
                'image_url': 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=400',
                'created_at': '2024-01-12'
            }
        ]
        self.products = sample_products
    
    def get_all_products(self):
        return self.products
    
    def get_product_by_id(self, product_id):
        for product in self.products:
            if product['id'] == product_id:
                return product
        return None
    
    def add_product(self, product_data):
        product = {
            'id': str(uuid.uuid4()),
            'name': product_data.get('name', 'New Product'),
            'price': float(product_data.get('price', 0)),
            'description': product_data.get('description', ''),
            'category': product_data.get('category', 'General'),
            'stock': int(product_data.get('stock', 0)),
            'rating': float(product_data.get('rating', 0)),
            'image_url': product_data.get('image_url', ''),
            'created_at': datetime.now().strftime('%Y-%m-%d')
        }
        self.products.append(product)
        return product
    
    def update_product(self, product_id, product_data):
        for i, product in enumerate(self.products):
            if product['id'] == product_id:
                for key, value in product_data.items():
                    if key in product:
                        if key in ['price', 'rating']:
                            product[key] = float(value)
                        elif key in ['stock']:
                            product[key] = int(value)
                        else:
                            product[key] = value
                return product
        return None
    
    def delete_product(self, product_id):
        self.products = [p for p in self.products if p['id'] != product_id]
        return True
    
    def search_products(self, query):
        query = query.lower()
        results = []
        for product in self.products:
            if (query in product['name'].lower() or 
                query in product['description'].lower() or 
                query in product['category'].lower()):
                results.append(product)
        return results
    
    def get_products_by_category(self, category):
        return [p for p in self.products if p['category'] == category]
    
    def get_categories(self):
        categories = set()
        for product in self.products:
            categories.add(product['category'])
        return list(categories)

def create_static_folders():
    folders = ['static', 'templates']
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"✓ Created folder: {folder}")

product_manager = ProductManager()

@app.route('/')
def home():
    html_content = '''
<!DOCTYPE html>
<html lang="en" dir="ltr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Template Analysis System + Product Management + AST Diagrams</title>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap" rel="stylesheet">
    <script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Cairo', sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #333; line-height: 1.6; min-height: 100vh; }
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        header { text-align: center; margin-bottom: 30px; padding: 20px; background: rgba(255, 255, 255, 0.95); border-radius: 15px; box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1); }
        h1 { color: #2d3748; font-size: 2.2rem; margin-bottom: 10px; }
        .subtitle { color: #718096; font-size: 1.1rem; }
        .navigation { display: flex; justify-content: center; gap: 15px; margin-bottom: 30px; flex-wrap: wrap; }
        .nav-btn { padding: 12px 25px; background: white; border: none; border-radius: 10px; cursor: pointer; font-size: 1rem; font-weight: 600; transition: all 0.3s ease; box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1); display: flex; align-items: center; gap: 8px; }
        .nav-btn:hover { transform: translateY(-3px); box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15); }
        .nav-btn.active { background: #667eea; color: white; }
        .main-content { display: none; background: rgba(255, 255, 255, 0.95); border-radius: 15px; padding: 25px; box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1); margin-bottom: 20px; }
        .main-content.active { display: block; }
        .controls { display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }
        .btn { background: #667eea; color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; font-size: 1rem; transition: all 0.3s ease; display: flex; align-items: center; gap: 8px; }
        .btn:hover { background: #5a67d8; transform: translateY(-2px); }
        .btn-primary { background: #48bb78; }
        .btn-primary:hover { background: #38a169; }
        .btn-secondary { background: #e53e3e; }
        .btn-secondary:hover { background: #c53030; }
        .btn-tertiary { background: #805ad5; }
        .btn-tertiary:hover { background: #6b46c1; }
        textarea { width: 100%; min-height: 200px; padding: 15px; border: 2px solid #e2e8f0; border-radius: 10px; font-family: 'Cairo', monospace; font-size: 1rem; resize: vertical; background: #f7fafc; margin-bottom: 15px; }
        textarea:focus { outline: none; border-color: #667eea; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin: 20px 0; }
        .stat-card { background: white; padding: 15px; border-radius: 10px; text-align: center; box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05); }
        .stat-value { font-size: 1.8rem; font-weight: 700; color: #667eea; margin-bottom: 5px; }
        .stat-label { color: #718096; font-size: 0.9rem; }
        .results { display: grid; grid-template-columns: 1fr; gap: 20px; margin-top: 20px; }
        .section { background: white; border-radius: 10px; padding: 20px; box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05); }
        .section h3 { color: #2d3748; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 2px solid #e2e8f0; display: flex; align-items: center; gap: 10px; }
        .tokens-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 10px; max-height: 300px; overflow-y: auto; padding: 10px; }
        .token { padding: 10px; background: #f7fafc; border-radius: 8px; border-right: 4px solid #667eea; font-size: 0.9rem; }
        .ast-tree { background: #f8f9fa; border-radius: 8px; padding: 15px; max-height: 400px; overflow-y: auto; font-family: monospace; font-size: 0.9rem; white-space: pre; }
        .ast-diagram { background: #1a202c; color: #cbd5e0; padding: 15px; border-radius: 10px; font-family: monospace; white-space: pre; max-height: 500px; overflow-y: auto; margin-top: 15px; }
        .tree-visualization { height: 600px; border: 2px solid #e2e8f0; border-radius: 10px; margin-top: 15px; }
        .loading { display: none; text-align: center; padding: 20px; }
        .spinner { width: 40px; height: 40px; border: 4px solid #e2e8f0; border-top: 4px solid #667eea; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 10px; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .terminal-note { background: #1a202c; color: #cbd5e0; padding: 15px; border-radius: 10px; margin-top: 20px; font-family: monospace; display: none; }
        .diagram-controls { display: flex; gap: 10px; margin-bottom: 15px; }
        .diagram-btn { padding: 8px 15px; background: #e2e8f0; border: none; border-radius: 6px; cursor: pointer; font-size: 0.9rem; }
        .diagram-btn.active { background: #667eea; color: white; }
        .summary-diagram { background: #f7fafc; padding: 15px; border-radius: 10px; font-family: monospace; white-space: pre; max-height: 300px; overflow-y: auto; }
        .products-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; margin-top: 20px; }
        .product-card { background: white; border-radius: 15px; overflow: hidden; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1); transition: transform 0.3s ease; }
        .product-card:hover { transform: translateY(-10px); }
        .product-image { width: 100%; height: 200px; object-fit: cover; }
        .product-info { padding: 20px; }
        .product-name { font-size: 1.3rem; font-weight: 600; color: #2d3748; margin-bottom: 10px; }
        .product-price { color: #48bb78; font-size: 1.4rem; font-weight: 700; margin-bottom: 10px; }
        .product-description { color: #718096; margin-bottom: 15px; font-size: 0.9rem; }
        .product-meta { display: flex; justify-content: space-between; font-size: 0.9rem; color: #a0aec0; }
        .form-container { background: white; border-radius: 15px; padding: 30px; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1); }
        .form-group { margin-bottom: 20px; }
        .form-label { display: block; margin-bottom: 8px; font-weight: 600; color: #2d3748; }
        .form-input { width: 100%; padding: 12px 15px; border: 2px solid #e2e8f0; border-radius: 8px; font-size: 1rem; font-family: 'Cairo', sans-serif; }
        .form-input:focus { outline: none; border-color: #667eea; }
        .search-section { background: white; border-radius: 15px; padding: 20px; margin-bottom: 20px; box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05); }
        .search-input { width: 100%; padding: 12px 15px; border: 2px solid #e2e8f0; border-radius: 8px; font-size: 1rem; margin-bottom: 15px; }
        .categories { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 10px; }
        .category-btn { padding: 8px 15px; background: #e2e8f0; border: none; border-radius: 20px; cursor: pointer; transition: all 0.3s ease; }
        .category-btn:hover { background: #667eea; color: white; }
        .category-btn.active { background: #667eea; color: white; }
        .product-details { background: white; border-radius: 15px; padding: 30px; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1); margin-top: 20px; }
        .details-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px; }
        .details-image { width: 100%; border-radius: 10px; }
        .details-info h4 { margin-bottom: 10px; color: #2d3748; }
        .details-info p { margin-bottom: 15px; color: #718096; }
        @media (max-width: 768px) {
            .container { padding: 10px; }
            .navigation { flex-direction: column; }
            .nav-btn { width: 100%; }
            .products-grid { grid-template-columns: 1fr; }
            .details-grid { grid-template-columns: 1fr; }
            .tree-visualization { height: 400px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🌳 Template Analysis System + Product Management + AST Diagrams</h1>
            <p class="subtitle">Jinja2 Template Analyzer with Division Operator Support</p>
        </header>
        <div class="navigation">
            <button class="nav-btn active" onclick="showSection('analyzer')">🔍 Template Analyzer</button>
            <button class="nav-btn" onclick="showSection('products')">🛍️ View Products</button>
            <button class="nav-btn" onclick="showSection('add-product')">➕ Add Product</button>
            <button class="nav-btn" onclick="showSection('product-analysis')">📊 Product Analysis</button>
            <button class="nav-btn" onclick="showSection('ast-diagrams')">🌳 AST Diagrams</button>
        </div>
        <div id="analyzer" class="main-content active">
            <div class="controls">
                <button class="btn" onclick="analyzeTemplate()">🔍 Analyze Template</button>
                <button class="btn btn-primary" onclick="analyzeAndPrintAST()">🖨️ Print AST in Terminal</button>
                <button class="btn btn-secondary" onclick="clearAll()">🗑️ Clear All</button>
            </div>
            <textarea id="templateInput" placeholder="Enter Jinja2 template here...">
<html>
<head>
    <title>Page {{ page_title }}</title>
</head>
<body>
    <h1>Hello {{ user_name }}!</h1>  
    {% if user_logged_in %}
        <p>✅ You are logged in!</p>
    {% else %}
        <p>⚠️ Please log in</p>
    {% endif %}
    
    <div>
        <p>Math Operations:</p>
        <p>Addition: {{ 10 + 5 }}</p>
        <p>Subtraction: {{ 20 - 8 }}</p>
        <p>Multiplication: {{ 6 * 7 }}</p>
        <p>Division: {{ 100 / 4 }}</p>
        <p>Complex: {{ (price * quantity) / discount }}</p>
    </div>
    
    <ul>
    {% for product in products %}
        <li>{{ product.name }} - {{ product.price|currency }} Syrian Pounds</li>
    {% endfor %}
    </ul>
    <p>Total: {{ products|length }} products</p>
    <p>Average Price: {{ total_price / products|length }}</p>
</body>
</html></textarea>
            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p>Analyzing template...</p>
            </div>
            <div class="terminal-note" id="terminalNote">✅ AST tree printed successfully in Terminal!</div>
            <div class="stats" id="statsContainer" style="display: none;">
                <div class="stat-card">
                    <div class="stat-value" id="tokenCount">0</div>
                    <div class="stat-label">Tokens Count</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="astNodes">0</div>
                    <div class="stat-label">AST Nodes</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="symbolsCount">0</div>
                    <div class="stat-label">Variables Found</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="filtersCount">0</div>
                    <div class="stat-label">Filters Found</div>
                </div>
            </div>
            <div class="results" id="resultsContainer" style="display: none;">
                <div class="section">
                    <h3>🔤 Extracted Tokens</h3>
                    <div class="tokens-grid" id="tokensList"></div>
                </div>
                <div class="section">
                    <h3>🌳 AST Tree</h3>
                    <pre class="ast-tree" id="astViewer"></pre>
                </div>
                <div class="section">
                    <h3>📋 Symbol Table</h3>
                    <div class="symbols-list" id="symbolsList"></div>
                </div>
            </div>
        </div>
        <div id="ast-diagrams" class="main-content">
            <div class="section">
                <h3>🌳 AST Tree Diagrams</h3>
                <p>Visualize AST tree in different ways to help understand template structure</p>
                <div class="diagram-controls">
                    <button class="diagram-btn active" onclick="showDiagram('tree')">📊 AST Tree</button>
                    <button class="diagram-btn" onclick="showDiagram('network')">🕸️ Diagram</button>
                    <button class="diagram-btn" onclick="showDiagram('summary')">📈 Statistical chart</button>
                </div>
                <div id="diagramTree" class="diagram-section">
                    <div class="ast-diagram" id="treeDiagram"></div>
                </div>
                <div id="diagramNetwork" class="diagram-section" style="display: none;">
                    <div class="tree-visualization" id="networkDiagram"></div>
                </div>
                <div id="diagramSummary" class="diagram-section" style="display: none;">
                    <div class="summary-diagram" id="summaryDiagram"></div>
                </div>
            </div>
        </div>
        <div id="products" class="main-content">
            <div class="search-section">
                <input type="text" id="productSearch" class="search-input" placeholder="🔍 Search for product..." onkeyup="searchProducts()">
                <div class="categories" id="categoriesList"></div>
            </div>
            <div class="products-grid" id="productsGrid"></div>
        </div>
        <div id="add-product" class="main-content">
            <div class="form-container">
                <h3 style="margin-bottom: 20px;">➕ Add New Product</h3>
                <div class="form-group">
                    <label class="form-label">Product Name</label>
                    <input type="text" id="productName" class="form-input" placeholder="Enter product name">
                </div>
                <div class="form-group">
                    <label class="form-label">Price (Syrian Pounds)</label>
                    <input type="number" id="productPrice" class="form-input" placeholder="Enter price">
                </div>
                <div class="form-group">
                    <label class="form-label">Description</label>
                    <textarea id="productDescription" class="form-input" rows="3" placeholder="Enter product description"></textarea>
                </div>
                <div class="form-group">
                    <label class="form-label">Category</label>
                    <select id="productCategory" class="form-input">
                        <option value="Electronics">Electronics</option>
                        <option value="Accessories">Accessories</option>
                        <option value="Clothing">Clothing</option>
                        <option value="Books">Books</option>
                        <option value="Other">Other</option>
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label">Available Quantity</label>
                    <input type="number" id="productStock" class="form-input" placeholder="Quantity">
                </div>
                <div class="form-group">
                    <label class="form-label">Rating (0-5)</label>
                    <input type="number" id="productRating" class="form-input" min="0" max="5" step="0.1" placeholder="0-5">
                </div>
                <div class="form-group">
                    <label class="form-label">Image URL (Optional)</label>
                    <input type="text" id="productImage" class="form-input" placeholder="https://example.com/image.jpg">
                </div>
                <div class="controls" style="margin-top: 30px;">
                    <button class="btn btn-primary" onclick="addNewProduct()">➕ Add Product</button>
                    <button class="btn" onclick="clearProductForm()">🗑️ Clear Form</button>
                </div>
                <div id="productMessage" style="margin-top: 20px;"></div>
            </div>
        </div>
        <div id="product-analysis" class="main-content">
            <div class="search-section">
                <h3>📊 Product Analysis</h3>
                <p>Analyze template to display product statistics</p>
            </div>
            <div class="section">
                <h3>📈 Product Analysis Template</h3>
                <textarea id="productAnalysisTemplate" class="form-input" rows="10">
<!DOCTYPE html>
<html>
<head>
    <title>Product Analysis</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .stat-box { background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0; }
        .chart { height: 300px; background: linear-gradient(90deg, #667eea, #764ba2); margin: 20px 0; }
    </style>
</head>
<body>
    <h1>📊 Product Analysis</h1>
    <div class="stat-box">
        <h3>General Statistics</h3>
        <p>Total Products: {{ total_products }}</p>
        <p>Average Price: {{ average_price|round(2) }} Syrian Pounds</p>
        <p>Total Stock: {{ total_stock }}</p>
        <p>Average Rating: {{ average_rating|round(2) }}</p>
    </div>
    <div class="stat-box">
        <h3>Distribution by Categories</h3>
        <ul>
        {% for category, count in category_distribution.items() %}
            <li>{{ category }}: {{ count }} products ({{ (count/total_products*100)|round(1) }}%)</li>
        {% endfor %}
        </ul>
    </div>
    <div class="stat-box">
        <h3>Most Expensive Products</h3>
        <ol>
        {% for product in expensive_products %}
            <li>{{ product.name }} - {{ product.price }} Syrian Pounds</li>
        {% endfor %}
        </ol>
    </div>
    <div class="stat-box">
        <h3>Highest Rated Products</h3>
        <ol>
        {% for product in top_rated_products %}
            <li>{{ product.name }} - {{ product.rating }} ⭐</li>
        {% endfor %}
        </ol>
    </div>
</body>
</html></textarea>
                <div class="controls" style="margin-top: 20px;">
                    <button class="btn btn-primary" onclick="analyzeProducts()">📊 Analyze and Show Results</button>
                </div>
                <div id="analysisResults" style="margin-top: 30px;"></div>
            </div>
        </div>
    </div>
    <script>
        let currentProducts = [];
        let currentASTData = null;
        let network = null;
        function showSection(sectionId) {
            document.querySelectorAll('.main-content').forEach(section => {
                section.classList.remove('active');
            });
            document.querySelectorAll('.nav-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            document.getElementById(sectionId).classList.add('active');
            event.target.classList.add('active');
            if (sectionId === 'products') {
                loadProducts();
            } else if (sectionId === 'product-analysis') {
                loadProductAnalysis();
            } else if (sectionId === 'ast-diagrams' && currentASTData) {
                displayDiagrams(currentASTData);
            }
        }
        async function analyzeTemplate() {
            const template = document.getElementById('templateInput').value;
            const loading = document.getElementById('loading');
            const results = document.getElementById('resultsContainer');
            const stats = document.getElementById('statsContainer');
            const terminalNote = document.getElementById('terminalNote');
            if (!template.trim()) {
                alert('⚠️ Please enter a template first');
                return;
            }
            loading.style.display = 'block';
            results.style.display = 'none';
            stats.style.display = 'none';
            terminalNote.style.display = 'none';
            try {
                const response = await fetch('/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        template: template, 
                        print_ast: false,
                        generate_diagrams: true 
                    })
                });
                const data = await response.json();
                if (data.success) {
                    currentASTData = data;
                    displayResults(data);
                    if (document.getElementById('ast-diagrams').classList.contains('active')) {
                        displayDiagrams(data);
                    }
                } else {
                    alert('❌ Analysis error: ' + data.error);
                }
            } catch (error) {
                alert('❌ Connection error: ' + error.message);
            } finally {
                loading.style.display = 'none';
            }
        }
        async function analyzeAndPrintAST() {
            const template = document.getElementById('templateInput').value;
            const loading = document.getElementById('loading');
            const terminalNote = document.getElementById('terminalNote');
            if (!template.trim()) {
                alert('⚠️ Please enter a template first');
                return;
            }
            loading.style.display = 'block';
            terminalNote.style.display = 'none';
            try {
                const response = await fetch('/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        template: template, 
                        print_ast: true,
                        generate_diagrams: true 
                    })
                });
                const data = await response.json();
                if (data.success) {
                    currentASTData = data;
                    displayResults(data);
                    terminalNote.style.display = 'block';
                    if (document.getElementById('ast-diagrams').classList.contains('active')) {
                        displayDiagrams(data);
                    }
                } else {
                    alert('❌ Analysis error: ' + data.error);
                }
            } catch (error) {
                alert('❌ Connection error: ' + error.message);
            } finally {
                loading.style.display = 'none';
            }
        }
        async function generateDiagrams() {
            const template = document.getElementById('templateInput').value;
            if (!template.trim()) {
                alert('⚠️ Please enter a template first');
                return;
            }
            document.querySelectorAll('.nav-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            document.querySelectorAll('.main-content').forEach(section => {
                section.classList.remove('active');
            });
            document.getElementById('ast-diagrams').classList.add('active');
            event.target.classList.add('active');
            if (!currentASTData) {
                await analyzeTemplate();
            } else {
                displayDiagrams(currentASTData);
            }
        }
        function displayResults(data) {
            document.getElementById('tokenCount').textContent = data.token_count;
            document.getElementById('astNodes').textContent = data.ast_node_count;
            document.getElementById('symbolsCount').textContent = data.variables_count;
            document.getElementById('filtersCount').textContent = data.filters_count || 0;
            displayTokens(data.tokens);
            displayAST(data.ast);
            displaySymbols(data.symbol_table);
            document.getElementById('resultsContainer').style.display = 'grid';
            document.getElementById('statsContainer').style.display = 'grid';
            const variablesSection = document.createElement('div');
            variablesSection.className = 'section';
            variablesSection.innerHTML = `
                <h3>🔍 Variables Found in Template (${data.variables_count})</h3>
                <div style="display: flex; flex-wrap: wrap; gap: 10px; padding: 15px;">
                    ${data.variables_found && data.variables_found.length > 0 ? 
                        data.variables_found.map(v => `
                            <span style="background: #667eea; color: white; padding: 5px 10px; border-radius: 5px;">
                                ${escapeHtml(v)}
                            </span>
                        `).join('') : 
                        '<p style="color: #718096;">No variables found in template</p>'
                    }
                </div>
                ${data.filters_found && data.filters_found.length > 0 ? `
                    <h3>🔧 Filters Found (${data.filters_count})</h3>
                    <div style="display: flex; flex-wrap: wrap; gap: 10px; padding: 15px;">
                        ${data.filters_found.map(f => `
                            <span style="background: #48bb78; color: white; padding: 5px 10px; border-radius: 5px;">
                                ${escapeHtml(f)}
                            </span>
                        `).join('')}
                    </div>
                ` : ''}
            `;
            const resultsContainer = document.getElementById('resultsContainer');
            const symbolSection = resultsContainer.querySelector('.section:last-child');
            if (symbolSection) {
                resultsContainer.insertBefore(variablesSection, symbolSection);
            }
        }
        function displayTokens(tokens) {
            const tokensList = document.getElementById('tokensList');
            const limitedTokens = tokens.slice(0, 50);
            tokensList.innerHTML = limitedTokens.map(token => `
                <div class="token">
                    <div class="token-type">${token.type}</div>
                    <div class="token-value" title="${escapeHtml(token.value)}">
                        ${escapeHtml(token.value.length > 30 ? token.value.substring(0, 30) + '...' : token.value)}
                    </div>
                    <div style="font-size: 0.8rem; color: #718096;">
                        Line: ${token.line}
                    </div>
                </div>
            `).join('');
            if (tokens.length > 50) {
                tokensList.innerHTML += `
                    <div class="token" style="text-align: center; background: #fed7d7;">
                        +${tokens.length - 50} more tokens
                    </div>
                `;
            }
        }
        function displayAST(astNode) {
            const viewer = document.getElementById('astViewer');
            try {
                const simplified = simplifyAST(astNode);
                viewer.textContent = JSON.stringify(simplified, null, 2);
            } catch (e) {
                viewer.textContent = "Sorry, cannot display AST tree: " + e.message;
            }
        }
        function simplifyAST(node) {
            if (!node) return node;
            const simple = {
                type: node.type,
                name: node.name,
                line: node.line,
                id: node.id || ''
            };
            if (node.properties) {
                if (node.properties.tag) simple.tag = node.properties.tag;
                if (node.properties.is_closing !== undefined) simple.is_closing = node.properties.is_closing;
                if (node.properties.var_name) simple.variable = node.properties.var_name;
                if (node.properties.value) simple.value = node.properties.value;
                if (node.properties.operator) simple.operator = node.properties.operator;
                if (node.properties.filter_name) simple.filter = node.properties.filter_name;
                if (node.properties.content_preview) simple.content = node.properties.content_preview;
            }
            if (node.children && node.children.length > 0) {
                simple.children = node.children.slice(0, 5).map(child => 
                    typeof child === 'object' ? simplifyAST(child) : child
                );
                if (node.children.length > 5) {
                    simple.children.push(`+ ${node.children.length - 5} more...`);
                }
            }
            return simple;
        }
        function displaySymbols(symbolTable) {
            const symbolsList = document.getElementById('symbolsList');
            const symbols = symbolTable.all_symbols.slice(0, 20);
            symbolsList.innerHTML = symbols.map(symbol => `
                <div style="background: #f7fafc; padding: 10px; margin-bottom: 10px; border-radius: 8px; border-left: 4px solid #667eea;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                        <strong>${escapeHtml(symbol.name)}</strong>
                        <span style="background: #e2e8f0; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem;">
                            ${escapeHtml(symbol.type)}
                        </span>
                    </div>
                    <div style="font-size: 0.9rem; color: #718096;">
                        ${escapeHtml(formatValue(symbol.value))}
                    </div>
                    <div style="font-size: 0.8rem; color: #a0aec0; margin-top: 5px;">
                        Scope: ${symbol.scope} | Line: ${symbol.line || 'N/A'}
                    </div>
                </div>
            `).join('');
            if (symbolTable.all_symbols.length > 20) {
                symbolsList.innerHTML += `
                    <div class="symbol-item" style="text-align: center; background: #fed7d7; padding: 10px; border-radius: 8px;">
                        +${symbolTable.all_symbols.length - 20} more symbols
                    </div>
                `;
            }
        }
        function clearAll() {
            document.getElementById('templateInput').value = '';
            document.getElementById('resultsContainer').style.display = 'none';
            document.getElementById('statsContainer').style.display = 'none';
            document.getElementById('terminalNote').style.display = 'none';
            document.getElementById('tokensList').innerHTML = '';
            document.getElementById('astViewer').textContent = '';
            document.getElementById('symbolsList').innerHTML = '';
            currentASTData = null;
        }
        function displayDiagrams(data) {
            if (!data || !data.diagrams) {
                console.error('No data for diagrams');
                return;
            }
            document.getElementById('treeDiagram').textContent = data.diagrams.tree_diagram || 'No tree diagram available';
            document.getElementById('summaryDiagram').textContent = data.diagrams.summary_diagram || 'No summary available';
            createNetworkDiagram(data.diagrams.box_diagram);
        }
        function showDiagram(type) {
            document.querySelectorAll('.diagram-section').forEach(section => {
                section.style.display = 'none';
            });
            document.querySelectorAll('.diagram-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            document.getElementById('diagram' + type.charAt(0).toUpperCase() + type.slice(1)).style.display = 'block';
            event.target.classList.add('active');
            if (type === 'network' && network) {
                setTimeout(() => {
                    network.redraw();
                    network.fit();
                }, 100);
            }
        }
        function createNetworkDiagram(diagramData) {
            if (!diagramData || !diagramData.nodes || diagramData.nodes.length === 0) {
                document.getElementById('networkDiagram').innerHTML = 
                    '<div style="padding: 20px; text-align: center; color: #666;">No data for visual network</div>';
                return;
            }
            const nodes = new vis.DataSet(diagramData.nodes.map(node => ({
                id: node.id,
                label: node.label,
                color: node.color,
                shape: 'box',
                font: { size: 14 },
                margin: 10,
                shadow: true
            })));
            const edges = new vis.DataSet(diagramData.edges.map(edge => ({
                from: edge.from,
                to: edge.to,
                arrows: 'to',
                smooth: { type: 'cubicBezier', forceDirection: 'vertical' }
            })));
            const container = document.getElementById('networkDiagram');
            if (network) {
                network.destroy();
            }
            const data = { nodes: nodes, edges: edges };
            const options = {
                layout: {
                    hierarchical: {
                        direction: 'UD',
                        sortMethod: 'directed',
                        nodeSpacing: 150,
                        levelSeparation: 200
                    }
                },
                interaction: { dragNodes: true, dragView: true, zoomView: true },
                physics: { enabled: false },
                nodes: {
                    shape: 'box',
                    margin: 10,
                    widthConstraint: { maximum: 200 }
                },
                edges: { smooth: true, color: '#666666' }
            };
            network = new vis.Network(container, data, options);
            network.on("click", function(params) {
                if (params.nodes.length > 0) {
                    const nodeId = params.nodes[0];
                    const node = diagramData.nodes.find(n => n.id === nodeId);
                    if (node) {
                        showNodeDetails(node);
                    }
                }
            });
        }
        function showNodeDetails(node) {
            const details = `
                <div style="padding: 15px; background: white; border-radius: 10px; margin-top: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.1);">
                    <h4 style="margin-bottom: 10px; color: #2d3748;">Node Details</h4>
                    <div><strong>Type:</strong> ${node.type}</div>
                    <div><strong>Label:</strong> ${node.label}</div>
                    <div><strong>Line:</strong> ${node.line || 'Not specified'}</div>
                    ${node.properties ? `
                        <div style="margin-top: 10px;">
                            <strong>Properties:</strong>
                            <pre style="background: #f8f9fa; padding: 10px; border-radius: 5px; margin-top: 5px; font-size: 0.9rem;">
${JSON.stringify(node.properties, null, 2)}
                            </pre>
                        </div>
                    ` : ''}
                </div>
            `;
            const container = document.getElementById('networkDiagram');
            const existingDetails = container.querySelector('.node-details');
            if (existingDetails) {
                existingDetails.remove();
            }
            const detailsDiv = document.createElement('div');
            detailsDiv.className = 'node-details';
            detailsDiv.innerHTML = details;
            container.parentNode.appendChild(detailsDiv);
        }
        async function loadProducts() {
            try {
                const response = await fetch('/api/products');
                const data = await response.json();
                if (data.success) {
                    currentProducts = data.products;
                    displayProducts(currentProducts);
                    displayCategories(data.categories);
                }
            } catch (error) {
                console.error('Error loading products:', error);
                alert('❌ Error loading products');
            }
        }
        function displayProducts(products) {
            const productsGrid = document.getElementById('productsGrid');
            if (products.length === 0) {
                productsGrid.innerHTML = `
                    <div class="section" style="text-align: center; padding: 40px;">
                        <h3>📦 No Products</h3>
                        <p>No products found matching your search</p>
                    </div>
                `;
                return;
            }
            productsGrid.innerHTML = products.map(product => `
                <div class="product-card">
                    <img src="${product.image_url || 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400'}" 
                         alt="${product.name}" class="product-image">
                    <div class="product-info">
                        <div class="product-name">${escapeHtml(product.name)}</div>
                        <div class="product-price">${product.price.toFixed(2)} Syrian Pounds</div>
                        <div class="product-description">${escapeHtml(product.description)}</div>
                        <div class="product-meta">
                            <span>📦 ${product.stock} available</span>
                            <span>⭐ ${product.rating.toFixed(1)}</span>
                            <span>🏷️ ${escapeHtml(product.category)}</span>
                        </div>
                    </div>
                </div>
            `).join('');
        }
        function displayCategories(categories) {
            const categoriesList = document.getElementById('categoriesList');
            categoriesList.innerHTML = `
                <button class="category-btn active" onclick="filterByCategory('all')">All</button>
                ${categories.map(category => `
                    <button class="category-btn" onclick="filterByCategory('${escapeHtml(category)}')">
                        ${escapeHtml(category)}
                    </button>
                `).join('')}
            `;
        }
        function filterByCategory(category) {
            document.querySelectorAll('.category-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            event.target.classList.add('active');
            if (category === 'all') {
                displayProducts(currentProducts);
            } else {
                const filteredProducts = currentProducts.filter(p => p.category === category);
                displayProducts(filteredProducts);
            }
        }
        function searchProducts() {
            const query = document.getElementById('productSearch').value.toLowerCase();
            if (!query) {
                displayProducts(currentProducts);
                return;
            }
            const filteredProducts = currentProducts.filter(product => 
                product.name.toLowerCase().includes(query) ||
                product.description.toLowerCase().includes(query) ||
                product.category.toLowerCase().includes(query)
            );
            displayProducts(filteredProducts);
        }
        async function addNewProduct() {
            const productData = {
                name: document.getElementById('productName').value,
                price: document.getElementById('productPrice').value,
                description: document.getElementById('productDescription').value,
                category: document.getElementById('productCategory').value,
                stock: document.getElementById('productStock').value,
                rating: document.getElementById('productRating').value,
                image_url: document.getElementById('productImage').value
            };
            if (!productData.name || !productData.price) {
                showMessage('⚠️ Please enter product name and price', 'warning');
                return;
            }
            try {
                const response = await fetch('/api/products', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(productData)
                });
                const data = await response.json();
                if (data.success) {
                    showMessage('✅ Product added successfully!', 'success');
                    clearProductForm();
                    if (document.getElementById('products').classList.contains('active')) {
                        loadProducts();
                    }
                } else {
                    showMessage('❌ Error adding product: ' + data.error, 'error');
                }
            } catch (error) {
                showMessage('❌ Connection error: ' + error.message, 'error');
            }
        }
        function clearProductForm() {
            document.getElementById('productName').value = '';
            document.getElementById('productPrice').value = '';
            document.getElementById('productDescription').value = '';
            document.getElementById('productCategory').value = 'Electronics';
            document.getElementById('productStock').value = '';
            document.getElementById('productRating').value = '';
            document.getElementById('productImage').value = '';
        }
        function showMessage(message, type) {
            const messageDiv = document.getElementById('productMessage');
            messageDiv.innerHTML = `
                <div style="padding: 15px; border-radius: 10px; background: ${
                    type === 'success' ? '#c6f6d5' : 
                    type === 'warning' ? '#feebc8' : 
                    '#fed7d7'
                }; color: ${
                    type === 'success' ? '#22543d' : 
                    type === 'warning' ? '#744210' : 
                    '#742a2a'
                };">
                    ${message}
                </div>
            `;
            setTimeout(() => {
                messageDiv.innerHTML = '';
            }, 5000);
        }
        async function loadProductAnalysis() {
            try {
                const response = await fetch('/api/products/analysis');
                const data = await response.json();
                if (data.success) {
                    console.log('Product analysis data:', data);
                }
            } catch (error) {
                console.error('Error loading product analysis:', error);
            }
        }
        async function analyzeProducts() {
            try {
                const template = document.getElementById('productAnalysisTemplate').value;
                const analysisResponse = await fetch('/api/products/analysis');
                const analysisData = await analysisResponse.json();
                if (analysisData.success) {
                    const response = await fetch('/analyze-with-data', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ 
                            template: template,
                            data: analysisData.analysis
                        })
                    });
                    const data = await response.json();
                    if (data.success) {
                        displayAnalysisResults(data.result);
                    } else {
                        document.getElementById('analysisResults').innerHTML = `
                            <div class="section" style="background: #fed7d7; color: #742a2a;">
                                <h3>❌ Analysis Error</h3>
                                <p>${escapeHtml(data.error)}</p>
                            </div>
                        `;
                    }
                }
            } catch (error) {
                document.getElementById('analysisResults').innerHTML = `
                    <div class="section" style="background: #fed7d7; color: #742a2a;">
                        <h3>❌ Connection Error</h3>
                        <p>${escapeHtml(error.message)}</p>
                    </div>
                `;
            }
        }
        function displayAnalysisResults(html) {
            document.getElementById('analysisResults').innerHTML = `
                <div class="section">
                    <h3>📊 Analysis Results</h3>
                    <div style="background: white; padding: 20px; border-radius: 10px;">
                        ${html}
                    </div>
                </div>
            `;
        }
        function formatValue(value) {
            if (value === null || value === undefined) return 'Not set';
            if (typeof value === 'boolean') return value ? 'Yes' : 'No';
            if (typeof value === 'object') {
                try {
                    const str = JSON.stringify(value);
                    return str.length > 30 ? str.substring(0, 30) + '...' : str;
                } catch (e) {
                    return '[Object]';
                }
            }
            return String(value).length > 30 ? String(value).substring(0, 30) + '...' : String(value);
        }
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        window.onload = function() {
            setTimeout(() => {
                analyzeTemplate();
                loadProducts();
            }, 100);
        };
    </script>
</body>
</html>
'''
    return html_content, 200, {'Content-Type': 'text/html; charset=utf-8'}

@app.route('/api/products', methods=['GET', 'POST'])
def api_products():
    if request.method == 'GET':
        products = product_manager.get_all_products()
        categories = product_manager.get_categories()
        return jsonify({
            'success': True,
            'products': products,
            'categories': categories,
            'count': len(products)
        })
    elif request.method == 'POST':
        try:
            product_data = request.get_json()
            product = product_manager.add_product(product_data)
            return jsonify({
                'success': True,
                'message': 'Product added successfully',
                'product': product
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 400

@app.route('/api/products/<product_id>', methods=['GET', 'PUT', 'DELETE'])
def api_product_detail(product_id):
    if request.method == 'GET':
        product = product_manager.get_product_by_id(product_id)
        if product:
            return jsonify({
                'success': True,
                'product': product
            })
        return jsonify({
            'success': False,
            'error': 'Product not found'
        }), 404
    elif request.method == 'PUT':
        product_data = request.get_json()
        updated = product_manager.update_product(product_id, product_data)
        if updated:
            return jsonify({
                'success': True,
                'message': 'Product updated successfully',
                'product': updated
            })
        return jsonify({
            'success': False,
            'error': 'Product not found'
        }), 404
    elif request.method == 'DELETE':
        deleted = product_manager.delete_product(product_id)
        if deleted:
            return jsonify({
                'success': True,
                'message': 'Product deleted successfully'
            })
        return jsonify({
            'success': False,
            'error': 'Product not found'
        }), 404

@app.route('/api/products/analysis')
def api_products_analysis():
    products = product_manager.get_all_products()
    if not products:
        return jsonify({
            'success': False,
            'error': 'No products'
        })
    total_products = len(products)
    total_price = sum(p['price'] for p in products)
    total_stock = sum(p['stock'] for p in products)
    total_rating = sum(p['rating'] for p in products)
    average_price = total_price / total_products if total_products > 0 else 0
    average_rating = total_rating / total_products if total_products > 0 else 0
    category_distribution = {}
    for product in products:
        category = product['category']
        category_distribution[category] = category_distribution.get(category, 0) + 1
    expensive_products = sorted(products, key=lambda x: x['price'], reverse=True)[:5]
    top_rated_products = sorted(products, key=lambda x: x['rating'], reverse=True)[:5]
    low_stock_products = [p for p in products if p['stock'] < 10]
    analysis = {
        'total_products': total_products,
        'average_price': average_price,
        'total_stock': total_stock,
        'average_rating': average_rating,
        'category_distribution': category_distribution,
        'expensive_products': expensive_products,
        'top_rated_products': top_rated_products,
        'low_stock_products': low_stock_products,
        'categories': list(category_distribution.keys())
    }
    return jsonify({
        'success': True,
        'analysis': analysis
    })

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        if not data or 'template' not in data:
            return jsonify({
                'success': False,
                'error': 'No template provided for analysis'
            })
        template = data.get('template', '')
        print_ast = data.get('print_ast', False)
        generate_diagrams = data.get('generate_diagrams', True)
        if not template.strip():
            return jsonify({
                'success': False,
                'error': 'Template is empty'
            })
        result = TemplateProcessor.process_template(template, print_ast=print_ast, generate_diagrams=generate_diagrams)
        return jsonify(result)
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}',
            'traceback': traceback.format_exc()
        })

@app.route('/analyze-with-data', methods=['POST'])
def analyze_with_data():
    try:
        data = request.get_json()
        if not data or 'template' not in data:
            return jsonify({
                'success': False,
                'error': 'No template provided for analysis'
            })
        template = data.get('template', '')
        template_data = data.get('data', {})
        result_html = apply_template(template, template_data)
        return jsonify({
            'success': True,
            'result': result_html,
            'original_template': template
        })
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}',
            'traceback': traceback.format_exc()
        })

def apply_template(template, data):
    result = template
    for key, value in data.items():
        if isinstance(value, (int, float)):
            placeholder = f'{{{{ {key} }}}}'
            result = result.replace(placeholder, str(value))
    for key, value in data.items():
        if isinstance(value, dict):
            for subkey, subvalue in value.items():
                placeholder = f'{{{{ {key}.{subkey} }}}}'
                result = result.replace(placeholder, str(subvalue))
    import re
    for_pattern = r'\{%\s*for\s+(\w+)\s+in\s+(\w+)\s*%\}(.*?)\{%\s*endfor\s*%\}'
    def replace_for(match):
        item_name = match.group(1)
        list_name = match.group(2)
        content = match.group(3)
        if list_name in data and isinstance(data[list_name], list):
            items = []
            for item in data[list_name]:
                item_content = content
                if isinstance(item, dict):
                    for item_key, item_value in item.items():
                        placeholder = f'{{{{ {item_name}.{item_key} }}}}'
                        item_content = item_content.replace(placeholder, str(item_value))
                else:
                    placeholder = f'{{{{ {item_name} }}}}'
                    item_content = item_content.replace(placeholder, str(item))
                items.append(item_content)
            return ''.join(items)
        return ''
    result = re.sub(for_pattern, replace_for, result, flags=re.DOTALL)
    return result

@app.route('/health')
def health():
    products_count = len(product_manager.get_all_products())
    return jsonify({
        'status': 'healthy', 
        'service': 'Jinja2 Analyzer + Product Management',
        'version': '4.1.0',
        'features': ['Lexer', 'Parser', 'AST', 'Symbol Table', 'Product Management', 'Analysis', 'AST Diagrams', 'Division Operator Support'],
        'products_count': products_count
    })

if __name__ == '__main__':
    print("="*80)
    print("🚀 Starting Template Analysis System + Product Management (Version 4.1.0)")
    print("="*80)
    print("📌 New Feature: Added support for division operator (/)")
    print("📌 HTML tag closing validation with stack tracking")
    print("="*80)
    create_static_folders()
    print("📁 Open browser and go to: http://localhost:5000")
    print("⚡ Server running on port 5000")
    print("✨ New Features:")
    print("  - ➗ Division operator (/) support in expressions")
    print("  - 🔍 Improved HTML tag parsing (closing tags detection)")
    print("  - 🌳 AST tree diagrams in Terminal and Web")
    print("  - 📊 Three types of diagrams: Tree, Visual Network, Summary")
    print("  - 🕸️ Interactive visual network using vis.js")
    print("  - 🛍️ Complete product management system")
    print("  - 🔍 Product display with search and filtering")
    print("  - ➕ Add new products")
    print("  - 📊 Product statistical analysis")
    print("  - 💻 Print AST tree in Terminal")
    print("="*80)
    print("🎯 Use navigation buttons to switch between different features")
    print("="*80)
    try:
        app.run(debug=True, host='127.0.0.1', port=5000)
    except OSError as e:
        if "Address already in use" in str(e):
            print("⚠️ Port 5000 busy, trying port 5001...")
            app.run(debug=True, host='127.0.0.1', port=5001)
        else:
            raise e