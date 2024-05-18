from cProfile import label
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Load data from CSV files
q_learn_data = pd.read_csv('q_learn.csv').to_numpy()
leach_data = pd.read_csv('leach.csv').to_numpy()
beemh_data = pd.read_csv('beemh.csv').to_numpy()
kmeans_data = pd.read_csv('kmeans.csv').to_numpy()
nmleach_data = pd.read_csv('nmleach.csv').to_numpy()
ql_eebdg_data = pd.read_csv('ql_eebdg.csv').to_numpy()
dt_data = pd.read_csv('dt.csv').to_numpy()
ql_lof = pd.read_csv('ql_lof.csv').to_numpy()
genetic_data = pd.read_csv('ga.csv').to_numpy()

iters = [0, 200, 400, 600, 800, 1000, 1200, 1400, 1600, 1800, 2000]

# Plot for throughput ratio
throughput = plt.figure()
plt.xlabel('Number of iterations used for data transmission', fontsize=12)
plt.ylabel('Throughput ratio', fontsize=13)
plt.plot([iter for iter in iters], [q_learn_data[i][0] for i in range(len(iters))], figure=throughput, color='deepskyblue', marker='X', label='Q_learning')
plt.plot([iter for iter in iters], [leach_data[i][0] for i in range(len(iters))], figure=throughput, color='blue', marker='o', label='LEACH')
plt.plot([iter for iter in iters], [beemh_data[i][0] for i in range(len(iters))], figure=throughput, color='black', marker='s', label='BEEMH')
plt.plot([iter for iter in iters], [kmeans_data[i][0] for i in range(len(iters))], figure=throughput, color='red', marker='^', label='K-Means++')
plt.plot([iter for iter in iters], [nmleach_data[i][0] for i in range(len(iters))], figure=throughput, color='deeppink', marker='D', label='NM-LEACH')
plt.plot([iter for iter in iters], [ql_eebdg_data[i][0] for i in range(len(iters))], figure=throughput, color='orange', marker='P', label='QL-EEBDG')
plt.plot([iter for iter in iters], [dt_data[i][0] for i in range(len(iters))], figure=throughput, color='brown', marker='p', label='Direct Tx.')
plt.plot([iter for iter in iters], [ql_lof[i][0] for i in range(len(iters))], figure=throughput, color='darkviolet', marker='H', label='QL_LoF')
plt.plot([iter for iter in iters], [genetic_data[i][0] for i in range(len(iters))], figure=throughput, color='limegreen', marker='*', label='Proposed')
plt.legend()
plt.savefig('Throughput.eps')

# Plot for network life
life = plt.figure()
plt.xlabel('Number of iterations used for data transmission', fontsize=12)
plt.ylabel('Network lifetime', fontsize=13)
plt.plot([iter for iter in iters], [q_learn_data[i][1] for i in range(len(iters))], figure=life, color='deepskyblue', marker='X', label='Q_learning')
plt.plot([iter for iter in iters], [leach_data[i][1] for i in range(len(iters))], figure=life, color='blue', marker='o', label='LEACH')
plt.plot([iter for iter in iters], [beemh_data[i][1] for i in range(len(iters))], figure=life, color='black', marker='s', label='BEEMH')
plt.plot([iter for iter in iters], [kmeans_data[i][1] for i in range(len(iters))], figure=life, color='red', marker='^', label='K-Means++')
plt.plot([iter for iter in iters], [nmleach_data[i][1] for i in range(len(iters))], figure=life, color='deeppink', marker='D', label='NM-LEACH')
plt.plot([iter for iter in iters], [ql_eebdg_data[i][1] for i in range(len(iters))], figure=life, color='orange', marker='P', label='QL-EEBDG')
plt.plot([iter for iter in iters], [dt_data[i][1] for i in range(len(iters))], figure=life, color='brown', marker='p', label='Direct Tx.')
plt.plot([iter for iter in iters], [ql_lof[i][1] for i in range(len(iters))], figure=life, color='darkviolet', marker='H', label='QL_LoF')
plt.plot([iter for iter in iters], [genetic_data[i][1] for i in range(len(iters))], figure=life, color='limegreen', marker='*', label='Proposed')
plt.legend()

plt.savefig('Life.eps')

# Plot for total network energy
residual = plt.figure()
plt.xlabel('Number of iterations used for data transmission', fontsize=12)
plt.ylabel('Residual energy of the network (in Joule)', fontsize=13)
plt.plot([iter for iter in iters], [q_learn_data[i][2] for i in range(len(iters))], figure=residual, color='deepskyblue', marker='X', label='Q_learning')
plt.plot([iter for iter in iters], [leach_data[i][2] for i in range(len(iters))], figure=residual, color='blue', marker='o', label='LEACH')
plt.plot([iter for iter in iters], [beemh_data[i][2] for i in range(len(iters))], figure=residual, color='black', marker='s', label='BEEMH')
plt.plot([iter for iter in iters], [kmeans_data[i][2] for i in range(len(iters))], figure=residual, color='red', marker='^', label='K-Means++')
plt.plot([iter for iter in iters], [nmleach_data[i][2] for i in range(len(iters))], figure=residual, color='deeppink', marker='D', label='NM-LEACH')
plt.plot([iter for iter in iters], [ql_eebdg_data[i][2] for i in range(len(iters))], figure=residual, color='orange', marker='P', label='QL-EEBDG')
plt.plot([iter for iter in iters], [dt_data[i][2] for i in range(len(iters))], figure=residual, color='brown', marker='p', label='Direct Tx.')
plt.plot([iter for iter in iters], [ql_lof[i][2] for i in range(len(iters))], figure=residual, color='darkviolet', marker='H', label='QL_LoF')
plt.plot([iter for iter in iters], [genetic_data[i][2] for i in range(len(iters))], figure=residual, color='limegreen', marker='*', label='Proposed')
plt.legend()

