import pygame, sys, math, time, random
from queue import PriorityQueue
from pygame.constants import KEYDOWN
from pygame.locals import QUIT
import sqlite3
from database import create_table, insert_grid, fetch_grid
from inputboxfunc import input_box
clock = pygame.time.Clock()

create_table()



WIDTH = 800
pygame.init()
screen = pygame.display.set_mode((WIDTH, WIDTH)) #frame size of 800 by 800
pygame.display.set_caption('Pathfinding')

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
GREY = (128, 128, 128)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)


class Node:

  def __init__(self, row, col, width, totalrows):
    self.row = row
    self.col = col
    self.x = row * width
    self.y = col * width #finds the position of the node given its coordinates and width
    self.color = WHITE #all nodes start as being white(empty space/ free block)
    self.width = width #width and height of the blocks
    self.neighbors = [] #array for all the neighbors of a node
    self.totalrows = totalrows

  def get_node_info_(self):
    array = [self.row, self.col, self.color]
    return array


  def getpos(self):
    return self.row, self.col

  def isopen(self):
    return self.color == ORANGE #is node open

  def isclosed(self):
    return self.color == BLUE #is node closed

  def ispath(self):
    return self.color == PURPLE #is node open

  def isblock(self):
    return self.color == BLACK #is node a block

  def isstart(self):
    return self.color == GREEN #is node the start node

  def isend(self):
    return self.color == RED #is node the end node

  def ispath2(self):
    return self.color == MAGENTA #is node the end node

  def isplain(self):
    return self.color == WHITE # is node a plain node

  def makeopen(self):
    self.color = ORANGE #turn to opened

  def makeclose(self):
    self.color = BLUE #turn to closed

  def makeblock(self):
    self.color = BLACK #become a block

  def makestart(self):
    self.color = GREEN #chosen as start node

  def makeend(self):
    self.color = RED #chosen as end node

  def makepath2(self):
    self.color = MAGENTA #chosen as end node

  def makeplain(self):
    self.color = WHITE #switch back to plain node

  def makepath(self):
    self.color = PURPLE #for final path as optimal solution

  def draw(self, screen): #method we call when we want to draw node on the screen
    pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.width))
    #only parameter needed to draw the node when we call it later will be screen
    #the rest of the parameters here are stored as atributes


  def update_neighbors(self, grid): #so we know all of the available neighbors to a node
    self.neighbors = [] #create array for neighbors to go into, stored as an attribute

    if self.row < self.totalrows -1 and not grid[self.row+1][self.col].isblock(): #down
      self.neighbors.append(grid[self.row+1][self.col]) #is node below available
      #we need the -1 as we start from 0 in rows so the last row is totalrows -1

    if self.row > 0 and not grid[self.row-1][self.col].isblock(): #up
      self.neighbors.append(grid[self.row-1][self.col]) #is node above available

    if self.col < self.totalrows -1 and not grid[self.row][self.col+1].isblock(): #right
      self.neighbors.append(grid[self.row][self.col+1]) #is node right available

    if self.col > 0 and not grid[self.row][self.col-1].isblock(): #left
      self.neighbors.append(grid[self.row][self.col-1]) #is node left available

    if self.col > 0 and self.row > 0 and not grid[self.row-1][self.col-1].isblock():
      #leftup
      self.neighbors.append(grid[self.row-1][self.col-1]) #is node leftup available

    if self.col > 0 and self.row < self.totalrows -1 and \
    not grid[self.row+1][self.col-1].isblock(): #leftdown
      self.neighbors.append(grid[self.row+1][self.col-1]) #is node leftdown available


    if self.row > 0 and self.col < self.totalrows -1 and \
    not grid[self.row-1][self.col+1].isblock(): #rightup
      self.neighbors.append(grid[self.row-1][self.col+1]) #is node righup available

    if self.row < self.totalrows -1 and self.col < self.totalrows -1 and\
    not grid[self.row+1][self.col+1].isblock(): #rightdown
      self.neighbors.append(grid[self.row+1][self.col+1]) #is node rightdown available

