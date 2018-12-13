from get_grammar import read_grammar

#Creates a (Tree) Node for each nonterminal, with respect to the word in the sentence
class Node:
    def __init__(self, nonterm=None, start=None, end=None, word=None, left_node=None, right_Node=None, probability=0):
        self.nonterm = nonterm
        self.start_phrase = start
        self.end_phrase = end
        self.word = word
        self.left = left_node
        self.right = right_Node
        self.prob = probability

#Creates a NxN matrix of Nodes
def create_matrix(n):
    return [[Node() for _ in range(n)] for _ in range(n)]

'''
Three-indexed data structure to allow for storing and retrieval of Nodes used in the parsing of the sentence.
Represents the Bottom-up CYK-Parse Tree of the sentence. 
'''
class Chart:
    #Map storing each Nonterminal of the sentence, used to retrieve and set the Tree for each word
    data = {}
    n = -1
    #Initializes the Chart with an empty NxN matrix that stores the CYK-Parse tree of the sentence
    def __init__(self, nonterms):
        self.n = len(nonterms)
        for k in ["Noun", "Verb", "Prep"]:
            self.data[k] = create_matrix(self.n)
        for nonterm in nonterms:
            self.data[nonterm.p_nont] = create_matrix(self.n)

    #Allows for the 3-indexing of the data structure, overrides the [] operator
    def __getitem__(self, key):
        nonterminal_pos,first_index, second_index = key
        return self.data[nonterminal_pos][first_index][second_index]

    # Allows for the 3-indexing of the data structure, overrides the [] operator
    def __setitem__(self, key, value):
        nonterminal_pos, first_index, second_index = key
        if nonterminal_pos not in self.data:
            self.data[nonterminal_pos] = create_matrix(self.n)
        self.data[nonterminal_pos][first_index][second_index] = value

    #Prints the Chart, Calls recursive method `display` on the top CYK-Parse Tree node, S.
    #Displays the Tree structure of the parsed sentence, allong with the probability of the parse of the sentence.
    def printChart(self, end):
        tree = self.data["S"][0][end-1]
        if tree.left is None and tree.right is None:
            print("This sentence cannot be parsed.")
        else:
            self.display(tree)
        print("Probability = ", format(tree.prob))

    def display(self, tree, indent=0):
        if tree is not None:
            for _ in range(indent): print(" ", end='')
            print(tree.nonterm, end=' ')
            if tree.word is not None:
                print(tree.word, end=' ')
            print()
            self.display(tree.left, indent+3)
            self.display(tree.right, indent+3)
    
    def retrieve_sentence(self, end):
        tree = self.data["S"][0][end-1]
        if tree.left is None and tree.right is None:
            return "This sentence cannot be parsed."
        else:
            sentence = []
            self.get_sentence(tree, sentence)
            return " ".join(sentence)

    def get_sentence(self, tree, sentence):
        if tree is None: return
        s = tree.nonterm
        sentence.append(s)
        if tree.word is not None:
            sentence.append(tree.word)

        self.get_sentence(tree.left, sentence)
        self.get_sentence(tree.right, sentence)

'''
    Parses a sentence in Chomsky-Normal Form using the CYK-Parse algorithm, based on a given grammar.
'''
def cyk_parse(sentence, grammar):
    words_in_sentence = sentence.strip().lower().split() #Breaks the sentence into a list of words
    P = Chart(grammar.get_rules()) #Creates a Chart of the sentence
    n = len(words_in_sentence)

    #Populate the Chart with Tree nodes represnting the possible trees for each word
    for i, word in enumerate(words_in_sentence):
        for wrule in grammar.word_rules:
            if wrule.p_nont != word:
                continue
            else:
                P[wrule.pos, i,i] = Node(wrule.pos, i, i, word, None, None, wrule.prob)

    '''
    Loops O(N^3) times calculating the maximum probability of each word in the sentence based on it's previously created
    tree and calculates the probability of the meaning of the overall sentence. 
    '''
    for length in range(1, n):
        for i in range(n-length):
            j = i + length  # type: int
            for nonterm in grammar.get_rules():
                P[nonterm.p_nont, i, j] = Node(nonterm.p_nont, i, j, None, None, None, 0)
                for k in range(i, j):
                    for nrule in grammar.nonterminal_rules:
                        new_prob = P[nrule.fnonterm, i, k].prob * P[nrule.snonterm, k+1, j].prob * nrule.prob
                        if new_prob > P[nonterm.p_nont, i, j].prob:
                            P[nonterm.p_nont, i, j].left = P[nrule.fnonterm, i, k]
                            P[nonterm.p_nont, i, j].right = P[nrule.snonterm, k+1, j]
                            P[nonterm.p_nont, i, j].prob = new_prob

    return (P,n)


if __name__ == "__main__":
    grammar = read_grammar() #Reads and parses the grammar from file.
    with open("input/cyk_sentences.txt", "r") as fp:
        for line in fp:
            parse_chart, num_words = cyk_parse(line, grammar)
            print("Sentence: %s\nParse Tree: "%line)
            parse_chart.printChart(num_words)
            print("-------------------------------------------------------------------\n")
