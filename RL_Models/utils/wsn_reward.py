import numpy as np
import networkx as nx
from typing import Dict, List, Tuple

class WSNRewardFunction:
    """
    Practical WSN reward function implementation that can be directly integrated
    into your existing environment
    """

    def __init__(self, network):
        self.network = network
        self.initial_total_energy = self._calculate_initial_energy()

        # Normalization bounds (you may need to adjust these based on your network)
        self.max_possible_apl = min(network.number_of_nodes, 20)  # Reasonable upper bound
        self.min_possible_apl = 2.0

        # Weight configuration (you can tune these)
        self.weights = {
            'energy_efficiency': 0.25,      # Energy consumption per edge
            'network_lifetime': 0.25,       # Energy balance and minimum energy
            'connectivity': 0.20,           # Clustering + path length (your original)
            'load_balance': 0.15,           # Energy distribution fairness
            'topology_quality': 0.15        # Network properties (degree distribution, etc.)
        }

        # Track metrics for adaptive behavior
        self.step_count = 0
        self.energy_history = []

    def calculate_reward(self, edge_repeat: bool, action=None) -> float:
        """
        Main reward calculation function - drop-in replacement for your get_reward
        """
        if edge_repeat:
            return -10.0  # Strong penalty for invalid actions

        # Calculate individual reward components
        r_energy = self._energy_efficiency_reward(action)
        r_lifetime = self._network_lifetime_reward()
        r_connectivity = self._connectivity_reward()
        r_balance = self._load_balance_reward()
        r_topology = self._topology_quality_reward()

        # Weighted combination
        total_reward = (
            self.weights['energy_efficiency'] * r_energy +
            self.weights['network_lifetime'] * r_lifetime +
            self.weights['connectivity'] * r_connectivity +
            self.weights['load_balance'] * r_balance +
            self.weights['topology_quality'] * r_topology
        )

        # Apply penalties
        penalty = self._calculate_penalties()
        final_reward = total_reward - penalty

        # Update tracking
        self.step_count += 1
        self._update_tracking()

        # Optional: Print debug info every 10 steps
        if self.step_count % 10 == 0:
            self._print_reward_breakdown(r_energy, r_lifetime, r_connectivity,
                                       r_balance, r_topology, penalty, final_reward)

        return round(final_reward, 4)

    def _energy_efficiency_reward(self, action) -> float:
        """
        Reward based on energy efficiency of the action and current energy state
        """
        # Current total energy ratio
        current_energy = sum(max(node.current_energy, 0) for node in self.network.node_list if node.id != 0)
        energy_ratio = current_energy / self.initial_total_energy if self.initial_total_energy > 0 else 0

        # Energy cost of the last added edge
        edge_cost_reward = 0.0
        if hasattr(self.network, 'edges_added') and len(self.network.edges_added) > 0:
            try:
                last_edge = self.network.edges_added[-1]
                if len(last_edge) >= 2:
                    node1_id, node2_id = last_edge[0], last_edge[1]

                    # Handle both node objects and IDs
                    if hasattr(node1_id, 'id'):
                        node1 = node1_id
                        node2 = node2_id
                    else:
                        node1 = self.network.node_map.get(node1_id)
                        node2 = self.network.node_map.get(node2_id)

                    if node1 and node2:
                        distance = node1.dist(node2)
                        energy_cost = node1.energy_for_transmission(self.network.packet_length, distance)

                        # Normalize energy cost (lower cost = higher reward)
                        max_energy = node1.initial_energy
                        normalized_cost = energy_cost / max_energy if max_energy > 0 else 1.0
                        edge_cost_reward = max(0.0, 1.0 - normalized_cost)
            except Exception as e:
                edge_cost_reward = 0.0

        # Combine energy preservation and edge efficiency
        efficiency_reward = 0.7 * energy_ratio + 0.3 * edge_cost_reward

        return max(0.0, min(1.0, efficiency_reward))

    def _network_lifetime_reward(self) -> float:
        """
        Reward based on energy balance and predicted network lifetime
        """
        energies = [node.current_energy for node in self.network.node_list if node.id != 0]

        if not energies:
            return 0.0

        # Minimum energy (bottleneck node)
        min_energy = min(energies)
        initial_energy = self.network.node_list[1].initial_energy if self.network.node_list else 1.0
        min_energy_ratio = min_energy / initial_energy if initial_energy > 0 else 0

        # Energy variance (lower is better for balanced consumption)
        energy_variance = np.var(energies) if len(energies) > 1 else 0
        max_variance = (initial_energy ** 2) if initial_energy > 0 else 1
        normalized_variance = min(energy_variance / max_variance, 1.0) if max_variance > 0 else 0
        balance_reward = 1.0 - normalized_variance

        # Average energy level
        avg_energy_ratio = np.mean([e / initial_energy for e in energies]) if initial_energy > 0 else 0

        # Combine: bottleneck protection + energy balance + overall energy level
        lifetime_reward = 0.4 * min_energy_ratio + 0.3 * balance_reward + 0.3 * avg_energy_ratio

        return max(0.0, min(1.0, lifetime_reward))

    def _connectivity_reward(self) -> float:
        """
        Your original connectivity reward but properly normalized
        """
        try:
            acc = self.network.acc
            apl = self.network.apl

            # Normalize clustering coefficient (already in [0,1])
            normalized_acc = max(0.0, min(1.0, acc))

            # Normalize average path length (lower is better)
            if apl > 0:
                normalized_apl = max(0.0, min(1.0,
                    (self.max_possible_apl - apl) / (self.max_possible_apl - self.min_possible_apl)
                ))
            else:
                normalized_apl = 0.0

            # Small-world coefficient (your original intuition)
            small_world = normalized_acc / apl if apl > 0 else 0
            normalized_small_world = min(small_world, 1.0)

            # Network connectivity check
            try:
                is_connected = nx.is_connected(self.network.nxg)
                connectivity_bonus = 1.0 if is_connected else 0.5
            except:
                connectivity_bonus = 0.5

            # Combine metrics
            connectivity_reward = (0.3 * normalized_acc +
                                 0.4 * normalized_apl +
                                 0.2 * normalized_small_world +
                                 0.1 * connectivity_bonus)

            return max(0.0, min(1.0, connectivity_reward))

        except Exception as e:
            return 0.0

    def _load_balance_reward(self) -> float:
        """
        Reward for balanced energy consumption across nodes
        """
        try:
            # Calculate energy depletion for each node
            energy_depletions = []
            for node in self.network.node_list:
                if node.id != 0:  # Exclude sink
                    depletion_ratio = (node.initial_energy - node.current_energy) / node.initial_energy
                    energy_depletions.append(max(0.0, depletion_ratio))

            if len(energy_depletions) <= 1:
                return 1.0

            # Calculate standard deviation of energy depletions
            std_depletion = np.std(energy_depletions)

            # Normalize (lower std = better balance = higher reward)
            max_possible_std = 0.5  # Reasonable upper bound
            normalized_std = min(std_depletion / max_possible_std, 1.0) if max_possible_std > 0 else 0
            balance_reward = 1.0 - normalized_std

            return max(0.0, min(1.0, balance_reward))

        except Exception as e:
            return 0.5

    def _topology_quality_reward(self) -> float:
        """
        Reward for good network topology properties
        """
        try:
            # Node degree distribution
            degrees = [self.network.nxg.degree(node) for node in self.network.nxg.nodes() if node != 0]

            if not degrees:
                return 0.0

            # Prefer moderate, balanced degree distribution
            avg_degree = np.mean(degrees)
            degree_variance = np.var(degrees)

            # Ideal average degree (not too sparse, not too dense)
            ideal_avg_degree = max(3, min(8, np.sqrt(self.network.number_of_nodes)))
            degree_reward = max(0.0, 1.0 - abs(avg_degree - ideal_avg_degree) / ideal_avg_degree)

            # Lower degree variance is better (more balanced)
            max_variance = (ideal_avg_degree ** 2)
            variance_reward = max(0.0, 1.0 - min(degree_variance / max_variance, 1.0)) if max_variance > 0 else 0

            # Network diameter (shorter is generally better for WSN)
            try:
                diameter = nx.diameter(self.network.nxg)
                max_diameter = min(self.network.number_of_nodes, 15)
                diameter_reward = max(0.0, (max_diameter - diameter) / max_diameter) if max_diameter > 0 else 0
            except:
                diameter_reward = 0.5

            # Combine topology metrics
            topology_reward = 0.4 * degree_reward + 0.3 * variance_reward + 0.3 * diameter_reward

            return max(0.0, min(1.0, topology_reward))

        except Exception as e:
            return 0.5

    def _calculate_penalties(self) -> float:
        """
        Calculate penalties for undesirable behaviors
        """
        penalty = 0.0

        try:
            # Penalty for network fragmentation
            try:
                num_components = nx.number_connected_components(self.network.nxg)
                if num_components > 1:
                    penalty += 0.2 * (num_components - 1) / self.network.number_of_nodes
            except:
                pass

            # Penalty for nodes with very low energy
            critical_nodes = sum(1 for node in self.network.node_list
                               if node.id != 0 and node.current_energy < 0.1 * node.initial_energy)
            if critical_nodes > 0:
                penalty += 0.1 * critical_nodes / self.network.number_of_nodes

            # Penalty for excessive edge additions (over-connectivity)
            if hasattr(self.network, 'edges_added'):
                total_possible_edges = self.network.number_of_nodes * (self.network.number_of_nodes - 1) // 2
                edge_density = len(self.network.edges_added) / total_possible_edges if total_possible_edges > 0 else 0
                if edge_density > 0.3:  # More than 30% of possible edges
                    penalty += 0.1 * (edge_density - 0.3)

        except Exception as e:
            penalty = 0.0

        return min(penalty, 0.5)  # Cap penalty

    def _calculate_initial_energy(self) -> float:
        """Calculate initial total energy in the network"""
        try:
            return sum(node.initial_energy for node in self.network.node_list if node.id != 0)
        except:
            print("[EXCEPTION] : _calculate_initial_energy method raised exception")
            return self.network.number_of_nodes * 1000  # Default assumption

    def _update_tracking(self):
        """Update internal tracking variables"""
        try:
            current_energy = sum(max(node.current_energy, 0) for node in self.network.node_list if node.id != 0)
            self.energy_history.append(current_energy)

            # Keep only recent history
            if len(self.energy_history) > 100:
                self.energy_history = self.energy_history[-50:]
        except:
            pass

    def _print_reward_breakdown(self, r_energy, r_lifetime, r_connectivity,
                               r_balance, r_topology, penalty, final_reward):
        """Print detailed reward breakdown for debugging"""
        print(f"\n=== Reward Breakdown (Step {self.step_count}) ===")
        print(f"Energy Efficiency: {r_energy:.3f} (weight: {self.weights['energy_efficiency']:.2f})")
        print(f"Network Lifetime:  {r_lifetime:.3f} (weight: {self.weights['network_lifetime']:.2f})")
        print(f"Connectivity:      {r_connectivity:.3f} (weight: {self.weights['connectivity']:.2f})")
        print(f"Load Balance:      {r_balance:.3f} (weight: {self.weights['load_balance']:.2f})")
        print(f"Topology Quality:  {r_topology:.3f} (weight: {self.weights['topology_quality']:.2f})")
        print(f"Penalty:           -{penalty:.3f}")
        print(f"Final Reward:      {final_reward:.3f}")
        print(f"Network: ACC={self.network.acc:.3f}, APL={self.network.apl:.3f}")
        print("="*50)

# Integration function for your existing env.py
def integrate_with_existing_env(env_instance):
    """
    Function to integrate the new reward system with your existing environment
    """
    # Initialize the reward calculator
    env_instance.reward_calculator = WSNRewardFunction(env_instance.net)

    # Replace the get_reward method
    def new_get_reward(edge_repeat, action=None):
        return env_instance.reward_calculator.calculate_reward(edge_repeat, action)

    # Monkey patch the method
    env_instance.get_reward = new_get_reward

    return env_instance