def endscreen(screen, winnner_text):
  screen.fill(GREEN)
  font = pygame.font.Font(None, 74)
  text = font.render(winnner_text, True, (255, 255, 255))  # White color for text
  text_rect = text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
  screen.blit(text, text_rect)
  pygame.display.flip()
  pygame.time.delay(1000)



def savemap(grid, screen):
  grid_name = input_box(screen, "choose map name:")
  if grid_name:
    insert_grid(grid_name, grid)

def getmap(screen, rows, width):
  grid = []
  grid_name = input_box(screen, "name the map:")
  if grid_name:
    got_grid = fetch_grid(grid_name)
    if got_grid:
      grid = turn_data_to_map(draw, got_grid, rows, width)
    else:
      print("no grid with that name")

  return grid

def turn_data_to_map(draw, got_grid, rows, width):
  spacing = width // rows
  grid = makegrid(rows, width)
  count = 0
  grid = []
  for i in range(rows):
    grid.append([])  # creates a 2d array/ adds a new array for each row
    for j in range(rows):
      row = got_grid[count][0]
      col = got_grid[count][1]
      color = got_grid[count][2]
      count += 1
      node = Node(row, col, spacing, rows)  # pass all the parameters of node class in
      grid[i].append(node)
      if color == [255, 255, 255]:
        node.makeplain()
      elif color == [0, 0, 0]:
        node.makeblock()
      elif color == [0, 255, 0]:
        node.makestart()
        start = node
      elif color == [255, 0, 0]:
        node.makeend()
        end = node

  return grid, start, end





def reset(grid, start, end):
  for row in grid:  # for every node when we start a new map we must
    for node in row:  # update all of the neighbors for this new setup of nodes
      node.update_neighbors(grid)
      if node.isopen() or node.ispath() or node.isclosed() or node.ispath2():
        node.makeplain()
  start.makestart()
  end.makeend()


def heuristic(p1, p2): # finds shortest distance between 2 points
  x1, y1 = p1 # point 1
  x2, y2 = p2 # point 2 (end node)
  xchange = abs(x2 - x1) #(change in x cordinate)
  ychange = abs(y2 - y1) #(change in y cordinate)
  return ((xchange**2)+(ychange**2))**0.5 #pythagoras theorem a^2+b^2 = c^2

def reconstruct_path(came_from, current, draw):
  while current in came_from: #loop through all nodes stored as current in came_from
    current = came_from[current]
    current.makepath()
    draw()

def greedy1(draw, grid, start, end):
  count = 0
  open_set = PriorityQueue()
  open_set.put((0, count, start))   #put just adds(term for append), the 0 is our f_cost
  #add the start node to the open set, count keeps track of when node was inserted
  came_from = {} #where each node came from so we can retrace path at the end
  g_score = {node: float("inf") for row in grid for node in row} #all nodes start at
  #infinty distance away from start node as there's no path to get there yet
  g_score[start] = 0 #g_score is distance from start, so 0 for start
  f_score = {node: float("inf") for row in grid for node in row}
  f_score[start] = heuristic(start.getpos(), end.getpos()) #estimate start- end distance

  open_set_tracker = {start} #set to keep track of presents of nodes in priority queue
# so we can determine if a node needs to be evaluated or not
  while not open_set.empty(): #if open set is empty we've considered every node
    #that is 'promising', if no path is yet found then there is no path to end
    for event in pygame.event.get():
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_r:
          reset(grid, start, end)
          return True #allows exit before end is found

    current = open_set.get()[2] #get the node from the priority queue
    #the priority queue will mean we get the node with the lowest f-cost(the most
#promising node),if the f-cost is the same then go by count(order of entry into queue)
    open_set_tracker.remove(current) #we are now looking at current so its no longer
