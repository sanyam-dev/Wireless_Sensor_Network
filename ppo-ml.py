import numpy as np
from RL import Agent
# from utils import plot_learning_curve
from env import env
import random
import os
import copy
parent_dir_path = "/Users/ashu/Projects/python/wsn/results/"

def dir():
	parent_dir = parent_dir_path
	filename = 'result'
	path = os.path.join(parent_dir,filename)
	try:
		os.makedirs(path)
		os.makedirs(path+"/env")
		os.makedirs(path+"/temp")
	except FileExistsError:
		filename += str(random.randint(0,1000))
		path = os.path.join(parent_dir, filename)
		os.makedirs(path)
		os.makedirs(path+"/env")
		os.makedirs(path+"/temp")
	print("result path:", path)
	return path

def write_history(par_path, history, round):
	fname = "history"
	if(round != -1):
		fname += str(round)
	fname += ".txt"
	path = os.path.join(par_path,  fname)
	try:
		os.makedirs(par_path)
	except FileExistsError:
		pass
	fp = open(path, "w")
	# with open(path, "w") as fp:
	fp.write("no.,acc,apl,small_worldness\n")
	for i in range(len(history)):
		s = str(i) + "," + str(history[i][0]) + "," + str(history[i][1]) + "," + str(history[i][2])+ "\n"
		fp.write(s)
	fp.close()

def write_history_sub(par_path, history, round, subround, i):
	if(round != -1):
		fname += str(i) + "-" + str(round)
	# fname += ".txt"
	path = os.path.join(par_path,  fname)
	try:
		os.makedirs(path)
	except FileExistsError:
		path+='1'
		fname = path
		os.makedirs(path)
	fname += str(subround) + '.txt'
	path = os.path.join(par_path, fname)
	fp = open(path, "w")
	# with open(path, "w") as fp:
	fp.write("no.,acc,apl,small_worldness\n")
	for i in range(len(history)):
		s = str(i) + "," + str(history[i][0]) + "," + str(history[i][1]) + "," + str(history[i][2])+ "\n"
		fp.write(s)
	fp.close()

N = 5
batch_size = 5
n_epochs = 4
alpha = 0.0003
env1 = env()
env1.set_nxg()
acc = env1.acc
apl =  env1.apl
best_apl = apl
best_acc = acc
n_games = 20
number_of_edges = 200



path = dir()
tmp_path = path + '/temp'
env_path = path + '/env'

print(env1.action_space_n)
env1.save_graph(path, -1)
temp = copy.deepcopy(env1)

episode_history = []
total_edges_added = 0
for i in range(number_of_edges): #episode
	best_score = 0
	score_history = []
	learn_iters = 0
	avg_score = 0
	n_steps = 0
	fl = 0

	episode_history.append([env1.acc, env1.apl, round(env1.acc/env1.apl, 4)])
	game_history = []

	print("for episode:", i, "action_space_len", env1.action_space_n)
	agent = Agent(n_actions=env1.action_space_n, batch_size=batch_size,
				alpha=alpha, n_epochs=n_epochs,
				input_dims=[env1.get_observation_space_shape()])

	for j in range(n_games): #game
		edges_added_this_round = set()
		temp.reset_to_copy(env1)
		rnd_his = []
		rnd_his.append([temp.acc, temp.apl, round(temp.acc/temp.apl, 4)])
		done = 0
		observation_flatten = temp.flatten_obs_sp()
		score = 0
		while not done == 200:	#round
			print("episode:", i,"game:",j,"round:",done)
			action, prob, val = agent.choose_action(observation_flatten)
			obs_, reward = temp.step(action)
			rnd_his.append([temp.acc, temp.apl, round(temp.acc/temp.apl, 4)])
			n_steps += 1
			score += reward
			done += 1
			agent.remember(obs_, action, prob, val, reward, done)
			edges_added_this_round.add(action)
			if n_steps % N == 0:
				agent.learn()
				learn_iters += 1
			observation_flatten = obs_
		print('x-x-x')
		agent.learn()
		print("edges added this round", len(edges_added_this_round))
		write_history(tmp_path + "/" + str(i), rnd_his, j)
		score_history.append(score)
		avg_score
		avg_score = np.mean(score_history[-100:])
		if avg_score > best_score:
			best_score = avg_score
		if best_acc < env1.acc or best_apl > env1.apl:
			best_acc = env1.acc
			best_apl = env1.apl

		game_history.append([temp.acc, temp.apl, round(temp.acc/temp.apl, 4)])
		temp.save_graph(tmp_path + "/" + str(i), j)
		temp.save_graph_npy(tmp_path + "/" + str(i), j)
		print('episode', i, 'score %.1f' % score, 'avg score %.1f' % avg_score,
				'time_steps', n_steps, 'learning_steps', learn_iters)

		if len(edges_added_this_round) <= 3:
			total_edges_added += len(edges_added_this_round)
			print('prev action space len:', env1.action_space_n)
			for action_number in edges_added_this_round:
				edge = env1.action_space[action_number]
				env1.add(edge)
				fl = 1
				print("edge added to env1")
				print("curr action space len", env1.action_space_n)
				# action space re-eval done
				# obs space re-eval done
			break
	print('=======')
	if(total_edges_added == number_of_edges):
		break
	episode_history.append([env1.acc, env1.apl, round(env1.acc/env1.apl, 4)])
	env1.save_graph(env_path, i)
	env1.save_graph_npy(env_path, i)
	write_history(env_path, game_history, i)

write_history(env_path, episode_history, -1)





