import battlecode as bc
import random
import sys
import traceback
import pathfinding as pf

def invert(loc):			  
	# assumes Earth
	newx = earth_map.width-1-loc.x
	newy = earth_map.height-1-loc.y
	return bc.MapLocation(bc.Planet.Earth,newx,newy)

def rotate(dir,amount):
	ind = directions.index(dir)
	return directions[(ind+amount)%8]

def locToStr(loc):
	return '('+str(loc.x)+','+str(loc.y)+')'

def goto(unit,dest):
	d = unit.location.map_location().direction_to(dest)
	if gc.can_move(unit.id, d) and gc.is_move_ready(unit.id):
		gc.move_robot(unit.id,d)
		
def fuzzygoto(unit,dest):
	toward = unit.location.map_location().direction_to(dest)
	if toward == bc.Direction.Center:
		return
	for tilt in tryRotate:
		d = rotate(toward,tilt)
		if gc.can_move(unit.id, d) and gc.is_move_ready(unit.id):
			gc.move_robot(unit.id,d)
			break

def getLocations(planet, loc, dimension):
	result = []
	for i in range(-dimension, dimension+1):
		for j in range(-dimension, dimension+1):
			result.append(bc.MapLocation(planet, i, j))
	return result

def bfs_goto(unit,dest):
	unitLoc = unit.location.map_location()
	if unitLoc == dest:
		return
	if(unitLoc.planet == bc.Planet.Earth):
		paths = earth_paths
		graph = earth_squaregrid
	else:
		paths = mars_paths
		graph = mars_squaregrid
	d = pf.path_bfs(paths, graph, (unitLoc.x, unitLoc.y), (dest.x, dest.y))
	if gc.can_move(unit.id, d) and gc.is_move_ready(unit.id):
		gc.move_robot(unit.id,d)
		
def astar_goto(unit,dest):
	unitLoc = unit.location.map_location()
	if unitLoc == dest:
		return
	if(unitLoc.planet == bc.Planet.Earth):
		paths = earth_paths
		graph = earth_squaregrid
	else:
		paths = mars_paths
		graph = mars_squaregrid
	d = pf.path_astar(paths, graph, (unitLoc.x, unitLoc.y), (dest.x, dest.y))
	if gc.can_move(unit.id, d) and gc.is_move_ready(unit.id):
		gc.move_robot(unit.id,d)

def get_karbonite_deposits():
	try:
		current_karbonite_earth = {}
		for x in range(earth_map.width):
			for y in range(earth_map.height):
				if gc.can_sense_location(bc.MapLocation(bc.Planet.Earth, x, y)):
					current_karbonite_earth[(x,y)] = gc.karbonite_at(bc.MapLocation(bc.Planet.Earth,x,y))
		return current_karbonite_earth
	except Exception as e:
		print('Error:', e)
		traceback.print_exc()
		
def get_unit_numbers(units):
	try:
		numbers = {'Factories': 0, 'Rockets': 0, 'Workers': 0, 'Knights': 0, 'Rangers': 0, 'Mages': 0, 'Healers': 0}
		for unit in units:
			if unit.unit_type == bc.UnitType.Factory:
				numbers['Factories'] += 1
			elif unit.unit_type == bc.UnitType.Rocket:
				numbers['Rockets'] += 1
			elif unit.unit_type == bc.UnitType.Worker:
				numbers['Workers'] += 1
			elif unit.unit_type == bc.UnitType.Knight:
				numbers['Knights'] += 1
			elif unit.unit_type == bc.UnitType.Ranger:
				numbers['Rangers'] += 1
			elif unit.unit_type == bc.UnitType.Mage:
				numbers['Mages'] += 1
			elif unit.unit_type == bc.UnitType.Healer:
				numbers['Healers'] += 1
		return numbers
	except Exception as e:
		print('Error:', e)
		traceback.print_exc()

def snipe(ranger):
	allUnits = gc.units()
	for unit in allUnits:
		if unit.team != my_team and unit.unit_type == bc.UnitType.Rocket:
			if gc.can_begin_snipe(ranger.id, unit.location.map_location()):
				gc.begin_snipe(ranger.id, unit.location.map_location())
				break

