def create_pumpkin_farm():
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


clear()

while True:
	create_pumpkin_farm()