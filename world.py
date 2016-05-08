from tkinter import *
import math
import time
import threading


##TODO: implement velocity slider - calc velocity components
##TODO: check to see if calculations are acurate - range equation


class shot:
	#world - the instance of world that created the shot
	def __init__(self, vel_x, vel_y, world):
		#Note actual real world velocities and positions 
		self.vel_x = vel_x
		self.vel_y = vel_y

		self.radius = 10

		self.world = world

		launcher_pos_x, launcher_pos_y = world.getLauncherPos()

		self.pos_x = launcher_pos_x * world.DIST_PER_PIXEL_L
		self.pos_y = (480 - launcher_pos_y) * world.DIST_PER_PIXEL_H

		self.shape = world.canvas.create_oval(launcher_pos_x - self.radius, launcher_pos_y - self.radius, launcher_pos_x + self.radius, launcher_pos_y + self.radius, fill = "green")
		print("Shot created at: ", self.pos_x, self.pos_y, sep = ' ')

	def local_update(self, delta_t):

		#update coordinates with given method
		dx, dy, self.vel_x, self.vel_y = self.world.update(self.vel_x, self.vel_y, delta_t)

		self.pos_x += dx
		self.pos_y += dy

		print("Shot coordinates:", self.pos_x, self.pos_y, sep = ' ')
		print("Shot speed:", self.vel_x, self.vel_y, sep = ' ')

		#redraw shape with new coordinates
		self.world.canvas.move(self.shape, dx/self.world.DIST_PER_PIXEL_L, -dy/self.world.DIST_PER_PIXEL_H)

	def undraw_self(self):
		self.world.canvas.delete(self.shape)

class world_update_callback (threading.Thread):

	def __init__(self, shot_list):
		threading.Thread.__init__(self)
		self.shot_list = shot_list
		self.current_time = time.clock()

	def run(self):
		while True:
			if len(self.shot_list) > 0:
				delta_t = time.clock() - self.current_time

				for i in self.shot_list:
					i.local_update(delta_t)

					if i.pos_y < 0:
						i.undraw_self()
						self.shot_list.remove(i)
						print("Shot destroyed...")

			self.current_time = time.clock()
			time.sleep(.01)

class World:

	#root of window
	root = Tk()

	#Canvas setup - draws launcher
	canvas = Canvas(root, width = 640, height = 480)

	#starting cannon polygon corrdinates
	launcher_coords = [0,470,0,490,70,490,70,470]

	#initial cannon object - will be overwritten with rotations later
	cannon = canvas.create_polygon(tuple(launcher_coords), fill = "gray", outline = "black")

	cannon_angle = 0
	cannon_velocity = 0

	#Shots currently on the screen
	shots = []

	#Real life length of range is 250 meters
	#calculate the length per pixel
	DIST_PER_PIXEL_L = 120/640
	DIST_PER_PIXEL_H = 50/480

	#Change in time between updating positions of shots
	current_time = time.clock()
	delta_t = 0

	#variable to contain range
	r = StringVar()

	#label for range
	label_range = None

	#initiate display - pass in the method to update positions and velocities as update
	def __init__(self, update):
		
		self.update = update

		#Frame for sliders
		slider_frame = Frame(self.root)

		#Draw slider for angle
		angle_scale = Scale(slider_frame, orient = HORIZONTAL, from_ = 0, to = 90, label = "Angle", command = self.angle_slider_update)
		angle_scale.pack(side = LEFT)

		#Draw slider for velocity
		vel_scale = Scale(slider_frame, orient = HORIZONTAL, from_ = 0, to = 500, label = "Launch Velocity", command = self.vel_slider_update)
		vel_scale.pack(side = RIGHT)

		#Draw launch button
		launch_button = Button(slider_frame, text = "Fire!", command = self.launch_button_callback, padx = 60)
		launch_button.pack(side = BOTTOM)

		#range label setup
		self.label_range = Label(slider_frame, textvariable=self.r)
		self.r.set("Range: 0 meters")
		self.label_range.pack()

		#Pack slider frame
		slider_frame.pack(side = BOTTOM)

		#draw launcher body
		launcher_body = self.canvas.create_arc(-40, 440, 40, 530, start = 0, extent = 90, fill = "gray")

		#Send cannon arm to back
		self.canvas.tag_lower(self.cannon)

		#Pack canvas
		self.canvas.pack()
		
		#Start thread to calculate where shots are
		callback = world_update_callback(self.shots)
		callback.setDaemon(True)
		callback.start()

		#Start display loop
		self.root.mainloop()

	#note - canvas.delete(item) delets a certain item from the canvas.
	def angle_slider_update(self, val):
		self.canvas.delete(self.cannon)

		for i in range(0,8,2):
			rotx = 0
			roty = 0
			rotx, roty = self.rotate_coordinate(self.launcher_coords[i], self.launcher_coords[i+1], 0, 480, int(val) - int(self.cannon_angle))
			self.launcher_coords[i] = rotx
			self.launcher_coords[i+1] = roty

		self.cannon = self.canvas.create_polygon(tuple(self.launcher_coords), fill = "gray", outline = "black")

		self.canvas.tag_lower(self.cannon)

		self.cannon_angle = int(val)

		##update range
		launcher_pos_x, launcher_pos_y = self.getLauncherPos()

		y0 = (480 - launcher_pos_y) * self.DIST_PER_PIXEL_H

		r = self.calculate_range(self.cannon_velocity, val, y0)

		self.r.set("Rage: " + str(int(r)) + " meters")


	def vel_slider_update(self, val):
		self.cannon_velocity = int(val)/10

		##update range
		launcher_pos_x, launcher_pos_y = self.getLauncherPos()

		y0 = (480 - launcher_pos_y) * self.DIST_PER_PIXEL_H

		r = self.calculate_range(self.cannon_velocity, self.cannon_angle, y0)

		self.r.set("Rage: " + str(int(r)) + " meters")

		
	def launch_button_callback(self):
		if len(self.shots) < 11:
			vx, vy = self.calculate_vel_comp()
			self.shots.append(shot(vx, vy, self))
			print("FIRE!")
		

	def rotate_coordinate(self, x, y, xp, yp, theta):
		alpha = -math.radians(float(theta))
		rotx = xp + (x-xp)*math.cos(alpha) - (y-yp)*math.sin(alpha)
		roty = yp + (x-xp)*math.sin(alpha) + (y-yp)*math.cos(alpha)

		return (rotx, roty)

	def calculate_range(self, v, theta, y0):
		alpha = math.radians(float(theta))
		vf = float(v)
		r = (vf*math.cos(alpha))/(9.8) * ((vf*math.sin(alpha)) + (vf**2 * math.sin(alpha)**2 + 2 * 9.8 * y0)**.5)
		return r

	def calculate_vel_comp(self):
		alpha = math.radians(float(self.cannon_angle))
		vx = self.cannon_velocity * math.cos(alpha)
		vy = self.cannon_velocity * math.sin(alpha)
		return vx, vy

	def getLauncherPos(self):
		return (self.launcher_coords[4] + self.launcher_coords[6])/2, (self.launcher_coords[5] + self.launcher_coords[7])/2

#Method to update position - takes vel_x, vel_y, delta_t and returns delta_x , delta_y and a new vel_x and vel_y
def update(vel_x, vel_y, delta_t):
	pass
	return dx, dy, nvx, nvy

w = World(update)

