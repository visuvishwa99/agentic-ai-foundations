import os
import json
import networkx as nx
from pyvis.network import Network
import matplotlib.pyplot as plt

class GraphBuilder:
    def __init__(self, data_file: str):
        self.data_file = data_file
        self.nx_graph = nx.DiGraph() # Directed Graph

    def load_graph(self):
        """Loads nodes/edges from JSON."""
        if not os.path.exists(self.data_file):
            print(f"❌ Graph data file not found: {self.data_file}")
            return False

        with open(self.data_file, 'r') as f:
            data = json.load(f)
            
        # Add Nodes
        for node in data.get("nodes", []):
            self.nx_graph.add_node(node["id"], type=node.get("type", "table"))
            
        # Add Edges
        for edge in data.get("edges", []):
            self.nx_graph.add_edge(edge["source"], edge["target"])
            
        print(f"🕸️ Graph Loaded: {self.nx_graph.number_of_nodes()} Nodes, {self.nx_graph.number_of_edges()} Edges")
        return True

    def analyze_graph(self):
        """Calculates basic graph metrics."""
        if self.nx_graph.number_of_nodes() == 0:
            return

        print("\n📊 Graph Analysis:")
        
        # 1. Degree Centrality (Most connected nodes)
        try:
            centrality = nx.degree_centrality(self.nx_graph)
            # Sort by centrality score
            top_nodes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:3]
            
            print("   🏆 Central Nodes (Most Dependencies):")
            for node, score in top_nodes:
                print(f"      - {node}: {score:.4f}")
        except Exception as e:
            print(f"   ⚠️ Could not calculate centrality: {e}")
            
        # 2. Cycles (Lineage Loops = Bad)
        try:
            cycles = list(nx.simple_cycles(self.nx_graph))
            if cycles:
                print(f"   ⚠️ WARNING: Circular Dependency Detected! {cycles}")
            else:
                print("   ✅ Lineage is acyclic (No loops).")
        except Exception as e:
             print(f"   ⚠️ Error checking cycles: {e}")

    def get_upstream(self, table_name: str):
        """Finds all tables that 'table_name' depends on."""
        if table_name not in self.nx_graph:
            print(f"   ❌ Table '{table_name}' not found.")
            return []
            
        deps = list(nx.ancestors(self.nx_graph, table_name))
        print(f"   ⬆️ Upstream Dependencies for '{table_name}': {deps}")
        return deps

    def get_downstream(self, table_name: str):
        """Finds all tables that depend on 'table_name'."""
        if table_name not in self.nx_graph:
            print(f"   ❌ Table '{table_name}' not found.")
            return []
            
        deps = list(nx.descendants(self.nx_graph, table_name))
        print(f"   ⬇️ Downstream Impact for '{table_name}': {deps}")
        return deps

    def visualize(self, output_file="lineage_graph.html"):
        """Generates interactive HTML graph."""
        if self.nx_graph.number_of_nodes() == 0:
            return

        try:
            net = Network(notebook=False, height="500px", width="100%", bgcolor="#222222", font_color="white", directed=True)
            # Add nodes/edges manually to pyvis network from nx graph to preserve attributes if needed
            # Or use from_nx directly
            net.from_nx(self.nx_graph)
            
            # Save
            net.save_graph(output_file)
            print(f"\n🎨 Visualization saved to: {output_file}")
            print(f"   Opening visualization...")
            # Automatically try to open in browser? (Optional)
            # os.system(f"start {output_file}")
        except Exception as e:
            print(f"   ⚠️ visualization failed: {e}")

if __name__ == "__main__":
    # Path to graph data
    json_path = os.path.join(os.path.dirname(__file__), "graph_data.json")
    
    builder = GraphBuilder(json_path)
    
    if builder.load_graph():
        builder.analyze_graph()
        
        # Test Dependency Check
        print("\n🔍 Dependency Checks:")
        builder.get_upstream("fct_orders")
        builder.get_downstream("dim_users")
        
        # Visualize
        viz_path = os.path.join(os.path.dirname(__file__), "lineage_graph.html")
        builder.visualize(viz_path)
