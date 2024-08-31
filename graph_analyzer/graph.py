from typing import List, Dict, Union


class GraphNode:
    def __init__(self, name: str, pos: int = -1, operator_name: str = "", return_variable: str = "", return_value: str = "",
                 var_inputs: List[str] = None, has_constant_input: bool = False, scope: str = "", code_info: List[str] = None,
                 is_subgraph: bool = False, attrs: Union[Dict[str, str], List[str]] = None):
        self.name = name
        self.pos = pos
        self.operator_name = operator_name
        self.return_variable = return_variable
        self.return_value = return_value
        self.var_inputs = var_inputs if var_inputs else []
        self.has_constant_input = has_constant_input
        self.scope = scope
        self.code_info = code_info if code_info else []
        self.attrs = attrs if attrs else ({} if not is_subgraph else [])
        self.nodes = {}  # Internal nodes if this is a subgraph
        self.predecessors = []  # Predecessor nodes
        self.successors = []    # Successor nodes
        self.is_subgraph = is_subgraph

    def topological_sort(self, sorted_nodes: List[str], visited: Dict[str, bool], parser) -> None:
        if visited[self.name]:
            return
        visited[self.name] = True
        for successor in self.successors:
            successor_node = parser.get_nodes()[successor]
            successor_node.topological_sort(sorted_nodes, visited, parser)
        sorted_nodes.append(self.name)

    def trace_back_ancestors(self, ancestors: List[str], visited: Dict[str, bool], parser) -> None:
        if visited[self.name]:
            return
        visited[self.name] = True
        ancestors.append(self.name)
        for predecessor in self.predecessors:
            predecessor_node = parser.get_nodes()[predecessor]
            predecessor_node.trace_back_ancestors(ancestors, visited, parser)