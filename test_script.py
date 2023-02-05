import pytest
from hypothesis import given, assume, strategies as st
from script import wff, wff_node, alphabet


good_sentences = ['a', 'p', 'p⊃q','¬(p⊃q)']

def test_simple_wff():
    for s in good_sentences:
        assert wff(s).accepted() == True


@given(st.text(alphabet = alphabet))
def test_wff_input_handling(s):
    # Testing that
    try:
        wff(s)
    except ValueError:
        pass
