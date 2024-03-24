# Adjacency Matrix representation in Python


class Graph(object):

    # Initialize the matrix
    def __init__(self, size):
        self.adjMatrix = []
        for i in range(size):
            self.adjMatrix.append([0 for i in range(size)])
        self.size = size

    # Add edges
    def add_edge(self, v1, v2):
        if v1 == v2:
            raise ValueError("Same vertex %d and %d" % (v1, v2))
        self.adjMatrix[v1][v2] = 1
        self.adjMatrix[v2][v1] = 1

    # Remove edges
    def remove_edge(self, v1, v2):
        if self.adjMatrix[v1][v2] == 0:
            raise ValueError("No edge between %d and %d" % (v1, v2))
        self.adjMatrix[v1][v2] = 0
        self.adjMatrix[v2][v1] = 0

    def __len__(self):
        return self.size

    # Print the matrix
    def print_matrix(self):
            print(self.__repr__())
    
    def __getitem__(self, *args):
        width, height = args[0][0],args[0][1]
        return self.adjMatrix[width][height]
    
    def __repr__(self) -> str:
        res = '  '
        for cnt in range(self.size): res+= '{:4}'.format(cnt)
        res+='{:4}'.format('\n')+'  '+'{:4}'.format('_')*self.size+'\n'
        cnt = 0
        for row in self.adjMatrix:
            res+= str(cnt) + '|'
            for val in row:
                res+='{:4}'.format(val)
            res+='\n'
            cnt+=1
        return res

