import numpy as np
from RL import Agent
from utils import plot_learning_curve
from env import env

if __name__ == '__main__':
	N = 20
	batch_size = 5
	n_epochs = 4
	alpha = 0.0003
	env1 = env()
	acc = env1.acc
	apl =  env1.apl
	print(env1.action_space_n)
	agent = Agent(n_actions=env1.action_space_n, batch_size=batch_size,
					alpha=alpha, n_epochs=n_epochs,
					input_dims=[env1.get_observation_space_shape()])
	n_games = 3

	# figure_file = 'plots/learning.png'

	best_score = 0
	score_history = []

	learn_iters = 0
	avg_score = 0
	n_steps = 0

	for i in range(n_games):
		observation_flatten = env1.reset()
		# done = False
		done = 0
		score = 0
		while not done == 5:
			action, prob, val = agent.choose_action(observation_flatten)
			# observation_, reward, done, info = env.step(action)

			observation_, reward = env1.step(action)	## commment later
			n_steps += 1
			score += reward
			env1.show_graph()
			done += 1	## comment later
			agent.remember(observation_flatten, action, prob, val, reward, done)
			if n_steps % N == 0:
				agent.learn()
				learn_iters += 1
			observation_flatten = observation_
		score_history.append(score)
		avg_score = np.mean(score_history[-100:])
		if avg_score > best_score:
			best_score = avg_score
			# agent.save_models()

		print('episode', i, 'score %.1f' % score, 'avg score %.1f' % avg_score,
				'time_steps', n_steps, 'learning_steps', learn_iters)
	x = [i+1 for i in range(len(score_history))]
	plot_learning_curve(x, score_history)
	print(acc, apl)
	print(env1.net.acc, env1.net.apl)
	# for i in range(env1.initial_net.number_of_nodes + 1):
	# 	print(i, ": ", end = "")
	# 	for j in range(env1.net.number_of_nodes + 1):
	# 		if env1.net.graph[i][j]:
	# 			print(j, end = " ")
	# 	print()

	# for i in range(env1.net.number_of_nodes + 1):
	# 	print(i, ": ", end = "")
	# 	for j in range(env1.net.number_of_nodes + 1):
	# 		if env1.net.graph[i][j]:
	# 			print(j, end = " ")
	# 	print()
