import ast
import os
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional
from src.utils.embedding_generator import load_embedding_model, generate_embeddings

# Load the embedding model once when the module is imported
_embedding_model_instance = load_embedding_model()

class CodeEntity:
    def __init__(self, path: str, type: str, name: str, lineno: Optional[int] = None, end_lineno: Optional[int] = None, embedding: Optional[List[float]] = None):
        self.path = path
        self.type = type  # e.g., 'file', 'class', 'function', 'import'
        self.name = name
        self.lineno = lineno
        self.end_lineno = end_lineno
        self.embedding = embedding

    def to_dict(self):
        return {
            "path": self.path,
            "type": self.type,
            "name": self.name,
            "lineno": self.lineno,
            "end_lineno": self.end_lineno,
            "embedding": self.embedding
        }

class CodeRelationship:
    def __init__(self, source_path: str, target_path: str, type: str, line: Optional[int] = None):
        self.source_path = source_path
        self.target_path = target_path
        self.type = type  # e.g., 'imports', 'calls', 'defines'
        self.line = line

    def to_dict(self):
        return {
            "source_path": self.source_path,
            "target_path": self.target_path,
            "type": self.type,
            "line": self.line
        }

class CodeParser(ast.NodeVisitor):
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.entities: List[CodeEntity] = []
        self.relationships: List[CodeRelationship] = []
        self.current_class: Optional[str] = None

    def visit_ClassDef(self, node):
        entity_name = node.name
        embedding = generate_embeddings([entity_name])[0] if _embedding_model_instance else None
        entity = CodeEntity(self.file_path, "class", entity_name, node.lineno, node.end_lineno, embedding)
        self.entities.append(entity)
        old_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = old_class

    def visit_FunctionDef(self, node):
        entity_type = "method" if self.current_class else "function"
        entity_name = f"{self.current_class}.{node.name}" if self.current_class else node.name
        embedding = generate_embeddings([entity_name])[0] if _embedding_model_instance else None
        entity = CodeEntity(self.file_path, entity_type, entity_name, node.lineno, node.end_lineno, embedding)
        self.entities.append(entity)
        self.generic_visit(node)

    def visit_Import(self, node):
        for alias in node.names:
            entity_name = alias.name
            embedding = generate_embeddings([entity_name])[0] if _embedding_model_instance else None
            self.entities.append(CodeEntity(self.file_path, "import", entity_name, node.lineno, embedding=embedding))
            # For now, target_path is just the module name. Later, resolve to actual file path.
            self.relationships.append(CodeRelationship(self.file_path, alias.name, "imports", node.lineno))
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        module = "." * (node.level or 0) + (node.module or "")
        for alias in node.names:
            imported_name = f"{module}.{alias.name}" if module else alias.name
            embedding = generate_embeddings([imported_name])[0] if _embedding_model_instance else None
            self.entities.append(CodeEntity(self.file_path, "import", imported_name, node.lineno, embedding=embedding))
            self.relationships.append(CodeRelationship(self.file_path, imported_name, "imports", node.lineno))
        self.generic_visit(node)

    # Basic call detection (can be greatly expanded)
    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            # Simple function call
            self.relationships.append(CodeRelationship(self.file_path, node.func.id, "calls", node.lineno))
        elif isinstance(node.func, ast.Attribute):
            # Method call (e.g., obj.method())
            if isinstance(node.func.value, ast.Name):
                # Simple method call on an object
                target_name = f"{node.func.value.id}.{node.func.attr}"
                self.relationships.append(CodeRelationship(self.file_path, target_name, "calls", node.lineno))
            # More complex attribute access would need deeper analysis
        self.generic_visit(node)

def parse_python_file(file_path: str) -> Dict[str, Any]:
    """
    Parses a Python file and extracts code entities and relationships.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    tree = ast.parse(content, filename=file_path)
    parser = CodeParser(file_path)
    parser.visit(tree)

    return {
        "entities": [e.to_dict() for e in parser.entities],
        "relationships": [r.to_dict() for r in parser.relationships],
        "file_checksum": hashlib.sha256(content.encode()).hexdigest(),
        "last_modified": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
    }

# Example Usage
if __name__ == "__main__":
    sample_code = """
import os
from my_module import MyClass

def my_function(arg1, arg2):
    print(f"Args: {arg1}, {arg2}")
    MyClass().my_method()
    return arg1 + arg2

class AnotherClass:
    def __init__(self):
        self.value = 10

    def calculate(self, x):
        result = my_function(self.value, x)
        return result

if __name__ == "__main__":
    val = my_function(1, 2)
    print(val)
    ac = AnotherClass()
    ac.calculate(5)
"""
    # Create a dummy file for testing
    dummy_file_path = "./temp_code_parser_test.py"
    with open(dummy_file_path, "w") as f:
        f.write(sample_code)

    parsed_data = parse_python_file(dummy_file_path)
    print("\n--- Entities ---")
    for entity in parsed_data["entities"]:
        print(entity)

    print("\n--- Relationships ---")
    for rel in parsed_data["relationships"]:
        print(rel)

    print(f"\nFile Checksum: {parsed_data['file_checksum']}")
    print(f"Last Modified: {parsed_data['last_modified']}")

    os.remove(dummy_file_path)
