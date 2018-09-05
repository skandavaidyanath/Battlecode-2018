import battlecode as bc
import random
import sys
import traceback
import operator

import os
print(os.getcwd())

print("pystarting")


gc = bc.GameController()
tryRotate = [0,-1,1,-2,2]
directions = [bc.Direction.North, bc.Direction.Northeast, bc.Direction.East, bc.Direction.Southeast, bc.Direction.South, bc.Direction.Southwest, bc.Direction.West, bc.Direction.Northwest]	  
earth_map = gc.starting_map(bc.Planet.Earth)
mars_map = gc.starting_map(bc.Planet.Mars)

print("pystarted")

def rotate(dir,amount):
	ind = directions.index(dir)
	return directions[(ind+amount)%8]

def goto(unit,dest):
	d = unit.location.map_location().direction_to(dest)
	if gc.can_move(unit.id, d):
		gc.move_robot(unit.id,d)
		
def fuzzygoto(unit,dest):
	toward = unit.location.map_location().direction_to(dest)
	if toward == bc.Direction.Center:
		return
	for tilt in tryRotate:
		d = rotate(toward,tilt)
		if gc.can_move(unit.id, d):
			gc.move_robot(unit.id,d)
			break

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
		
def get_unit_numbers():
	try:
		numbers = {'Factories': 0, 'Rockets': 0, 'Workers': 0, 'Knights': 0, 'Rangers': 0, 'Mages': 0, 'Healer': 0}
		for unit in gc.my_units():
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

random.seed(455)

gc.queue_research(bc.UnitType.Worker)
gc.queue_research(bc.UnitType.Rocket)
gc.queue_research(bc.UnitType.Knight)
gc.queue_research(bc.UnitType.Mage)
gc.queue_research(bc.UnitType.Ranger)
gc.queue_research(bc.UnitType.Ranger)
gc.queue_research(bc.UnitType.Ranger)

my_team = gc.team()

