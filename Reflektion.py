#Applicant Name: Leo Zhao
#University: University of Waterloo
#Purpose: Simulate 4 users buying stocks at the same time. We can retrieve the top trades at anytime.

#Utilizing global variable that is necesary in multiple functions to reduce passing of parameters
global concurrentUsers
global commands
global commandsCounter
global userCount
global maxEntry
global tradeLog
global nodesCount
global topCounter
maxEntry = 0
userCount = 0
nodesCount = 0
commandsCounter = 0
topCounter = 0
concurrentUsers = {}
commandList = {}

#Initializing the tree from the previous day record. 
#Could be combined with the insertAVL() but since we know the previous record has been sorted we might as well take advantage
class TreeNode: 
	def MinimumBST(self, value, parent = None, leftChild = None, rightChild = None, startIndex = None, endIndex = None, trades = None, childType = None):
		global nodesCount
		self.value = value
		self.leftChild = leftChild
		self.rightChild = rightChild
		self.parent = parent 
		self.childNodes = 0
		self.childType = childType

		#Creating a BST from a sorted array
		if (startIndex is not None):
			if(startIndex>endIndex):
				return
			currentIndex = int((startIndex+endIndex)/2)
			self.value = int (trades[currentIndex].replace("\n",""))
			self.updateChildNodes()
			nodesCount += 1
			if(self.value <= int (trades[(currentIndex+1+endIndex)/2].replace("\n",""))):
				childR = TreeNode()
				self.rightChild = childR.MinimumBST (0, self, None, None, currentIndex+1, endIndex, trades, -1)

			if(self.value > int (trades[(currentIndex-1+startIndex)/2].replace("\n",""))):
				childL = TreeNode()
				self.leftChild = childL.MinimumBST (0, self, None, None, startIndex, currentIndex-1, trades, 1)
			return self
		return self

	#Recursively update the childNodes counter
	#A right child node counts as -1 and a left child node counts as +1. A node with childNodes counter between -1 and 1 is balanced
	def updateChildNodes(self):
		if(self.parent is not None):
				if (self.childType == 1):
					self.parent.childNodes += 1
				elif (self.childType == -1):
					self.parent.childNodes -= 1
				self.parent.updateChildNodes()


	def hasLeftchild (self):
		return self.leftChild

	def hasrightChild (self):
		return self.rightChild

	def isLeftChild(self):
		if(self.parent.leftChild is not None):
			if (self.parent is not None and self.parent.leftChild.value == self.value):
				return True
		else:
			return False

	def isRightChild(self):
		if(self.parent.rightChild is not None):
			if (self.parent is not None and self.parent.rightChild.value == self.value):
				return True
		else:
			return False

	def isRoot (self):
		if (self.parent is None):
			return True
		else: 
			return False


#Imports the previous day data from file
def ImportHistory (inputFile):
	global tradeLog 

	with open(inputFile) as f:
		trades = []
		trades = f.readlines()
		Tree = TreeNode ()
		tradeLog = Tree.MinimumBST(0, None, None, None, 0, len(trades)-1, trades)

#Import current day data from file
def ImportCurrent (inputFile):
	global userCount
	global maxEntry
	global concurrentUsers

	with open(inputFile) as f:
		concurrentUsers[userCount] = []
		concurrentUsers[userCount] = f.readlines()
	if (maxEntry < len(concurrentUsers[userCount])):
		maxEntry = len(concurrentUsers[userCount])

	userCount += 1

#Import commands from file
def ImportCommands(inputFile):
	global commandList

	with open(inputFile) as f:
		commandList = f.readlines()

#Execute the commands read from the command file
def ReadCommands():
	global commandList
	global commandsCounter
	global topCounter
	stringBuffer = ""

	if(commandsCounter<len(commandList)):
		stringBuffer = commandList[commandsCounter].replace("\n","").replace("\r","").split()
		if (len(stringBuffer)==0):
			commandsCounter += 1
		elif(len(stringBuffer)>0):
			if (stringBuffer[0] != "end"):
				if (int(stringBuffer[1]) <= nodesCount and int(stringBuffer[2]) <= int(stringBuffer[1])):
					topCounter = int(stringBuffer[2])
					retrieveTop (tradeLog)
					commandsCounter += 1
			#Success exit condition
			elif (stringBuffer[0] == "end"):
				print "Thank you for the consideration. The program has ended. Please check file 'file_3.txt' for output."
				outputFile.close()
				exit()

