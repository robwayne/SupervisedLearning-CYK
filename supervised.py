import sys
import argparse
from collections import Counter

from read_input import read_file
from get_grammar import read_grammar
import cyk_parse

#Using arg_parse to get the command line arguments and provide helpful commandline info for the arguments
def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('n', type=int, help='number of training cases')
    parser.add_argument('-v', action='store_true', help="determines if the output should be verbose (detailed)")
    return parser.parse_args()

#Node class represents each terminal in the string
class Node:
    def __init__(self, val, children=[]): # type: string, list
        self.value = val # represents either a phrase marker or a POS
        self.children = children # chidlren of this node / all other POS or phrase markers
    
    def __repr__(self):
        return self.value

def is_op(c): #determines whether or not a string is special POS or phrase marker (PM) (operator)
    return c.startswith("+") or c.startswith("*")

def get_num_args(c): #returns the number of arguments a operator (POS/PM) has
    return 2 if c.startswith("*") else 1 #PM have 2 arguments, POS only 1

#these are global variables used to determine the frequency of a rule A -> W , A -> B C
occurrences = Counter() #counts the number of occurrences of a node / operator/word
child_occurrences = {} #details a count of all the list of special children a node has, 

# This is used to reconstruct the tree that is generated from a preorder search of the labels 
def prefixToExpTree(S, k): # type list (of words), int
    N = Node(S[k])
    occurrences[S[k]] += 1 #everytime we see a new PM/POS we increment it's count
    k += 1
    if is_op(S[k-1]):
        l = []
        args = get_num_args(S[k-1])
        for _ in range(get_num_args(S[k-1])): # for all the arguments of a PM/POS node we add it to our current children list
            T, k = prefixToExpTree(S, k)
            if N.value not in child_occurrences: 
                child_occurrences[N.value] = Counter() # create a unique count of all the children of this current node
            l.append(T)
        N.children = l #add all the newly discovered children to the current node's list 

        if (args == 2):
            key = "%s %s"%(l[0].value, l[1].value)
            child_occurrences[N.value][key] += 1 #PM have multiple arguments so we need to specify that we are incrementing each child
        else:
            child_occurrences[N.value][l[0].value] += 1 #POS only have 1 child so we only need to icrement that chil's count

    return N, k

#Train the corpus of data and generate the necessary probabilities for the rules
def train(sentences, verbose):
    def get_occurrences(sentences):
        for sentence in sentences:
            sentence = sentence.strip().split()
            prefixToExpTree(sentence, 0) #reconstruct the preorder tree and get all the counts

    # calculate all the probabilities of the the rules A -> B C, A -> W
    def get_probabilities(): # also generate the output that is necessary for the cyk-parse
        if not len(child_occurrences): get_occurrences(sentences)
        output = [[],[]]
        for key, values in child_occurrences.items():
            n = occurrences[key]
            for child,count in values.items():
                child = child.replace("*", "")
                child = child.replace("+", "")
                line = "%s -> %s [%f]"%(key[1:], child, (count/n)) # Create the grammar 
                if key.startswith("+"):
                    output[1].append(line)
                elif key.startswith("*"):
                    output[0].append(line)

        return output # return a list of all the lines that should be in the grammar.txt file that is used by cyk-parse

    # after generating all the input for the cyk-parse, write it to file
    def write_grammar(grammar, file='input/grammar.txt'):
        with open(file, 'w+') as fp:
            k = len(grammar[1])
            grammar[0].sort(key=lambda x: x.startswith('* S'))
            if verbose: # if the program was called with verbose flag, print all the run time messages
                print("\nGrammar")
            for line in grammar[0]:
                fp.write(line+"\n") # write the grammar to file
                if verbose:
                    print(line)
            fp.write("\n")
            if verbose:
                print("\nLexicon")
            for i,line in enumerate(grammar[1]): 
                if verbose:
                    print(line)
                if i < k-1:
                    line += "\n"
                fp.write(line) # write the lexicon to the file

    get_occurrences(sentences)
    write_grammar(get_probabilities())

# test the accuracy of the training set by running it with labelled corpus
def test(test_sentences, verbose):
    gram = read_grammar()
    accuracy = 0
    if verbose: print("\nParses:") # verbose output
    for ts in test_sentences:
        orig = ts
        ts = ts.strip().split()
        s = ""
        for word in ts:
            if is_op(word):
                continue
            s += word+" " # read the sentences and generate human readable sentences without the classifying tags eg. '+Noun dog' -> 'dog'

        pchart, n = cyk_parse.cyk_parse(s, gram) # run the cyk_parse on all the generated grammar
        orig = orig.replace("*", "").replace("+", "")
        parsed_sentence = pchart.retrieve_sentence(n)
        if verbose: # verbose output
            print(parsed_sentence, end=' ')
            if orig == parsed_sentence: # if the cyk generated parse matches the labelled parses then we have a correct label
                print("Right")  
                accuracy += 1
            else: 
                print("Wrong")
    n = len(test_sentences)
    if verbose: # determine the accuracy of the training of the data 
        print("\nAccuracy: The parser was tested on %d sentences. It got %d right, for an accuracy of %.2f."%(n, accuracy, accuracy/n))


if __name__ == "__main__":
    args = get_args()
    n = args.n
    training_set, test_set = read_file(n)
    train(training_set, args.v)
    test(test_set, args.v)



