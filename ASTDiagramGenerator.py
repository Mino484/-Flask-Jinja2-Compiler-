
class ASTDiagramGenerator:
    """AST tree diagram generator for display in Terminal and Web"""
    
    @staticmethod
    def generate_tree_diagram(node, show_ids=False, max_depth=10):
        """Create textual tree diagram for Terminal display"""
        lines = []
        ASTDiagramGenerator._add_tree_node(lines, node, "", "", show_ids, 0, max_depth)
        return "\n".join(lines)
    
    @staticmethod
    def _add_tree_node(lines, node, prefix, children_prefix, show_ids, depth, max_depth):
        """Add node to tree diagram"""
        if depth > max_depth:
            lines.append(prefix + "└── ... (hidden due to depth)")
            return
        
        if not node:
            return
        
        # Node information
        node_info = ASTDiagramGenerator._get_node_label(node, show_ids)
        lines.append(prefix + node_info)
        
        # Add children
        children = getattr(node, 'children', [])
        for i, child in enumerate(children):
            is_last = (i == len(children) - 1)
            
            if hasattr(child, 'children'):
                # Child node
                new_prefix = children_prefix + ("└── " if is_last else "├── ")
                new_children_prefix = children_prefix + ("    " if is_last else "│   ")
                ASTDiagramGenerator._add_tree_node(
                    lines, child, new_prefix, new_children_prefix, show_ids, depth + 1, max_depth
                )
            else:
                # Simple value
                child_prefix = children_prefix + ("└── " if is_last else "├── ")
                lines.append(child_prefix + str(child)[:50])
    
    @staticmethod
    def _get_node_label(node, show_ids):
        """Get node label"""
        node_type = getattr(node, 'node_type', 'Unknown')
        line = getattr(node, 'line', 0)
        node_id = getattr(node, 'id', '')[:4] if show_ids else ''
        
        # Icons based on node type
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
        
        # Additional information based on node type
        extra_info = ""
        if node_type == 'HTML':
            tag = getattr(node, 'tag', '')
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
        """Create box diagram for web display"""
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
        """Traverse tree to collect nodes and edges"""
        if not node:
            return
        
        # Create node
        node_id = getattr(node, 'id', str(uuid.uuid4())[:8])
        node_type = getattr(node, 'node_type', 'Unknown')
        line = getattr(node, 'line', 0)
        
        # Set colors based on node type
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
        
        # Add edge from parent if exists
        if parent_id:
            edges.append({
                "from": parent_id,
                "to": node_id,
                "label": f"child",
                "arrows": "to"
            })
        
        # Traverse children
        children = getattr(node, 'children', [])
        for child in children:
            if hasattr(child, 'children'):
                ASTDiagramGenerator._traverse_for_box_diagram(child, nodes, edges, node_id)
            else:
                # Create node for simple child
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
        """Get label for display in box"""
        node_type = getattr(node, 'node_type', 'Unknown')
        
        if node_type == 'HTML':
            tag = getattr(node, 'tag', '')
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
        """Get node properties"""
        props = {}
        
        if hasattr(node, 'attributes'):
            props['attributes'] = getattr(node, 'attributes', {})
        if hasattr(node, 'tag'):
            props['tag'] = getattr(node, 'tag', '')
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
        """Create summary diagram of tree"""
        if not ast_root:
            return ""
        
        summary_lines = []
        ASTDiagramGenerator._collect_summary(ast_root, summary_lines, 0)
        
        # Convert to text layout
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
        """Collect node statistics by depth"""
        if not node:
            return
        
        node_type = getattr(node, 'node_type', 'Unknown')
        
        # Search for depth and node type in list
        found = False
        for i, (d, nt, count) in enumerate(summary_lines):
            if d == depth and nt == node_type:
                summary_lines[i] = (d, nt, count + 1)
                found = True
                break
        
        if not found:
            summary_lines.append((depth, node_type, 1))
        
        # Traverse children
        children = getattr(node, 'children', [])
        for child in children:
            if hasattr(child, 'children'):
                ASTDiagramGenerator._collect_summary(child, summary_lines, depth + 1)

