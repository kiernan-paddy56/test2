import pygame, sys, math
from queue import PriorityQueue
from pygame.constants import KEYDOWN
from pygame.locals import QUIT

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
      if event.type == pygame.QUIT:
        pygame.quit() #so we can exit function if takes too long or error occurs

    current = open_set.get()[2] #get the node from the priority queue
    #the priority queue will mean we get the node with the lowest f-cost(the most 
#promising node),if the f-cost is the same then go by count(order of entery into queue)
    open_set_tracker.remove(current) #we are now looking at current so its no longer
# a part of the open set
    if current == end:
      reconstruct_path(came_from, end, draw) #call function to draw shortest path
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
      if event.type == pygame.QUIT:
          pygame.quit() #so we can exit function if takes too long or error occurs

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

def play(draw, start, end):
  came_from = {} #where each node came from so we can retrace path at the end
  found = False
  current = start
  while not found: #if open set is empty we've considered every node
      #that is 'promising', if no path is yet found then there is no path to end
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
          pygame.quit() #so we can exit function if takes too long or error occurs
  # a part of the open set
    
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
      reconstruct_path(came_from, end, draw) #call function to draw shortest path
      end.makeend() #so we can see the end and start nodes
      start.makestart()
      found = True
      return True
      
    draw()

  return False


def makegrid(rows, width): #store all of the nodes so they can be used
  grid = [] #make the array for other arrays to be added to
  spacing = width // rows #finds the spacing between the nodes/node width
  for i in range(rows):
   grid.append([]) # creates a 2d array/ adds a new array for each row
   for j in range(rows):
     node = Node(i, j, spacing, rows) #pass all of the parameters of node class in
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
        elif node != start and node != end:
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
          for row in grid: #for every node when we start a new map we must
            for node in row: # update all of the neighbors for this new setup of nodes
              node.update_neighbors(grid)
              if node.isopen() or node.ispath() or node.isclosed():
                node.makeplain()

          astar(lambda: draw(screen, grid, ROWS, width), grid, start, end)
# this calls the algorithm that we are using and has a function within it (draw())
# lambda is an anonymous function that calls draw function we run it, without having
# to know everything from the draw function
# we need this so that when we try to run the algorithm it calls the draw function
# so it is visually displayed
        if event.key == pygame.K_c:
          start = None
          end = None
          grid = makegrid(ROWS, width)
        
        
        if event.key == pygame.K_d and start and end:
          #check to make sure there is a start and end node before algorithm is run
            for row in grid: #for every node when we start a new map we must
              for node in row: # update all of the neighbors for this new setup of nodes
                node.update_neighbors(grid)
                if node.isopen() or node.ispath() or node.isclosed():
                  node.makeplain()

            dijkstra(lambda: draw(screen, grid, ROWS, width), grid, start, end)

        if event.key == pygame.K_p and start and end:
          #check to make sure there is a start and end node before algorithm is run
            for row in grid: #for every node when we start a new map we must
              for node in row: # update all of the neighbors for this new setup of nodes
                node.update_neighbors(grid)
                if node.isopen() or node.ispath() or node.isclosed():
                  node.makeplain()

            play(lambda: draw(screen, grid, ROWS, width), start, end)
          
        
  pygame.quit()
  
main(screen, WIDTH) #call function