#from script import wff, wff_node
import graphviz


def simple_graphviz_test():
    dot = graphviz.Digraph(comment='The Round Table')

    dot.node('A', 'King Arthur')  
    dot.node('B', 'Sir Bedevere the Wise')
    dot.node('L', 'Sir Lancelot the Brave')

    dot.edges(['AB', 'AL'])
    dot.edge('B', 'L', constraint='false')
    dot.render('doctest-output/round-table.gv', view=True) 

def make_DOT_tree(formula: 'wff_node', graph: graphviz.Digraph=None, parent: 'wff_node' = None):
    assert type(graph) == graphviz.Graph, f"graph sould be of type 'graphviz.Graph', not '{str(type(graph))}'"
    graph.node(str(id(formula)), formula.symbol)
    if parent:
        graph.edge(str(id(parent)), str(id(formula)))
        pass

