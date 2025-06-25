"""
Test script to validate and compare the new reward function
Run this to ensure everything is working correctly
"""

import numpy as np
import matplotlib.pyplot as plt
from core import env
import time

def old_reward_function(env_instance, edge_repeat):
	"""Your original reward function for comparison"""
	if edge_repeat:
		return -10
	acc = env_instance.acc
	apl = env_instance.apl
	w1 = 1
	w2 = 1
	reward = w1*acc + w2*(1/apl)
	return round(reward, 3)

def test_reward_functions(logger):
    """
    Test both old and new reward functions
    """
    logger.log("Initializing environment...")
    env1 = env()
    env1.set_nxg()

    logger.log(f"Initial network state:")
    logger.log(f"  Nodes: {env1.net.number_of_nodes}")
    logger.log(f"  ACC: {env1.acc:.3f}")
    logger.log(f"  APL: {env1.apl:.3f}")
    logger.log(f"  Action space size: {env1.action_space_n}")

    # Test both reward functions on the same actions
    num_test_actions = min(20, env1.action_space_n)
    old_rewards = []
    new_rewards = []
    actions_tested = []

    logger.log(f"\nTesting {num_test_actions} random actions...")

    for i in range(num_test_actions):
        # Reset environment to initial state
        env1.reset()

        # Choose a random action
        action_idx = np.random.randint(0, env1.action_space_n)
        actions_tested.append(action_idx)

        # Execute action and record states
        observation_, _ = env1.step(action_idx)

        # Calculate old reward
        old_reward = old_reward_function(env1, False)
        old_rewards.append(old_reward)

        # Calculate new reward (already calculated in step, but let's be explicit)
        new_reward = env1.reward_calculator.calculate_reward(False)
        new_rewards.append(new_reward)

        logger.log(f"Action {i+1}: Old={old_reward:.3f}, New={new_reward:.3f}, "
              f"ACC={env1.acc:.3f}, APL={env1.apl:.3f}")

    return old_rewards, new_rewards, actions_tested

