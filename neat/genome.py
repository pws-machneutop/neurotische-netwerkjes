import random
import math
from .nodetype import NodeType

GLOBAL_INNOVATION = 1

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
        return "Connection(Node %r => Node %r, Weight %f, %s)" \
            % (self.source.nodeId, self.sink.nodeId, self.weight, "Enabled" if self.enabled else "Disabled")
    def __eq__(self, other):
        return self.unique == other.unique

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.unique)

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

