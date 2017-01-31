from neat.pool import NetworkPool
from neat.network import Network
from neat.genome import NodeGene, ConnectionGene, Genome
from neat import configuration


if __name__ == '__main__':
    config = configuration.loadConfig("NEAT.toml")

    # xor initial network

    genome = Genome([NodeGene(NodeType.SENSOR), NodeGene(NodeType.SENSOR),
                     NodeGene(NodeType.BIAS), NodeGene(NodeType.OUTPUT)])

    genome.addConnection(genome.node(1), genome.node(4))
    genome.addConnection(genome.node(2), genome.node(4))
    genome.addConnection(genome.node(3), genome.node(4))

    pool = NetworkPool(genome)

    pool.run([(1, 0), (0, 1), (1, 1), (0, 0)], lambda ip, op: 1-abs(op[0] - (ip[0]^ip[1])))
