import random
import math
import copy
from statistics import mean
from .nodetype import NodeType

GLOBAL_INNOVATION = 1
GLOBAL_NODES = 1

class NodeGene():
    def __init__(self, nodeId, nodeType, activationFunction = lambda x: (1/(1+math.exp(-x)))):
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
        return "Connection(#%d, Node %r => Node %r, Weight %f, %s)" \
            % (self.unique, self.source.nodeId, self.sink.nodeId, self.weight, "Enabled" if self.enabled else "Disabled")

    def __eq__(self, other):
        return self.unique == other.unique

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.unique)

class Genome():
    def __init__(self, nodes=None, connections=None):
        self.nodes = {node.nodeId:node for node in (nodes or [])}
        self.connections = {connection.unique:connection for connection in (connections or [])}

    def addNode(self, node):
        self.nodes[node.nodeId] = node

    def node(self, nodeId):
        return self.nodes.get(nodeId, False)

    def connection(self, unique):
        return self.connections.get(unique, False)

    def addConnection(self, source, sink, weight=None, unique=None, enabled=None):
        global GLOBAL_INNOVATION
        connection = ConnectionGene(source, sink, weight, unique, enabled)
        self.connections[connection.unique] = connection
        GLOBAL_INNOVATION += 1

    def copy(self):
        return copy.deepcopy(self)

    def distance(self, other, c_1 = 1.0, c_2 = 1.0, c_3 = 0.4):
        # d = c_1*E/N + c_2*D/N + c_3 * W
        nGenes = (len(self.connections), len(other.connections))

        N = 1 if max(nGenes) < 20 else max(nGenes)

        # Gene uniques below this threshold are disjoint. Uniques higher than this threshold are excess.
        excessThresh = min(max(unique for unique in self.connections.keys()), max(unique for unique in other.connections.keys()))

        matchingGenes = {gene: other.connection(gene.unique) for gene in self.connections.values() if other.connection(gene.unique)}

        weightDiff = mean([abs(a.weight - b.weight) for a,b in matchingGenes.items()])

        otherGenes    = set(self.connections.values()) ^ set(other.connections.values())

        disjoints = {gene for gene in otherGenes if gene.unique > excessThresh}
        excesses  = otherGenes - disjoints

        return (c_1 * len(excesses) + c_2 * len(disjoints)) / N + c_3 * weightDiff