def get_required_unit_numbers(units):
	required_numbers = {'Factories': 0, 'Rockets': 0, 'Workers': 0, 'Knights': 0, 'Rangers': 0, 'Mages': 0, 'Healers': 0}
	factor = (earth_map.width - 20)
	required_numbers['Factories'] = 5 + round(factor*10/30)
	required_numbers['Rockets'] = 4 + round(factor*10/30)
	required_numbers['Workers'] = 8 + round(factor*10/30)
	required_numbers['Rangers'] = 15 + round(factor*25/30)
	required_numbers['Mages'] = 10 + round(factor*10/30)
	required_numbers['Knights'] = 0
	required_numbers['Healers'] = 5 + round(factor*10/30)
	required_numbers['Attack'] = required_numbers['Rangers'] + required_numbers['Mages'] + required_numbers['Knights'] + required_numbers['Healers']
	return required_numbers

# import os
# print(os.getcwd())

print("starting bot")

gc = bc.GameController()
tryRotate = [0,-1,1,-2,2]
directions = [bc.Direction.North, bc.Direction.Northeast, bc.Direction.East, bc.Direction.Southeast, bc.Direction.South, bc.Direction.Southwest, bc.Direction.West, bc.Direction.Northwest]	  

earth_map = gc.starting_map(bc.Planet.Earth)
earth_squaregrid = pf.SquareGrid(earth_map)
mars_map = gc.starting_map(bc.Planet.Mars)
mars_squaregrid = pf.SquareGrid(mars_map)

earth_paths = {'planet': bc.Planet.Earth}
mars_paths = {'planet': bc.Planet.Mars}

my_team = gc.team()
if my_team == bc.Team.Red:
	other_team = bc.Team.Blue
else:
	other_team = bc.Team.Red
random.seed(455)

if gc.planet() == bc.Planet.Earth:
	my_start = gc.my_units()[0].location.map_location()
	enemy_start = invert(my_start)
	print('worker starts at '+locToStr(my_start))
	print('enemy worker presumably at '+locToStr(enemy_start))

gc.queue_research(bc.UnitType.Worker)
gc.queue_research(bc.UnitType.Rocket)
gc.queue_research(bc.UnitType.Ranger)
gc.queue_research(bc.UnitType.Ranger)
gc.queue_research(bc.UnitType.Healer)
gc.queue_research(bc.UnitType.Mage)
gc.queue_research(bc.UnitType.Healer)
gc.queue_research(bc.UnitType.Ranger)
gc.queue_research(bc.UnitType.Mage)
gc.queue_research(bc.UnitType.Rocket)

