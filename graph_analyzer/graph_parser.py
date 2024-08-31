import re
import logging
from typing import Tuple, List, Dict
from graph_analyzer.graph import GraphNode


class Parser:
    def __init__(self):
        self.nodes = {}
        self.local_dict = {}

    def parse_func_graph(self, text: str) -> None:
        func_graph_pattern = re.compile(r'# IR entry: @(\S+)')
        matches = func_graph_pattern.finditer(text)
        for match in matches:
            func_name = match.group(1)
            func_graph_info = GraphNode(name=func_name, pos=match.start(), is_subgraph=False)
            self.nodes[func_name] = func_graph_info

    def parse_graph_attributes(self, text: str, graph_node: GraphNode) -> None:
        attr_pattern = re.compile(r'# Attrs:\s*(.*)', re.DOTALL)
        match = attr_pattern.search(text, graph_node.pos)
        if match:
            attrs = match.group(1).strip().split('\n')
            for attr in attrs:
                if not attr:  # if end line
                    break
                key, value = attr.split(':')
                if isinstance(graph_node.attrs, dict):
                    graph_node.attrs[key.strip()] = value.strip()

    def parse_subgraph_attributes(self, text: str, subgraph_node: GraphNode, start_pos: int, end_pos: int) -> None:
        subgraph_attr_pattern = re.compile(r'subgraph attr:\s*(.*)', re.DOTALL)
        match = subgraph_attr_pattern.search(text, start_pos, end_pos)
        if match:
            attrs = match.group(1).strip().split('\n')
            if isinstance(subgraph_node.attrs, list):
                subgraph_node.attrs.extend(attrs)

    def parse_nodes(self, text: str, subgraph_info: GraphNode) -> None:
        node_pattern = re.compile(r'(%\d+)\((\S+)\)\s*=\s*(\S+)\(')
        matches = list(node_pattern.finditer(text))
        for i, match in enumerate(matches):
            series_number = match.group(1)
            variable_name = match.group(2)
            operator_name = match.group(3)
            unique_name = series_number + '_' + variable_name
            self.local_dict[series_number] = unique_name

            args_str, end_pos = self.extract_bracket_content(text, match.end() - 1)

            inputs = re.findall(r'%\w+', args_str)
            subgraph_inputs = re.findall(r'@\w+', args_str)
            inputs += subgraph_inputs

            constants = self.extract_constants(args_str)

            scope_pattern = re.compile(r'# .*scope.*:\s*\((.*?)\)', re.IGNORECASE | re.MULTILINE)
            scope_match = scope_pattern.search(text, end_pos)
            scope = scope_match.group(1) if scope_match else ""

            if scope:
                next_match = matches[i + 1].start() - 1 if i < len(matches) - 1 else None
                code_info = self.parse_code_info(text, scope_match.end(), next_match)
            else:
                code_info = None

            node_info = GraphNode(name=variable_name, operator_name=operator_name, var_inputs=inputs + constants, scope=scope, code_info=code_info)
            if subgraph_info:
                subgraph_info.nodes[unique_name] = node_info
            if not self.nodes.get(unique_name, None):
                self.nodes[unique_name] = node_info

            for const in constants:
                if const not in self.nodes:
                    const_node = GraphNode(name=const, operator_name="Constant", var_inputs=[], has_constant_input=True)
                    if not self.nodes.get(const_node, None):
                        self.nodes[const] = const_node
                    if subgraph_info:
                        subgraph_info.nodes[const] = const_node
                    self.local_dict[const] = const

            for input_var in node_info.var_inputs:
                if input_var in self.local_dict or input_var in self.nodes:
                    input_name = self.local_dict.get(input_var, None)
                    input_node = self.nodes.get(input_name, None)
                    if input_node:
                        node_info.predecessors.append(input_name)
                        input_node.successors.append(unique_name)
                else:
                    param_node = GraphNode(name=input_var, operator_name="Param", var_inputs=[], has_constant_input=False)
                    if not self.nodes.get(input_var, None):
                        self.nodes[input_var] = param_node
                    node_info.predecessors.append(input_var)
                    param_node.successors.append(unique_name)

    def parse_code_info(self, text: str, start_pos: int, end_pos: int) -> List[str]:
        code_info = []
        code_info_pattern = re.compile(r'# .*', re.MULTILINE)
        final_pos = end_pos if end_pos else len(text) - 1
        lines = text[start_pos + 1:final_pos].split('\n')
        for line in lines:
            match = code_info_pattern.search(line)
            if not match and line:
                break
            code_info.append(match.group(0))
        return code_info

    def extract_bracket_content(self, text: str, start_pos: int) -> Tuple[str, int]:
        stack = []
        content = []
        for i in range(start_pos, len(text)):
            char = text[i]
            if char == '(':
                stack.append('(')
            elif char == ')':
                stack.pop()
                if not stack:
                    return ''.join(content), i
            content.append(char)
        raise ValueError("Mismatched parentheses")

    def extract_constants(self, inputs_str: str) -> List[str]:
        constant_pattern = re.compile(r'\b(\w+\(.*?\))')
        constants = constant_pattern.findall(inputs_str)
        return constants

    def extract_callees(self, text: str) -> None:
        for node_name, node_info in self.nodes.items():
            func_start_pos = node_info.pos
            func_end_pos = text.find('}', func_start_pos)
            func_text = text[func_start_pos:func_end_pos]
            callee_pattern = re.compile(r'Partial\(@(\S+)\(')
            callee_matches = callee_pattern.finditer(func_text)
            for callee_match in callee_matches:
                callee_name = callee_match.group(1)
                if callee_name not in node_info.var_inputs:
                    node_info.var_inputs.append(callee_name)

    def parse_subgraphs(self, text: str) -> None:
        subgraph_pattern = re.compile(r'subgraph\s+@(\S+)(\([^\)]*\))?\s+.*\{')
        matches = list(subgraph_pattern.finditer(text))
        end_pos = 0
        for match in matches:
            last_pos = end_pos + 2
            subgraph_name = match.group(1).split('(')[0]
            start_pos = match.start()
            end_pos = self.find_matching_brace(text, start_pos)
            subgraph_text = text[start_pos:end_pos + 1]
            attr_text = text[last_pos:start_pos]
            subgraph_info = GraphNode(name=subgraph_name, pos=start_pos, is_subgraph=True)
            self.nodes[subgraph_name] = subgraph_info
            self.parse_subgraph_attributes(text, subgraph_info, last_pos, start_pos)
            self.parse_nodes(subgraph_text, subgraph_info)
            subgraph_info.end = end_pos
            logging.info(f'Parsed subgraph: {subgraph_name}')

    def find_matching_brace(self, text: str, start_pos: int) -> int:
        stack = []
        for i in range(start_pos, len(text)):
            if text[i] == '{':
                stack.append('{')
            elif text[i] == '}':
                stack.pop()
                if not stack:
                    return i
        raise ValueError("Matching closing brace not found")

    def count_nodes(self) -> Tuple[int, int]:
        total_nodes = len(self.nodes)
        total_cnodes = sum(1 for node in self.nodes.values() if node.name.startswith('CNode'))
        return total_nodes, total_cnodes

    def parse(self, text: str) -> None:
        self.parse_func_graph(text)
        self.parse_subgraphs(text)
        self.parse_nodes(text, None)
        self.extract_callees(text)

    def get_nodes(self) -> Dict[str, GraphNode]:
        return self.nodes