#Read the imported current day data from multiple file 
#Every line from the current day data files are considered as a time frame
def LoadCurrent ():
	global userCount
	global maxEntry
	global concurrentUsers
	global tradeLog
	global nodesCount
	stringBuffer = ""

	#interate through the time frames
	for x in range (0, maxEntry):
		#interate through the number of users
		for y in range (0, userCount):
			if (len(concurrentUsers[y]) > x): 
				stringBuffer = concurrentUsers[y][x].replace("\r","")
				stringBuffer = concurrentUsers[y][x].replace("\n","")
				if(stringBuffer != "" and stringBuffer != "\r"):
					nodesCount += 1
					insertAVL (int (stringBuffer), tradeLog)
		#Check if the command can be executed every time frame
		ReadCommands()

#Insert node via AVL method
def insertAVL(newTrade, node):
	if (newTrade < int(node.value)):
		if (node.hasLeftchild() is not None):
			insertAVL(newTrade, node.leftChild)
		else:
			newNode = TreeNode ()
			node.leftChild = newNode.MinimumBST(newTrade, node)
			balanceTree (node.leftChild)
	else:
		if (node.hasrightChild() is not None):
			insertAVL(newTrade, node.rightChild)
		else:
			newNode = TreeNode ()
			node.rightChild = newNode.MinimumBST(newTrade, node)
			balanceTree (node.rightChild)

#Check if the tree is balanced. If not balance
#A right child node counts as -1 and a left child node counts as +1. A node with childNodes counter between -1 and 1 is balanced
def balanceTree (node):
	if (node.childNodes > 1 or node.childNodes < -1):
		rebalanceTree(node)
		return
	if (node.parent is not None):
		if (node.isLeftChild()):
			node.parent.childNodes += 1
		elif (node.isRightChild()):
			node.parent.childNodes -= 1

		if (node.parent.childNodes != 0):
			balanceTree(node.parent)

#Rebalancing the tree
def rebalanceTree(node):
	if (node.childNodes < 0):
		if (node.rightChild.childNodes > 0):
			rotateRight(node.rightChild)
			rotateLeft(node)
		else:
			rotateLeft(node)
	elif (node.childNodes > 0):
		if (node.leftChild.childNodes < 0):
			rotateLeft(node.leftChild)
			rotateRight(node)
		else:
			rotateRight(node)

#Single and double rotation to the left combined into one method
def rotateLeft(rotationPoint):
	global tradeLog
	newRoot = rotationPoint.rightChild
	rotationPoint.rightChild = newRoot.leftChild
	if (newRoot.leftChild is not None):
		newRoot.leftChild.parent = rotationPoint
	newRoot.parent = rotationPoint.parent
	if (rotationPoint.isRoot()):
		tradeLog = newRoot
	else:
		if (rotationPoint.isLeftChild()):
			rotationPoint.parent.leftChild = newRoot
		else:
			rotationPoint.parent.rightChild = newRoot
	newRoot.leftChild = rotationPoint
	rotationPoint.parent = newRoot
	rotationPoint.childNodes = rotationPoint.childNodes + 1 - min(newRoot.childNodes, 0)
	newRoot.childNodes = newRoot.childNodes + 1 + max(rotationPoint.childNodes, 0)

#Single and double rotation to the right combined into one method
def rotateRight(rotationPoint):
	global tradeLog
	newRoot = rotationPoint.leftChild
	rotationPoint.leftChild = newRoot.rightChild
	if (newRoot.rightChild is not None):
		newRoot.rightChild.parent = rotationPoint
	newRoot.parent = rotationPoint.parent
	if (rotationPoint.isRoot()):
		tradeLog = newRoot
	else:
		if (rotationPoint.isRightChild()):
			rotationPoint.parent.rightChild = newRoot
		else:
			rotationPoint.parent.leftChild = newRoot
	newRoot.rightChild = rotationPoint
	rotationPoint.parent = newRoot
	rotationPoint.childNodes = rotationPoint.childNodes - 1 - max(newRoot.childNodes, 0)
	newRoot.childNodes = newRoot.childNodes - 1 + min(rotationPoint.childNodes, 0)

#Print to outputfile
def printer(printNode):
    outputFile.write (str(printNode)+" ")

#Traverse through the tree in reverse of in order traversal 
def retrieveTop(node, printNode = printer):
	global topCounter
	if (node is not None):
		retrieveTop(node.rightChild, printNode)
		if (topCounter > 0): 
			printNode(node.value)
			topCounter -= 1
		if (topCounter == 0):
			topCounter -= 1
			outputFile.write ("\n")
		retrieveTop(node.leftChild, printNode)


#Loading files
outputFile = open ("file_3.txt", "w")
ImportHistory ("file_1.txt")
ImportCurrent ("file_4.txt")
ImportCurrent ("file_5.txt")
ImportCurrent ("file_6.txt")
ImportCurrent ("file_7.txt")
ImportCommands ("file_2.txt")
LoadCurrent()

#Erroneous exit
print "An Error has occured. please makes sure the top requests could be fulfilled."

outputFile.close()
