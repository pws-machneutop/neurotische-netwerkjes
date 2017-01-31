from collections import defaultdict, namedtuple
from .nodetype import NodeType
import sys

class Node():
    def __init__(self, nodeGene, connections):
        self.nodeType = nodeGene.nodeType
        self.nodeId = nodeGene.nodeId
        self.weights = {conn.source.nodeId:conn.weight for conn in connections
                        if conn.enabled and conn.sink == self}
        self.activationFunction = nodeGene.activationFunction
        self.connections = connections
        self.dependencies = {conn.source.nodeId for conn in connections
                             if conn.sink == self and conn.enabled}

    def __eq__(self, other):
        if (self.nodeId == other.nodeId) and (self.nodeType == other.nodeType):
            return True
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.nodeId)

    def __call__(self, output, inputs=None):
        if (self.nodeType == NodeType.SENSOR):
            input = inputs.get(self.nodeId)
        else:
            input = sum(inputs.get(dependency)*self.weights[dependency] for dependency in self.dependencies)

        if (self.nodeType == NodeType.BIAS):
            input = 1.0

        if (self.nodeType in (NodeType.HIDDEN, NodeType.OUTPUT)):
            input = self.activationFunction(input)

        output[self.nodeId] = input

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

    def runWith(self, inputdata=None):
        data_pool = defaultdict(float)

        # First, run the inputs and bias nodes
        inputs = [node for node in self.nodes.values() if node.nodeType == NodeType.SENSOR or node.nodeType == NodeType.BIAS]
        inputs.sort(key=lambda node:node.nodeId)

        for ip in inputs:
            ip(data_pool, dict(zip([node.nodeId for node in inputs], inputdata)))


        # Then the hidden nodes
        hidden_nodes = [node for node in self.nodes.values() if node.nodeType == NodeType.HIDDEN]
        nodes_left = {node.nodeId for node in hidden_nodes}

        while (nodes_left):
            for node in hidden_nodes:
                if not (nodes_left & node.dependencies) and node.nodeId in nodes_left:
                    node(data_pool, data_pool)
                    nodes_left -= {node.nodeId}

        # Then the outputs

        outputs = [node for node in self.nodes.values() if node.nodeType == NodeType.OUTPUT]
        output_data = defaultdict(float)

        for node in outputs:
            node(output_data, data_pool)

        output_data = list(output_data.items())
        output_data.sort(key=lambda node: node[0])

        return [x[1] for x in output_data]
