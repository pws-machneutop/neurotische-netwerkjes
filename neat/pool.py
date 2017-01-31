#
# NetworkPool
#

import pprint
import random
import sys
import pdb
import traceback
from .species import Species
from .network import Network
from . import configuration

class NetworkPool():
    def __init__(self, initialGenome, fitnessFunction):
        self.fitnessFn = fitnessFunction
        self.config = configuration.getGlobalConfig()
        self.species = []
        for i in range(self.config["pool"]["population"]):
            initialGenome.mutate()
            newGenome = initialGenome.copy()
            self.addToSpecies(newGenome)

        self.maxFitness = 0.0
        self.maxPrevFitness = 0.0
        self.maxGenome = None
        self.evaluatedGenomes = 0
        self.generation = 0

    def addToSpecies(self, genome):
        for species in self.species:
            if species.genomes[0].sameSpecies(genome):
                species.genomes.append(genome)
                return

        newSpecies = Species()
        newSpecies.genomes.append(genome)
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
        self.rankGlobally()
        self.removeStaleSpecies()
        self.rankGlobally()
        for species in self.species: species.calculateAverageFitness()
        #self.removeWeakSpecies()

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

        self.logData(self)
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

        self.species = survived

    def runOnce(self, inputsFn, sendGenome, sendOutput):
        for species in self.species:
            for n, genome in enumerate(species.genomes):
                network = Network(genome)
                fitness = 0
                sendGenome(self, species, genome, n)
                for input in inputsFn():
                    print(input)
                    output = network.runWith(input)
                    sendOutput(output)
                    try:
                        fitness += self.fitnessFn(input, output)
                    except:
                        traceback.print_exc()
                        pprint.pprint(genome.nodes)
                        pprint.pprint(genome.connections)
                        sys.exit(1)
                genome.fitness = fitness

                self.evaluatedGenomes += 1

        self.maxPrevFitness = self.maxFitness
        self.maxPrevGenome = self.maxGenome
        self.maxGenome = max(((genome,species) for species in self.species for genome in species.genomes), key=lambda g: g[0].fitness)
        self.maxFitness = self.maxGenome[0].fitness
        self.maxSpecies = self.maxGenome[1]
        self.maxGenome = self.maxGenome[0]
