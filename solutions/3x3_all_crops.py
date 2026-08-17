while True:
	for col in range(get_world_size()):
		for _ in range(get_world_size()):
			if can_harvest():
				harvest()
			x = get_pos_x()
			if x == 0:
				if get_ground_type() != Grounds.Soil:
					till()
				if get_water() <= 0.6:
					use_item(Items.Water)
				plant(Entities.Carrot)
			elif x == 1:
				plant(Entities.Bush)
			else:
				plant(Entities.Grass)
			move(South)
		move(East)