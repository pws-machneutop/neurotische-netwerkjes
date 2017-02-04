from neat.pool import NetworkPool
from neat.genome import Genome, NodeGene, ConnectionGene, modSigmoid
from neat.nodetype import NodeType
from neat.loader import Loader

from neat import configuration

import json
import pprint
import os
import sys

configuration.loadConfig("Mario.toml")

initialGenome = Genome([*(NodeGene(NodeType.SENSOR, i+1) for i in range(240)), NodeGene(NodeType.BIAS, 241), *(NodeGene(NodeType.OUTPUT, 242+i) for i in range(4))])

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
    data = json.dumps({"output": [*output[:2], 0, 0, *output[2:]]}) + '\n'
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

if len(sys.argv) > 1:
    loadPath = sys.argv[1]
    genNumber = sys.argv[2]
    pool = Loader(loadPath, genNumber).getGenomes(fitnessFunction)
    pool.fitnessFn = fitnessFunction
else:
    pool = NetworkPool(initialGenome, fitnessFunction)

try:
    while 1:
        pool.runOnce(getInput, sendGenome, sendOutput)
        pool.nextGeneration()
        print("Max fitness in generation %d (S %d G %s): %.20f | Staleness of species %d: %d" % (pool.generation, pool.maxSpecies.id, pool.maxGenome.idStr(), pool.maxFitness, pool.maxSpecies.id, pool.maxSpecies.staleness))
except EndRun:
    print("Run ends!")
    