while True:
	
	try:
		
		units = gc.my_units()
		numbers = get_unit_numbers(units)
		required_numbers = get_required_unit_numbers(units)
		roundno = gc.round()
		print('pyround:', roundno, 'time left:', gc.get_time_left_ms(), 'ms')
		print('karbonite pool:', gc.karbonite())
		
		# EARTH LOGIC
		if(gc.planet() == bc.Planet.Earth):
		
			current_karbonite_earth = get_karbonite_deposits()

			blueprintLocation = None
			blueprintWaiting = False
			
			for unit in units:
				if unit.location.is_on_map() and unit.unit_type != bc.UnitType.Rocket and unit.unit_type != bc.UnitType.Factory:
					rockets = gc.sense_nearby_units_by_type(unit.location.map_location(), unit.vision_range, bc.UnitType.Rocket)
					if rockets:
						fuzzygoto(unit, rockets[0].location.map_location())
				
				# attack if min no of units
				if len(units) > required_numbers['Attack'] and unit.location.is_on_map() and unit.unit_type != bc.UnitType.Worker:
					if unit.location.map_location().distance_squared_to(enemy_start) > 50:
						if gc.get_time_left_ms() > 6000:
							try:
								astar_goto(unit, enemy_start)
							except Exception as e:
								print('Error:', e)
								# use this to show where the error was
								traceback.print_exc()
								continue
						else:
							fuzzygoto(unit, enemy_start)
						#fuzzygoto(unit, enemy_start)
					else:
						nearby = gc.sense_nearby_units_by_team(unit.location.map_location(), unit.vision_range, other_team)
						if nearby:
							fuzzygoto(unit,nearby[0].location.map_location())
						else:
							fuzzygoto(unit, enemy_start)
					
				if unit.location.is_on_map() and unit.unit_type != bc.UnitType.Healer and unit.unit_type != bc.UnitType.Mage:
					# let's move in a random direction
					d = random.choice(directions)
					if gc.is_move_ready(unit.id) and gc.can_move(unit.id, d):
						gc.move_robot(unit.id, d)
						
				'''# I want my healers in a corner, ready to heal
				if unit.location.is_on_map() and unit.unit_type == bc.UnitType.Healer:
					ml = unit.location.map_location()
					d1 = ml.distance_squared_to(bc.MapLocation(bc.Planet.Earth, 0, 0))
					d2 = ml.distance_squared_to(bc.MapLocation(bc.Planet.Earth, earth_map.width-1, 0))
					d3 = ml.distance_squared_to(bc.MapLocation(bc.Planet.Earth, earth_map.width-1, earth_map.height-1))
					d4 = ml.distance_squared_to(bc.MapLocation(bc.Planet.Earth, 0, earth_map.height-1))
					d = min(d1, d2, d3, d4)
					if d == d1:
						fuzzygoto(unit, bc.MapLocation(bc.Planet.Earth, 0, 0))
						my_healing_spot = bc.MapLocation(bc.Planet.Earth, 0, 0)
					elif d == d2:
						fuzzygoto(unit, bc.MapLocation(bc.Planet.Earth, earth_map.width-1, 0))
						my_healing_spot = bc.MapLocation(bc.Planet.Earth, earth_map.width-1, 0)
					elif d == d3:
						fuzzygoto(unit, bc.MapLocation(bc.Planet.Earth, earth_map.width-1, earth_map.height-1))
						my_healing_spot = bc.MapLocation(bc.Planet.Earth, earth_map.width-1, earth_map.height-1)
					else :
						fuzzygoto(unit,bc.MapLocation(bc.Planet.Earth, 0, earth_map.height-1))	
						my_healing_spot = bc.MapLocation(bc.Planet.Earth, 0, earth_map.height-1)'''
					
				'''if unit.location.is_on_map() and unit.unit_type == bc.UnitType.Mage:
					# form a guard of honour leading up to our start location
					fuzzygoto(unit,enemy_start)
					#pass
				'''
				
				if unit.location.is_on_map():
					# let's declutter our factories
					if unit.unit_type != bc.UnitType.Factory and unit.unit_type != bc.UnitType.Rocket:
						myfactories = gc.sense_nearby_units_by_type(unit.location.map_location(), 2, bc.UnitType.Factory)
						for factory in myfactories:
							d = unit.location.map_location().direction_to(factory.location.map_location())
							d = rotate(d, 4)
							if gc.is_move_ready(unit.id) and gc.can_move(unit.id, d):
								gc.move_robot(unit.id, d)
					# worker logic
					if unit.unit_type == bc.UnitType.Worker:
						if roundno > 450:
							if gc.can_blueprint(unit.id, bc.UnitType.Rocket, d):
								gc.blueprint(unit.id, bc.UnitType.Rocket, d)
								continue
						# try to build nearby units
						adjacentUnits = gc.sense_nearby_units(unit.location.map_location(), 2)
						for adjacent in adjacentUnits:
							if gc.can_build(unit.id,adjacent.id):
								gc.build(unit.id,adjacent.id)
								continue
						d = random.choice(directions)
						# blueprint factories
						if numbers['Factories'] < required_numbers['Factories'] and gc.can_blueprint(unit.id, bc.UnitType.Factory, d):
							gc.blueprint(unit.id, bc.UnitType.Factory, d)
							continue
						# blueprinting rockets
						if numbers['Rockets'] < required_numbers['Rockets'] or roundno > 600:
							if gc.can_blueprint(unit.id, bc.UnitType.Rocket, d):
								gc.blueprint(unit.id, bc.UnitType.Rocket, d)
								continue
						# replicate workers
						if numbers['Workers'] < required_numbers['Workers'] and gc.can_replicate(unit.id, d):
							gc.replicate(unit.id,d)
							print('replicated a worker!')
							continue
						# head toward blueprint location that are far away
						if blueprintWaiting:
							if gc.is_move_ready(unit.id):
								ml = unit.location.map_location()
								bdist = ml.distance_squared_to(blueprintLocation)
								if bdist>2:
									fuzzygoto(unit,blueprintLocation)
						# harvesting karbonite
						for d in directions:
							if gc.can_harvest(unit.id, d):
								gc.harvest(unit.id, d)
								continue
						
						if(gc.karbonite() < 100):
							x, y = max(current_karbonite_earth, key=current_karbonite_earth.get)
							if gc.is_move_ready(unit.id):
								fuzzygoto(unit, bc.MapLocation(bc.Planet.Earth, x, y))
								continue
					
					# factory logic
					if unit.unit_type == bc.UnitType.Factory and (numbers['Rockets'] > 0 or roundno < 250):
						if not unit.structure_is_built():
							ml = unit.location.map_location()
							blueprintLocation = ml
							blueprintWaiting = True
						
						garrison = unit.structure_garrison()
						if len(garrison) > 0:
							d = random.choice(directions)
							if gc.can_unload(unit.id, d):
								print('unloaded a thing from factory!')
								gc.unload(unit.id, d)
								#continue
						if numbers['Workers'] == 0 and gc.can_produce_robot(unit.id, bc.UnitType.Worker):
							gc.produce_robot(unit.id, bc.UnitType.Worker)
							print('produced a worker!')
							continue
							
						elif numbers['Rangers'] < required_numbers['Rangers'] and gc.can_produce_robot(unit.id, bc.UnitType.Ranger):
							gc.produce_robot(unit.id, bc.UnitType.Ranger)
							print('produced a ranger!')
							continue
						elif gc.can_produce_robot(unit.id, bc.UnitType.Mage) and numbers['Mages'] < required_numbers['Mages']:
							gc.produce_robot(unit.id, bc.UnitType.Mage)
							print('produced a mage!')
							continue
						elif gc.can_produce_robot(unit.id, bc.UnitType.Healer) and numbers['Healers'] < required_numbers['Healers']:
							gc.produce_robot(unit.id, bc.UnitType.Healer)
							print('produced a healer!')
							continue
						elif gc.can_produce_robot(unit.id, bc.UnitType.Ranger):
							gc.produce_robot(unit.id, bc.UnitType.Ranger)
							print('produced a ranger!')
							continue
				
					# do some attacking
					if unit.unit_type == bc.UnitType.Healer:
						location = unit.location
						if location.is_on_map():
							nearby = gc.sense_nearby_units(location.map_location(), bc.Unit.attack_range(unit))
							for other in nearby:
								if other.team == my_team and gc.is_heal_ready(unit.id) and gc.can_heal(unit.id, other.id):
									gc.heal(unit.id,other.id)
									print('healer healed a thing!')
								elif other.team == other_team:
									d = unit.location.map_location().direction_to(other.location.map_location())
									d = rotate(d, 4)
									if gc.is_move_ready(unit.id) and gc.can_move(unit.id, d):
										gc.move_robot(unit.id, d)
										continue
									
					if unit.unit_type == bc.UnitType.Ranger:
						location = unit.location
						if location.is_on_map():
							nearby = gc.sense_nearby_units_by_team(location.map_location(), bc.Unit.attack_range(unit), other_team)
							for other in nearby:
								if gc.is_attack_ready(unit.id) and gc.can_attack(unit.id, other.id):
									gc.attack(unit.id,other.id)
									print('ranger attacked a thing!')
								if unit.location.map_location().distance_squared_to(other.location.map_location()) <= 10:
									d = unit.location.map_location().direction_to(other.location.map_location())
									d = rotate(d, 4)
									if gc.is_move_ready(unit.id) and gc.can_move(unit.id, d):
										gc.move_robot(unit.id, d)
										continue
							if unit.health < 0.25 * unit.max_health:
								close_heals = gc.sense_nearby_units(location.map_location(), unit.vision_range)
								if close_heals:
									fuzzygoto(unit,close_heals[0].location.map_location())
								
					if unit.unit_type == bc.UnitType.Mage:
						location = unit.location
						if location.is_on_map():
							nearby = gc.sense_nearby_units(location.map_location(), bc.Unit.attack_range(unit))
							if not nearby:
								fuzzygoto(unit,enemy_start)
								continue
							for other in nearby:
								if other.team != my_team and gc.is_attack_ready(unit.id) and gc.can_attack(unit.id, other.id):
									if unit.location.map_location().distance_squared_to(other.location.map_location()) <= 2:
										d = unit.location.map_location().direction_to(other.location.map_location())
										d = rotate(d, 4)
										if gc.is_move_ready(unit.id) and gc.can_move(unit.id, d):
											gc.move_robot(unit.id, d)
											continue
									else:
										gc.attack(unit.id,other.id)
										print('mage attacked a thing!')
										continue
						  
					# let's leave to mars
					if unit.unit_type == bc.UnitType.Rocket and unit.structure_is_built():
						location = unit.location
						if location.is_on_map():
							nearby = gc.sense_nearby_units(location.map_location(), 2)
							for guys in nearby:
								if guys.team == my_team and guys.unit_type is not bc.UnitType.Factory and guys.unit_type is not bc.UnitType.Rocket:
									if gc.can_load(unit.id,guys.id):
										gc.load(unit.id,guys.id)
							garrison = unit.structure_garrison()
							# if len(garrison) > 4 and mymembers == 0):
							if len(garrison) > 4 or (len(garrison) > 1 and gc.round() > 600) or gc.get_time_left_ms() < 500:
								x = random.randrange(0,mars_map.width)
								y = random.randrange(0,mars_map.height)
								mymembers = 0
								for guys in nearby:
									if guys.team == my_team:
										mymembers += 1
								if gc.can_launch_rocket(unit.id, bc.MapLocation(bc.Planet.Mars,x,y)) and mymembers < 4:
									gc.launch_rocket(unit.id,bc.MapLocation(bc.Planet.Mars,x,y))
									print('launched a rocket')
					
					'''if unit.unit_type == bc.UnitType.Rocket and unit.structure_is_built():
						location = unit.location
						if location.is_on_map():
							nearby = gc.sense_nearby_units_by_team(location.map_location(), 3, my_team)
							if(len(nearby) < 5):
								for guys in nearby:
									if guys.unit_type is not bc.UnitType.Factory and guys.unit_type is not bc.UnitType.Rocket:
										if gc.can_load(unit.id,guys.id):
											gc.load(unit.id,guys.id)
							garrison = unit.structure_garrison()
							# if len(garrison) > 4 and mymembers == 0):
							if len(garrison) > 4 or (len(garrison) > 2 and gc.round() > 500) or (gc.get_time_left_ms() < 2000 and len(garrison) > 2):
								x = random.randrange(0,mars_map.width)
								y = random.randrange(0,mars_map.height)
								if gc.can_launch_rocket(unit.id, bc.MapLocation(bc.Planet.Mars,x,y)):
									gc.launch_rocket(unit.id,bc.MapLocation(bc.Planet.Mars,x,y))
									print('launched a rocket')'''
									
					'''if unit.unit_type == bc.UnitType.Rocket and unit.structure_is_built():
						location = unit.location
						if location.is_on_map():
							nearby = gc.sense_nearby_units_by_team(location.map_location(), 3, my_team)
							if(len(nearby) < 5):
								for guys in nearby:
									if guys.unit_type is bc.UnitType.Worker and gc.round() < 200:
										if gc.can_load(unit.id,guys.id):
											gc.load(unit.id,guys.id)
									elif (guys.unit_type is bc.UnitType.Worker or guys.unit_type is bc.UnitType.Ranger) and gc.round() < 400:
										if gc.can_load(unit.id,guys.id):
											gc.load(unit.id,guys.id)
									elif guys.team == my_team and guys.unit_type is not bc.UnitType.Factory and guys.unit_type is not bc.UnitType.Rocket:
										if gc.can_load(unit.id,guys.id):
											gc.load(unit.id,guys.id)
							garrison = unit.structure_garrison()
							# if len(garrison) > 4 and mymembers == 0):
							if len(garrison) > 4 or (len(garrison) > 1 and gc.round() > 600) :
								x = random.randrange(0,mars_map.width)
								y = random.randrange(0,mars_map.height)
								if gc.can_launch_rocket(unit.id, bc.MapLocation(bc.Planet.Mars,x,y)):
									gc.launch_rocket(unit.id,bc.MapLocation(bc.Planet.Mars,x,y))
									print('launched a rocket')'''
										
		# MARS LOGIC
		elif(gc.planet() == bc.Planet.Mars):
			
			asteroid_pattern = gc.asteroid_pattern()
			for unit in units:
			
				if unit.location.is_on_map():
					# let's move in A random direction
					d = random.choice(directions)
					if gc.is_move_ready(unit.id) and gc.can_move(unit.id, d):
						gc.move_robot(unit.id, d)
			
					# time to unload
					if unit.unit_type == bc.UnitType.Rocket:
						garrison = unit.structure_garrison()
						if len(garrison) > 0:
							for d in directions:
								if gc.can_unload(unit.id, d):
									gc.unload(unit.id, d)
									print('unloaded a dude!')
									continue
			
					# let's do some harvesting
					if unit.unit_type == bc.UnitType.Worker:
						for d in directions:
							if gc.can_harvest(unit.id, d):
								gc.harvest(unit.id, d)
								continue
					if asteroid_pattern.has_asteroid(gc.round()):
						asteroid = asteroid_pattern.asteroid(gc.round())
						if(asteroid.karbonite > 35):
							location = asteroid.location
							if location.is_on_map():
								maplocation = location.map_location()
								fuzzygoto(unit,maplocation)
								continue
					# worker logic (replication)
					if unit.unit_type == bc.UnitType.Worker:
						if numbers['Workers'] < 25 and gc.can_replicate(unit.id, d):
							gc.replicate(unit.id,d)
							print('replicated a worker!')
						elif gc.round() >= 700 and gc.can_replicate(unit.id, d):
							gc.replicate(unit.id,d)
							print('replicated a worker!')
							continue
					# let's do some hitting
					if unit.unit_type == bc.UnitType.Healer:
						location = unit.location
						if location.is_on_map():
							nearby = gc.sense_nearby_units(location.map_location(), bc.Unit.attack_range(unit))
							for other in nearby:
								if other.team == my_team and gc.is_heal_ready(unit.id) and gc.can_heal(unit.id, other.id):
									gc.heal(unit.id,other.id)
									print('healer healed a thing!')
								elif other.team == other_team:
									d = unit.location.map_location().direction_to(other.location.map_location())
									d = rotate(d, 4)
									if gc.is_move_ready(unit.id) and gc.can_move(unit.id, d):
										gc.move_robot(unit.id, d)
										continue
				  
					if unit.unit_type == bc.UnitType.Ranger and not unit.ranger_is_sniping:
						
						location = unit.location
						if location.is_on_map():
							nearby = gc.sense_nearby_units_by_team(location.map_location(), bc.Unit.attack_range(unit), other_team)
							if nearby:
								for other in nearby:
									if gc.is_attack_ready(unit.id) and gc.can_attack(unit.id, other.id):
										gc.attack(unit.id,other.id)
										print('ranger attacked a thing!')
							elif gc.is_begin_snipe_ready(unit.id):
								print('setting up a snipe')
								snipe(unit)
							  
						if unit.location.map_location().distance_squared_to(other.location.map_location()) <= 10:
							d = unit.location.map_location().direction_to(other.location.map_location())
							d = rotate(d, 4)
							if gc.is_move_ready(unit.id) and gc.can_move(unit.id, d):
								gc.move_robot(unit.id, d)
								continue
							if unit.health < 0.25 * unit.max_health:
								close_heals = gc.sense_nearby_units(location.map_location(), unit.vision_range)
								if close_heals:
									for healer in close_heals:
										fuzzygoto(unit,healer.location.map_location())
										continue
								
					if unit.unit_type == bc.UnitType.Mage:
						location = unit.location
						if location.is_on_map():
							nearby = gc.sense_nearby_units(location.map_location(), bc.Unit.attack_range(unit))
							if not nearby:
								fuzzygoto(unit,enemy_start)
								continue
							for other in nearby:
								if other.team != my_team and gc.is_attack_ready(unit.id) and gc.can_attack(unit.id, other.id):
									if unit.location.map_location().distance_squared_to(other.location.map_location()) <= 2:
										d = unit.location.map_location().direction_to(other.location.map_location())
										d = rotate(d, 4)
										if gc.is_move_ready(unit.id) and gc.can_move(unit.id, d):
											gc.move_robot(unit.id, d)
											continue
									else:
										gc.attack(unit.id,other.id)
										print('mage attacked a thing!')
										continue

		
	except Exception as e:
		print('Error:', e)
		# use this to show where the error was
		traceback.print_exc()

	# send the actions we've performed, and wait for our next turn.
	gc.next_turn()

	# these lines are not strictly necessary, but it helps make the logs make more sense.
	# it forces everything we've written this turn to be written to the manager.
	sys.stdout.flush()
	sys.stderr.flush()