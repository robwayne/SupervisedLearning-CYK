'''Class that represents the 'POS -> Word[prob]' grammatical rule of the grammar.'''
class WordRule:
    #Stores the word (p_nont), part of speech (pos) and probability of each word rule.
    def __init__(self, parent_nont, part_of_speech, probability):
        self.p_nont = parent_nont
        self.prob = probability
        self.pos = part_of_speech

'''
Class that represents the 'NonTerminal -> Nonterminal, Nonterminal [prob]' grammatical rule of the predefined grammar
'''
class NonTerminalRule:
       def __init__(self, parent_nont, first_term, second_term, prob):
           self.p_nont = parent_nont
           self.fnonterm = first_term
           self.snonterm = second_term
           self.prob = prob

'''Class that stores the entirety of the predefined grammar rules'''
class Grammar:
    word_rules = [] # type: List[WordRule]
    nonterminal_rules = [] #type: List[NonTerminalRule]

    def get_rules(self):
        return self.nonterminal_rules+self.word_rules

#Reads the grammar necessary to parsing the sentence from file (grammar.txt) and returns a Grammar object containing all of it
def read_grammar(input="input/grammar.txt"):
    grammar = Grammar()
    is_nonterminal_rules = True
    with open(input, "r") as fp:
        rules = []
        for line in fp:
            #The different rules of the grammar are separated by a blank newline,
            #therefore if one is encountered then the word rules are being read.
            if line == "\n":
                grammar.nonterminal_rules = rules
                rules = []
                is_nonterminal_rules = False
                continue

            line_terms = line.split("->")
            parent_nonterminal = line_terms[0].strip()

            line_terms = line_terms[1].split()

            if is_nonterminal_rules:
                fterm = line_terms[0]
                sterm = line_terms[1]
                prob = float(line_terms[2].replace("]", "").replace("[", ""))
                rule = NonTerminalRule(parent_nonterminal, fterm, sterm, prob)
            else:
                prob = float(line_terms[1].replace("[", "").replace("]", ""))
                rule = WordRule(line_terms[0], parent_nonterminal,  prob)

            rules.append(rule)
        grammar.word_rules = rules

    return grammar