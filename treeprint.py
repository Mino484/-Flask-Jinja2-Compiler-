class TreePrinter:
    """Print AST tree beautifully in Terminal"""
    
    def __init__(self, show_line_numbers=True):
        self.show_line_numbers = show_line_numbers
        self.node_counts = {}
        self.show_ids = False
    
    def print_tree(self, node, indent="", is_last=True):
        """Print node and its children tree"""
        if not node:
            return
        
        # Create prefix
        prefix = indent
        if indent:
            prefix = prefix[:-2] + ("└── " if is_last else "├── ")
        
        # Print node information
        node_info = self._get_node_info(node)
        print(f"{prefix}{node_info}")
        
        # Count nodes by type
        node_type = getattr(node, 'node_type', 'Unknown')
        self.node_counts[node_type] = self.node_counts.get(node_type, 0) + 1