# a part of the open set
    if current == end:
      reconstruct_path(came_from, end, draw) #call function to draw the shortest path
      end.makeend() #so we can see the end node
      start.makestart()
      return True

    for neighbor in current.neighbors: #look at every neighbor of current
      temp_g_score = g_score[current] + heuristic(current.getpos(),neighbor.getpos())

      if temp_g_score < g_score[neighbor]: #if we have found a shorter path to neighbor
        came_from[neighbor] = current #update so that current node is stored as path to
        #get to neighbor
        g_score[neighbor] = temp_g_score #new distance away from start node
        f_score[neighbor] =  heuristic(neighbor.getpos(),end.getpos())
        if neighbor not in open_set_tracker: #if not in open_set queue we need to add it
          count = count + 1
          open_set.put((f_score[neighbor], count, neighbor))
          open_set_tracker.add(neighbor) #we also need to add it to our tracker set
          neighbor.makeopen() #add open to the attribute of this neighbor as we have put
          #it in open set so it will turn orange
    draw()

    if current != start:
      current.makeclose() #we have finished looking at all the neighbors of this node
      # so we add closed as an attribute and turn it to blue

  return False

def astar(draw, grid, start, end):
  count = 0
  open_set = PriorityQueue()
  open_set.put((0, count, start))   #put just adds(term for append), the 0 is our f_cost
  #add the start node to the open set, count keeps track of when node was inserted
  came_from = {} #where each node came from so we can retrace path at the end
  g_score = {node: float("inf") for row in grid for node in row} #all nodes start at
  #infinty distance away from start node as there's no path to get there yet
  g_score[start] = 0 #g_score is distance from start, so 0 for start
  f_score = {node: float("inf") for row in grid for node in row}
  f_score[start] = heuristic(start.getpos(), end.getpos()) #estimate start- end distance

  open_set_tracker = {start} #set to keep track of presents of nodes in priority queue
# so we can determine if a node needs to be evaluated or not
  while not open_set.empty(): #if open set is empty we've considered every node
    #that is 'promising', if no path is yet found then there is no path to end
    for event in pygame.event.get():
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_r:
          reset(grid, start, end)
          return True #allows exit before end is found

    current = open_set.get()[2] #get the node from the priority queue
    #the priority queue will mean we get the node with the lowest f-cost(the most
#promising node),if the f-cost is the same then go by count(order of entry into queue)
    open_set_tracker.remove(current) #we are now looking at current so its no longer
# a part of the open set
    if current == end:
      reconstruct_path(came_from, end, draw) #call function to draw the shortest path
      end.makeend() #so we can see the end node
      start.makestart()
      return True

    for neighbor in current.neighbors: #look at every neighbor of current
      temp_g_score = g_score[current] + heuristic(current.getpos(),neighbor.getpos())

      if temp_g_score < g_score[neighbor]: #if we have found a shorter path to neighbor
        came_from[neighbor] = current #update so that current node is stored as path to
        #get to neighbor
        g_score[neighbor] = temp_g_score #new distance away from start node
        f_score[neighbor] = temp_g_score + heuristic(neighbor.getpos(),end.getpos())
        if neighbor not in open_set_tracker: #if not in open_set queue we need to add it
          count = count + 1
          open_set.put((f_score[neighbor], count, neighbor))
          open_set_tracker.add(neighbor) #we also need to add it to our tracker set
          neighbor.makeopen() #add open to the attribute of this neighbor as we have put
          #it in open set so it will turn orange
    draw()

    if current != start:
      current.makeclose() #we have finished looking at all the neighbors of this node
      # so we add closed as an attribute and turn it to blue

  return False


