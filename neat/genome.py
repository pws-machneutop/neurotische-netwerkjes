import random
import math
import copy
from statistics import mean
from . import configuration
from collections import defaultdict
from .nodetype import NodeType
import itertools
from tarjan.tc import tc as transitive_closure
from tarjan import tarjan
from pprint import pprint

GLOBAL_INNOVATION = 1
GLOBAL_NODES = 1

GENOME_ID = 1

def modSigmoid(x):
    return (2 / (1 + math.exp(-4.9*x)))-1

class NodeGene():
    def __init__(self, nodeType, nodeId=None, activationFunction = modSigmoid):
        global GLOBAL_NODES
        global GLOBAL_INNOVATION
        self.nodeId = nodeId or GLOBAL_NODES
        GLOBAL_NODES += 1
        self.nodeType = nodeType
        self.activationFunction = activationFunction

    def __eq__(self, other):
        try:
            return self.nodeId == other.nodeId
        except:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.nodeId)

    def __repr__(self):
        if self.nodeType in (NodeType.SENSOR, NodeType.BIAS):
            return "Node(#%r, %r)" % (self.nodeId, self.nodeType)
        return "Node(#%r, %r, %s)" % (self.nodeId, self.nodeType, self.activationFunction.__name__)

class ConnectionGene():
    def __init__(self, source, sink, weight = None, connectionId = None, enabled = None):
        global GLOBAL_INNOVATION
        self.source = source
        self.sink = sink
        self.weight = weight or random.gauss(0.0, 1.0)
        self.connectionId = connectionId or GLOBAL_INNOVATION
        GLOBAL_INNOVATION += 1
        self.enabled = enabled or True

    def __repr__(self):
        return "Connection(#%d, Node %r => Node %r, Weight %f, %s)" \
            % (self.connectionId, self.source.nodeId, self.sink.nodeId, self.weight, "Enabled" if self.enabled else "Disabled")

    def __eq__(self, other):
        return self.connectionId == other.connectionId

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.connectionId)

