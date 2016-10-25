class NodePool:
    """
    A pool manager for nodes to distribute available resources.
    """
    # mapping id to nodes which are free for processing
    free_nodes = {}

    # mapping id to nodes which are currently being used
    occupied_nodes = {}

    _pool = None

    def __init__(self):
        pass

    @classmethod
    def get_pool(cls):
        if (cls._pool == None):
            cls._pool = NodePool()
        return cls._pool

    def add_new_node(self, node):
        print 'Adding Node %s to pool' % node.id
        self.free_nodes[str(node.id)] = node

    def remove_node(self, node_id):
        """
        Remove a node from the pool since it can no longer be used.
        """
        print "Removing node %s from pool" % node_id

        node = self.free_nodes.pop(node_id) or self.occupied_nodes.pop(node_id)

        if node:
            node.finish()

    def get_free_node_count(self):
        return len(self.free_nodes)

    def get_occupied_node_count(self):
        return len(self.occupied_nodes)

    def free_node(self, node_id):
        """
        Free a currently occupied node.
        """
        if node_id not in self.occupied_nodes:
            return None

        print 'Freeing node %s' % node_id
        node = self.occupied_nodes.pop(node_id)
        if node:
            self.free_nodes.update({str(node.id):node})
            node.finish()

        return node

    def consume_free_node(self):
        """
        Get a node that is free and mark it as occupied

        Return:
            node: the node that can be used for processing
        """
        node = self.free_nodes.popitem()

        self.occupied_nodes.update({str(node[0]): node[1]})
        return node[1]

    def consume_free_nodes(self, number_of_nodes):
        """
        Args:
            number_of_nodes: number of nodes that a client requests to process the request.

        Return:
            The nodes which are free to be used for processing now
        """
        nodes = []
        for x in xrange(number_of_nodes):
            nodes.append(self.consume_free_node())
        return nodes
