"""
A script implementing a recursive definition of wff within hypothesis.
It first samples from the atomics, then chooses a strategy to combine two
into a disjunction for instance.

some usefull sorces:
https://hypothesis.works/articles/recursive-data/
https://www.inspiredpython.com/course/testing-with-hypothesis/testing-your-python-code-with-hypothesis
https://hypothesis.readthedocs.io/en/latest/data.html#core-strategies
"""
from hypothesis import given, assume, strategies as st
from hypothesis.strategies import composite
from script import wff, wff_node, alphabet, atomics, dyacdic, operations, monadic

# A simple test for a gentle start :)
@given(st.text(alphabet=alphabet))
def test_simple_wff_input_handling(s):
    # Testing that all errors are handled correctly
    try:
        f = wff(s)
        if s != '':
            assert f.accepted()
    except ValueError:
        pass


# Allowed transformations. Since the logic is symbol agnostic in regards to
# the logical notation, i simply use a conventient one.  
def conjunction(input):
    l, r = input
    return f'({l}∨{r})'

def disjunction(input):
    l, r = input
    return f'({l}∧{r})'

def implication(input):
    l, r = input
    return f'({l}⊃{r})'

def negation(input):
    l, r = input
    return f'¬{r}'

def equivalence(input):
    l, r = input
    return f'({l}≡{r})'

recursive_wff = st.recursive(
    st.sampled_from(list(atomics)[:5]), 
    lambda children: st.one_of(
    st.builds(conjunction, st.tuples(children, children)), 
    st.builds(implication, st.tuples(children, children)), 
    st.builds(negation, st.tuples(children, children)), 
    st.builds(equivalence, st.tuples(children, children)), 
    st.builds(disjunction, st.tuples(children, children))
    ),
    max_leaves = 300
)

@given(recursive_wff)
def test_wff_input_handling_recusively(s):
    # Testing that
    f = wff(s)
    assert f.accepted()

# @given(recursive_wff)
# def test_tautalogy_negation(s):
#     f = wff(s)
#     assume(f.tatulogy())
#     f2 = wff('¬' + s)
#     assert f2.contradiction()

# @given(recursive_wff)
# def test_contingency_negation(s):
#     f = wff(s)
#     assert f.accepted()
#     assume(f.contingent())
#     f2 = wff('¬' + s)
#     assert f2.contingent()

@given(recursive_wff)
def test_general_negation(s):
    f = wff(s)
    f2 = wff('¬' + s)

    if f.tatulogy():
        assert f2.contradiction()
    elif f.contradiction():
        assert f2.tatulogy()
    elif f.contingent():
        assert f2.contingent()
    else:
        raise RuntimeError
    
@given(recursive_wff)
def test_table_graph_making(s):
    f = wff(s)
    f.make_table()
    f.make_graph()

if __name__ == '__main__':
    print(recursive_wff.example())