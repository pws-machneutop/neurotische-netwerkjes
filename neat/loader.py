from .genome import NodeGene, ConnectionGene, Genome
from .pool import NetworkPool
from .nodetype import NodeType

import json, os

class Loader():
    def __init__(self, rundir, gen):
        self.gendir = os.path.join(rundir, "gen-%s" % gen) 

    def getGenomes(self, fitnessFunction):
        pool = NetworkPool()

        for genome in os.listdir(self.gendir):
            data = json.load(open(os.path.join(self.gendir, genome)))
            g = Genome()

            for node in data["nodes"]:
                g.addNode(node[0], node[1])

            for connection in data["connections"]:
                g.addConnection(g.node(connection[1]), g.node(connection[2]), connection[-1], connection[0])

            pool.maxFitness = data["maxFitness"]
            pool.generation = data["generation"]
            pool.addToSpecies(g, speciesId=data["speciesId"], staleness=data["staleness"])

        return pool
