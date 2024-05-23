"""
This class represents a graph using an adjacency matrix.

Attributes:
    adjMatrix (list): 2D list representing the adjacency matrix.
    size (int): Size of the matrix.

Methods:
    __init__: Constructor method to initialize the graph with a given size.
    add_edge: Method to add an edge between two vertices.
    remove_edge: Method to remove an edge between two vertices.
    __len__: Method to return the size of the graph.
    print_matrix: Method to print the adjacency matrix.
    __getitem__: Method to get the value at a specific index of the matrix.
    __repr__: Method to return a string representation of the matrix.
"""

class Graph(object):

    def __init__(self, size):
        """
        Constructor method to initialize the graph with a given size.

        Args:
            size (int): The size of the adjacency matrix.
        """
        self.adjMatrix = []
        for i in range(size):
            self.adjMatrix.append([0 for i in range(size)])
        self.size = size

    def add_edge(self, v1, v2):
        """
        Method to add an edge between two vertices.

        Args:
            v1 (int): Vertex 1.
            v2 (int): Vertex 2.

        Raises:
            ValueError: If v1 and v2 are the same.
        """
        if v1 == v2:
            raise ValueError("Same vertex %d and %d" % (v1, v2))
        self.adjMatrix[v1][v2] = 1
        self.adjMatrix[v2][v1] = 1

    def remove_edge(self, v1, v2):
        """
        Method to remove an edge between two vertices.

        Args:
            v1 (int): Vertex 1.
            v2 (int): Vertex 2.

        Raises:
            ValueError: If there is no edge between v1 and v2.
        """
        if self.adjMatrix[v1][v2] == 0:
            raise ValueError("No edge between %d and %d" % (v1, v2))
        self.adjMatrix[v1][v2] = 0
        self.adjMatrix[v2][v1] = 0

    def __len__(self):
        """
        Method to return the size of the graph.

        Returns:
            int: The size of the graph.
        """
        return self.size

    def print_matrix(self):
        """
        Method to print the adjacency matrix.
        """
        print(self.__repr__())
    
    def __getitem__(self, *args):
        """
        Method to get the value at a specific index of the matrix.

        Args:
            args (tuple): Tuple containing the index.

        Returns:
            int: The value at the specified index.
        """
        width, height = args[0][0], args[0][1]
        return self.adjMatrix[width][height]
    
    def __repr__(self) -> str:
        """
        Method to return a string representation of the matrix.

        Returns:
            str: String representation of the matrix.
        """
        res = '  '
        for cnt in range(self.size):
            res += '{:4}'.format(cnt)
        res += '{:4}'.format('\n') + '  ' + '{:4}'.format('_') * self.size + '\n'
        cnt = 0
        for row in self.adjMatrix:
            res += str(cnt) + '|'
            for val in row:
                res += '{:4}'.format(val)
            res += '\n'
            cnt += 1
        return res