def analyze_reward_differences(old_rewards, new_rewards, logger):
    """
    Analyze differences between old and new reward functions
    """
    old_rewards = np.array(old_rewards)
    new_rewards = np.array(new_rewards)

    logger.log(f"\n=== Reward Function Analysis ===")
    logger.log(f"Old Reward - Mean: {np.mean(old_rewards):.3f}, Std: {np.std(old_rewards):.3f}")
    logger.log(f"New Reward - Mean: {np.mean(new_rewards):.3f}, Std: {np.std(new_rewards):.3f}")
    logger.log(f"Correlation: {np.corrcoef(old_rewards, new_rewards)[0,1]:.3f}")

    # Plot comparison
    plt.figure(figsize=(15, 5))

    # Subplot 1: Reward comparison
    plt.subplot(1, 3, 1)
    plt.scatter(old_rewards, new_rewards, alpha=0.7)
    plt.xlabel('Old Reward')
    plt.ylabel('New Reward')
    plt.title('Old vs New Reward')
    plt.plot([min(old_rewards), max(old_rewards)],
             [min(old_rewards), max(old_rewards)], 'r--', alpha=0.5)

    # Subplot 2: Reward distributions
    plt.subplot(1, 3, 2)
    plt.hist(old_rewards, alpha=0.7, label='Old', bins=10)
    plt.hist(new_rewards, alpha=0.7, label='New', bins=10)
    plt.xlabel('Reward Value')
    plt.ylabel('Frequency')
    plt.title('Reward Distributions')
    plt.legend()

    # Subplot 3: Reward difference
    plt.subplot(1, 3, 3)
    reward_diff = new_rewards - old_rewards
    plt.plot(reward_diff, 'o-')
    plt.xlabel('Action Index')
    plt.ylabel('New - Old Reward')
    plt.title('Reward Difference')
    plt.axhline(y=0, color='r', linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.savefig('reward_comparison.png', dpi=300, bbox_inches='tight')
    plt.show()

    return reward_diff

def test_reward_components(logger):
    """
    Test individual components of the new reward function
    """
    logger.log("\n=== Testing Reward Components ===")
    env1 = env()
    env1.set_nxg()

    # Test normal action
    action_idx = np.random.randint(0, min(env1.action_space_n, 10))
    env1.step(action_idx)

    # Access individual reward components
    calc = env1.reward_calculator

    r_energy = calc._energy_efficiency_reward(None)
    r_lifetime = calc._network_lifetime_reward()
    r_connectivity = calc._connectivity_reward()
    r_balance = calc._load_balance_reward()
    r_topology = calc._topology_quality_reward()
    penalty = calc._calculate_penalties()

    logger.log(f"Energy Efficiency: {r_energy:.3f}")
    logger.log(f"Network Lifetime:  {r_lifetime:.3f}")
    logger.log(f"Connectivity:      {r_connectivity:.3f}")
    logger.log(f"Load Balance:      {r_balance:.3f}")
    logger.log(f"Topology Quality:  {r_topology:.3f}")
    logger.log(f"Penalty:           {penalty:.3f}")

    # Test edge repeat penalty
    repeat_reward = calc.calculate_reward(True)
    logger.log(f"Edge Repeat Penalty: {repeat_reward}")

    return {
        'energy': r_energy,
        'lifetime': r_lifetime,
        'connectivity': r_connectivity,
        'balance': r_balance,
        'topology': r_topology,
        'penalty': penalty
    }

def test_weight_adjustment(logger):
    """
    Test adjusting reward weights
    """
    logger.log("\n=== Testing Weight Adjustment ===")
    env1 = env()
    env1.set_nxg()

    # Test with different weight configurations
    weight_configs = [
        {'energy': 0.5, 'lifetime': 0.2, 'connectivity': 0.1, 'balance': 0.1, 'topology': 0.1},  # Energy focused
        {'energy': 0.1, 'lifetime': 0.1, 'connectivity': 0.6, 'balance': 0.1, 'topology': 0.1},  # Connectivity focused
        {'energy': 0.2, 'lifetime': 0.4, 'connectivity': 0.2, 'balance': 0.1, 'topology': 0.1},  # Lifetime focused
    ]

    action_idx = np.random.randint(0, min(env1.action_space_n, 5))

    for i, config in enumerate(weight_configs):
        env1.reset()
        env1.set_reward_weights(**config)
        env1.step(action_idx)

        reward = env1.get_reward(False)
        logger.log(f"Config {i+1} (Energy={config['energy']:.1f}): Reward={reward:.3f}")

def performance_test(logger):
    """
    Test computational performance of new reward function
    """
    logger.log("\n=== Performance Test ===")
    env1 = env()
    env1.set_nxg()

    num_iterations = 100

    # Time old reward function
    start_time = time.time()
    for _ in range(num_iterations):
        old_reward_function(env1, False)
    old_time = time.time() - start_time

    # Time new reward function
    start_time = time.time()
    for _ in range(num_iterations):
        env1.reward_calculator.calculate_reward(False)
    new_time = time.time() - start_time

    logger.log(f"Old reward function: {old_time:.4f}s for {num_iterations} calls")
    logger.log(f"New reward function: {new_time:.4f}s for {num_iterations} calls")
    logger.log(f"Slowdown factor: {new_time/old_time:.2f}x")

def log_test_results(log_content, log_filename="test_log.txt"):
    """
    Create a descriptive log of the test and store it in a log sub-directory in rl-ppo-1.
    If the directory does not exist, it will be created.
    """
    import os
    from datetime import datetime

    script_dir = os.path.dirname(os.path.abspath(__file__))
    log_dir = os.path.join(script_dir, "log")
    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    full_log_filename = f"{timestamp}_{log_filename}"
    log_path = os.path.join(log_dir, full_log_filename)
    with open(log_path, "w") as f:
        f.write(log_content)
    print(f"Test log saved to {log_path}")

# --- Logging helper ---
class Logger:
    def __init__(self):
        self.lines = []
    def log(self, msg):
        print(msg)
        self.lines.append(str(msg))
    def get_log(self):
        return "\n".join(self.lines)

if __name__ == "__main__":
    logger = Logger()
    logger.log("Starting comprehensive reward function testing...")

    # Test 1: Compare old vs new rewards
    old_rewards, new_rewards, actions = test_reward_functions(logger)
    reward_diff = analyze_reward_differences(old_rewards, new_rewards, logger)

    # Test 2: Individual components
    components = test_reward_components(logger)

    # Test 3: Weight adjustment
    test_weight_adjustment(logger)

    # Test 4: Performance
    performance_test(logger)

    logger.log("\nTesting complete! Check 'reward_comparison.png' for visualizations.")
    logger.log("\nKey observations:")
    logger.log(f"- New reward range: [{min(new_rewards):.3f}, {max(new_rewards):.3f}]")
    logger.log(f"- Old reward range: [{min(old_rewards):.3f}, {max(old_rewards):.3f}]")
    logger.log(f"- Average difference: {np.mean(reward_diff):.3f}")

    # Recommendations
    logger.log("\nRecommendations:")
    if np.std(new_rewards) > np.std(old_rewards):
        logger.log("✓ New reward has higher variance - better for RL exploration")
    if any(comp > 0.8 for comp in components.values()):
        logger.log("✓ Some reward components are near maximum - good range utilization")
    if components['penalty'] < 0.1:
        logger.log("✓ Low penalty suggests network is in good state")

    logger.log("\nNext steps:")
    logger.log("1. Run training with new reward function")
    logger.log("2. Monitor reward components during training")
    logger.log("3. Adjust weights based on learning progress")
    logger.log("4. Compare final network performance metrics")

    # --- LOGGING SECTION ---
    log_test_results(logger.get_log())