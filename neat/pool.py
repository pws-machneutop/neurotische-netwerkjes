#
# NetworkPool
#

import pprint
import random
import sys
import os
import pdb
import datetime
import json
import traceback
from .species import Species
from .network import Network
from . import configuration

class NetworkPool():
    def __init__(self, initialGenome=None, fitnessFunction=None):
        print("Constructing pool.")
        self.fitnessFn = fitnessFunction
        self.config = configuration.getGlobalConfig()
        self.species = []
        if initialGenome:
            for i in range(self.config["pool"]["population"]):
                print("Constructing genome %d" % i)
                copy = initialGenome.copy()
                copy.mutate()
                self.addToSpecies(copy)

        self.maxFitness = 0.0
        self.maxPrevFitness = 0.0
        self.maxGenome = None
        self.evaluatedGenomes = 0
        self.generation = 1
        
        self.rtdir = "run-" + datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        os.mkdir(self.rtdir)

    def addToSpecies(self, genome, speciesId=None, staleness=None):
        for species in self.species:
            if species.genomes[0].sameSpecies(genome):
                species.genomes.append(genome)
                return

        newSpecies = Species()
        newSpecies.genomes.append(genome)
        newSpecies.staleness = staleness or 0
        self.species.append(newSpecies)

    def rankGlobally(self):
        globalList = [genome for species in self.species for genome in species.genomes]

        globalList.sort(key=lambda x: x.fitness)

        for n, genome in enumerate(globalList):
            genome.globalRank = n

    def totalAverageFitness(self):
        total = 0

        for species in self.species:
            total = total + species.averageFitness

        return total

    def nextGeneration(self):
        self.cullSpecies(cutToOne=False)
        self.removeStaleSpecies()
        self.rankGlobally()
        for species in self.species: species.calculateAverageFitness()
        self.removeWeakSpecies()

        self.totalFitness = self.totalAverageFitness()

        children = []

        for species in self.species:
            toBreed = (self.config["pool"]["population"] * species.averageFitness) // self.totalFitness
            toBreed -= 1

            children.append(self.generateOffspring(species))

        self.cullSpecies(cutToOne=True)

        while (len(children) + len(self.species) < self.config["pool"]["population"]):
            species = random.choice(self.species)
            children.append(self.generateOffspring(species))

        for child in children: self.addToSpecies(child)

        self.generation += 1

    def generateOffspring(self, species):
        if random.random() < self.config["rates"]["crossover"]:
            if (random.random() < self.config["rates"]["interspecies"]):
                species2 = random.choice(self.species)
                genome = random.choice(species2.genomes)
                child = genome.crossover(random.choice(species.genomes))
                child.mutate()
                return child
            elif len(species.genomes) >= 2:
                g1, g2 = random.sample(species.genomes, 2)
                child = g1.crossover(g2)
                child.mutate()
                return child

        child = random.choice(species.genomes).copy()
        child.mutate()
        return child


    def cullSpecies(self, cutToOne = False):
        for species in self.species:
            species.sortGenomes()

            remaining = (len(species.genomes) // 2) + 1

            if (cutToOne):
                remaining = 1

            species.genomes = species.genomes[:remaining]

    def removeWeakSpecies(self):
        survived = []

        self.totalFitness = self.totalAverageFitness()

        for species in self.species:
            toBreed = (self.config["pool"]["population"] * species.averageFitness) // self.totalFitness
            if toBreed >= 1:
                survived.append(species)
            else:
                print("Removing species %d (tB: %d, avF: %f, tF: %f)" % (species.id, toBreed, species.averageFitness, self.totalFitness))

        self.species = survived

    def removeStaleSpecies(self):
        survived = []
        for species in self.species:
            species.sortGenomes()

            if (species.genomes[0].fitness > species.topFitness):
                species.topFitness = species.genomes[0].fitness
                species.staleness = 0
            else:
                species.staleness += 1

            if (species.staleness < self.config["speciation"]["stagnation_threshold"]) or (species.topFitness >= self.maxFitness):
                survived.append(species)
            else:
                print("Removing stale species %d." % (species.id))

        self.species = survived
    
    def saveGenome(self, species, n, genome):
        dataFile = open(os.path.join(self.rtdir, "gen-%d" % self.generation, "spc-%d-gnm-%d" % (species.id, n)), "w")
        data = {"connections": sorted([(conn.connectionId, conn.source.nodeId, conn.sink.nodeId, conn.weight) for conn in genome.connections.values()
                                if conn.enabled], key=lambda x: x[0]),
        "nodes": sorted([(node.nodeId, node.nodeType.value) for node in genome.nodes.values()]),
        "maxFitness": self.maxFitness,
        "generation": self.generation,
        "genomeId": n,
        "staleness": species.staleness,
        "speciesId": species.id}
        
        dataFile.write(json.dumps(data))
        dataFile.close()

    def runOnce(self, inputsFn, sendGenome, sendOutput):
        pprint.pprint([(sp.id, len(sp.genomes)) for sp in self.species])
        print("Running generation %d" % (self.generation))
        os.mkdir(os.path.join(self.rtdir, "gen-%d" % self.generation))
        for species in self.species:
            for n, genome in enumerate(species.genomes):
                sys.stdout.write("Gen %d S %d G %s" % (self.generation, species.id, genome.idStr()))
                sys.stdout.flush()
                network = Network(genome)
                fitness = 0
                sendGenome(self, species, genome, n)
                nInputs = 0
                for input in inputsFn():
                    nInputs += 1
                    output = network.runWith(input)
                    sendOutput(output)
                    try:
                        fitness = self.fitnessFn(input, output)
                    except:
                        traceback.print_exc()
                        pprint.pprint(genome.nodes)
                        pprint.pprint(genome.connections)
                        sys.exit(1)
                genome.fitness = fitness
                sys.stdout.write(" fitness: %d\n" % fitness)
                
                self.saveGenome(species, n, genome)

                self.evaluatedGenomes += 1

        self.maxPrevFitness = self.maxFitness
        self.maxPrevGenome = self.maxGenome
        self.maxGenome = max(((genome,species) for species in self.species for genome in species.genomes), key=lambda g: g[0].fitness)
        self.maxFitness = self.maxGenome[0].fitness
        self.maxSpecies = self.maxGenome[1]
        self.maxGenome = self.maxGenome[0]