while True:
  	
	try:
      	
        # EARTH LOGIC
		if(gc.planet() == bc.Planet.Earth):
			roundno = gc.round()
			print('pyround:', roundno)
			print('karbonite pool:', gc.karbonite())
			numbers = get_unit_numbers()

			blueprintLocation = None
			blueprintWaiting = False
			for unit in gc.my_units():
				
				# let's move in A random direction
				d = random.choice(directions)
				if gc.is_move_ready(unit.id) and gc.can_move(unit.id, d):
					gc.move_robot(unit.id, d)

				# worker logic
				if unit.unit_type == bc.UnitType.Worker:
					d = random.choice(directions)
                    # blueprint factories
					if numbers['Factories'] < 5 and gc.can_blueprint(unit.id, bc.UnitType.Factory, d):
						gc.blueprint(unit.id, bc.UnitType.Factory, d)
						continue
                    # replicate workers
					if numbers['Workers'] < 5 and gc.can_replicate(unit.id, d):
						gc.replicate(unit.id,d)
						print('replicated a worker!')
						continue
                    # try to build nearby units
					adjacentUnits = gc.sense_nearby_units(unit.location.map_location(), 2)
					for adjacent in adjacentUnits:
						if gc.can_build(unit.id,adjacent.id):
							gc.build(unit.id,adjacent.id)
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
                    
                    current_karbonite_earth = get_karbonite_deposits()
					x, y = max(current_karbonite_earth, key=current_karbonite_earth.get)
					if gc.is_move_ready(unit.id):
						fuzzygoto(unit, bc.MapLocation(bc.Planet.Earth, x, y))
						continue
						
					if gc.karbonite() > 300:
						for d in directions:
							if gc.can_blueprint(unit.id, bc.UnitType.Rocket, d):
								gc.blueprint(unit.id, bc.UnitType.Rocket, d)
								continue
                    
				# factory logic
				if unit.unit_type == bc.UnitType.Factory:
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
							continue
					elif numbers['Workers'] == 0 and gc.can_produce_robot(unit.id, bc.UnitType.Worker):
						gc.produce_robot(unit.id, bc.UnitType.Worker)
						print('produced a worker!')
						continue
					elif gc.can_produce_robot(unit.id, bc.UnitType.Knight) and numbers['Knights'] < 10:
						gc.produce_robot(unit.id, bc.UnitType.Knight)
						print('produced a knight!')
						continue
					elif gc.can_produce_robot(unit.id, bc.UnitType.Mage) and numbers['Mages'] < 20:
						gc.produce_robot(unit.id, bc.UnitType.Mage)
						print('produced a mage!')
						continue
					elif gc.can_produce_robot(unit.id, bc.UnitType.Ranger):
						gc.produce_robot(unit.id, bc.UnitType.Ranger)
						print('produced a ranger!')
						continue
                
				# do some attacking
				if unit.unit_type == bc.UnitType.Knight or unit.unit_type == bc.UnitType.Mage or unit.unit_type == bc.UnitType.Ranger:
					location = unit.location
					if location.is_on_map():
						nearby = gc.sense_nearby_units(location.map_location(), bc.Unit.attack_range(unit))
						for other in nearby:
							if other.team != my_team and gc.is_attack_ready(unit.id) and gc.can_attack(unit.id, other.id):
								gc.attack(unit.id,other.id)
								print('attacked a thing!')
								continue
                            
                # let's leave to mars
				if unit.unit_type == bc.UnitType.Rocket and unit.structure_is_built():
					location = unit.location
					if location.is_on_map():
						nearby = gc.sense_nearby_units(location.map_location(), 2)
						mymembers = 0
						for guys in nearby:
							if guys.team() == my_team:
								mymembers++
						if(mymembers < 4 ):
							for guys in nearby:
								if guys.team() == my_team and guys.unit_type is not bc.UnitType.Factory and guys.unit_type is not bc.UnitType.Rocket:
									if gc.can_load(unit.id,guys.id):
										gc.load(unit.id,guys.id)
                        garrison = unit.structure_garrison()
                        if len(garrison) == 8 or (len(garrison) > 4 and mymembers == 0):
                          x = randrange(0,mars_map.width)
                          y = randrange(0,mars_map.height)
                          if gc.can_launch_rocket(unit.id,MapLocation(bc.Planet.Mars,x,y)):
                                                  gc.launch_rocket(unit.id,MapLocation(bc.Planet.Mars,x,y))
                              
                                            
                
        # MARS LOGIC
		elif(gc.planet() == bc.Planet.Mars):
			
            asteroid_pattern = gc.asteroid_pattern()
            for unit in gc.my_units():
              
              # time to unload 
              if unit.unit_type == bc.UnitType.Rocket:
                garrison = unit.structure_garrison()
                if len(garrison) > 0:
                    d = random.choice(directions)
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
                	asteroid = asteroid_pattern.asteroid()
                  	if(asteroid.karbonite > 35 ):
                    	location = asteroid.location
                    	if location.is_on_map():
                    		maplocation = location.map_location()
                        	fuzzygoto(unit,maplocation)
                      		continue
              # let's replicate
                if unit.unit_type == bc.UnitType.Worker:
                    if numbers['Workers'] < 25 and gc.can_replicate(unit.id, d):
						gc.replicate(unit.id,d)
						print('replicated a worker!')
						continue
              # let's do some hitting
              if unit.unit_type == bc.UnitType.Knight or unit.unit_type == bc.UnitType.Mage or unit.unit_type == bc.UnitType.Ranger:
					location = unit.location
					if location.is_on_map():
						nearby = gc.sense_nearby_units(location.map_location(), bc.Unit.attack_range(unit))
						for other in nearby:
							if other.team != my_team and gc.is_attack_ready(unit.id) and gc.can_attack(unit.id, other.id):
								gc.attack(unit.id,other.id)
								print('attacked a thing!')
								continue
                                
              
                                
              
              #if unit.unit_type == bc.UnitType.Ranger:
                
                # if gc.can_begin_snipe(unit.id,location) and gc.is_begin_snipe_ready(unit.id):
                #  gc.begin_snipe(unit.id,location)
                  
                
          
          
          
          
          
          
          
          
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