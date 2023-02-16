"""
This is a simple script which analyses sentences in propositional logic.
It accepts any sentencen that follows the grammar which i maybe shall outline at a later date.
"""
import numpy as np
import graphviz
from graphing import make_DOT_tree
from itertools import product
from tabulate import tabulate
import re

# Atomics are letters for formulae assumed to be formule (??)
atomics = 'abcdefghijklmnopqrstuwxyz'

# Punctoation specify order of operations
punctoation = '()'

# single variable operators
negation    = '¬˜!∼'

# double variable operators
implication = '⇒→⊃'
equivalence = '⇔≡↔'
conjunction = '∧·&'
disjunction = '∨+∥v'

# Truth value functions
def negation_eval(r):
    return int(not r)

def implication_eval(l,r):
    return int((l == False) or (r == True))

def equivalence_eval(l, r):
    return int(l == r)

def conjunction_eval(l, r):
    return int(l and r)

def disjunction_eval(l, r):
    return int(l or r)

operations = {
    negation: negation_eval,
    implication: implication_eval,
    equivalence: equivalence_eval,
    conjunction: conjunction_eval,
    disjunction: disjunction_eval
}

# Combining classes of symbols for ease of use later by making the methods refer to them generically
# rather than by name.
monadic = negation
dyacdic = implication + equivalence + conjunction + disjunction
alphabet = monadic + dyacdic + atomics + punctoation

##### ##### ##### ##### ##### #####  
##### #####   CLASSES   ##### ##### 
##### ##### ##### ##### ##### #####  

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
        self.string = ''.join(string.split())
        string = self.string

        # Propositions with any symbol outside the alphabet
        # is automatically rejected
        for symbol in string:
            if symbol not in alphabet:
                self._empty = True
                raise ValueError(f"Rejected symbol '{symbol}' found")

        self.root = wff_node(string)
        if self.accepted:
            self.find_atmoics()
            self.graph = graphviz.Graph(comment= self.string, format='PNG')

        self.main_column = []


    def truth_table(self):
        pass

    def accepted(self) -> bool:
        """
        Returns True if the string was parsed without error
        """
        if not self._empty:
            return self.root.accepted
        else:
            return False

    def __str__(self):
        return "wff: " + str(self.root)

    def find_atmoics(self) -> None:
        """
        Finds all the unique atmoic sentences for making truth tables.
        """
        self.atomics = set()

        # Callback function which appends leaves to the atomic set
        func = lambda x: self.atomics.add(x.symbol) if(x.leaf) else None
        traverse_tree(self.root, func )
        self.atomics_ordered = list(self.atomics)
        self.atomics_ordered.sort()

    def make_graph(self) -> None:
        """
        Makes a DOT graph
        """
        #traverse_tree(self.root, lambda x: self.graph.node(str(id(x)), x.symbol))
        func = lambda x, y: make_DOT_tree(x, graph=self.graph, parent=y)
        traverse_tree_parent(self.root, None, func)

    def display_graph(self):
        self.graph.render('doctest-output/round-table.gv', view=True)


    def make_table(self):
        #print(f'\nMaking table for {self.string}')
        self.Table = TableMaker(self.string)
            
        for index in range(2**self.Table.depth):
            line = self.Table.get_line()
            value, string = self.root.evaluate_line(line, self.atomics_ordered)
            self.main_column.append(value)
            #print(f'VALUE: {value}, LINE: {string}')
            self.Table.add_truth_value_line(string)

    def display(self):
        self.Table.display()

    def tatulogy(self):
        return not any(x == 0 for x in self.main_column)
    
    def contradiction(self):
        return not any(x == 1 for x in self.main_column)
    
    def contingent(self):
        return not self.tatulogy() and not self.contradiction()
    
class wff_node:
    def __init__(self, string: str):
        self.l      = None
        self.r      = None
        self.symbol = None
        self.well_formed = True
        self.leaf = False

        if find_outer_parenthesis(string):
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
            self.symbol, index = find_outer_operation(string)
            if index <= 0 or len(string)<= index :
                self.well_formed = False
                raise ValueError(f"'{string}' is not valid")
            
            self.l = wff_node(string[:index])
            self.r = wff_node(string[index+1:])

                    
        for key in operations:
            if self.symbol in key:
                self._eval_func = operations[key]

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

    def evaluate_line(self, line: np.array, colnames: list, callback = lambda x: x):
        """
        Takes a line from a truth table and returns
        """
        # initialize with an illegal value to catch errors
        value = -2

        if self.leaf:
            value = line[colnames.index(self.symbol)]
            return value, str(value)


        elif self.symbol in monadic:
            r, rstring = self.r.evaluate_line(line, colnames, callback=callback)
            value = self._eval_func(r)
            return value, str(value) + rstring


        else:
            l, lstring = self.l.evaluate_line(line, colnames, callback=callback)
            r, rstring = self.r.evaluate_line(line, colnames, callback=callback)
            value = self._eval_func(l, r)
            return value, lstring + str(value) + rstring


    def __str__(self):
        if not self.well_formed:
            #raise ValueError
            return 'Bad sentence'
        if self.leaf:
            return self.symbol
        if self.symbol in monadic:
            return self.symbol + self.r.__str__()

        return '(' + str(self.l) + self.symbol + str(self.r) + ')'


