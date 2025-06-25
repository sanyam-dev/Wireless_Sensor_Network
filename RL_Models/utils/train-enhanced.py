"""
Modified training loop with comprehensive reward monitoring and adaptive weights
Replace your existing train.py main loop with this enhanced version
"""

import time
import numpy as np
from RL import Agent
from env import env
from wsn_reward import integrate_with_existing_env
import os
import matplotlib.pyplot as plt
import json

def enhanced_training_loop():
	"""
	Enhanced training loop with comprehensive reward monitoring
	"""
	# Training parameters
	N = 20  # Number of episodes
	batch_size = 64
	n_epochs = 20
	alpha = 0.0003

	# Initialize environment with new reward function
	env1 = env()
	env1 = integrate_with_existing_env(env1)
	env1.set_nxg()

	# Initialize agent
	agent = Agent(n_actions=env1.action_space_n, batch_size=batch_size,
				alpha=alpha, n_epochs=n_epochs,
				input_dims=[env1.get_observation_space_shape()])

	# Setup directories
	path = create_training_directories()

	# Training metrics tracking
	training_metrics = {
		'episode_rewards': [],
		'reward_components': [],
		'network_metrics': [],
		'energy_metrics': [],
		'learning_metrics': []
	}

	print(f"Starting enhanced training with {N} episodes...")
	print(f"Initial network: ACC={env1.acc:.3f}, APL={env1.apl:.3f}")
	print(f"Action space size: {env1.action_space_n}")

	best_score = -float('inf')
	learn_iters = 0
	n_steps = 0

	for episode in range(N):
		print(f"\n{'='*50}")
		print(f"Episode {episode + 1}/{N}")
		print(f"{'='*50}")

		# Reset environment
		env1.reset()
		observation_flatten = env1.flatten_obs_sp()

		# Example usage in your training loop:
		"""
		# In your main training file, replace this:
		# env1 = env()

		# With this:

		# Now your environment will use the comprehensive reward function!
		# You can also adjust weights:
		env1.reward_calculator.weights['energy_efficiency'] = 0.35  # Increase energy focus
		env1.reward_calculator.weights['connectivity'] = 0.15       # Decrease connectivity focus
		"""

		# Episode variables
		episode_score = 0
		episode_steps = 0
		episode_reward_components = []
		episode_energy_history = []
		invalid_actions = 0

		# Adaptive weight adjustment based on episode progress
		adjust_reward_weights(env1, episode, N)

		number_of_edges = 200  # Maximum edges per episode
		done = 0

		while done < number_of_edges:
			# Store initial energy state
			initial_energies = [node.current_energy for node in env1.net.node_list if node.id != 0]

			# Agent action selection
			action, prob, val = agent.choose_action(observation_flatten)

			# Environment step
			observation_, reward = env1.step(action)

			# Store experience
			agent.remember(observation_flatten, action, prob, val, reward, done)

			# Learning
			if n_steps % batch_size == 0 and n_steps > 0:
				agent.learn()
				learn_iters += 1

			# Detailed reward component tracking
			if reward != -10:  # Valid action
				components = extract_reward_components(env1)
				episode_reward_components.append(components)

				# Energy tracking
				final_energies = [node.current_energy for node in env1.net.node_list if node.id != 0]
				energy_change = sum(initial_energies) - sum(final_energies)
				episode_energy_history.append({
					'step': done,
					'total_energy': sum(final_energies),
					'energy_change': energy_change,
					'min_energy': min(final_energies),
					'avg_energy': np.mean(final_energies)
				})

				print(f"Step {done}: Reward={reward:.3f}, ACC={env1.acc:.3f}, "
					f"APL={env1.apl:.3f}, Energy={sum(final_energies):.0f}")
			else:
				invalid_actions += 1
				print(f"Step {done}: Invalid action (repeat edge)")

			# Update for next step
			observation_flatten = observation_
			episode_score += reward
			episode_steps += 1
			done += 1
			n_steps += 1

		# Episode summary
		print(f"\nEpisode {episode + 1} Summary:")
		print(f"  Total reward: {episode_score:.3f}")
		print(f"  Valid actions: {episode_steps - invalid_actions}/{episode_steps}")
		print(f"  Final ACC: {env1.acc:.3f}, APL: {env1.apl:.3f}")
		print(f"  Learning iterations: {learn_iters}")

		# Store episode metrics
		training_metrics['episode_rewards'].append(episode_score)
		training_metrics['reward_components'].append(episode_reward_components)
		training_metrics['network_metrics'].append({
			'episode': episode,
			'acc': env1.acc,
			'apl': env1.apl,
			'edges_added': len(env1.edges_added),
			'invalid_actions': invalid_actions
		})
		training_metrics['energy_metrics'].append(episode_energy_history)
		training_metrics['learning_metrics'].append({
			'episode': episode,
			'learn_iters': learn_iters,
			'n_steps': n_steps
		})

		# Save episode results
		env1.save_graph(path, episode)
		env1.save_graph_npy(path, episode)

		# Update best score
		if episode_score > best_score:
			best_score = episode_score
			agent.save_models()
			print(f"  New best score! Saved models.")

	# Training complete - generate comprehensive analysis
	print(f"\n{'='*50}")
	print("Training Complete!")
	print(f"{'='*50}")

	generate_training_analysis(training_metrics, path)
	plot_training_progress(training_metrics, path)

	return training_metrics, agent, env1

