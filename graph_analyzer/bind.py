import os
import csv
from typing import Dict, List
from pathlib import Path
from graph_analyzer.graph import GraphNode


def bind_code_info_for_data(input_dir: str, nodes: List[GraphNode]) -> Dict[str, str]:    
    npy_files = find_npy_files(input_dir)
    match_dict = {}
    for node in nodes:
        # 屏蔽子图节点
        if node.is_subgraph:
            continue
        scope_name = node.scope.replace("/", "_")
        code_info = '\n'.join(node.code_info)
        match_dict[scope_name] = code_info
    
    bind_result = {}
    for npy_file in npy_files:
        npy_path = os.path.realpath(npy_file)
        basename = os.path.basename(npy_path)
        node_scope = basename.split(".")[1]
        bind_code = match_dict.get(node_scope, None)
        bind_result[npy_path] = bind_code
    return bind_result


def find_npy_files(directory):
    npy_files = list(Path(directory).rglob('*.npy'))
    return npy_files


def write_to_csv(param: Dict, file_name: str = 'output.csv'):
    # 打开CSV文件以写入模式
    with open(file_name, mode='w', newline='') as file:
        writer = csv.writer(file)
        
        # 遍历字典并逐行写入键值对
        for key, value in param.items():
            writer.writerow([key, value])

        