def hillrfs(draw, grid, start, end):
  count = 0
  open_set = PriorityQueue()
  open_set.put((0, count, start))  # put just adds(term for append), the 0 is our f_cost
  # add the start node to the open set, count keeps track of when node was inserted
  came_from = {}  # where each node came from so we can retrace path at the end
  closed_set = set()
  closed_set.add(start)
  f_score = {node: float("inf") for row in grid for node in row}
  f_score[start] = heuristic(start.getpos(), end.getpos())  # estimate start-end distance

  open_set_tracker = {start}  # set to keep track of presents of nodes in priority queue
  # so we can determine if a node needs to be evaluated or not
  while not open_set.empty():  # if open set is empty we've considered every node
    # that is 'promising', if no path is yet found then there is no path to end
    for event in pygame.event.get():  # allows us to exit before finish
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_r:
          reset(grid, start, end)
          return True

    current = open_set.get()[2]  # get the node from the priority queue
    # the priority queue will mean we get the node with the lowest f-cost(the most
    # promising node),if the f-cost is the same then go by count(order of entry into queue)
    open_set_tracker.remove(current)  # we are now looking at current so its no longer
    # a part of the open set

    if current == end:
      current.makeclose()
      reconstruct_path(came_from, end, draw)  # call function to draw shortest path
      end.makeend()  # so we can see the end node
      start.makestart()
      return True

    for neighbor in current.neighbors:  # look at every neighbor of current
      if neighbor not in closed_set:
        f_score[neighbor] = heuristic(neighbor.getpos(), end.getpos())
        if neighbor not in open_set_tracker:  # if not in open_set queue we need to add it
          count = count + 1
          open_set.put((1/(f_score[neighbor]+1), count, neighbor))
          came_from[neighbor] = current
          open_set_tracker.add(neighbor)  # we also need to add it to our tracker set
          neighbor.makeopen()  # add open to the attribute of this neighbor as we have put
        # it in open set so it will turn orange
    draw()

    if current != start:
      closed_set.add(current)
      current.makeclose()  # we have finished looking at all the neighbors of this node
      # so we add closed as an attribute and turn it to blue

  return False

def elcleggfs(draw, grid, start, end):
  count = 0
  open_set = PriorityQueue()
  open_set.put((0, count, start))   #put just adds(term for append), the 0 is our f_cost
  #add the start node to the open set, count keeps track of when node was inserted
  came_from = {} #where each node came from so we can retrace path at the end
  g_score = {node: float("inf") for row in grid for node in row} #all nodes start at
  #infinty distance away from start node as there's no path to get there yet
  g_score[start] = 0 #g_score is distance from start, so 0 for start
  closed_set = set()
  closed_set.add(start)
  f_score = {node: float("inf") for row in grid for node in row}
  f_score[start] = heuristic(start.getpos(), end.getpos()) #estimate start- end distance

  open_set_tracker = {start} #set to keep track of presents of nodes in priority queue
# so we can determine if a node needs to be evaluated or not
  while not open_set.empty(): #if open set is empty we've considered every node
    #that is 'promising', if no path is yet found then there is no path to end
    for event in pygame.event.get():
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_r:
          reset(grid, start, end)
          return True #allows exit before end is found

    current = open_set.get()[2] #get the node from the priority queue
    #the priority queue will mean we get the node with the lowest f-cost(the most
#promising node),if the f-cost is the same then go by count(order of entry into queue)
    open_set_tracker.remove(current) #we are now looking at current so its no longer
# a part of the open set
    if current == end:
      reconstruct_path(came_from, end, draw) #call function to draw the shortest path
      end.makeend() #so we can see the end node
      start.makestart()
      return True

    for neighbor in current.neighbors: #look at every neighbor of current
      if neighbor not in closed_set:
        temp_g_score = g_score[current] + heuristic(current.getpos(),neighbor.getpos())
        if temp_g_score < g_score[neighbor]: #if we have found a shorter path to neighbor
          came_from[neighbor] = current #update so that current node is stored as path to
        #get to neighbor
          g_score[neighbor] = temp_g_score #new distance away from start node
          f_score[neighbor] = temp_g_score + heuristic(neighbor.getpos(),end.getpos())
          if neighbor not in open_set_tracker: #if not in open_set queue we need to add it
            count = count + 1
            open_set.put((1/f_score[neighbor], count, neighbor))
            open_set_tracker.add(neighbor) #we also need to add it to our tracker set
            neighbor.makeopen() #add open to the attribute of this neighbor as we have put
          #it in open set so it will turn orange
    draw()

    if current != start:
      closed_set.add(current)
      current.makeclose() #we have finished looking at all the neighbors of this node
      # so we add closed as an attribute and turn it to blue

  return False