def adjust_reward_weights(env1, episode, total_episodes):
	"""
	Dynamically adjust reward weights based on training progress
	"""
	progress = episode / total_episodes

	if progress < 0.3:  # Early training: Focus on connectivity
		env1.set_reward_weights(
			energy=0.15, lifetime=0.15, connectivity=0.40,
			balance=0.15, topology=0.15
		)
		print("Early training: Emphasizing connectivity")
	elif progress < 0.7:  # Mid training: Balance energy and connectivity
		env1.set_reward_weights(
			energy=0.25, lifetime=0.25, connectivity=0.25,
			balance=0.15, topology=0.10
		)
		print("Mid training: Balancing energy and connectivity")
	else:  # Late training: Focus on energy efficiency and lifetime
		env1.set_reward_weights(
			energy=0.35, lifetime=0.30, connectivity=0.15,
			balance=0.15, topology=0.05
		)
		print("Late training: Emphasizing energy efficiency")

def extract_reward_components(env1):
	"""
	Extract individual reward components for analysis
	"""
	calc = env1.reward_calculator
	return {
		'energy': calc._energy_efficiency_reward(None),
		'lifetime': calc._network_lifetime_reward(),
		'connectivity': calc._connectivity_reward(),
		'balance': calc._load_balance_reward(),
		'topology': calc._topology_quality_reward(),
		'penalty': calc._calculate_penalties()
	}

def create_training_directories():
	"""
	Create organized directory structure for training results
	"""
	parent_dir = "./enhanced_training_results/"
	timestamp = str(int(time.time()))
	filename = f'enhanced_run_{timestamp}'
	path = os.path.join(parent_dir, filename)

	os.makedirs(path, exist_ok=True)
	os.makedirs(os.path.join(path, 'graphs'), exist_ok=True)
	os.makedirs(os.path.join(path, 'analysis'), exist_ok=True)

	return path

