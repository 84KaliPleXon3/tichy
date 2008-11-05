
from box import Box
from geo import Vect

class Table(Box):
    def __init__(self, parent, axis = 0, nb = 3, **kargs):
        # Here we may need to set the optimal size or the size ?? (I am not sure)
        self.nb = nb
        super(Table, self).__init__(parent, axis, **kargs)
        
    def cell_optimal_size(self):
        return Vect(max(w.optimal_size[0] for w in self.children), max(w.optimal_size[1] for w in self.children))
        
    def cell_min_size(self):
        return Vect(max(w.min_size[0] for w in self.children), max(w.min_size[1] for w in self.children))
    
    def resize(self):
        if not self.children:
            return
        axis = self.axis
        cell_optimal_size = self.cell_optimal_size()
        cell_min_size = self.cell_min_size()
        
        nb_per_line =  self.nb
        
        # Quite ugly algorithm to compute the number of lines
        # I do like this cause I want to avoid importing math
        nb_lines = len(self.children) / nb_per_line
        if len(self.children) % nb_per_line != 0:
            nb_lines += 1
        
        # self.optimal_size = Vect(nb_per_line * cell_optimal_size[0], nb_lines * cell_optimal_size[1])
        self.min_size = Vect(
            nb_per_line * (cell_min_size[0] + self.spacing) - self.spacing,
            nb_lines * (cell_min_size[1] + self.spacing) - self.spacing
        )
        
        self.optimal_size = self.min_size
        
    def organize(self):
        if not self.children:
            return
        axis = self.axis
        cell_size = self.cell_min_size()
        for i, c in enumerate(self.children):
            c.pos = Vect(0,0).set(
                axis, i / self.nb * (cell_size[axis] + self.spacing)
            ).set(
                axis - 1, i % self.nb * (cell_size[axis - 1] + self.spacing)
            )
            c.size = cell_size
