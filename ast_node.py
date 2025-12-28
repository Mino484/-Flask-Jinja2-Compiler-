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
        
    def __init__(self, tag: str, line: int):
        super().__init__("HTML", line)
        self.tag = tag
        self.attributes = {}
        self.name = f"HTML_{tag}_Node"
    
    def add_attribute(self, name: str, value: str):
        self.attributes[name] = value
    
    def _get_properties(self):
        props = super()._get_properties()
        props['attributes'] = self.attributes
        props['tag'] = self.tag
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

