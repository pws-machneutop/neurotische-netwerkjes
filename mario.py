from neat.pool import NetworkPool
from neat.genome import Genome, NodeGene, ConnectionGene
from neat.nodetype import NodeType

from neat import configuration

import json
import pprint
import os

configuration.loadConfig("Mario.toml")

initialGenome = Genome([*(NodeGene(NodeType.SENSOR) for i in range(240)), NodeGene(NodeType.BIAS), *(NodeGene(NodeType.OUTPUT) for i in range(6))])

if (not os.path.exists("ptol.fifo")):
    os.mkfifo("ptol.fifo")

if (not os.path.exists("ltop.fifo")):
    os.mkfifo("ltop.fifo")

# Don't ask about the file open modes. No, really, don't.
outFifo = open("ptol.fifo", "rb+", 0)
inFifo = open("ltop.fifo", "rb+", 0)

def fitnessFunction(input, output):
    return json.loads(inFifo.readline())["fitness"]

def getInput():
    ip = json.loads(inFifo.readline())
    if (ip.get("noInput", False)):
        raise StopIteration
    yield ip["input"]

def sendOutput(output):
    data = json.dumps({"output": output}) + '\n'
    outFifo.write(data.encode('utf-8'))

def sendGenome(pool, species, genome, nthGenome):
    data = {"connections": sorted([(conn.source, conn.sink) for conn in genome.connections.values()], key=lambda x: x[0]),
            "nodes": sorted([node.nodeId for node in genome.nodes.values()]),
            "maxFitness": pool.maxFitness,
            "generation": pool.generation,
            "genomeId": nthGenome,
            "speciesId": species.id}
    asJson = json.dumps(data)
    outFifo.write((asJson + '\n').encode('utf-8'))

def sendMaxFitness(pool):
    data = json.dumps({"maxFitness": pool.maxFitness}) + '\n'
    outFifo.write(data.encode('utf-8'))

pool = NetworkPool(initialGenome, fitnessFunction)

while (16 - pool.maxFitness) > 1.5:
    pool.runOnce(getInput, sendGenome, sendOutput)
    pool.nextGeneration()
    print("Max fitness in generation %d (GID %d): %.20f | Staleness of species %d: %d" % (pool.generation, pool.maxGenome.id, pool.maxFitness, pool.maxSpecies.id, pool.maxSpecies.staleness))
    