def greedy(draw, grid, start, end):
  count = 0
  open_set = PriorityQueue()
  open_set.put((0, count, start))  # put just adds(term for append), the 0 is our f_cost
  # add the start node to the open set, count keeps track of when node was inserted
  came_from = {}  # where each node came from so we can retrace path at the end
  closed_set = set()
  closed_set.add(start)
  f_score = {node: float("inf") for row in grid for node in row}
  f_score[start] = heuristic(start.getpos(), end.getpos())  # estimate start-end distance

  open_set_tracker = {start}  # set to keep track of presents of nodes in priority queue
  # so we can determine if a node needs to be evaluated or not
  while not open_set.empty():  # if open set is empty we've considered every node
    # that is 'promising', if no path is yet found then there is no path to end
    for event in pygame.event.get(): #allows us to exit before finish
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_r:
          reset(grid, start, end)
          return True

    current = open_set.get()[2]  # get the node from the priority queue
    # the priority queue will mean we get the node with the lowest f-cost(the most
    # promising node),if the f-cost is the same then go by count(order of entry into queue)
    open_set_tracker.remove(current)  # we are now looking at current so its no longer
    # a part of the open set
    if current == end:
      reconstruct_path(came_from, end, draw)  # call function to draw shortest path
      end.makeend()  # so we can see the end node
      start.makestart()
      return True

    for neighbor in current.neighbors: # look at every neighbor of current
      if neighbor not in closed_set:
          f_score[neighbor] = heuristic(neighbor.getpos(), end.getpos())
          if neighbor not in open_set_tracker:  # if not in open_set queue we need to add it
            count = count + 1
            open_set.put((f_score[neighbor], count, neighbor))
            came_from[neighbor] = current
            print(f"Added {neighbor.getpos()} to came_from with parent {current.getpos()}")
            open_set_tracker.add(neighbor)  # we also need to add it to our tracker set
            neighbor.makeopen()  # add open to the attribute of this neighbor as we have put
          # it in open set so it will turn orange
    draw()

    if current != start:
      closed_set.add(current)
      current.makeclose()  # we have finished looking at all the neighbors of this node
      # so we add closed as an attribute and turn it to blue

  return False


def dijkstra(draw, grid, start, end):
  count = 0
  open_set = PriorityQueue()
  open_set.put((0, count, start))   #the 0 is our g-score(how far from start)
  #add the start node to the open set, count keeps track of when node was inserted
  came_from = {} #where each node came from so we can retrace path at the end
  g_score = {node: float("inf") for row in grid for node in row} #all nodes start at 
    #infinty distance away from start node as there's no path to get there yet
  g_score[start] = 0 #g_score is distance from start, so 0 for start

  open_set_tracker = {start} #set to keep track of presents of nodes in priority queue
  # so we can determine if a node needs to be evaluated or not
  while not open_set.empty(): #if open set is empty we've considered every node
      #that is 'promising', if no path is yet found then there is no path to end
    for event in pygame.event.get():
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_r:
          reset(grid, start, end)
          return True

    current = open_set.get()[2] #get the node from the priority queue
      #the priority queue will mean we get the node with the lowest f-cost(the most 
  #promising node),if the f-cost is the same then go by count(order of entery into queue)
    open_set_tracker.remove(current) #we are now looking at current so its no longer
  # a part of the open set
    if current == end:
      reconstruct_path(came_from, end, draw) #call function to draw shortest path
      end.makeend() #so we can see the end and start nodes
      start.makestart()
      return True

    for neighbor in current.neighbors: #look at every neighbor of current
      temp_g_score = g_score[current] + heuristic(current.getpos(),neighbor.getpos())

      if temp_g_score < g_score[neighbor]: #if we have found a shorter path to neighbor
        came_from[neighbor] = current #update so that current node is stored as path to
          #get to neighbor
        g_score[neighbor] = temp_g_score #new distance away from start node
        if neighbor not in open_set_tracker: #if not in open_set queue we need to add it
          count = count + 1
          open_set.put((g_score[neighbor], count, neighbor))
          open_set_tracker.add(neighbor) #we also need to add it to our tracker set
          neighbor.makeopen() #add open to the attribute of this neighbor as we have put
            #it in open set so it will turn orange
    draw()

    if current != start:
      current.makeclose() #we have finished looking at all the neighbors of this node
        # so we add closed as an attribute and turn it to blue

  return False

