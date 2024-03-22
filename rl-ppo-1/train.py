import numpy as np
from RL import Agent
from env import env
import random
import os

def dir():
	parent_dir = "./training-results/ppo/"
	filename = 'result'
	path = os.path.join(parent_dir,filename)
	try:
		os.makedirs(path)
	except FileExistsError:
		filename += str(random.randint(0,100))
		path = os.path.join(parent_dir, filename)
		os.makedirs(path)
	return path

def write_history(par_path, history, round):
	fname = "history"
	if(round != -1):
		fname += str(round)
	fname += ".txt"
	path = os.path.join(par_path,  fname)
	with open(path, "w") as fp:
		fp.write("no.,acc,apl,small_worldness\n")
		for i in range(len(history)):
			s = str(i) + "," + str(history[i][0]) + "," + str(history[i][1]) + "," + str(history[i][2])+ "\n"
			fp.write(s)


if __name__ == '__main__':
	N = 5
	batch_size = 64
	n_epochs = 20
	alpha = 0.0003
	env1 = env()
	env1.set_nxg()
	acc = env1.acc
	apl =  env1.apl
	best_apl = apl
	best_acc = acc
	agent = Agent(n_actions=env1.action_space_n, batch_size=batch_size,
					alpha=alpha, n_epochs=n_epochs,
					input_dims=[env1.get_observation_space_shape()])
	number_of_edges = 200
	history = []
	print(env1.action_space_n)
	path = dir()
	env1.save_graph(path, -1)

	best_score = 0
	score_history = []

	learn_iters = 0
	avg_score = 0
	n_steps = 0
	prev_acc = env1.net.acc
	prev_apl = env1.net.apl
	curr_apl = env1.net.apl
	curr_acc = env1.net.acc
	
	for i in range(n_epochs):  #game
		env1.reset()
		observation_flatten = env1.flatten_obs_sp()
		done = 0
		score = 0
		rnd_his = []
		rnd_his.append([env1.acc, env1.apl, round(env1.acc/env1.apl, 4)])
		while not done == number_of_edges and (abs(curr_apl - prev_apl) >= abs(curr_acc - prev_acc)):	#round
			prev_acc = env1.net.acc
			prev_apl = env1.net.apl
			print("round : ", done)
			action, prob, val = agent.choose_action(observation_flatten)
			# observation_, reward, done, info = env.step(action)
			observation_, reward = env1.step(action)										## commment later
			rnd_his.append([env1.acc, env1.apl, round(env1.acc/env1.apl, 4)])
			agent.remember(observation_, action, prob, val, reward, done)
			agent.learn()
			learn_iters += 1
			curr_acc = env1.net.acc
			curr_apl = env1.net.apl
			if reward == -10:
				continue
			# if n_steps % N == 0:
			# 	agent.learn()
			# 	learn_iters += 1
			observation_flatten = observation_
			print("-------")
			done += 1
			n_steps += 1
			score += reward																	## comment later
		write_history(path, rnd_his, i)
		score_history.append(score)
		avg_score = np.mean(score_history[-100:])
		if avg_score > best_score:
			best_score = avg_score
		if best_acc < env1.acc or best_apl > env1.apl:
			best_acc = env1.acc
			best_apl = env1.apl
		history.append([env1.acc, env1.apl, round(env1.acc/env1.apl, 4)])
		env1.save_graph(path, i)
		env1.save_graph_npy(path, i)
		print('episode', i, 'score %.1f' % score, 'avg score %.1f' % avg_score,
				'time_steps', n_steps, 'learning_steps', learn_iters)
	x = [i+1 for i in range(len(score_history))]
	# plot_learning_curve(x, score_history)
	write_history(path, history,-1)
	print("done")
agent.save_models()