class TableMaker:
    def __init__(self, string: str) -> None:
        """
        A class which generates the template table for a truth table.
        Ii calculates the needed size and creates a 2d array of it. 
        
        It then makes the left hand side with the assigned truth values for the 
        atmoic prepositions.

        It uses tabulate internally for pretty printing.
        """
        self._unparsed_string = string

        # Remove punctioation
        for i in punctoation:
            string = string.replace(i, '')

        self.atomics = [i for i in string if i in atomics]
        self.operations = [i for i in string if i in monadic or i in dyacdic]
        self.depth = len(set(self.atomics))
        self.out_widt = len(self.atomics) + len(self.operations)

        assert len(string) == len(self.atomics) + len(self.operations)
        
        self.left_table = np.zeros((2**self.depth, self.depth), dtype=int)
        self.right_table = np.zeros((2**self.depth, self.out_widt), dtype=int) - 1
        self._make_table()


        # counter used to keep track where to insert calculated truth values
        self._current_line = -1
        self._current_col = -1
        self._current_flat_index = -1
        self.left_header = list(set(self.atomics))
        self.left_header.sort()
        

    def _make_table(self):
        for i, line in enumerate(product((1, 0), repeat=self.depth)):
            self.left_table[i:] = line

    def display(self):
        print(f'\nTruth table for {self._unparsed_string}')
        full_table = np.concatenate((self.left_table, self.right_table), axis=1)
        print(tabulate(full_table, headers=self._make_table_header()))

    def _make_table_header(self):        
        ls = re.split( f'(\\(*[{atomics + monadic + dyacdic}]\\)*)', self._unparsed_string)
        right_header = [i for i in ls if i != '']
        assert ''.join(right_header) == self._unparsed_string, \
            f"Parsing error: '{self._unparsed_string}' was parsed to '{''.join(right_header)}'"

        return self.left_header + right_header


    def get_line(self):
        self._current_line += 1
        assert self._current_line <= len(self.left_table), \
            f'Tried to acces line {self._current_line} in table with {len(self.left_table)} lines'

        return self.left_table[self._current_line]
    
    def add_truth_value_line(self, line: str):
        line = [int(i) for i in line]
        for v in line:
            assert v == 0 or v == 1, f'Illegal value {v} found in line'
        
        self.right_table[self._current_line] = line



##### ##### ##### ##### ##### ##### 
#####  Some helper functions  #####
##### ##### ##### ##### ##### ##### 

def find_outer_parenthesis(string: str)->bool:
    """
    Returns True if a string needs its outermost parenthesis removed before further parsing
    """
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

def find_outer_operation(string: str):
    """
    Finds the outermost operation in a given string. Raises
    a ValueError if not found.
    """
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

def traverse_tree(formula: wff_node, func: callable) -> None:
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

def traverse_tree_parent(formula: wff_node, parent:wff_node, func: callable):
    """
    Traverses wff-tree and callbacks the function func. The callback function expects only one argument
    which is the current wff.
    """
    if not formula.accepted:
        return
    # Apply function 
    func(formula, parent)

    # Stop recursion at leaves
    if formula.leaf:
        return

    # Recursive logic
    if formula.l and formula.r:
        traverse_tree_parent(formula.l, formula, func)
        traverse_tree_parent(formula.r, formula, func)

    elif formula.l:
        traverse_tree_parent(formula.l, formula, func)

    elif formula.r:
        traverse_tree_parent(formula.r, formula, func)
    
    else:
        raise RuntimeError('This is all wrong!! The switch statement was supposed to cover all cases?!')

def make_wff(s_1: wff, s_2: wff) -> wff:
    """
    Makes a random wff from the tw
    """
    if s_1[0] != '(' and s_1 not in atomics:
        s_1 = '('+s_1+')'

    if np.random.random() < 0.2:
        return negation[0] + s_1
    
    if s_2[0] != '(' and s_2 not in atomics:
        s_2 = '(' + s_2 + ')'

    return '(' + s_1 + np.random.choice(dyacdic) + s_2 + ')'



if __name__ == '__main__':
    good_sentences = ['a', 'p', 'p⊃q', 'p+¬p' ,'¬(p⊃q)', '((p⊃q)⊃r)⊃(∼t⊃q)']
    f = wff(good_sentences[3])
    f.make_table()

    for s in good_sentences:
        f = wff(s)
        f.make_table()
        print(f.contradiction())

    """
    for i in range(100):
        tmp_string = make_wff(*np.random.choice(good_sentences, 2))
        tmp = wff(tmp_string)
        print(tmp, tmp.accepted(), tmp.atomics)
    """