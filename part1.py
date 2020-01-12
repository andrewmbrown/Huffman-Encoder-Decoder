# Andrew Brown 20070987 17amb
# all of this code was written by me
import os  # to parse through each canonical text file
import csv  # to read in external files requiring delimiters


class node:
    def __init__(self, letter, freq):
        self.letter = letter
        self.freq = freq
        self.right = None
        self.left = None
        self.code = ""

    def __lt__(self, other):
        if (other == None):
            return True
        return self.freq < other.freq

    def calcFreq(self):
        # note overwrite not increment (no issue if called many times)
        self.freq = self.left.freq + self.right.freq


ascii_freq = 127 * [0]  # for the "printables"
huffman_freq = []
common_path = "C:/Users/andre/Desktop/OneDrive/QueensUniversity/ThirdYear/FirstSemester/ELEC365/Assignment3/CanonicalCollection"


def decodingTree(leaf, tree):  # takes bit pattern and places a corresponding node with the letter
    instructions = leaf[1]  # keep bit patterns strings to avoid chopping of bottom zeros
    tempNode = tree[0]  # point temp node to the root of the tree
    for i in range(len(str(instructions))):  # use bit pattern to place a node
        if int(instructions[i]) == 0:  # left node
            if i == (len(str(instructions))) - 1:  # we have reached the final instruction
                tempNode.left = node(leaf[0], 0)  # create new node with correst ascii code
                tempNode = tempNode.left
                tree.append(tempNode)
            else:
                if tempNode.left is None:  # if the node does not exist yet
                    tempNode.left = node("no code left", 0)
                    tempNode = tempNode.left
                    tree.append(tempNode)
                else:  # the node exists
                    #   print("left already exists, advance left")
                    tempNode = tempNode.left  # advance left

        else:  # right node
            if i == (len(str(instructions))) - 1:  # we have reached the final instruction
                tempNode.right = node(leaf[0], 0)
                tempNode = tempNode.right
                tree.append(tempNode)
            else:
                if tempNode.right is None:
                    tempNode.right = node("no code right", 0)
                    tempNode = tempNode.right
                    tree.append(tempNode)
                else:
                    tempNode = tempNode.right
    return tree  # our completed tree with correct code


def assignStringsToTree(tree: node):  # using tree make codes on where node is
    if not (tree.left is None):
        tree.left.code = tree.code + "0"
        assignStringsToTree(tree.left)  # recursive call to keep building code
    if not (tree.left is None):
        tree.right.code = tree.code + "1"
        assignStringsToTree(tree.right)  # recursive


def treeToArry(tree: node, arry):
    # simple inorder traversal
    if (tree == None):
        return
    if (tree.letter != ""):
        arry.append(tree)
    treeToArry(tree.left, arry)
    treeToArry(tree.right, arry)


def codebuilder():  # this code builder only uses file1.txt to decode file2.txt
    ascii_freq = 127 * [0]  # reset in case it's called multiple times

    # open file + get contents
    file = open("File1.txt")
    contents = file.read()

    # get char freqs
    for char in contents:
        asciiVal = ord(char)  # ord() returns ascii value of each char
        if (126 >= asciiVal >= 32) or asciiVal == 10:  # within bound or feed-line
            ascii_freq[asciiVal] = ascii_freq[asciiVal] + 1
        else:
            print("invalid character found in input file: " + char + " " + str(asciiVal))
    huffman_freq.append(node("\n", ascii_freq[10]))  # at position 10 is linefeed character
    for i in range(32, 126):
        huffman_freq.append(node(chr(i), ascii_freq[i]))  # non accounted chars are 0 -- add the rest of it and sort
    huffman_freq.sort()  # frequencies from smallest to largest

    while len(huffman_freq) >= 2:  # need two points for tree
        tempNode = node("", 0)  # root of tree (letter, frequency)
        # OK to directly access here as the while condition ensures at least 2 items in arr
        tempNode.left = huffman_freq.pop(0)  # 0 twice as first pop makes what was
        tempNode.right = huffman_freq.pop(0)  # previously the second element the first one.
        tempNode.calcFreq()  # self freq = left freq + right freq
        huffman_freq.append(tempNode)
        huffman_freq.sort()  # huffman_freq is now containing all the nodes within our trees
    assignStringsToTree(huffman_freq[0])  # generates corresponding binary code for our tree
    huffman_complete = []
    treeToArry(huffman_freq[0], huffman_complete)  # the

    f = open("Codes.txt", "w+")  # output code file that has codes
    for n in huffman_complete:
        f.write(str(ord(n.letter)) + "\t" + n.code + "\n")
    f.close()
    return huffman_complete


def encoder():
    with open("Codes.txt") as file:
        reader = csv.reader(file, delimiter='\t')
        line_count = 0
        codes = []
        for row in reader:
            codes.append(row)
    # number on left is ascii, right is huffman code
    encoded = ""
    i = 0
    flag = 1  # active low to move to next character
    with open("File2.txt") as f:
        for line in f:
            for c in line:
                while flag == 1:
                    if ord(c) == int(codes[i][0]):
                        encoded += codes[i][1]  # the corresponding huffman \n not needed
                        flag = 0
                    else:
                        i += 1  # try next ascii code
                i = 0  # reset i, new character to try
                flag = 1  # next char

    newFile = open("encoded.txt", "w")
    newFile.write(encoded)


# open a specific encoded file and specific huffman code to translate
# take huffman codes -> make binary tree out of them
def decoder():
    tempNode = node("andrew root", 56)  # the root node
    tree = []
    tree.append(tempNode)
    with open("Codes.txt") as file:
        reader = csv.reader(file, delimiter='\t')
        for row in reader:
            tree = decodingTree(row, tree)  # for each node place in tree
    # tree has now been created
    newFile = open("encoded.txt", "r")
    encoded = newFile.read()
    decoded = ""

    print(encoded)
    currentNode = tree[0]
    newFile = open("decoded.txt", "w")
    index = 0
    while encoded[index + 1] is not None:  # Errors but with correct answer!
        flag = False
        if currentNode.left is None and currentNode.right is None:  # no children -- its the correct node!
            decoded += chr(int(currentNode.letter))  # chr() decoded bit for corresponding letter
            newFile.write(chr(int(currentNode.letter)))
            currentNode = tree[0]  # need to set back to the root of the tree
            index -= 1
            flag = True  # wrote a character
        elif int(encoded[index]) == 0 and flag == False:  # move left
            currentNode = currentNode.left
        elif int(encoded[index]) == 1 and flag == False:
            currentNode = currentNode.right
        index += 1


# DRIVER PROGRAM
# CODE BUILDER - read all canonical collection, determine overall frequency, create code strings
# file should have 96 lines

# 1. build codes
# 2. encode using codes
# 3. decode
codebuilder()
encoder()
decoder()