def play(draw, grid, start, end):
  came_from = {} #where each node came from so we can retrace path at the end
  found = False #while the end node is not reached
  current = start
  while not found: #if open set is empty we've considered every node
      #that is 'promising', if no path is yet found then there is no path to end
    for event in pygame.event.get():
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_r:
          reset(grid, start, end)
          return True
    
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_d:
          for neighbor in current.neighbors: 
            if current.row + 1 == neighbor.row and current.col == neighbor.col: 
              came_from[neighbor] = current
              neighbor.makeclose()
              current.makeopen()
              current = neighbor

        elif event.key == pygame.K_a:
          for neighbor in current.neighbors: 
            if current.row - 1 == neighbor.row and current.col == neighbor.col: 
              came_from[neighbor] = current
              neighbor.makeclose()
              current.makeopen()
              current = neighbor

        elif event.key == pygame.K_s:
          for neighbor in current.neighbors: 
            if current.col + 1 == neighbor.col and current.row == neighbor.row:
              came_from[neighbor] = current
              neighbor.makeclose()
              current.makeopen()
              current = neighbor

        elif event.key == pygame.K_w:
          for neighbor in current.neighbors: 
            if current.col - 1 == neighbor.col and current.row == neighbor.row:
              came_from[neighbor] = current
              neighbor.makeclose()
              current.makeopen()
              current = neighbor

        elif event.key == pygame.K_z:
          for neighbor in current.neighbors: 
            if current.row - 1 == neighbor.row and current.col == neighbor.col -1:
              came_from[neighbor] = current
              neighbor.makeclose()
              current.makeopen()
              current = neighbor

        elif event.key == pygame.K_q:
          for neighbor in current.neighbors: 
            if current.row - 1 == neighbor.row and current.col == neighbor.col +1:
              came_from[neighbor] = current
              neighbor.makeclose()
              current.makeopen()
              current = neighbor

        elif event.key == pygame.K_e:
          for neighbor in current.neighbors: 
            if current.row + 1 == neighbor.row and current.col == neighbor.col +1:
              came_from[neighbor] = current
              neighbor.makeclose()
              current.makeopen()
              current = neighbor

        elif event.key == pygame.K_c:
          for neighbor in current.neighbors: 
            if current.row + 1 == neighbor.row and current.col == neighbor.col -1:
              came_from[neighbor] = current
              neighbor.makeclose()
              current.makeopen()
              current = neighbor

    if current == end:
      for row in grid:  # for every node when we start a new map we must
        for node in row:
          if node.isopen():
            node.makepath()
      #call function to draw shortest path
      end.makeend() #so we can see the end and start nodes
      start.makestart()
      found = True
      return True
      
    draw()

  return False


