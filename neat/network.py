from collections import defaultdict
from .nodetype import NodeType
import sys

class Node():
    def __init__(self, nodeGene, connections):
        self.nodeType = nodeGene.nodeType
        self.nodeId = nodeGene.nodeId
        self.weights = {conn.sink:conn.weight for conn in connections
                        if conn.enabled and conn.source == self}
        self.activationFunction = nodeGene.activationFunction
        self.connections = connections
        self.dependencies = {conn.source.nodeId for conn in connections
                             if conn.sink == self}

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
            return "Node(#%r, %r, %r)" % (self.nodeId, self.nodeType,
                    self.weights)
        return "Node(#%r, %r, %s, %r)" % (self.nodeId, self.nodeType,
                self.activationFunction.__name__, self.weights)

class Network():
    def __init__(self, genome):
        self.nodes = dict(self.createNodes(genome))

    def createNodes(self, genome):
        for nGene in genome.nodes.values():
            connections = [c for c in genome.connections.values()
                    if c.sink == nGene or c.source == nGene]
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
