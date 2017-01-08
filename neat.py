from neat.pool import NetworkPool
from neat.network import Network
from neat.genome import NodeGene, ConnectionGene, Genome

import toml

config = toml.load("NEAT.toml")

if __name__ == '__main__':
    print(config)