def versus(draw, grid, start, end):
  came_from = {}  # where each node came from so we can retrace path at the end
  came_from2 = {}
  found = False  # while the end node is not reached
  current = start
  current2 = start
  while not found:  # if open set is empty we've considered every node
    # that is 'promising', if no path is yet found then there is no path to end
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        pygame.quit()  # so we can exit function if it takes too long or error occurs
      # a part of the open set

      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_r:
          reset(grid, start, end)
          return True

    keys = pygame.key.get_pressed()

    if  keys[pygame.K_d]:
      for neighbor in current.neighbors:
        if current.row + 1 == neighbor.row and current.col == neighbor.col:
          came_from[neighbor] = current
          neighbor.makeclose()
          current.makeopen()
          current = neighbor

    if keys[pygame.K_a]:
      for neighbor in current.neighbors:
        if current.row - 1 == neighbor.row and current.col == neighbor.col:
          came_from[neighbor] = current
          neighbor.makeclose()
          current.makeopen()
          current = neighbor

    if keys[pygame.K_s]:
      for neighbor in current.neighbors:
        if current.col + 1 == neighbor.col and current.row == neighbor.row:
          came_from[neighbor] = current
          neighbor.makeclose()
          current.makeopen()
          current = neighbor

    if keys[pygame.K_w]:
      for neighbor in current.neighbors:
        if current.col - 1 == neighbor.col and current.row == neighbor.row:
          came_from[neighbor] = current
          neighbor.makeclose()
          current.makeopen()
          current = neighbor

    if keys[pygame.K_RIGHT]:
      for neighbor in current2.neighbors:
        if current2.row + 1 == neighbor.row and current2.col == neighbor.col:
          came_from2[neighbor] = current2
          neighbor.makeclose()
          current2.makepath2()
          current2 = neighbor


    if keys[pygame.K_LEFT]:
      for neighbor in current2.neighbors:
        if current2.row - 1 == neighbor.row and current2.col == neighbor.col:
          came_from2[neighbor] = current2
          neighbor.makeclose()
          current2.makepath2()
          current2 = neighbor


    if keys[pygame.K_DOWN]:
      for neighbor in current2.neighbors:
        if current2.col + 1 == neighbor.col and current2.row == neighbor.row:
          came_from2[neighbor] = current2
          neighbor.makeclose()
          current2.makepath2()
          current2 = neighbor

    if keys[pygame.K_UP]:
      for neighbor in current2.neighbors:
        if current2.col - 1 == neighbor.col and current2.row == neighbor.row:
          came_from2[neighbor] = current2
          neighbor.makeclose()
          current2.makepath2()
          current2 = neighbor



    if current == end:
      for row in grid:  # for every node when we start a new map we must
        for node in row:
          if node.isopen():
            node.makepath()
      # call function to draw shortest path
      end.makeend()  # so we can see the end and start nodes
      start.makestart()
      endscreen(screen, "player 1 won")

      return True

    elif current2 == end:
      for row in grid:  # for every node when we start a new map we must
        for node in row:
          if node.ispath2():
            node.makepath()
      # call function to draw shortest path
      end.makeend()  # so we can see the end and start nodes
      start.makestart()
      endscreen(screen, "player 2 won")
      return True

    draw()
    clock.tick(10)
  return False

def randmap(draw, grid, ROWS):

  for row in grid:  # for every node when we start a new map we must
    for node in row:  # update all of the neighbors for this new setup of nodes
      if node.isopen() or node.ispath() or node.isclosed() or node.ispath2() or node.isblock:
        node.makeplain()
      if random.randint(1,6) < 3:
        node.makeblock()
  draw()
  return grid
      


def makegrid(rows, width): #store all of the nodes so they can be used
  grid = [] #make the array for other arrays to be added to
  spacing = width // rows #finds the spacing between the nodes/node width
  for i in range(rows):
   grid.append([]) # creates a 2d array/ adds a new array for each row
   for j in range(rows):
     node = Node(i, j, spacing, rows) #pass all the parameters of node class in
     grid[i].append(node) #adds the new node to the correct array for its row
  return grid
  

def drawgrid(screen, rows, width): #for drawing our background grid lines
  spacing = width// rows #finds the spacing between the nodes/node width
  for i in range(rows):
    pygame.draw.line(screen, GREY,(0, i*spacing), (width,i*spacing)) #horizontal lines
    pygame.draw.line(screen, GREY,(i*spacing, 0), (i*spacing,width)) #verticle lines

def draw(screen, grid, rows, width): #function to do all of the drawing with each frame
  screen.fill(WHITE) #paint over everthing on the last frame
  for row in grid: #for every row(array) within grid
    for node in row: #for every node within that row(array)
      node.draw(screen) #draw the node onto the screen

  drawgrid(screen, rows, width)
  pygame.display.update()

def mousepos(rows, width):
  pos = pygame.mouse.get_pos()  # pos = (x, y) mouse position
  y, x = pos  # get value of x and y from the mouse position
  spacing = width // rows
  row = y//spacing # get row from y coordinate
  col = x//spacing # get col from x coordinate
  return row, col


