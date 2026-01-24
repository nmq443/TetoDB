import sys
import struct

# CONFIGURATION (Must match your C++ Btree.h)
PAGE_SIZE = 4096
# Header: Type(1), IsRoot(1), NumCells(2), Parent(4)
HEADER_FMT = "BBHi" 
HEADER_SIZE = 8

# Cell Sizes (int32 key + int32 rowId)
LEAF_CELL_FMT = "ii"
LEAF_CELL_SIZE = 8

# Internal Cell (int32 key + int32 rowId + uint32 childPage)
INTERNAL_CELL_FMT = "iii"
INTERNAL_CELL_SIZE = 12

NODE_INTERNAL = 0
NODE_LEAF = 1

def read_page(f, page_num):
    f.seek(page_num * PAGE_SIZE)
    data = f.read(PAGE_SIZE)
    if not data: return None
    
    header_raw = data[:HEADER_SIZE]
    node_type, is_root, num_cells, parent = struct.unpack(HEADER_FMT, header_raw)
    
    return {
        "page": page_num,
        "type": "LEAF" if node_type == NODE_LEAF else "INTERNAL",
        "is_root": is_root,
        "num_cells": num_cells,
        "parent": parent,
        "data": data
    }

def verify_tree(filename):
    with open(filename, "rb") as f:
        # 1. Read Root (Page 0)
        root = read_page(f, 0)
        if not root:
            print("Empty file")
            return

        print(f"ROOT: {root}")
        
        # Queue for BFS traversal
        queue = [0]
        visited = set()
        
        # To track parent validity
        child_to_parent_map = {}

        while queue:
            curr_page_num = queue.pop(0)
            if curr_page_num in visited:
                print(f"ERROR: Cycle detected at Page {curr_page_num}")
                continue
            visited.add(curr_page_num)

            node = read_page(f, curr_page_num)
            print(f"\n[Page {curr_page_num}] Type: {node['type']}, Parent: {node['parent']}, Cells: {node['num_cells']}")

            # Verify Parent Pointer matches what we recorded
            if curr_page_num != 0: # Skip root check
                expected_parent = child_to_parent_map.get(curr_page_num, -1)
                if node['parent'] != expected_parent:
                    print(f"  >>> CRITICAL ERROR: Page {curr_page_num} thinks parent is {node['parent']}, but it is actually child of {expected_parent}")

            if node['type'] == "INTERNAL":
                # Parse keys and children
                offset = HEADER_SIZE
                
                # Parse Right Child (First 4 bytes after header in InternalNode struct)
                # Wait, struct InternalNode { Header; uint32 rightChild; Cell cells[] }
                # So RightChild is at offset 8
                right_child = struct.unpack("I", node['data'][8:12])[0]
                
                # Check Double Parent Bug for Right Child
                if right_child in child_to_parent_map:
                     print(f"  >>> CRITICAL ERROR: Page {right_child} is owned by multiple parents! (Double Parent Bug)")
                child_to_parent_map[right_child] = curr_page_num
                queue.append(right_child)
                print(f"  -> Right Child: {right_child}")

                # Cells start after Header (8) + RightChild (4) = 12
                cell_offset = 12
                for i in range(node['num_cells']):
                    raw_cell = node['data'][cell_offset : cell_offset + INTERNAL_CELL_SIZE]
                    key, row_id, child_page = struct.unpack(INTERNAL_CELL_FMT, raw_cell)
                    
                    print(f"  -> Key: {key}, Child: {child_page}")
                    
                    if child_page in child_to_parent_map:
                        print(f"  >>> CRITICAL ERROR: Page {child_page} is owned by multiple parents! (Double Parent Bug)")
                    
                    child_to_parent_map[child_page] = curr_page_num
                    queue.append(child_page)
                    
                    cell_offset += INTERNAL_CELL_SIZE

            elif node['type'] == "LEAF":
                # Print Leaf Keys
                offset = HEADER_SIZE
                keys = []
                for i in range(node['num_cells']):
                    raw_cell = node['data'][offset : offset + LEAF_CELL_SIZE]
                    key, row_id = struct.unpack(LEAF_CELL_FMT, raw_cell)
                    keys.append(key)
                    offset += LEAF_CELL_SIZE
                print(f"  Keys: {keys}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python check_tree.py <filename>")
    else:
        verify_tree(sys.argv[1])