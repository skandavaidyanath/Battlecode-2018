import heapq
import collections
import battlecode as bc

class SquareGrid:
	def __init__(self, map):
		self.map = map
		self.impassable = []
		for x in range(self.map.width):
			for y in range(self.map.height):
				if(not self.map.is_passable_terrain_at(bc.MapLocation(self.map.planet,x, y))):
					self.impassable.append((x,y))
					
	def in_bounds(self, id):
		(x, y) = id
		return 0 <= x < self.map.width and 0 <= y < self.map.height
	
	def passable(self, id):
		return id not in self.impassable
	
	def neighbors(self, id):
		(x, y) = id
		results = [(x+1, y), (x, y-1), (x-1, y), (x, y+1), (x+1,y+1),(x+1,y-1),(x-1,y-1),(x-1,y+1)]
		results = filter(self.in_bounds, results)
		results = filter(self.passable, results)
		return results
		

class PriorityQueue:
	def __init__(self):
		self.elements = []
	
	def empty(self):
		return len(self.elements) == 0
	
	def put(self, item, priority):
		heapq.heappush(self.elements, (priority, item))
	
	def get(self):
		return heapq.heappop(self.elements)[1]


class Queue:
	def __init__(self):
		self.elements = collections.deque()
	
	def empty(self):
		return len(self.elements) == 0
	
	def put(self, x):
		self.elements.append(x)
	
	def get(self):
		return self.elements.popleft()
		
def breadth_first_search(graph, start, goal):
	frontier = Queue()
	frontier.put(start)
	came_from = {}
	came_from[start] = None
	
	while not frontier.empty():
		current = frontier.get()
		
		if current == goal:
			break
		
		for next in graph.neighbors(current):
			if next not in came_from:
				frontier.put(next)
				came_from[next] = current
	
	path = []
	while current != start: 
		path.append(current)
		current = came_from[current]
	path.append(start)	 
	path.reverse()		  
	
	return path


def heuristic(a, b):
	(x1, y1) = a
	(x2, y2) = b
	xdistance = abs(x1 - x2)  
	ydistance = abs(y1 - y2)
	if(xdistance < ydistance) :
		return ydistance
	else :
		return xdistance

def a_star_search(graph, start, goal):
	frontier = PriorityQueue()
	frontier.put(start, 0)
	came_from = {}
	cost_so_far = {}
	came_from[start] = None
	cost_so_far[start] = 0
	
	while not frontier.empty():
		current = frontier.get()
		
		if current == goal:
			break
		
		for next in graph.neighbors(current):
			new_cost = cost_so_far[current] + 1
			if next not in cost_so_far or new_cost < cost_so_far[next]:
				cost_so_far[next] = new_cost
				priority = new_cost + heuristic(goal, next)
				frontier.put(next, priority)
				came_from[next] = current
				
	current = goal 
	path = []
	while current != start: 
		path.append(current)
		current = came_from[current]
	path.append(start)	 
	path.reverse()		  
	
	return path