def generate_training_analysis(metrics, save_path):
	"""
	Generate comprehensive training analysis
	"""
	print("\nGenerating training analysis...")

	# Calculate statistics
	episode_rewards = metrics['episode_rewards']
	final_network_metrics = metrics['network_metrics'][-1]

	analysis = {
		'training_summary': {
			'total_episodes': len(episode_rewards),
			'final_avg_reward': np.mean(episode_rewards[-5:]) if len(episode_rewards) >= 5 else np.mean(episode_rewards),
			'best_reward': max(episode_rewards),
			'reward_improvement': episode_rewards[-1] - episode_rewards[0] if len(episode_rewards) > 1 else 0,
			'final_acc': final_network_metrics['acc'],
			'final_apl': final_network_metrics['apl']
		},
		'reward_component_analysis': analyze_reward_components(metrics['reward_components']),
		'energy_analysis': analyze_energy_trends(metrics['energy_metrics']),
		'convergence_analysis': analyze_convergence(episode_rewards)
	}

	# Save analysis to file
	with open(os.path.join(save_path, 'training_analysis.json'), 'w') as f:
		json.dump(analysis, f, indent=2)

	# Print key insights
	print(f"Final average reward (last 5 episodes): {analysis['training_summary']['final_avg_reward']:.3f}")
	print(f"Best episode reward: {analysis['training_summary']['best_reward']:.3f}")
	print(f"Total reward improvement: {analysis['training_summary']['reward_improvement']:.3f}")
	print(f"Final network metrics: ACC={analysis['training_summary']['final_acc']:.3f}, APL={analysis['training_summary']['final_apl']:.3f}")

def analyze_reward_components(component_history):
	"""
	Analyze how reward components evolved during training
	"""
	if not component_history or not component_history[0]:
		return {}

	# Aggregate components across all episodes
	all_components = {'energy': [], 'lifetime': [], 'connectivity': [], 'balance': [], 'topology': []}

	for episode_components in component_history:
		for step_components in episode_components:
			for key in all_components:
				if key in step_components:
					all_components[key].append(step_components[key])

	# Calculate statistics for each component
	component_stats = {}
	for component, values in all_components.items():
		if values:
			component_stats[component] = {
				'mean': np.mean(values),
				'std': np.std(values),
				'min': np.min(values),
				'max': np.max(values),
				'trend': 'improving' if len(values) > 10 and np.mean(values[-10:]) > np.mean(values[:10]) else 'stable'
			}

	return component_stats

def analyze_energy_trends(energy_history):
	"""
	Analyze energy consumption trends
	"""
	if not energy_history:
		return {}

	# Extract energy data from all episodes
	total_energies = []
	min_energies = []

	for episode_energy in energy_history:
		if episode_energy:
			total_energies.extend([step['total_energy'] for step in episode_energy])
			min_energies.extend([step['min_energy'] for step in episode_energy])

	if not total_energies:
		return {}

	return {
		'energy_utilization': {
			'avg_total_energy': np.mean(total_energies),
			'min_total_energy': np.min(total_energies),
			'energy_variance': np.var(total_energies)
		},
		'bottleneck_analysis': {
			'avg_min_energy': np.mean(min_energies),
			'min_bottleneck_energy': np.min(min_energies),
			'bottleneck_variance': np.var(min_energies)
		}
	}

