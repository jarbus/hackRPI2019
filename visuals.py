import pyglet
import time
from pyglet.gl import *

# vis = pyglet.window.Window()

# @vis.event
# def on_draw():
#     glClear(GL_COLOR_BUFFER_BIT)
#     glBegin(GL_LINES)
#     glVertex3f(0.0,0.0,0)
#     glVertex3f(630.0,470.0,0)
#     glEnd()

# pyglet.app.run()

def update_frame(x, y):
	global i
	if(i < len(frames_data)):
		i += 1
	else:
		i = 0

def play_graphics(win_x, win_y, max_x, max_y, fd):
	global frames_data
	global i
	global x_scale
	global y_scale
	global w

	frames_data = fd
	i = 0

	x_scale = (win_x / max_x)
	y_scale = (win_y / max_y)

	w = pyglet.window.Window()
	@w.event
	def on_draw():
		glClear(GL_COLOR_BUFFER_BIT)

		if(i >= len(frames_data)):
			return

		current_frame = frames_data[i]
		for o in current_frame:
			x = x_scale * o[0]
			y = y_scale * o[1]
			o_type = o[2]

			if (o_type == "droid"):
				pyglet.graphics.draw(4, GL_QUADS, ('v2f', [x, y, x + x_scale, y, x, y + y_scale, x + x_scale, y + y_scale]))
			elif (o_type == "basecamp"):
				pyglet.graphics.draw(3, GL_TRIANGLES, ('v2f', [x, y, x + (x_scale/2), y + y_scale, x + x_scale, y]))


		time.sleep(1)


		# pyglet.graphics.draw_indexed(4, pyglet.gl.GL_TRIANGLES,
		# 	[0, 1, 2, 0, 2, 3],
		# 		('v2i', (100, 100,
		# 		100, 50,
		# 		200, 250,
		# 		300, 150)
		# 	)
		# )

		# glClear(GL_COLOR_BUFFER_BIT)
		# glBegin(GL_LINES)
		# glVertex3f(0.0,0.0,0)
		# glVertex3f(630.0,470.0,0)
		# glEnd()

	pyglet.clock.schedule(update_frame, 0)
	pyglet.app.run()


play_graphics(640, 480, 64, 48, [[(18,24,"droid"), (7,21,"droid"), (44,44,"basecamp")], [(9,12,"droid"), (36,42,"droid"), (44,44,"basecamp")]])