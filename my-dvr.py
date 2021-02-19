import threading
from socket import *
import pickle
from copy import copy, deepcopy

LOCALHOST="127.0.0.1"
server_port = [65431,65432,65433,65434,65435] 
nodes = ['A','B','C','D','E']

#this function is used to print matrices
def printmat(mat):
	print("\tA\tB\tC\tD\tE")
	for x in range(5):
		print(nodes[x],end="\t")
		for y in range(5):
			print(mat[x][y],end="\t")
		print()

#tThis function is used to send client request
def client(name,dv):
	serverName = '127.0.0.1'
	serverPort = server_port[name]
	clientSocket = socket(AF_INET, SOCK_STREAM)
	clientSocket.connect((serverName,serverPort))
	sentence=pickle.dumps(dv)
	#sentence = "tatti"
	clientSocket.send(sentence)
	modifiedSentence = clientSocket.recv(1024)
	data=pickle.loads(modifiedSentence) 
	clientSocket.close()
	#it returns the data from server to the caller
	return data

#These nodes are used as threads and they are basically our computers
def node_th(name, mat):
	neighbour=[]
	matrix=[]
	last_matrix=[]
	count=0
	#initialising the DV matrix for the given node 
	for x in range(5):
		m=[]
		for y in range(5):
			if x==y:
				m.append(0)
			else:
				m.append(999)
		matrix.append(m)

	#Initialising the neighbours
	for i in range(5):
			if i!=name and mat[i]=='0':
				mat[i]=999
			else:
				mat[i]=int(mat[i])
				if i!=name:
					neighbour.append(i)

	matrix[name] = deepcopy(mat)
	neighbour_weight = deepcopy(mat)
	#Creating a socket for server
	server = socket(AF_INET, SOCK_STREAM)
	server.bind((LOCALHOST, server_port[int(name)]))
	server.listen(5)

	while True:
		connection, client_address = server.accept()
		sentence = connection.recv(1024)
		data=pickle.loads(sentence)

		if data == -1:
			#if server receives -1, the server returns the matrix and closes
			sentence=pickle.dumps(matrix)
			connection.send(sentence)
			connection.close()
			break

		elif data==1:
			#if server receives 1, the server sends the client request to the neighbours 
			print("Current DV matrix = ")
			printmat(matrix)
			print("\nLast DV matrix = ")
			if last_matrix != []:
				printmat(last_matrix)
			print("\nUpdated from last DV matrix or the same?",end=" ")
			if last_matrix != matrix:
				#We send the DV matrix when the matrix is updated
				print("Updated\n")
				for x in neighbour:
					#We are sending DV go each neighbour
					send_dv=[]
					print("")
					print("Sending DV to "+nodes[x])
					send_dv=deepcopy(matrix[name])
					send_dv.append(name)
					data=client(x,send_dv)
					matrix[x]=deepcopy(data[x])

				last_matrix=deepcopy(matrix)
				sentence=pickle.dumps(0)
				connection.send(sentence)
				connection.close()
			else:
				#if matrix is not updated, we will return
				print("Not Updated\n")
				sentence=pickle.dumps(1)
				connection.send(sentence)
				connection.close()
					
		else:
			#This part act as the receiving end and implements DIstance Vector algorithm
			count=count+1
			check_change=matrix[:]
			check_change[data[5]]=data[0:5]
			print("Node "+nodes[name]+" received DV from "+nodes[data[5]])
			print("Updating DV matrix at node "+nodes[name])

			for i in range(5):
				min_list=[]
				#Here we find the cost for each neighbour and then find the minimum cost
				for x in neighbour:
					min_list.append(neighbour_weight[x]+check_change[x][i])
				minimun_node=min(min_list)
				if minimun_node>999:
					minimun_node=999

				check_change[name][i]=minimun_node
				if name==i:
					check_change[name][i]=0

			if check_change == matrix:
				data="false"

			matrix=deepcopy(check_change)
			print("New DV matrix at node "+nodes[name]+" = ")
			printmat(matrix)
			sentence=pickle.dumps(matrix)
			connection.send(sentence)
			connection.close()

def network_init():

	with open("network.txt", "r") as f:
		content = f.readlines()

	for x in range(5):
		content[x]=content[x].strip('\n')
		content[x]=content[x].strip(' ')
		content[x]=content[x].split('\t')

	#Initialising threds
	node1 = threading.Thread(target=node_th, args=(0,content[0][:],),daemon=True)
	node2 = threading.Thread(target=node_th, args=(1,content[1][:],),daemon=True)
	node3 = threading.Thread(target=node_th, args=(2,content[2][:],),daemon=True)
	node4 = threading.Thread(target=node_th, args=(3,content[3][:],),daemon=True)
	node5 = threading.Thread(target=node_th, args=(4,content[4][:],),daemon=True)

	#Starting threads
	node1.start()
	node2.start()
	node3.start()
	node4.start()
	node5.start()

	i=0
	round_number=0
	
	#Here we iterate in the order A,B,C,D,E
	while True:
		i=i+1
		print("-------------------------------------- \n")
		print("\nRound "+str(i)+": "+nodes[0]+"\n")
		n1=client(0,1)
		if n1==0:
			round_number=i
		i=i+1
		print("-------------------------------------- \n")
		print("\nRound "+str(i)+": "+nodes[1]+"\n")
		n2=client(1,1)
		if n2==0:
			round_number=i
		i=i+1
		print("-------------------------------------- \n")
		print("\nRound "+str(i)+": "+nodes[2]+"\n")
		n3=client(2,1)
		if n3==0:
			round_number=i
		i=i+1
		print("-------------------------------------- \n")
		print("\nRound "+str(i)+": "+nodes[3]+"\n")
		n4=client(3,1)
		if n4==0:
			round_number=i
		i=i+1
		print("-------------------------------------- \n")
		print("\nRound "+str(i)+": "+nodes[4]+"\n")
		n5=client(4,1)
		if n5==0:
			round_number=i

		if n1==1 and n2==1 and n3==1 and n4==1 and n5==1:
			break
		
	print(" -------------------------------------- \n")
	n1=client(0,-1)
	n2=client(1,-1)
	n3=client(2,-1)
	n4=client(3,-1)
	n5=client(4,-1)

	node1.join()
	node2.join()
	node3.join()
	node4.join()
	node5.join()

	print("Final output :\n")
	print("Node A DV: ")
	printmat(n1)

	print("\nNode B DV: ")
	printmat(n2)

	print("\nNode B DV: ")
	printmat(n3)

	print("\nNode B DV: ")
	printmat(n4)

	print("\nNode B DV: ")
	printmat(n5)

	print("\nFinal DV: ")
	



	final=[]
	final.append(n1[0])
	final.append(n2[1])
	final.append(n3[2])
	final.append(n4[3])
	final.append(n5[4])

	printmat(final)

	print("\n\nNumber of rounds till convergence (Round # when one of the nodes last updated its DV) =",end=" ")
	print(round_number)
	

def main():
	network_init()

if __name__== "__main__":	
	local1= threading.local()
	main()