def analyze_convergence(episode_rewards):
	"""
	Analyze reward convergence
	"""
	if len(episode_rewards) < 5:
		return {'status': 'insufficient_data'}

	# Calculate moving average
	window_size = min(5, len(episode_rewards) // 4)
	moving_avg = np.convolve(episode_rewards, np.ones(window_size)/window_size, mode='valid')

	# Check for convergence (low variance in recent episodes)
	recent_variance = np.var(episode_rewards[-window_size:])

	return {
		'converged': recent_variance < 0.1,
		'final_moving_avg': moving_avg[-1] if len(moving_avg) > 0 else episode_rewards[-1],
		'recent_variance': recent_variance,
		'trend': 'improving' if episode_rewards[-1] > episode_rewards[0] else 'declining'
	}

def plot_training_progress(metrics, save_path):
	"""
	Create comprehensive training progress plots
	"""
	fig, axes = plt.subplots(2, 3, figsize=(18, 12))

	# Plot 1: Episode rewards
	axes[0,0].plot(metrics['episode_rewards'])
	axes[0,0].set_title('Episode Rewards')
	axes[0,0].set_xlabel('Episode')
	axes[0,0].set_ylabel('Total Reward')
	axes[0,0].grid(True)

	# Plot 2: Network metrics evolution
	network_metrics = metrics['network_metrics']
	episodes = [m['episode'] for m in network_metrics]
	accs = [m['acc'] for m in network_metrics]
	apls = [m['apl'] for m in network_metrics]

	axes[0,1].plot(episodes, accs, label='ACC', marker='o')
	axes[0,1].plot(episodes, apls, label='APL', marker='s')
	axes[0,1].set_title('Network Metrics Evolution')
	axes[0,1].set_xlabel('Episode')
	axes[0,1].set_ylabel('Metric Value')
	axes[0,1].legend()
	axes[0,1].grid(True)

	# Plot 3: Reward components (if available)
	if metrics['reward_components'] and metrics['reward_components'][0]:
		component_means = {}
		for episode_components in metrics['reward_components']:
			if episode_components:
				for key in ['energy', 'lifetime', 'connectivity', 'balance', 'topology']:
					if key not in component_means:
						component_means[key] = []
					episode_mean = np.mean([step.get(key, 0) for step in episode_components])
					component_means[key].append(episode_mean)

		for key, values in component_means.items():
			if values:
				axes[0,2].plot(values, label=key.capitalize())

		axes[0,2].set_title('Reward Components Evolution')
		axes[0,2].set_xlabel('Episode')
		axes[0,2].set_ylabel('Component Value')
		axes[0,2].legend()
		axes[0,2].grid(True)

	# Plot 4: Energy trends
	if metrics['energy_metrics']:
		all_total_energies = []
		all_min_energies = []
		step_numbers = []
		step_counter = 0

		for episode_energy in metrics['energy_metrics']:
			for step_data in episode_energy:
				all_total_energies.append(step_data['total_energy'])
				all_min_energies.append(step_data['min_energy'])
				step_numbers.append(step_counter)
				step_counter += 1

		if all_total_energies:
			axes[1,0].plot(step_numbers, all_total_energies, label='Total Energy', alpha=0.7)
			axes[1,0].plot(step_numbers, all_min_energies, label='Min Energy', alpha=0.7)
			axes[1,0].set_title('Energy Evolution')
			axes[1,0].set_xlabel('Training Step')
			axes[1,0].set_ylabel('Energy')
			axes[1,0].legend()
			axes[1,0].grid(True)

	# Plot 5: Learning progress
	learning_metrics = metrics['learning_metrics']
	learn_iters = [m['learn_iters'] for m in learning_metrics]

	axes[1,1].plot(episodes, learn_iters, marker='o')
	axes[1,1].set_title('Learning Iterations')
	axes[1,1].set_xlabel('Episode')
	axes[1,1].set_ylabel('Cumulative Learning Iterations')
	axes[1,1].grid(True)

	# Plot 6: Reward distribution
	axes[1,2].hist(metrics['episode_rewards'], bins=min(10, len(metrics['episode_rewards'])), alpha=0.7)
	axes[1,2].set_title('Episode Reward Distribution')
	axes[1,2].set_xlabel('Reward')
	axes[1,2].set_ylabel('Frequency')
	axes[1,2].grid(True)

	plt.tight_layout()
	plt.savefig(os.path.join(save_path, 'training_progress.png'), dpi=300, bbox_inches='tight')
	plt.close()

	print(f"Training progress plots saved to {save_path}/training_progress.png")

if __name__ == '__main__':

	print("Starting enhanced training with comprehensive reward function...")
	start_time = time.time()

	metrics, agent, final_env = enhanced_training_loop()

	end_time = time.time()
	print(f"\nTraining completed in {(end_time - start_time)/60:.2f} minutes")
	print("Check the generated analysis files and plots for detailed insights!")