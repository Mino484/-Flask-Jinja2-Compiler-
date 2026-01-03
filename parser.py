class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.position = 0
        self.current_token = tokens[0] if tokens else Token(TokenType.EOF, "", 1, 1)
    
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
        tag_name = self.consume(TokenType.IDENTIFIER).value
        html_node = HTMLNode(tag_name, line)
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
        if self.current_token.type == TokenType.TAG_SELF_CLOSE:
            self.advance()
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