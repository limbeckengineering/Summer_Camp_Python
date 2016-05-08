#Method to update position - takes vel_x, vel_y, delta_t and returns delta_x , delta_y and a new vel_x and vel_y
def update(vel_x, vel_y, delta_t):
	
	dx = vel_x*delta_t
	dy = vel_y*delta_t

	nvx = vel_x
	nvy = vel_y - 9.8*delta_t
	return dx, dy, nvx, nvy
