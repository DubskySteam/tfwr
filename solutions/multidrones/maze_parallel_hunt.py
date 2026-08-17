def maze_substance():
	return get_world_size() * (2 ** (num_unlocked(Unlocks.Mazes) - 1))


def create_maze():
	clear()
	plant(Entities.Bush)
	use_item(Items.Weird_Substance, maze_substance())


def rotate_cw(d):
	if d == North:
		return East
	if d == East:
		return South
	if d == South:
		return West
	if d == West:
		return North
	return d


def rotate_ccw(d):
	if d == North:
		return West
	if d == West:
		return South
	if d == South:
		return East
	if d == East:
		return North
	return d


def hunt(is_seeder):
	direction = North
	while True:
		if get_entity_type() == Entities.Treasure:
			harvest()
		elif get_entity_type() == Entities.Grass and is_seeder:
			plant(Entities.Bush)
			use_item(Items.Weird_Substance, maze_substance())
		if is_seeder:
			preferred = rotate_cw(direction)
			fallback = rotate_ccw(direction)
		else:
			preferred = rotate_ccw(direction)
			fallback = rotate_cw(direction)
		if can_move(preferred):
			direction = preferred
			move(direction)
		elif can_move(direction):
			move(direction)
		elif can_move(fallback):
			direction = fallback
			move(direction)
		else:
			direction = rotate_cw(rotate_cw(direction))
			move(direction)


def make_hunter():
	def hunter():
		hunt(False)
	return hunter


def farm_mazes_multidrone():
	create_maze()
	spawn_count = max_drones() - 1
	for i in range(spawn_count):
		spawn_drone(make_hunter())
	hunt(True)