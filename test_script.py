import pytest
from script import wff, wff_node, alphabet


good_sentences = ['a', 'p', 'p⊃q','¬(p⊃q)']

def test_simple_wff():
    for s in good_sentences:
        assert wff(s).accepted() == True




def test_simple_truth_table():
    string = 'p⊃q'

    w = wff(string)
    assert w.accepted()
    w.make_table()
    assert w.contingent()