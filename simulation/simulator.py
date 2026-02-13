from simulation.path_godot_parser import *
from simulation.base_statistics_godot_parser import *
from simulation.vector import *
import random
from copy import deepcopy
from math import sin, cos

def reset():
		global wavecount, base_health, base_money, enemies, waves, towers, tower_queue, lvlname
		LevelData = deepcopy(level_data[lvlname])
		wavecount = 0
		wavetotal = LevelData['number_of_waves']
		waves = deepcopy([LevelData[f'wave_{n+1}'] for n in range(wavetotal)])
		base_health = player_base_health
		base_money = player_base_money
		enemies = []
		tower_queue = []
		towers = []

def simulation(test_count, level):
	global wavecount, base_health, base_money, enemies, waves, towers, tower_queue, lvlname

	# FAST API NEEDED HERE
	enemy_damage_mult = 0.34
	enemy_health_mult = 1
	enemy_speed_mult = 1
	player_rof_mult = 1
	# END FAST API



	timesamplerate = 0.01 #seconds / iteration: how many "seconds" are simulated every second
	spacesamplerate = 0.01 #pixels / sample: what length is sampled when checking the path to make the hit mask
	tower_spread = 50 #pixels: average distance from the path the tower is placed.
	tower_deviance = 50 #pixels: average deviation between distances from the path. 

	def within_bounds(tower_type, tower_location: tuple, path_location: tuple)  -> bool:
		match tower_type:
			case 'triangle_stock':
				return abs(Vector(tower_location) - Vector(path_location)) < tower_data['triangle_stock']['range']
			case 'square_stock':
				return (abs(tower_location[1] - path_location[1]) < 30) or (abs(tower_location[1] - path_location[1]) < 30)
			case 'star_stock':
				return abs(Vector(tower_location) - Vector(path_location)) < tower_data['star_stock']['range']
			case _:
				return False
			

	lvlname = 'Level' + str(level)
	mapname = "map_" + str(level)
	length, path = path_interpreter(mapname)
	successes = 0

	#Time is distance / speed

	speeds = dict((enemy, enemy_speed_mult*enemy_data[enemy]['speed']) for enemy in enemy_data)


	#effectively running reset(), but just so VSCode doesn't yell saying "OH NO THESE AREN'T DEFINED YET" smh
	LevelData = deepcopy(level_data[lvlname])
	wavecount = 0
	wavetotal = LevelData['number_of_waves']
	waves = deepcopy([LevelData[f'wave_{n+1}'] for n in range(wavetotal)])
	base_health = player_base_health
	base_money = player_base_money
	enemies = []
	tower_queue = []
	towers = []

	durations = dict((enemy, length/speeds[enemy]) for enemy in speeds)
	maxduration = 0
	offset = 0
	earnable = 0
	for wave in waves:
		for enemy in wave:
			maxduration = max(maxduration, offset + durations[enemy[0]])
			offset += enemy[1]
			earnable += enemy_data[enemy[0]]['cash']
		offset = maxduration
	totaliterations = int(round(maxduration/timesamplerate,0))
	sample_points = tuple(path(index*spacesamplerate) for index in range(int(round(length/spacesamplerate,0))))

	for i in range(test_count):
		hit_mask = list(0 for _ in sample_points)
		#print(f'                                 SIMULATION {i+1}                                 ')
		enemy_ids = []
		ctrs = []
		money = base_money
		# This code will make some simplifying assumptions to decrease simulation time
		# First:  towers can be placed anywhere
		# Second: that towers are constantly shooting damage at a rate equal to (damage*rateoffire) per second
		# Third: this constant rate of fire will deal an average amount of damage for the duration the enemy is within line of fire.
		# Fourth: if you can place a tower, you will place a tower.
		while base_money + earnable > 0:
			tower = random.choice(list(tower_data.keys()))
			#tower = 'triangle_stock'
			tower_queue.append(tower)
			base_money -= tower_data[tower]['cost']
			if base_money >= 0:
				money = base_money
				towers.append(tower)
		for index, tower in enumerate(tower_queue):
			alongcurve = random.randint(0,int(round(length,0)))
			direction = 2*3.14159265358979323*random.random()
			distance = random.gauss(tower_spread,tower_deviance)
			offset = Vector(sin(direction), cos(direction)) * distance
			pathpoint = Vector(path(alongcurve))
			towerCentre = tuple((offset + pathpoint).values)
			ctrs.append(towerCentre)
			# for each point in the hit_mask, there will be a number, whos binary representation is which towers can hit this point.
		for i in range(len(towers)):
			# mask calculation
			for pointindex, point in enumerate(sample_points):
				if within_bounds(towers[i], ctrs[i], point):
					hit_mask[pointindex] += 2**i
			tower_queue.pop(0)
			##print(f'Tower {i} ({towers[i]}) created at {ctrs[i]}')
		# The towers are now all set up, time to simulate the game
		cooldown = 0
		for iteration in range(totaliterations): #stops infinte loops ^_^
			if enemies == [] and (len(waves[wavecount-1]) == 0 or wavecount == 0): # enemies of current wave defeated
				cooldown = 0
				wavecount += 1
				if wavecount > wavetotal: #we're trying to spawn a wave which doesn't exist
					break # run game_over checks
			#run movement
			topop = []
			for enemyind,enemy in enumerate(enemies):
				enemy[1] += speeds[enemy[0]] * timesamplerate # timesamplerate is assumed here to mean "secondpersample"
				if enemy[1]/spacesamplerate >= len(hit_mask): # this means the enemy has reached the end without dying, so deal damage to player and remove the enemy
					base_health -= enemy_damage_mult * enemy_data[enemy[0]]['damage']
					topop.append(enemyind)
				else:
					enemy[2] = hit_mask[int(round(enemy[1],0))]
			for pop in topop[::-1]:
				##print(f"Enemy {enemy_ids[pop]} reached end, dealing {enemy_damage_mult * enemy_data[enemies[pop][0]]['damage']} damage")
				enemies.pop(pop)
				enemy_ids.pop(pop)
			#run enemy damage
			for index,tower in enumerate(towers):
				enemies_hit_by_tower = tuple(map(lambda enemy: bool((enemy[2] >> index) & 1),enemies))
				total_hit = sum(enemies_hit_by_tower)
				if total_hit == 0:
					pass
				else:
					damage = tower_data[tower]['damage'] * player_rof_mult * timesamplerate/ (tower_data[tower]['rof'])
					average_damage  = damage/total_hit
					for enemyind, enemyhit in enumerate(enemies_hit_by_tower):
						if enemyhit and (tower == 'star_stock'):
							enemy[3] -= damage
						elif enemyhit:
							enemy[3] -= average_damage
					for enemyind, enemy in list(enumerate(enemies.copy()))[::-1]:
						if enemy[3] <= 0:
							##print(f"Tower {index} has destroyed enemy {enemy_ids[enemyind]}, earning {enemy_data[enemy[0]]['cash']}")
							money += enemy_data[enemy[0]]['cash']
							enemies.pop(enemyind)
							enemy_ids.pop(enemyind)
			# run player health checks
			if base_health <= 0:
				break
			# run tower spawning checks
			while money >= tower_data[tower_queue[0]]['cost']:
				money -= tower_data[tower_queue[0]]['cost']
				for pointindex, point in enumerate(sample_points):
					if within_bounds(tower_queue[0], ctrs[len(towers)], point):
						hit_mask[pointindex] += 2**len(towers)
				towers.append(tower_queue.pop(0))
				##print(f"Built new tower {len(towers)-1}: {towers[len(towers)-1]}")
			# run enemy spawning checks
			if cooldown == 0 and len(waves[wavecount-1]) != 0:
				nextenemy = waves[wavecount-1].pop(0)
				enemies.append([nextenemy[0], 0, hit_mask[0], enemy_data[nextenemy[0]]['health']*enemy_health_mult])
				cooldown = nextenemy[1]
				##print(f'{nextenemy[0]} spawned: ENEMY ID: {0 if len(enemy_ids) == 0 else max(enemy_ids)+1}')
				enemy_ids.append(0 if len(enemy_ids) == 0 else max(enemy_ids)+1)
			cooldown = max(0, cooldown - timesamplerate)
		##print("GAME WON" if base_health > 0 else "GAME LOST")
		successes += base_health > 0
		reset()

	# FAST API:
	#print("                RESULTS                ")
	print(f"{successes} out of {test_count} were successful ({round(successes*100/test_count,1)}%)")
	return {
		"success_rate": successes*100/test_count,
		"suggestedAction": "Near expected, no action required" if successes*100/test_count > 80 else "Consider decreasing enemy damage"
	}

#simulation(2,1)
