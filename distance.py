from neat.genome import NodeType, Genome, NodeGene, ConnectionGene

g1 = Genome([NodeGene(1, NodeType.SENSOR), NodeGene(2, NodeType.BIAS), NodeGene(3, NodeType.OUTPUT), NodeGene(5, NodeType.HIDDEN)])
g2 = Genome([NodeGene(1, NodeType.SENSOR), NodeGene(2, NodeType.BIAS), NodeGene(3, NodeType.OUTPUT), NodeGene(4, NodeType.HIDDEN)])

g1.addConnection(g1.node(1), g1.node(3), None, 1)
g1.addConnection(g1.node(2), g1.node(3), None, 2, False)
g1.addConnection(g1.node(2), g1.node(5), None, 5)
g1.addConnection(g1.node(5), g1.node(3), None, 6)

g2.addConnection(g2.node(1), g2.node(3), None, 1, False)
g2.addConnection(g2.node(2), g2.node(3), None, 2)
g2.addConnection(g2.node(4), g2.node(3), None, 3)
g2.addConnection(g2.node(1), g2.node(4), None, 4)
g2.addConnection(g2.node(2), g2.node(4), None, 7)

print(g2.distance(g1))

