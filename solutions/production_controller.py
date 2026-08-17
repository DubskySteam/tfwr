def farm_grass():
	for _ in range(get_world_size()):
		for _ in range(get_world_size()):
			if get_ground_type() != Grounds.Grassland:
				till()
			if can_harvest():
				harvest()
			move(South)
		move(East)


def farm_trees():
	for _ in range(get_world_size()):
		for _ in range(get_world_size()):
			if get_ground_type() != Grounds.Grassland:
				till()
			if can_harvest():
				harvest()
			if (get_pos_x() + get_pos_y()) % 2 == 0:
				plant(Entities.Tree)
			move(South)
		move(East)


def farm_carrots():
	for _ in range(get_world_size()):
		for _ in range(get_world_size()):
			if get_ground_type() != Grounds.Soil:
				till()
			if get_water() <= 0.5:
				use_item(Items.Water)
			if can_harvest():
				harvest()
			plant(Entities.Carrot)
			move(South)
		move(East)


def farm_pumpkins():
	for _ in range(get_world_size()):
		for _ in range(get_world_size()):
			if get_water() == 0:
				use_item(Items.Water)
			if get_pos_x() == 0 and get_pos_y() == 0 and can_harvest():
				harvest()
			if get_ground_type() != Grounds.Soil:
				till()
			if plant(Entities.Pumpkin):
				use_item(Items.Fertilizer)
			move(South)
		move(East)


def num_plantable(crop):
	cost = get_cost(crop)
	if cost is None:
		return 10 ** 9
	affordable = 10 ** 9
	for item in list(cost):
		affordable = min(affordable, num_items(item) // cost[item])
	return affordable


def can_afford(cost):
	for item in list(cost):
		if num_items(item) < cost[item]:
			return False
	return True


def unlock_priority():
	return [
		Unlocks.Speed,
		Unlocks.Sunflowers,
		Unlocks.Expand,
		Unlocks.Watering,
		Unlocks.Fertilizer,
		Unlocks.Pumpkins,
		Unlocks.Carrots,
		Unlocks.Grass,
		Unlocks.Trees,
		Unlocks.Mazes,
		Unlocks.Dinosaurs,
		Unlocks.Megafarm,
		Unlocks.Cactus,
		Unlocks.Polyculture,
	]


def auto_unlock():
	for u in unlock_priority():
		cost = get_cost(u)
		if cost is None:
			continue
		if can_afford(cost):
			unlock(u)


def choose_farm():
	candidates = [
		(Entities.Pumpkin, Items.Pumpkin, farm_pumpkins),
		(Entities.Carrot, Items.Carrot, farm_carrots),
		(Entities.Tree, Items.Wood, farm_trees),
		(Entities.Grass, Items.Hay, farm_grass),
	]
	targets = {
		Items.Hay: 1500,
		Items.Wood: 1500,
		Items.Carrot: 1500,
		Items.Pumpkin: 2500,
	}
	best_farm = farm_pumpkins
	best_score = -1
	for crop, out_item, farm in candidates:
		if num_plantable(crop) == 0:
			continue
		score = targets[out_item] - num_items(out_item)
		if score > best_score:
			best_score = score
			best_farm = farm
	if best_score < 0:
		return farm_pumpkins
	return best_farm


clear()

while True:
	auto_unlock()
	choose_farm()()