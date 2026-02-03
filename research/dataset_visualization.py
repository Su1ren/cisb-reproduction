import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import networkx as nx
import textwrap

# Set style for academic papers
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("colorblind")
OUTPUT_DIR = "figures"
HUB_RATIO_THRESHOLD = 10  # Define hub threshold ratio

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def load_data():
    # Load Introduction.csv
    # Skipping footer rows usually found in spreadsheets (checking for NaN in key columns)
    intro_df = pd.read_csv('Introduction.csv')
    intro_df = intro_df.dropna(subset=['Unique bug id']) # remove summary rows
    # Convert years to numeric just in case
    intro_df['Bug Residence'] = pd.to_numeric(intro_df['Bug Residence'], errors='coerce')
    
    # Load Regression.csv
    reg_df = pd.read_csv('Regression.csv')
    reg_df = reg_df.dropna(subset=['Unique bug id'])
    
    # Load Mitigation.csv
    mit_df = pd.read_csv('Mitigation.csv')
    mit_df = mit_df.dropna(subset=['Unique bug id'])
    # Clean up mitigation columns - replace NaN with 0, existing values with 1
    mit_cols = ['Normalization', 'Language/Hardware Mechanism', 'Compiler Flag', 'Blocking Optimizations']
    for col in mit_cols:
        mit_df[col] = mit_df[col].notna().astype(int)

    # Load CWEModel.csv
    cwe_df = pd.read_csv('CWEModel.csv')
    cwe_df = cwe_df.dropna(subset=['Unique bug id'])
    
    return intro_df, reg_df, mit_df, cwe_df

def plot_lifecycle(intro_df, reg_df):
    # 1. Distribution of Bug Residence Time
    plt.figure(figsize=(10, 6))
    sns.histplot(data=intro_df, x='Bug Residence', kde=True, bins=10)
    plt.title('Distribution of Bug Residence Time (Years)')
    plt.xlabel('Residence Time (Years)')
    plt.ylabel('Count of Bugs')
    plt.savefig(f'{OUTPUT_DIR}/1_residence_distribution.png', bbox_inches='tight')
    plt.close()

    # 2. Residence Time by Special Cause
    plt.figure(figsize=(12, 6))
    # Order by median residence time
    order = intro_df.groupby('Special Cause')['Bug Residence'].median().sort_values().index
    sns.boxplot(data=intro_df, x='Special Cause', y='Bug Residence', order=order)
    sns.swarmplot(data=intro_df, x='Special Cause', y='Bug Residence', order=order, color=".25", size=4)
    plt.title('Bug Residence Time by Special Cause Category')
    plt.savefig(f'{OUTPUT_DIR}/2_residence_by_cause.png', bbox_inches='tight')
    plt.close()

    # 3. Regression Analysis (Time to Recurrence)
    # Calculate recurrence interval assuming Regression Year and Fix Year exist
    # Note: Regression.csv format needs verification, assuming 'Regression Year' and 'Fix Year' columns
    if 'Regression Year' in reg_df.columns and 'Fix Year' in reg_df.columns:
        reg_df['Regression Year'] = pd.to_numeric(reg_df['Regression Year'], errors='coerce')
        reg_df['Fix Year'] = pd.to_numeric(reg_df['Fix Year'], errors='coerce')
        reg_df['Recurrence Interval'] = reg_df['Regression Year'] - reg_df['Fix Year']
        
        plt.figure(figsize=(8, 6))
        sns.stripplot(x=reg_df['Recurrence Interval'], jitter=True, size=10)
        plt.title('Time Interval Between Fix and Regression')
        plt.xlabel('Years until Regression')
        plt.xlim(left=0)
        plt.savefig(f'{OUTPUT_DIR}/3_regression_interval.png', bbox_inches='tight')
        plt.close()

def plot_mitigation(mit_df):
    # 4. Mitigation Effectiveness
    mit_cols = ['Normalization', 'Language/Hardware Mechanism', 'Compiler Flag', 'Blocking Optimizations']
    counts = mit_df[mit_cols].sum().sort_values(ascending=False)
    
    plt.figure(figsize=(10, 6))
    sns.barplot(x=counts.values, y=counts.index, orient='h')
    plt.title('Effectiveness of Mitigation Strategies (Count of Bugs Covered)')
    plt.xlabel('Number of Bugs')
    plt.savefig(f'{OUTPUT_DIR}/4_mitigation_effectiveness.png', bbox_inches='tight')
    plt.close()

def plot_cwe(cwe_df):
    # 5. Top CWEs
    # Filter out 'null' strings if any
    clean_cwe = cwe_df[cwe_df['CWE-ID'].astype(str) != 'null'].copy()
    top_cwes = clean_cwe['CWE-ID'].value_counts().head(10)
    
    plt.figure(figsize=(10, 6))
    sns.barplot(x=top_cwes.values, y=top_cwes.index, hue=top_cwes.index, palette='viridis', legend=False)
    plt.title('Top Common Weakness Enumerations (CWE)')
    plt.xlabel('Count')
    plt.savefig(f'{OUTPUT_DIR}/5_top_cwes.png', bbox_inches='tight')
    plt.close()

    # 6. Cause vs Consequence
    # Clean data
    role_counts = cwe_df['Cause or Consequence'].value_counts()
    
    plt.figure(figsize=(7, 7))
    plt.pie(role_counts, labels=role_counts.index, autopct='%1.1f%%', startangle=140, colors=sns.color_palette("pastel"))
    plt.title('Role of Bug in Vulnerability Model')
    plt.savefig(f'{OUTPUT_DIR}/6_cwe_role.png', bbox_inches='tight')
    plt.close()

