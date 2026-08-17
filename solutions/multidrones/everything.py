def move_to(x, y):
	ws = get_world_size()
	dx = (x - get_pos_x()) % ws
	if dx > ws // 2:
		dx = dx - ws
	dy = (y - get_pos_y()) % ws
	if dy > ws // 2:
		dy = dy - ws
	if dx > 0:
		for _ in range(dx):
			move(East)
	else:
		for _ in range(-dx):
			move(West)
	if dy > 0:
		for _ in range(dy):
			move(North)
	else:
		for _ in range(-dy):
			move(South)


def ground_for(entity):
	if entity == Entities.Carrot:
		return Grounds.Soil
	if entity == Entities.Pumpkin:
		return Grounds.Soil
	if entity == Entities.Sunflower:
		return Grounds.Soil
	if entity == Entities.Cactus:
		return Grounds.Soil
	return Grounds.Grassland


def sow(entity, water):
	if entity == Entities.Grass:
		if can_harvest():
			harvest()
		if get_ground_type() != Grounds.Grassland:
			till()
		return
	if get_entity_type() != entity or can_harvest():
		harvest()
	if get_ground_type() != ground_for(entity):
		till()
	if water and num_unlocked(Unlocks.Watering) > 0 and get_ground_type() == Grounds.Soil:
		while get_water() < 0.5 and num_items(Items.Water) > 0:
			use_item(Items.Water)
	if get_entity_type() != entity:
		plant(entity)


def do_tile(phase):
	if phase == "grass":
		if can_harvest():
			harvest()
	elif phase == "trees":
		if (get_pos_x() + get_pos_y()) % 2 == 0:
			sow(Entities.Tree, True)
		else:
			sow(Entities.Grass, True)
	elif phase == "carrots":
		sow(Entities.Carrot, True)
	elif phase == "pumpkins":
		sow(Entities.Pumpkin, True)
	elif phase == "sunflowers":
		sow(Entities.Sunflower, True)
	elif phase == "weird":
		sow(Entities.Grass, True)
		use_item(Items.Fertilizer)


def sweep_stripe(phase, x0, x1):
	ws = get_world_size()
	for x in range(x0, x1):
		move_to(x, 0)
		for y in range(ws):
			do_tile(phase)
			move(North)


def make_sweeper(phase, x0, x1):
	def sweeper():
		sweep_stripe(phase, x0, x1)
	return sweeper


def farm_phase(phase):
	ws = get_world_size()
	n = max_drones()
	for i in range(1, n):
		boundary_0 = (i * ws) // n
		boundary_1 = ((i + 1) * ws) // n
		move_to(boundary_0, 0)
		spawn_drone(make_sweeper(phase, boundary_0, boundary_1))
	move_to(0, 0)
	sweep_stripe(phase, 0, ws // n)
	while num_drones() > 1:
		pass
	move_to(0, 0)


def can_afford(cost):
	for item in list(cost):
		if num_items(item) < cost[item]:
			return False
	return True


def auto_unlock():
	priority = [Unlocks.Megafarm, Unlocks.Speed, Unlocks.Expand, Unlocks.Sunflowers,
		Unlocks.Watering, Unlocks.Fertilizer, Unlocks.Pumpkins, Unlocks.Carrots,
		Unlocks.Grass, Unlocks.Trees, Unlocks.Mazes, Unlocks.Cactus,
		Unlocks.Polyculture, Unlocks.Dinosaurs]
	for tech in priority:
		cost = get_cost(tech)
		if cost != None and can_afford(cost):
			unlock(tech)


def decide_phase():
	if num_items(Items.Weird_Substance) < 1000 and num_items(Items.Fertilizer) >= 50:
		return "weird"
	if num_items(Items.Power) < 400:
		return "sunflowers"
	if num_items(Items.Pumpkin) < 1200:
		return "pumpkins"
	if num_items(Items.Carrot) < 1800:
		return "carrots"
	if num_items(Items.Wood) < 1800:
		return "trees"
	if num_items(Items.Hay) < 1800:
		return "grass"
	return "sunflowers"


def coordinator():
	while True:
		auto_unlock()
		farm_phase(decide_phase())


def main():
	clear()
	coordinator()


main()