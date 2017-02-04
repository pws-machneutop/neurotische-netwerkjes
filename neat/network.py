from collections import defaultdict, namedtuple, OrderedDict
from .nodetype import NodeType
from pprint import pprint
import random
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
    
    def __repr__(self):
        if self.nodeType in (NodeType.SENSOR, NodeType.BIAS):
            return "Node(#%r, %r, %r)" % (self.nodeId, self.nodeType,
                    self.weights)
        return "Node(#%r, %r, %s, %r)" % (self.nodeId, self.nodeType,
                self.activationFunction.__name__, self.weights)

    def __call__(self, output, inputs=None, final_out=None):
        if (self.nodeType == NodeType.SENSOR):
            input = inputs.get(self.nodeId)
        else:
            input = 0
            for dependency in self.dependencies:
                val = inputs.get(dependency, 0.0)
                cW = self.weights.get(dependency, 0.0)
                if (val == None):
                    inputs[dependency] = 0.0
                    val = 0.0
                input += val * cW

        if (self.nodeType == NodeType.BIAS):
            input = 1.0

        if (self.nodeType in (NodeType.HIDDEN, NodeType.OUTPUT)):
            input = self.activationFunction(input)

        output[self.nodeId] = input
        
        if self.nodeType == NodeType.OUTPUT:
            final_out[self.nodeId] = input

        return output


class Network():
    def __init__(self, genome):
        self.nodes = OrderedDict(sorted(self.createNodes(genome), key=lambda x:x[0]))
        self.values = defaultdict(float)

    def node(self, nodeId):
        return self.nodes[nodeId]
        
    def createNodes(self, genome):
        for nGene in genome.nodes.values():
            connections = [c for c in genome.connections.values()
                    if c.sink == nGene or c.source == nGene]
            node = Node(nGene, list(connections))
            yield (node.nodeId, node)

    def runWith(self, inputdata=None):
        data_pool = defaultdict(float)
        output_data = defaultdict(float)

        # First, run the inputs and bias nodes
        inputs = [node for node in self.nodes.values() if node.nodeType == NodeType.SENSOR or node.nodeType == NodeType.BIAS]
        inputs.sort(key=lambda node:node.nodeId)

        for ip in inputs:
            ip(self.values, dict(zip([node.nodeId for node in inputs], inputdata)), output_data)


        # Then the other nodes
        other_nodes = [node for node in self.nodes.values() if node.nodeType in (NodeType.OUTPUT, NodeType.HIDDEN)]

        for node in other_nodes:
            node(self.values, self.values, output_data)

        self.values.update(output_data)
        output_data = list(output_data.items())
        output_data.sort(key=lambda node: node[0])

        return [x[1] for x in output_data]
