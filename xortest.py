from neat.pool import NetworkPool
from neat.genome import Genome, NodeGene, ConnectionGene
from neat.nodetype import NodeType
from neat import configuration
import pickle
import pprint

configuration.loadConfig("NEAT.toml")

initialGenome = Genome([NodeGene(NodeType.SENSOR), NodeGene(NodeType.SENSOR), NodeGene(NodeType.BIAS), NodeGene(NodeType.OUTPUT)])
initialGenome.addConnection(initialGenome.node(1), initialGenome.node(4))
initialGenome.addConnection(initialGenome.node(2), initialGenome.node(4))
initialGenome.addConnection(initialGenome.node(3), initialGenome.node(4))

def fitnessFunction(input, output):
    out = output[0]
    correct_answer = input[0] ^ input[1]

    return 1 - abs(out - correct_answer)

openFiles = {}

def writeSpeciesData(gen, species, f):
    f.write("%d\t%f" % (gen, species.topFitness))

def logSpeciesData(pool):
    for species in pool.species:
        if species.id in openFiles:
            writeSpeciesData(pool.generation, species, openFiles[species.id])
        else:
            openFiles[species.id] = open("sp-%d.data" % (species.id))
            writeSpeciesData(pool.generation, species, openFiles[species.id])


pool = NetworkPool(initialGenome, fitnessFunction, lambda *args, **kwargs: None)

inputs = [(1, 0), (0, 1), (0, 0), (1, 1)]

while (16 - pool.maxFitness) > 1.5:
    pool.runOnce(inputs)
    pool.nextGeneration()
    print("Max fitness in generation %d (GID %d): %.20f | Staleness of species %d: %d" % (pool.generation, pool.maxGenome.id, pool.maxFitness, pool.maxSpecies.id, pool.maxSpecies.staleness))

print("Found winning generation %d!" % (pool.generation))

print("Genome nodes: %s" % pprint.pformat(pool.maxGenome.nodes))
print("Genome connections: %s" % pprint.pformat(pool.maxGenome.connections))