plt.savefig('Residual.eps')

# Plot for average data latency
latency = plt.figure()
plt.xlabel('Number of iterations used for data transmission', fontsize=12)
plt.ylabel('Average data latency (in Seconds)', fontsize=13)
plt.plot([iter for iter in iters], [q_learn_data[i][3] for i in range(len(iters))], figure=latency, color='deepskyblue', marker='X', label='Q_learning')
plt.plot([iter for iter in iters], [leach_data[i][3] for i in range(len(iters))], figure=latency, color='blue', marker='o', label='LEACH')
plt.plot([iter for iter in iters], [beemh_data[i][3] for i in range(len(iters))], figure=latency, color='black', marker='s', label='BEEMH')
plt.plot([iter for iter in iters], [kmeans_data[i][3] for i in range(len(iters))], figure=latency, color='red', marker='^', label='K-Means++')
plt.plot([iter for iter in iters], [nmleach_data[i][3] for i in range(len(iters))], figure=latency, color='deeppink', marker='D', label='NM-LEACH')
plt.plot([iter for iter in iters], [ql_eebdg_data[i][3] for i in range(len(iters))], figure=latency, color='orange', marker='P', label='QL-EEBDG')
plt.plot([iter for iter in iters], [dt_data[i][3] for i in range(len(iters))], figure=latency, color='brown', marker='p', label='Direct Tx.')
plt.plot([iter for iter in iters], [ql_lof[i][3] for i in range(len(iters))], figure=latency, color='darkviolet', marker='H', label='QL_LoF')
plt.plot([iter for iter in iters], [genetic_data[i][3] for i in range(len(iters))], figure=latency, color='limegreen', marker='*', label='Proposed')
plt.legend()

plt.savefig('Latency.eps')

# Plot for energy balance
energy_balance = plt.figure()
plt.xlabel('Number of iterations used for data transmission', fontsize=12)
plt.ylabel('S.D. of energy consumed by all nodes', fontsize=13)
plt.plot([iter for iter in iters], [q_learn_data[i][4] for i in range(len(iters))], figure=energy_balance, color='deepskyblue', marker='X', label='Q_learning')
plt.plot([iter for iter in iters], [leach_data[i][4] for i in range(len(iters))], figure=energy_balance, color='blue', marker='o', label='LEACH')
plt.plot([iter for iter in iters], [beemh_data[i][4] for i in range(len(iters))], figure=energy_balance, color='black', marker='s', label='BEEMH')
plt.plot([iter for iter in iters], [kmeans_data[i][4] for i in range(len(iters))], figure=energy_balance, color='red', marker='^', label='K-Means++')
plt.plot([iter for iter in iters], [nmleach_data[i][4] for i in range(len(iters))], figure=energy_balance, color='deeppink', marker='D', label='NM-LEACH')
plt.plot([iter for iter in iters], [ql_eebdg_data[i][4] for i in range(len(iters))], figure=energy_balance, color='orange', marker='P', label='QL-EEBDG')
plt.plot([iter for iter in iters], [dt_data[i][4] for i in range(len(iters))], figure=energy_balance, color='brown', marker='p', label='Direct Tx.')
plt.plot([iter for iter in iters], [ql_lof[i][4] for i in range(len(iters))], figure=energy_balance, color='darkviolet', marker='H', label='QL_LoF')
plt.plot([iter for iter in iters], [ql_lof[i][4] for i in range(len(iters))], figure=energy_balance, color='limegreen', marker='*', label='Proposed')
plt.legend()

plt.savefig('Energy_balance.eps')


# Plot for bandwidth
bandwidth = plt.figure() 
plt.xlabel('Number of iterations used for data transmission', fontsize=12)
plt.ylabel('Bandwidth(bps)', fontsize=13)
plt.plot([iter for iter in iters], [q_learn_data[i][5] for i in range(len(iters))], figure=bandwidth, color='deepskyblue', marker='X', label='Q_learning')
plt.plot([iter for iter in iters], [leach_data[i][5] for i in range(len(iters))], figure=bandwidth, color='blue', marker='o', label='LEACH')
plt.plot([iter for iter in iters], [beemh_data[i][5] for i in range(len(iters))], figure=bandwidth, color='black', marker='s', label='BEEMH')
plt.plot([iter for iter in iters], [kmeans_data[i][5] for i in range(len(iters))], figure=bandwidth, color='red', marker='^', label='K-Means++')
plt.plot([iter for iter in iters], [nmleach_data[i][5] for i in range(len(iters))], figure=bandwidth, color='deeppink', marker='D', label='NM-LEACH')
plt.plot([iter for iter in iters], [ql_eebdg_data[i][5] for i in range(len(iters))], figure=bandwidth, color='orange', marker='P', label='QL-EEBDG')
plt.plot([iter for iter in iters], [dt_data[i][5] for i in range(len(iters))], figure=bandwidth, color='brown', marker='p', label='Direct Tx.')
plt.plot([iter for iter in iters], [ql_lof[i][5] for i in range(len(iters))], figure=bandwidth, color='darkviolet', marker='H', label='QL_LoF')
plt.plot([iter for iter in iters], [genetic_data[i][5] for i in range(len(iters))], figure=bandwidth, color='limegreen', marker='*', label='Proposed')
plt.legend()

plt.savefig('Bandwidth.eps')

plt.show()