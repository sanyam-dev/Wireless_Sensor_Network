import numpy as np
import networkx as nx
import cma

# Define the objective function to optimize
def graph_objective_function(params):
    # Extract the graph rewiring parameters from the CMA-ES parameters
    alpha, beta = params

    # Rewire the graph with the given parameters
    rewire_graph(alpha, beta)

    # Compute the average path length and average clustering coefficient of the graph
    avg_path_length = nx.average_shortest_path_length(G)
    avg_clustering_coefficient = nx.average_clustering(G)

    # Return the negative weighted sum of the objectives to minimize (negative because CMA-ES minimizes)
    return [-avg_path_length, -avg_clustering_coefficient]

# Function to rewire the graph with the given parameters
def rewire_graph(alpha, beta):
    # Rewire the graph by adding and removing edges based on the given parameters

    # Add edges with probability alpha
    for node in G.nodes():
        if np.random.rand() < alpha:
            neighbors = list(G.neighbors(node))
            if len(neighbors) > 1:
                u, v = np.random.choice(neighbors, size=2, replace=False)
                G.remove_edge(node, u)
                G.add_edge(node, v)

    # Remove edges with probability beta
    for node in G.nodes():
        if np.random.rand() < beta:
            neighbors = list(G.neighbors(node))
            if len(neighbors) > 0:
                u = np.random.choice(neighbors)
                G.remove_edge(node, u)

# Create an initial graph
G = nx.random_regular_graph(4, 20)

# Define the CMA-ES parameters
cmaes_opts = {'bounds': [[0, 1], [0, 1]], 'seed': 0}

# Run the CMA-ES optimization
es = cma.CMAEvolutionStrategy(2 * [0.5], 0.1, inopts=cmaes_opts)
while not es.stop():
    solutions = es.ask()
    fitness_values = []
    for sol in solutions:
        fitness_values.append(graph_objective_function(sol))
    es.tell(solutions, fitness_values)
    es.disp()

# Extract the best solution from the CMA-ES optimization
best_solution = es.best.x

# Rewire the graph with the best solution
alpha, beta = best_solution
rewire_graph(alpha, beta)

# Compute the final average path length and average clustering coefficient of the graph
final_avg_path_length = nx.average_shortest_path_length(G)
final_avg_clustering_coefficient = nx.average_clustering(G)

print("Final Average Path Length: ", final_avg_path_length)
print("Final Average Clustering Coefficient: ", final_avg_clustering_coefficient)
