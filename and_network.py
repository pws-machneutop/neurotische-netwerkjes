from neat.genome import NodeGene, ConnectionGene, Genome
from neat.network import Node, Network
from neat.nodetype import NodeType

genome = Genome([NodeGene(NodeType.SENSOR), NodeGene(NodeType.SENSOR), NodeGene(NodeType.BIAS),
                 NodeGene(NodeType.HIDDEN), NodeGene(NodeType.HIDDEN),
                 NodeGene(NodeType.HIDDEN), NodeGene(NodeType.BIAS), NodeGene(NodeType.OUTPUT)])

x_1 = genome.node(1)
x_2 = genome.node(2)
b_1 = genome.node(3)

hiddens = [genome.node(x) for x in range(4,7)]
b_2 = genome.node(7)

h = genome.node(8)

for n, weight in enumerate((-1.9623, -2.2216, 3.1370)):
    genome.addConnection(x_1, hiddens[n], weight)

for n, weight in enumerate((-1.7715, -2.6616, 2.7087)):
    genome.addConnection(x_2, hiddens[n], weight)

for n, weight in enumerate((2.1962, 3.1903, -3.9824)):
    genome.addConnection(b_1, hiddens[n], weight)

for n, weight in enumerate((-3.9746, -6.0582, 6.5607)):
    genome.addConnection(hiddens[n], h, weight)

genome.addConnection(b_2, h, 0.092103)

network = Network(genome)


if __name__ == "__main__":
    # ---- NETWORK USE ----
    print("Neural network implementing the AND gate")
    print("Python runner written by Sam van Kampen")
    print("Source: https://github.com/pws-machneutop/neurotische-netwerkjes\n")

    #print("Network topology (I input B bias H hidden O output): \n")
    #print("\t4(H)")
    #print("1(I)\t5(H)")
    #print("2(I)\t\t8(O)")
    #print("3(B)\t6(H)")
    #print("\t7(B)\n\n")

    #for _,node in genome.nodes.items():
    #    print(node)

    #print("Connectivity: ")
    #for _, connection in genome.connections.items():
    #    print(connection)
    #print("")

    inputs = [(0,0),(1,0),(0,1),(1,1)]
    for input in inputs:
        print("Input: %r" % (input,))
        output = network.runWith((input[0], input[1]))
        print("Output: %r" % output[0])


