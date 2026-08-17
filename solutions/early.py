while True:
	if can_harvest():
		harvest()
	plant(Entities.Bush)
	move(South)