def main(screen, width): #Runs the whole process, eg if quit clicked or node changed
  ROWS = 50 #dynamic can be changed
  grid = makegrid(ROWS,width) #make grid

  start = None
  end = None # keep track of start and end position

  run = True #if main loop is running
  started = False #if algorithm has started or not

  while run:
    draw(screen, grid, ROWS, width)
    for event in pygame.event.get(): #loop through all events that could happen
      
      if event.type == pygame.QUIT: #if cross is hit in corner
        run = False
      if pygame.mouse.get_pressed()[0]: #if left mouse button clicked
        row,col = mousepos(ROWS,width) #gets row and col of what was clicked on
        node = grid[row][col]
        if not start and node != end: #if the start block hasnt yet been placed
          start = node
          start.makestart() #run the makestart function on the start object
        elif not end and node != start:
          end = node
          end.makeend()
        elif node != start and node != end and not node.isblock():
          node.makeblock()
      elif pygame.mouse.get_pressed()[2]: #if right mouse button clicked
        row,col = mousepos(ROWS,width) #gets row and col of what was clicked on
        node = grid[row][col]
        node.makeplain() #turn node back to a blank white square node
        if node == start:#so if start node is removed then the next time they left-
          start = None #click it will be the start node
        if node == end:
          end = None

      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_a and start and end:
        #check to make sure there is a start and end node before algorithm is run
          reset(grid, start, end) #removes all except the walls, start and end nodes

          astar(lambda: draw(screen, grid, ROWS, width), grid, start, end)
# this calls the algorithm that we are using and has a function within it (draw())
# lambda is an anonymous function that calls draw function we run it, without having
# to know everything from the draw function
# we need this so that when we try to run the algorithm it calls the draw function
# so it is visually displayed
        if event.key == pygame.K_c: #clear all
          start = None
          end = None
          grid = makegrid(ROWS, width)

        if event.key == pygame.K_r: #clear all
          reset(grid, start, end)
        
        
        if event.key == pygame.K_d and start and end:
          #check to make sure there is a start and end node before algorithm is run
            reset(grid, start, end) #removes all except the walls, start and end nodes

            dijkstra(lambda: draw(screen, grid, ROWS, width), grid, start, end)


        if event.key == pygame.K_g and start and end:
          #check to make sure there is a start and end node before algorithm is run
            reset(grid, start, end) #removes all except the walls, start and end nodes

            greedy(lambda: draw(screen, grid, ROWS, width), grid, start, end)


        if event.key == pygame.K_t and start and end:
          #check to make sure there is a start and end node before algorithm is run
            reset(grid, start, end) #removes all except the walls, start and end nodes

            greedy1(lambda: draw(screen, grid, ROWS, width), grid, start, end)

        if event.key == pygame.K_v and start and end:
          #check to make sure there is a start and end node before algorithm is run
            reset(grid, start, end) #removes all except the walls, start and end nodes

            versus(lambda: draw(screen, grid, ROWS, width), grid, start, end)

        if event.key == pygame.K_h and start and end:
          #check to make sure there is a start and end node before algorithm is run
            reset(grid, start, end) #removes all except the walls, start and end nodes

            hillrfs(lambda: draw(screen, grid, ROWS, width), grid, start, end)

        if event.key == pygame.K_e and start and end:
          #check to make sure there is a start and end node before algorithm is run
            reset(grid, start, end) #removes all except the walls, start and end nodes

            elcleggfs(lambda: draw(screen, grid, ROWS, width), grid, start, end)

        if event.key == pygame.K_p and start and end:
          #check to make sure there is a start and end node before algorithm is run
            reset(grid, start, end) #removes all except the walls, start and end nodes

            play(lambda: draw(screen, grid, ROWS, width), grid, start, end)

        if event.key == pygame.K_s and start and end:
          savemap(grid, screen)

        if event.key == pygame.K_m:
          grid, start, end = getmap(screen, ROWS, width)
          draw(screen, grid, ROWS, width)



        if event.key == pygame.K_q:
          start = None
          end = None
          grid = makegrid(ROWS, width)
          #check to make sure there is a start and end node before algorithm is run


          randmap(lambda: draw(screen, grid, ROWS, width), grid, ROWS)
          randrow = random.randint(0, ROWS - 1)
          randcol = random.randint(0, ROWS - 1)
          print(randrow, randcol)
          start = grid[randrow][randcol]
          start.makestart() #add random start and end nodes
          randrow = random.randint(0, ROWS - 1)
          randcol = random.randint(0, ROWS - 1)
          end = grid[randrow][randcol]
          end.makeend()
          print(start, end)

          
        
  pygame.quit()

main(screen, WIDTH) #call function