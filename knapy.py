import sys, random

##### Math #####
def gcd(a, b):
	while (a != b):
		if (a > b):
			a -= b
		else:
			b -= a
	return a

def getCoPrime(m):
	minNum = 2
	maxNum = m-1
	while (True):
		n = random.randint(minNum, maxNum)
		if (gcd(n, m) == 1):
			return n

def multiplicativeInverse(a, n):
	t = 0
	newT = 1
	r = n
	newR = a
	while (newR != 0):
		q = r/newR
		t, newT = newT, t - q*newT
		r, newR = newR, r - q*newR
	if t < 0:
		t += n
	return t

##### Super increasing knapsack #####
def generateSuperIncreasingKnapsack(size):
	first = random.randint(2**200, 2**200+size)
	knapsack = [first]
	sum = first

	for i in range(size-1):
		element = sum + random.randint(1, size)
		knapsack.append(element)
		sum += element
	return knapsack, sum

def isSuperIncreasingKnapsack(knapsack):
	sum = 0
	test = True
	for element in knapsack:
		if element <= sum: 
			test = False
			break
		sum += element
	return test

#####  Key generation ##### 
def generateMandN(sum):
	m = sum + random.randint(1, 10)
	n = getCoPrime(m)
	return m, n

def calcZmKnapsack(knapsack, m, n):
	newKnapsack = []
	for element in knapsack:
		newKnapsack.append(n*element % m)
	return newKnapsack

def generateKeyPair(size):
	privateKey, s = generateSuperIncreasingKnapsack(size)
	m, n = generateMandN(s)
	nInv = multiplicativeInverse(n, m)
	publicKey = calcZmKnapsack(privateKey, m, n)
	nFinalBits = len(bin(sum(publicKey))[2:])
	return (privateKey, m, nInv, nFinalBits), publicKey

##### Cypher / Decypher #####
def cypher(name):
	publicKey = readKey(name + ".pub")

	m = sys.stdin.read()
	m += chr(127)

	bits = ""
	for c in m:
		bits += bin(ord(c))[2:].zfill(7)

	size = len(publicKey)
	encM = []
	for i in range(0, len(bits), size):
		curPart = bits[i:i+size]
		s = 0
		for i in range(len(curPart)):
			if (curPart[i] == "1"):
				s += publicKey[i]
		encM.append(s)

	nFinalBits = len(bin(sum(publicKey))[2:])
	output = ""
	for n in encM:
		output += bin(n)[2:].zfill(nFinalBits)

	sys.stdout.write(output)

def decypher(name):
	privateKey, m, nInv, nFinalBits = readKey(name + ".priv")

	bits = sys.stdin.read()

	encM = []
	for i in range(0, len(bits), nFinalBits):
		encM.append(int(bits[i:i+nFinalBits], 2))
	
	aux = []
	for i in encM:
		aux.append(i * nInv % m)

	size = len(privateKey)
	dec = ""
	for i in aux:
		addends = ["0"]*size
		for j in range(size)[::-1]:
			if (privateKey[j] <= i):
				addends[j] = "1"
				i -= privateKey[j]
		dec += "".join(addends)

	output = ""
	for i in range(0, len(dec), 7):
		c = chr(int(dec[i:i+7], 2))
		if (ord(c) == 127):
			break
		output += c
	sys.stdout.write(output)

##### Files #####
def saveKeyPair(privateKey, publicKey, name):
	privateKeyPath = name + ".priv"
	publicKeyPath = name + ".pub"
	
	f = open(privateKeyPath, "w")
	key, m, nInv, nFinalBits = privateKey[0], privateKey[1], privateKey[2], privateKey[3]
	f.write(str(m) + "," + str(nInv) + "," + str(nFinalBits) + "\n")
	for i in key:
		f.write(str(i) + "\n")
	f.close()

	f = open(publicKeyPath, "w")
	for i in publicKey:
		f.write(str(i) + "\n")
	f.close()

def readKey(path):
	f = open(path, "r")
	s = f.read()
	f.close()

	list = s.split("\n")
	list.pop(-1)
	
	if ("priv" in path):
		m, nInv, nFinalBits = map(int, list[0].split(","))
		list.pop(0)
		return [map(int, list), m, nInv, nFinalBits]
	return map(int, list)

##### Print utils #####
TEXT_BOLD = "\033[1m"
TEXT_RED = "\033[91m"
TEXT_BLUE = "\033[94m"
TEXT_GREEN ="\033[92m"
TEXT_END = "\033[0m"

def printInfo(info, type=0):
	if (type == 0):
		m = TEXT_BLUE
	elif (type == 1):
		m = TEXT_GREEN
	elif (type == 2):
		m = TEXT_RED
	m += "[*] " + TEXT_END + TEXT_BOLD + info + TEXT_END
	print(m)

def printPublicKey(name):
	publicKey = readKey(name + ".pub")
	printInfo("Public key (" + name + ")")
	print(" "*4 + "k = " + str(publicKey))

def printPrivateKey(name):
	privateKey, m, nInv, nFinalBits = readKey(name + ".priv")
	printInfo("Private key (" + name + ")")
	print(" "*4 + "m = " + str(m) + ", n_inverse = " + str(nInv))
	print(" "*4 + "k = " + str(privateKey))

##### Main #####
def printUsage():
	printInfo("Usage: python knap.py [option]")
	print("\nOptions:  -gen N name      -> Generates a new keypair using a knapsack of size N")
	print("\t  -dispp name      -> Prints the public key stored in name.pub")
	print("\t  -disps name      -> Prints the private key stored in name.priv")
	print("\t  -cypher name     -> Encrypts using name.pub")
	print("\t  -decypher name   -> Decrypts using name.priv\n")

def parseArgs():
	if (len(sys.argv) < 3):
		printUsage()
		return
	if (sys.argv[1] == "-gen"):
		if (len(sys.argv) != 4):
			printUsage()
		else:
			size = sys.argv[2]
			name = sys.argv[3]
			if (not size.isdigit()):
				printInfo("Error: Invalid knapsack size", 2)
			else:
				privateKey, publicKey = generateKeyPair(int(size))
				saveKeyPair(privateKey, publicKey, name)
	elif (sys.argv[1] == "-dispp"):
		name = sys.argv[2]
		printPublicKey(name)
	elif (sys.argv[1] == "-disps"):
		name = sys.argv[2]
		printPrivateKey(name)
	elif (sys.argv[1] == "-cypher"):
		name = sys.argv[2]
		cypher(name)
	elif (sys.argv[1] == "-decypher"):
		name = sys.argv[2]
		decypher(name)
	else:
		printUsage()

if __name__ == "__main__":
	parseArgs()
