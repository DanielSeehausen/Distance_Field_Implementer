"""
Student portion of Zombie Apocalypse mini-project
"""

import random
import poc_grid
import poc_queue
import poc_zombie_gui

# global constants
EMPTY = 0 
FULL = 1
FOUR_WAY = 0
EIGHT_WAY = 1
OBSTACLE = 5
HUMAN = 6
ZOMBIE = 7


class Apocalypse(poc_grid.Grid):
    """
    Class for simulating zombie pursuit of human on grid with
    obstacles
    """

    def __init__(self, grid_height, grid_width, obstacle_list = None, 
                 zombie_list = None, human_list = None):
        """
        Create a simulation of given size with given obstacles,
        humans, and zombies
        """
        poc_grid.Grid.__init__(self, grid_height, grid_width)
        if obstacle_list != None:
            for cell in obstacle_list:
                self.set_full(cell[0], cell[1])
        if zombie_list != None:
            self._zombie_list = list(zombie_list)
        else:
            self._zombie_list = []
        if human_list != None:
            self._human_list = list(human_list)  
        else:
            self._human_list = []
        
    def clear(self):
        """
        Set cells in obstacle grid to be empty
        Reset zombie and human lists to be empty
        """
        self._zombie_list = []
        self._human_list = []
        poc_grid.Grid.clear(self) 
        
    def add_zombie(self, row, col):
        """
        Add zombie to the zombie list
        """
        self._zombie_list.append((row, col))
                
    def num_zombies(self):
        """
        Return number of zombies
        """
        return len(self._zombie_list)    
          
    def zombies(self):
        """
        Generator that yields the zombies in the order they were
        added.
        """
        curr_zombie = 0
        while curr_zombie < len(self._zombie_list):
            yield tuple(self._zombie_list[curr_zombie])
            curr_zombie += 1

    def add_human(self, row, col):
        """
        Add human to the human list
        """
        self._human_list.append((row, col))
        
    def num_humans(self):
        """
        Return number of humans
        """
        return len(self._human_list)
    
    def humans(self):
        """
        Generator that yields the humans in the order they were added.
        """
        curr_human = 0
        while curr_human < len(self._human_list):
            yield tuple(self._human_list[curr_human])
            curr_human += 1
        
    def compute_distance_field(self, entity_type):
        """
        Function computes and returns a 2D distance field
        Distance at member of entity_list is zero
        Shortest paths avoid obstacles and use four-way distances
        """
        clone_height = poc_grid.Grid.get_grid_height(self)
        clone_width = poc_grid.Grid.get_grid_width(self)
        visited = poc_grid.Grid(clone_height, clone_width)
        
        distance_field = []
        for dummy_x in range(clone_height):
            temp_row = []
            for dummy_y in range(clone_width):
                temp_row.append(clone_height * clone_width)
            distance_field.append(temp_row)
        
        boundary = poc_queue.Queue()
        
        if entity_type == ZOMBIE:
            for zom in self.zombies():
                boundary.enqueue(zom)
                visited.set_full(zom[0], zom[1])
                distance_field[zom[0]][zom[1]] = 0  
        elif entity_type == HUMAN:
            for hum in self.humans():
                boundary.enqueue(hum)
                visited.set_full(hum[0], hum[1])
                distance_field[hum[0]][hum[1]] = 0    
                
        #print "Creating distance field from:\n",visited
        while(len(boundary) > 0):
            curr_cell = boundary.dequeue()
            neighbors = visited.four_neighbors(curr_cell[0], curr_cell[1])
            for neighbor in neighbors:
                if visited.is_empty(neighbor[0], neighbor[1]) and self.is_empty(neighbor[0], neighbor[1]):
                    visited.set_full(neighbor[0], neighbor[1])
                    boundary.enqueue((neighbor[0], neighbor[1]))
                    distance_field[neighbor[0]][neighbor[1]] = distance_field[curr_cell[0]][curr_cell[1]] + 1
        #print "Finished Field:"            
        #for elem in distance_field:
        #    print elem
        #print
        return distance_field
    
    def move_value(self, entity, jaunt, best_found, field, obst):
        '''
        returns the spot value, which is the move value
        '''
        y_cord = entity[0] + jaunt[0]
        x_cord = entity[1] + jaunt[1]
        spot_value = field[y_cord][x_cord]
        if spot_value == obst:
            return -1
        return spot_value
    
    def within_bounds(self, entity, direction):
        '''
        checks whether we are attempting to check off of the grid
        '''
        if entity[0] + direction[0] < 0:
            return False
        if entity[0] + direction[0] > poc_grid.Grid.get_grid_height(self) - 1:
            return False
        if entity[1] + direction[1] < 0:
            return False
        if entity[1] + direction[1] > poc_grid.Grid.get_grid_width(self) - 1:
            return False
        
        return True
        
    def move_humans(self, zombie_distance_field):
        """
        Function that moves humans away from zombies, diagonal moves
        are allowed
        """
        new_human_list = []
        directions = [(-1, 0),(-1, 1),(0, 1),(1, 1),(1, 0),(1, -1),(0 ,-1),(-1, -1)]
        
        for human in self.humans():
            best_found = zombie_distance_field[human[0]][human[1]]
            best_moves = []
            obst = poc_grid.Grid.get_grid_height(self) * poc_grid.Grid.get_grid_width(self)
            
            if best_found == obst:
                new_human_list.append(([human[0], human[1]]))
                continue
            for direction in directions:
                if self.within_bounds(human, direction):
                    gain = self.move_value(human, direction, best_found, zombie_distance_field, obst)
                    if gain == -1:
                        continue
                    if gain > best_found:
                        best_found = gain
                        best_moves = [direction]
                    elif gain == best_found:
                        best_moves.append(direction)
                        
            if not best_moves:
                new_human_list.append(([human[0], human[1]]))
            else:
                decision = random.choice(best_moves) 
                new_human_list.append(([human[0] + decision[0], human[1] + decision[1]]))
            #print new_human_list
        
        self._human_list = new_human_list

    def move_zombies(self, human_distance_field):
        """
        Function that moves zombies towards humans, no diagonal moves
        are allowed
        """
        new_zombie_list = []
        directions = [(-1, 0),(0, 1),(1, 0),(0 ,-1)]
        
        for zombie in self.zombies():
            best_found = human_distance_field[zombie[0]][zombie[1]]
            best_moves = []
            obst = poc_grid.Grid.get_grid_height(self) * poc_grid.Grid.get_grid_width(self)
            
            if best_found == obst:
                new_zombie_list.append(([zombie[0], zombie[1]]))
                continue
            for direction in directions:
                if self.within_bounds(zombie, direction):
                    loss = self.move_value(zombie, direction, best_found, human_distance_field, obst)
                    if loss == -1:
                        continue
                    if loss < best_found:
                        best_found = loss
                        best_moves = [direction]
                    elif loss == best_found:
                        best_moves.append(direction)
                        
            if not best_moves:
                new_zombie_list.append(([zombie[0], zombie[1]]))
            else:
                decision = random.choice(best_moves) 
                new_zombie_list.append(([zombie[0] + decision[0], zombie[1] + decision[1]]))
            #print new_zombie_list
        
        self._zombie_list = new_zombie_list                        

