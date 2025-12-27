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