class Genome():
    def __init__(self, nodes=None, connections=None):
        global GENOME_ID
        self.config = configuration.getGlobalConfig()
        self.nodes = {node.nodeId:node for node in (nodes or [])}
        self.connections = {connection.connectionId:connection for connection in (connections or [])}
        self.fitness = 0
        self.id = GENOME_ID
        GENOME_ID += 1

        self.globalRank = 0

    def addNode(self, nodeId, nodeType):
        node = NodeGene(NodeType(nodeType), nodeId)
        self.nodes[node.nodeId] = node

    def mutateNode(self):
        if (not self.connections):
            return False

        node = NodeGene(NodeType.HIDDEN)
        # Add a node between an existing connection
        conn = random.choice(list(self.connections.values()))
        conn.enabled = False

        new_connections = (ConnectionGene(conn.source, node, weight = 1), ConnectionGene(node, conn.sink, weight=conn.weight))

        for connection in new_connections:
            self.connections[connection.connectionId] = connection

        self.nodes[node.nodeId] = node

    def mutateConnection(self):
        source_eligible = [node for node in self.nodes.values() if node.nodeType in (NodeType.SENSOR, NodeType.BIAS, NodeType.HIDDEN, NodeType.OUTPUT)]
        sink_eligible = [node for node in self.nodes.values() if node.nodeType in (NodeType.HIDDEN, NodeType.OUTPUT)]

        graph = defaultdict(list)
        for connection in self.connections.values(): graph[connection.source].append(connection.sink)

        # The transitive closure of a graph G is the graph G' for which there is an edge (v, w) where there is a path from v to w in G.
        # (more succinctly: every indirectly connected node pair (v,w) in G is also directly connected in G')
        tc = transitive_closure(graph)
        tc_pairs = [(source, sink) for source,sinks in tc.items() for sink in sinks]
        existing_connections = {(conn.source, conn.sink):conn for conn in self.connections.values()}

        combinations = [combination for combination in itertools.product(source_eligible, sink_eligible)
                            if combination[0] != combination[1] and combination[::-1] not in tc_pairs]

        if (not combinations):
            return False
        chosen = random.choice(combinations)

        if chosen in existing_connections.keys():
            conn = existing_connections[chosen]
            conn.enabled = True
            conn.weight = random.random()
        else:
            self.addConnection(*chosen)

        #pprint({k:v for k,v in self.connections.items() if v.enabled})
        #print()

    def node(self, nodeId):
        return self.nodes.get(nodeId, False)

    def connection(self, connectionId):
        return self.connections.get(connectionId, False)

    def addConnection(self, source, sink, weight=None, connectionId=None, enabled=None):
        connection = ConnectionGene(source, sink, weight, connectionId, enabled)
        self.connections[connection.connectionId] = connection

    def mutate(self):
        if (random.random() < self.config["rates"]["mutation"]):
            self.mutateWeights()

        if (random.random() < self.config["rates"]["newnode"]):
            self.mutateNode()

        if (random.random() < self.config["rates"]["newlink"]):
            self.mutateConnection()

    def mutateWeights(self):
        for connection in self.connections.values():
            if (random.random() < self.config["rates"]["perturbation"]):
                connection.weight += (random.gauss(0.0, 0.5))
            else:
                connection.weight = random.gauss(0.0, 1.0)

    def copy(self):
        return copy.deepcopy(self)

    def sameSpecies(self, other):
        c_1 = self.config["compatibility"]["excess"]
        c_2 = self.config["compatibility"]["disjoint"]
        c_3 = self.config["compatibility"]["weights"]

        # d = c_1*E/N + c_2*D/N + c_3 * W
        nGenes = (len(self.connections), len(other.connections))

        N = 1

        # Gene connectionIds below this threshold are disjoint. Uniques higher than this threshold are excess.
        if (len(self.connections) == 0) or (len(other.connections) == 0):
            excessThresh = 0
        else:
            excessThresh = min(max(cId for cId in self.connections.keys()), max(cId for cId in other.connections.keys()))

        matchingGenes = {gene: other.connection(gene.connectionId) for gene in self.connections.values() if other.connection(gene.connectionId)}

        weightDiff = [abs(a.weight - b.weight) for a,b in matchingGenes.items()]
        if (weightDiff):
            avgweightDiff = mean(weightDiff)
        else:
            avgweightDiff = 0

        otherGenes    = set(self.connections.values()) ^ set(other.connections.values())

        disjoints = {gene for gene in otherGenes if gene.connectionId > excessThresh}
        excesses  = otherGenes - disjoints

        return ((c_1 * len(excesses) + c_2 * len(disjoints)) / N + c_3 * avgweightDiff) < self.config["speciation"]["species_difference"]

    def isCyclic(self):
        graph = defaultdict(list)
        for connection in self.connections.values(): graph[connection.source].append(connection.sink)

        # The transitive closure of a graph G is the graph G' for which there is an edge (v, w) where there is a path from v to w in G.
        # (more succinctly: every indirectly connected node pair (v,w) in G is also directly connected in G')
        tj = tarjan(graph)

        return any(len(sc) >= 2 for sc in tj)

    def crossover(self, other):
        global GENOME_ID
        offspring = Genome()

        if (len(self.connections) == 0) or (len(other.connections) == 0):
            excessThresh = 0
        else:
            excessThresh = min(max(cId for cId in self.connections.keys()), max(cId for cId in other.connections.keys()))

        matchingGenes = [(gene, other.connection(gene.connectionId)) for gene in self.connections.values() if other.connection(gene.connectionId)]

        otherGenes = set(self.connections.values()) ^ set(other.connections.values())

        matchingChoices = [random.choice(x) for x in matchingGenes]

        if (self.fitness > other.fitness):
            otherChoices = [choice for choice in otherGenes if choice in self.connections.values()]
        elif (other.fitness > self.fitness):
            otherChoices = [choice for choice in otherGenes if choice in other.connections.values()]
        else:
            otherChoices = list(otherGenes)

        offspring.connections = {i.connectionId:i for i in (matchingChoices + otherChoices)}

        for connection in offspring.connections.values():
            if connection.enabled == False:
                connection.enabled == False if random.random() < self.config["rates"]["disabled_inherit"] else True

        offspring.nodes = {i.nodeId:i for i in (set(self.nodes.values()) | set(other.nodes.values()))}
        if (offspring.isCyclic()):
            print("YOU'VE MADE THE WRONG DECISIOOOONN!!!!")
            return random.choice((self, other))

        GENOME_ID += 1
        offspring.id = GENOME_ID

        return offspring


