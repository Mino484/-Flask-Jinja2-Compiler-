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