def plot_cwe_hierarchy(file_path='CWEModel-update.csv'):
    if nx is None:
        print("NetworkX is not installed. Skipping CWE forest visualization.")
        return

    if not os.path.exists(file_path):
        print(f"File {file_path} not found. Skipping CWE forest visualization.")
        return

    print(f"Generating CWE Forest visualization from {file_path}...")
    
    # Load data
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return

    G = nx.DiGraph()
    
    # Tracking for labels
    node_metadata = {} # {cwe_id: {'desc': description, 'count': 0}}
    
    # Parse rows
    # Columns structure: [ID, Desc, ID, Desc, ...]
    # We iterate pairs starting from col index 2 (since 0=BugId, 1=Cause/Conseq)
    total_paths = 0
    node_traffic = {} # Count how many paths pass through this node
    
    for _, row in df.iterrows():
        path = []
        # Extract path nodes
        for i in range(2, len(df.columns), 2):
            if i + 1 >= len(df.columns):
                break
                
            cwe_id = str(row.iloc[i]).strip()
            desc = str(row.iloc[i+1]).strip()
            
            # Stop at empty cells
            if cwe_id.lower() in ['nan', 'none', ''] or desc.lower() in ['nan', 'none', '']:
                break
                
            path.append({'id': cwe_id, 'desc': desc})
            
            if cwe_id not in node_metadata:
                node_metadata[cwe_id] = {'desc': desc, 'count': 0}
        
        if not path:
            continue

        total_paths += 1
        
        # Track node traffic
        for node in path:
            node_id = node['id']
            node_traffic[node_id] = node_traffic.get(node_id, 0) + 1

        # Increment count for the start node (finest granularity)
        start_node_id = path[0]['id']
        node_metadata[start_node_id]['count'] += 1
        
        # Add edges: Coarse -> Fine (Parent -> Child)
        # Original data is V -> B -> C -> P (Fine -> Coarse)
        # We traverse reversed path to add edges: P -> C, C -> B, B -> V
        path_reversed = path[::-1]
        for i in range(len(path_reversed) - 1):
            u = path_reversed[i]['id']
            v = path_reversed[i+1]['id']
            if u != v:
                G.add_edge(u, v)
    
    # Visualization
    plt.figure(figsize=(24, 16))
    
    # Layout algorithm selection - Prioritize Dot
    pos = None
    try:
        # Try graphviz first (best for trees/hierarchies)
        pos = nx.nx_agraph.graphviz_layout(G, prog='dot')
    except:
        try:
             # Fallback to pydot
             pos = nx.nx_pydot.graphviz_layout(G, prog='dot')
        except:
            # Fallback to standard networkx layouts if graphviz is missing
            print("Graphviz layout not available, using shell/spring layout (may be less optimal).")
            # Shell layout might be better for hierarchy than spring if dot fails
            pos = nx.shell_layout(G)

    # Prepare labels and sizes
    labels = {}
    node_sizes = []
    hub_threshold = total_paths / HUB_RATIO_THRESHOLD if total_paths > 0 else 0
    base_size = 5000
    
    for node in G.nodes():
        meta = node_metadata.get(node, {'desc': '', 'count': 0})
        desc = meta['desc']
        count = meta['count']
        traffic = node_traffic.get(node, 0)
        
        # Criteria for showing description:
        # 1. Start node (count > 0) [These are leaf nodes in Coarse->Fine graph]
        # 2. Hub node: Traffic >= hub_threshold (High aggregation)
        # 3. Root node (In-degree == 0 in Coarse->Fine graph)
        in_deg = G.in_degree(node)
        
        is_hub = traffic >= hub_threshold
        is_root = in_deg == 0
        has_count = count > 0
        
        # Calculate node size based on count
        # Base size + (count * multiplier)
        current_size = base_size
        if has_count:
            current_size += (count * 500) # Adjust multiplier as needed
        node_sizes.append(current_size)
        
        label_text = f"{node}"
        if has_count or is_hub or is_root:
            # Wrap description if too long
            short_desc = textwrap.fill(desc, width=20)
            label_text += f"\n{short_desc}"
            
        if has_count:
            label_text += f"\n(n={count})"
            
        labels[node] = label_text

    # Draw
    # Draw nodes
    # Color hubs differently? Optional, but keeping lightblue for now
    node_colors = ['#ff9999' if node_traffic.get(n, 0) >= hub_threshold else 'lightblue' for n in G.nodes()]
    nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color=node_colors, alpha=0.9)
    
    # Draw edges
    # Note: node_size for edges helps terminate the edge before the node center. 
    # Since node_sizes is a list, we might need to be careful. networkx documentation says node_size can be array.
    nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True, arrowsize=20, node_size=node_sizes)
    
    # Draw labels
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=9, font_weight='bold')
    
    plt.title("CWE Hierarchy Forest (Arrow: Coarse -> Fine)", fontsize=18)
    plt.axis('off')
    
    out_path = f'{OUTPUT_DIR}/cwe_hierarchy_forest.png'
    plt.savefig(out_path, bbox_inches='tight', dpi=300)
    plt.close()
    print(f"Saved CWE forest plot to {out_path}")

if __name__ == "__main__":
    try:
        print("Loading data...")
        # intro, reg, mit, cwe = load_data()
        
        print("Generating Lifecycle plots...")
        # plot_lifecycle(intro, reg)
        
        print("Generating Mitigation plots...")
        # plot_mitigation(mit)
        
        print("Generating CWE Model plots...")
        # plot_cwe(cwe)

        # Generate CWE Forest
        plot_cwe_hierarchy()
        
        print(f"All plots saved to {os.path.abspath(OUTPUT_DIR)}")
    except Exception as e:
        print(f"An error occurred: {e}")
