
class TemplateProcessor:
    """Main template processor"""
    
    @staticmethod
    def process_template(template_source: str, print_ast=False, generate_diagrams=True) -> dict:
        """Process template and return results as dictionary"""
        try:
            # 1. Lexical analysis
            lexer = Lexer(template_source)
            tokens = lexer.tokenize()
            
            # 2. Syntax analysis
            parser = Parser(tokens)
            ast_root = parser.parse()
            
            # 3. Count variables and filters in AST
            variable_counter = VariableCounter()
            ast_root.accept(variable_counter)
            actual_variables = list(variable_counter.variables)
            actual_filters = list(variable_counter.filters)
            
            # 4. Print AST in Terminal if requested
            if print_ast:
                print("\n" + "="*80)
                print("🌳 AST Tree (Printed in Terminal)")
                print("="*80)
                
                printer = TreePrinter(show_line_numbers=True)
                printer.print_tree(ast_root)
                printer.print_summary()
                
                # Print variables found
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
                
                # Print first 20 tokens
                print("\n🔤 First 20 Tokens:")
                print("-" * 40)
                for i, token in enumerate(tokens[:20]):
                    print(f"  {i+1:2d}. {token}")
                
                print("="*80)
            
            # 5. Create tree diagrams
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
            
            # 6. Build symbol table with actual variables found
            symbol_table = SymbolTable()
            symbol_table.enter_scope()
            
            # Add only variables that actually exist in the template
            for var_name in actual_variables:
                # Set default values based on variable names
                value = None
                if 'title' in var_name.lower():
                    value = 'My Page'
                elif 'user' in var_name.lower() and 'name' in var_name.lower():
                    value = 'Mohammed'
                elif 'logged' in var_name.lower():
                    value = True
                elif 'product' in var_name.lower() and 's' in var_name.lower():  # products
                    value = [
                        {'name': 'Product 1', 'price': 100},
                        {'name': 'Product 2', 'price': 200},
                        {'name': 'Product 3', 'price': 150}
                    ]
                elif 'price' in var_name.lower():
                    value = 100.0
                elif 'name' in var_name.lower():
                    value = 'Sample Name'
                
                symbol_table.add_symbol(var_name, 'variable', value, 1)
            
            # Add filters found in template
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
                'lexer_debug': TemplateProcessor._debug_lexer(tokens[:20])  # For debugging
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
        """Count all nodes in AST tree"""
        count = 1
        for child in node.children:
            if hasattr(child, 'children'):
                count += TemplateProcessor._count_ast_nodes(child)
            else:
                count += 1
        return count
    
    @staticmethod
    def _debug_lexer(tokens):
        """Return debug information about tokens"""
        return [str(token) for token in tokens]


