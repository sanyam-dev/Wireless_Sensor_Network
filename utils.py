import os

par_dir = "./result44"
file_name = "history.csv"
path = os.path.join(par_dir,file_name)

f = open(path, "w")
for line in open("./result44/history0.txt", "r"):
	n,acc,apl = line.split()
	s = str(n) + "," +str(acc)+ "," + str(apl) + "\n"
	f.write(s)
