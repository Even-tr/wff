"""
This is a simple script which analyses sentences in propositional logic.
It accepts any sentencen that follows the grammar which i maybe shall outline at a later date.
"""
import numpy as np

# Atomics are letters for formulae assumed to be formule (??)
atomics = 'abcdefghijklmnopqrstuwxyz'

# Punctoation specify order of operations
punctoation = '()'

# single variable operators
negation    = ['¬', '˜', '!', '∼']

# double variable operators
implication = ['⇒', '→', '⊃']
equivalence = ['⇔', '≡', '↔']
conjunction = ['∧', '·', '&']
disjunction = ['∨', '+', '∥', 'v']

# Combining classes of symbols for ease of use later by making the methods refer to them generically
# rather than by name.
monadic = negation
dyacdic = implication + equivalence + conjunction + disjunction
alphabet = monadic + dyacdic + list(atomics) + list(punctoation)

class wff:
    """
    A class which accept a string and builds a simple syntax tree. It strips all whitespaces before parsing.
    eventually it will print a visualization as well as make a truth table.
    """
    def __init__(self, string: str):
        # Handle edge case
        if string == '':
            self._empty = True
            return
        else:
            self._empty = False

        # Since spaces have no syntactic nor semantic meaning, they can be discarded 
        string = ''.join(string.split())

        # Propositions with any symbol outside the alphabet
        # is automatically rejected
        for symbol in string:
            if symbol not in alphabet:
                self._empty = True
                raise ValueError(f"Rejected symbol '{symbol}' found")

        self.root = wff_node(string)
        if self.accepted:
            self.find_atmoics()
        

    
    def accepted(self) -> bool:
        if not self._empty:
            return self.root.accepted
        else:
            return False

    def __str__(self):
        return "wff: " + str(self.root)

    def find_atmoics(self) -> set:
        """
        Finds all the unique atmoic sentences for making truth tables.
        """
        self.atomics = set()

        # Callback function which appends leaves to the atomic set
        func = lambda x: self.atomics.add(x.symbol) if(x.leaf) else None
        traverse_tree(self.root, func )


class wff_node:
    def __init__(self, string: str):
        self.l      = None
        self.r      = None
        self.symbol = None
        self.well_formed = True
        self.leaf = False


        if remove_outer_parenthesis(string):
            string = string[1:-1]

        # Base case
        if len(string) == 1:
            if string in atomics:
                self.symbol = string
                self.leaf = True
            else:
                # Only letters in the atmoics alphabet is accepted.
                self.well_formed = False
                raise ValueError(f"'{self.symbol}' is not an atomic")

        # Case: uniary operator (only negation at this moment)
        elif string[0] in monadic:
            self.symbol = string[0]
            self.r = wff_node(string[1:])

        # Case: binary operator
        else:
            self.symbol, index = find_outer_bijection(string)
            if index <= 0 or len(string)<= index :
                self.well_formed = False
                raise ValueError(f"'{string}' is not valid")
            
            self.l = wff_node(string[:index])
            self.r = wff_node(string[index+1:])

    @property 
    def accepted(self) -> bool:
        if self.leaf:
            return True

        if self.l and self.r:
            return self.l.accepted and self.r.accepted
        elif self.l:
            return self.l.accepted
        elif self.r:
            return self.r.accepted

        else:
            raise RuntimeError('This is all wrong!! The switch statement was supposed to cover all cases?!')


    def __str__(self):
        if not self.well_formed:
            #raise ValueError
            return 'Bad sentence'
        if self.leaf:
            return self.symbol
        if self.symbol in monadic:
            return self.symbol + self.r.__str__()

        return '(' + str(self.l) + self.symbol + str(self.r) + ')'


def remove_outer_parenthesis(string: str)->bool:
    if string[0] != '(' or string[-1] != ')':
        return False
    
    if len(string) < 3:
        raise ValueError(f"'{string}' is not accpeted")
    
    counter = 0
    for i, l in enumerate(string[1: -1]):

        if l == '(':
            counter += 1
        elif l ==')':
            counter -= 1

        if counter == -1 and l == ')':
            return False
        
    return True

##### Some helper functions #####
def find_outer_bijection(string: str):
    if len(string) <3:
        raise ValueError(f"'{string}' was passed as a bijoection, but is too short")

    counter = 0
    for i, l in enumerate(string):
        if l == '(':
            counter += 1
        elif l ==')':
            counter -= 1

        if counter == 0 and l in dyacdic:
            return l, i

    raise ValueError(f"'{string}' has no valid bijection")
    return None, -1


def traverse_tree(formula: wff, func: callable):
    """
    Traverses wff-tree and callbacks the function func. The callback function expects only one argument
    which is the current wff.
    """
    if not formula.accepted:
        return
    # Apply function 
    func(formula)

    # Stop recursion at leaves
    if formula.leaf:
        return


    # Recursive logic
    if formula.l and formula.r:
        traverse_tree(formula.l, func)
        traverse_tree(formula.r, func)

    elif formula.l:
        traverse_tree(formula.l, func)

    elif formula.r:
        traverse_tree(formula.r, func)
    
    else:
        raise RuntimeError('This is all wrong!! The switch statement was supposed to cover all cases?!')



def make_wff(s1, s2) -> wff:
    if s1[0] != '(' and s1 not in atomics:
        s1 = '('+s1+')'

    if np.random.random() < 0.2:
        return negation[0] + s1
    
    if s2[0] != '(' and s2 not in atomics:
        s2 = '(' + s2 + ')'

    return '(' + s1 + np.random.choice(dyacdic) + s2 + ')'


if __name__ == '__main__':
    good_sentences = ['a', 'p', 'p⊃q','¬(p⊃q)', '((p⊃q)⊃r)⊃(∼t⊃q)']
    for s in good_sentences:
        print(wff(s))

    for i in range(100):
        tmp_string = make_wff(*np.random.choice(good_sentences, 2))
        tmp = wff(tmp_string)
        print(tmp, tmp.accepted(), tmp.atomics)