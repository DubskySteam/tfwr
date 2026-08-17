def move_to_start():
	for _ in range(get_pos_y()):
		move(North)
	for _ in range(get_pos_x()):
		move(West)


def create_farm():
	move_to_start()
	for col in range(get_world_size()):
		for _ in range(get_world_size()):
			if can_harvest():
				harvest()
			if (get_pos_x() + get_pos_y()) % 2 == 0:
				plant(Entities.Tree)
			else:
				plant(Entities.Bush)
			move(South)
		move(East)


while True:
	create_farm()