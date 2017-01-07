import math
import random
import sys
from collections import defaultdict
from enum import Enum

GLOBAL_INNOVATION = 1
GLOBAL_NODES = 1

class NodeType(Enum):
    BIAS = 1
    SENSOR = 2
    HIDDEN = 3
    OUTPUT = 4

def modSigmoid(x):
    return 1 / (1 + math.exp(-4.9 * x))

def sigmoid(x):
    return 1 / (1 + math.exp(-x))

class NodeGene():
    def __init__(self, nodeId, nodeType, activationFunction = sigmoid):
        self.nodeId = nodeId
        self.nodeType = nodeType
        self.activationFunction = activationFunction

    def __hash__(self):
        return hash(self.nodeId)

    def __repr__(self):
        if self.nodeType in (NodeType.SENSOR, NodeType.BIAS):
            return "Node(#%r, %r)" % (self.nodeId, self.nodeType)
        return "Node(#%r, %r, %s)" % (self.nodeId, self.nodeType, self.activationFunction.__name__)

class ConnectionGene():
    def __init__(self, source, sink, weight = None, unique = None, enabled = None):
        self.source = source
        self.sink = sink
        self.weight = weight or random.random()
        self.unique = unique or GLOBAL_INNOVATION
        self.enabled = enabled or True

    def __repr__(self):
        return "Connection(Node %r => Node %r, Weight %f, %s)" \
            % (self.source.nodeId, self.sink.nodeId, self.weight, "Enabled" if self.enabled else "Disabled")

class Genome():
    def __init__(self, nodes=None, connections=None):
        self.nodes = nodes or []
        self.connections = connections or []

    def addNode(self, node):
        self.nodes.append(node)

    def node(self, nodeId):
        return [node for node in self.nodes if node.nodeId == nodeId][0]

    def addConnection(self, source, sink, weight=None, unique=None, enabled=None):
        global GLOBAL_INNOVATION
        self.connections.append(ConnectionGene(source, sink, weight, unique, enabled))
        GLOBAL_INNOVATION += 1

class Node():
    def __init__(self, nodeGene, connections):
        self.nodeType = nodeGene.nodeType
        self.nodeId = nodeGene.nodeId
        self.weights = {conn.sink:conn.weight for conn in connections if conn.enabled and conn.source == self}
        self.activationFunction = nodeGene.activationFunction
        self.connections = connections
        self.dependencies = {conn.source.nodeId for conn in connections if conn.sink == self}

    def __eq__(self, other):
        if (self.nodeId == other.nodeId) and (self.nodeType == other.nodeType):
            return True
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.nodeId)

    def __call__(self, output, inputs=None):
        inputs = inputs
        input = inputs[self.nodeId]

        if (self.nodeType == NodeType.BIAS):
            input = 1.0

        if (self.nodeType in (NodeType.HIDDEN, NodeType.OUTPUT)):
            input = self.activationFunction(input)

        for sink, weight in self.weights.items():
            output[sink.nodeId] += weight * input

        if (self.nodeType == NodeType.OUTPUT):
            # TODO: FIX INPUT MODEL!!!
            output[-self.nodeId] = input

        return output

    def __repr__(self):
        if self.nodeType in (NodeType.SENSOR, NodeType.BIAS):
            return "Node(#%r, %r, %r)" % (self.nodeId, self.nodeType, self.weights)
        return "Node(#%r, %r, %s, %r)" % (self.nodeId, self.nodeType, self.activationFunction.__name__, self.weights)

class Network():
    def __init__(self, genome):
        self.nodes = dict(self.createNodes(genome))

    def createNodes(self, genome):
        for nGene in genome.nodes:
            connections = filter(lambda c: c.sink == nGene or c.source == nGene, genome.connections)
            node = Node(nGene, list(connections))
            yield (node.nodeId, node)

    def node(self, nodeId):
        return self.nodes[nodeId]

    def runWith(self, inputs=None):
        output_pool = defaultdict(float, inputs)

        nodes_left = set(self.nodes.keys())

        sys.stdout.write("Running node ")
        while nodes_left:
            for nodeId, node in self.nodes.items():
                if not (nodes_left & node.dependencies) and nodeId in nodes_left:
                    sys.stdout.write("%d " % nodeId)
                    node(output_pool, output_pool)
                    nodes_left -= {nodeId}
        sys.stdout.write("\n")

        return {-key:val for key, val in output_pool.items() if key < 0}

if __name__ == "__main__":
    genome = Genome([
                                        NodeGene(4, NodeType.HIDDEN),
        NodeGene(1, NodeType.SENSOR),   NodeGene(5, NodeType.HIDDEN),
        NodeGene(2, NodeType.SENSOR),                                   NodeGene(8, NodeType.OUTPUT),
        NodeGene(3, NodeType.BIAS),     NodeGene(6, NodeType.HIDDEN),
                                        NodeGene(7, NodeType.BIAS)

        ])


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

    # ---- NETWORK USE ----
    print("Neural network implementing the AND gate")
    print("Python runner written by Sam van Kampen")
    print("Source: https://github.com/pws-machneutop/neurotische-netwerkjes\n")

    print("Network topology (I input B bias H hidden O output): \n")
    print("\t4(H)")
    print("1(I)\t5(H)")
    print("2(I)\t\t8(O)")
    print("3(B)\t6(H)")
    print("\t7(B)\n\n")

    print("Connectivity: ")
    for connection in genome.connections:
        print(connection)
    print("")

    inputs = [(0,0),(1,0),(0,1),(1,1)]
    for input in inputs:
        print("Input: %r" % (input,))
        output = network.runWith({1: input[0], 2: input[1]})
        print("Output: %r" % output[8])


