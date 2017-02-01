from neat.pool import NetworkPool
from neat.genome import Genome, NodeGene, ConnectionGene
from neat.nodetype import NodeType

from neat import configuration

import json
import pprint
import os

configuration.loadConfig("Mario.toml")

initialGenome = Genome([*(NodeGene(NodeType.SENSOR) for i in range(240)), NodeGene(NodeType.BIAS), *(NodeGene(NodeType.OUTPUT) for i in range(6))])

class FR:
    def __init__(self, f):
        self.f = f
    
    def readline(self):
        i = None
        while not i:
            i = self.f.readline()
        return i

    def write(self, data):
        self.f.write(data)
        self.f.flush()

inFifo = FR(open("ltop", "w+"))
outFifo = FR(open("ptol", "w+"))

def fitnessFunction(input, output):
    return json.loads(inFifo.readline())["fitness"]

class EndRun(RuntimeError):
    pass

def getInput():
    while 1:
        ip = json.loads(inFifo.readline())
        if (ip.get("noInput", False)):
            raise StopIteration
        if (ip.get("complete", False)):
            raise EndRun
        yield ip["input"]

def sendOutput(output):
    data = json.dumps({"output": output}) + '\n'
    outFifo.write(data)

def sendGenome(pool, species, genome, nthGenome):
    data = {"connections": sorted([(conn.source.nodeId, conn.sink.nodeId, conn.weight) for conn in genome.connections.values()
                                    if conn.enabled], key=lambda x: x[0]),
            "nodes": sorted([node.nodeId for node in genome.nodes.values()]),
            "maxFitness": pool.maxFitness,
            "generation": pool.generation,
            "genpercent": str(100*(nthGenome + 1) / len(species.genomes))[:4],
            "genomeId": nthGenome + 1,
            "speciesId": species.id}
    asJson = json.dumps(data)
    outFifo.write((asJson + '\n'))

def sendMaxFitness(pool):
    data = json.dumps({"maxFitness": pool.maxFitness}) + '\n'
    outFifo.write(data)

pool = NetworkPool(initialGenome, fitnessFunction)

try:
    while 1:
        pool.runOnce(getInput, sendGenome, sendOutput)
        pool.nextGeneration()
        print("Max fitness in generation %d (S %d G %d): %.20f | Staleness of species %d: %d" % (pool.generation, pool.maxSpecies.id, pool.maxGenome.id, pool.maxFitness, pool.maxSpecies.id, pool.maxSpecies.staleness))
except EndRun:
    print("Run ends!")
    
