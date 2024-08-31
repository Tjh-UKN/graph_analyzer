import re
import sys
import argparse
from typing import List
from graph_analyzer.graph_parser import Parser




def main():
    parser = argparse.ArgumentParser(description="IR Parser")
    parser.add_argument('--input', type=str, required=True, help="Path to the input file")
    args = parser.parse_args()

    file_path = args.input
    with open(file_path, 'r') as f:
        input_text = f.read()

    parser = Parser()
    parser.parse(input_text)

    nodes = parser.get_nodes()

    func_graph_output = []
    node_output = []

    func_graph_output.append("Graph Info:")
    for node_name, info in nodes.items():
        if info.is_subgraph:
            node_list = [ii.name for ii in info.nodes.values()]
            func_graph_output.append(f"Subgraph: {info.name}\nAttributes: {info.attrs}\nSubNodes: {node_list}")
        else:
            code_info = '\n'.join(info.code_info)
            node_output.append(f"Variable: {info.name}\nOperator: {info.operator_name}\nInputs: {info.var_inputs}\nScope: {info.scope}\nCode Info: {code_info}\n")
        sorted_nodes = []
        visited = {var_name: False for var_name in nodes.keys()}
        info.topological_sort(sorted_nodes, visited, parser)
        
        # Example: Ancestors trace back
        ancestors = []
        visited = {var_name: False for var_name in nodes.keys()}
        info.trace_back_ancestors(ancestors, visited, parser)
    total_nodes, total_cnodes = parser.count_nodes()
    func_graph_output.append(f"\nNode counting information:")
    func_graph_output.append(f"Total number of nodes: {total_nodes}")
    func_graph_output.append(f"Total number of cnodes: {total_cnodes}")

    output = "\n".join(func_graph_output + node_output)
    print(output)
    
    while(True):
        cmd = input("please write your command: ")
        if cmd == "stop":
            break

if __name__ == "__main__":
    main()
