import pygame
from pygame import gfxdraw
import random
import time
import numpy as np

dt = float(input("Enter a value for dt (0.01 for default): "))
color_factor = float(input("Enter a value for Colour Change Determinancy (0 - 100): ")) / 100

v_initial = float(input("Enter an initial value for velocity: "))  # initial velocity of particle
background_color = (0, 0, 0)
(width, height) = (1300, 700)
red = (255, 0, 0)
green = (0, 255, 0)
color1 = (255, 0, 0)
color2 = (0, 75, 255)
black = (0, 0, 0)
grey = (255, 255, 0)
white = (255, 255, 255)
thickness = 1  # thickness of particle
particle_size = 15
number_of_particles = 30
particles = []

# deterministic reverse velocity reverse_table
reverse_table = np.zeros((10000, 10))  # reverse_table to store velocities
t_iter = 0  # iterator for the reverse_table

mode = 0
reverse = 0  # flag for reverse motion by reversing direction of velocities
forward = 0  # flag for forward motion
hist = 0  # flag for reverse motion from memory
reverse_once = 0  # flag to stop reversing velocities every time it enters reverse motion for loop
deterministic = 0  # use deterministic reverse_table for reversal

# collision_count = 0  # counter for number of collisions

memory = np.zeros((10000, number_of_particles, 3), dtype=object)  # store position and color in memory
frame = 0  # counter for history

rev_frame = 0  # iterator for reverse frame
start_time = 0  # store time when 'f' is pressed
reverse_time = 0  # store time when 'r' is pressed

time_list = []  # stores time values in seconds
timer_counter = 0  # iterator for time_list
rr = 0  # flag to store index for time_list reversal when 'r' or 'h' is pressed

frame_rate = 0.03  # frame rate of display
time_elapsed = 0  # to store time elapsed for clock
display = 0  # flag for display of particles according to frame rate

running = True
pygame.init()
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Direction of Time')
screen.fill(background_color)
font = pygame.font.SysFont(None, 24, bold=True)


class Particle:

    def __init__(self, x, y, v_x, v_y, size, color):
        self.x = x
        self.y = y
        self.v_x = v_x
        self.v_y = v_y
        self.size = size
        self.color = color
        self.thickness = 1

    def display(self):
        pygame.gfxdraw.aacircle(screen, int(self.x), int(self.y), self.size, self.color)
        pygame.gfxdraw.filled_circle(screen, int(self.x), int(self.y), self.size, self.color)

    def wall_bounce(self):

        # collision with right wall
        if self.x >= width - self.size:  # if particle has moved beyond right wall
            self.x = 2 * (width - self.size) - self.x
            self.v_x = -self.v_x  # reverse velocity x-direction

        # collision with left wall
        if self.x <= self.size:  # if particle has moved beyond left wall
            self.x = 2 * self.size - self.x
            self.v_x = -self.v_x  # reverse velocity x-direction

        # collision with bottom wall
        if self.y >= height - self.size:  # if particle has moved beyond bottom wall
            self.y = 2 * (height - self.size) - self.y  #
            self.v_y = -self.v_y  # reverse velocity y-direction

        # collision with top wall
        if self.y <= self.size:  # if particle has moved beyond top wall
            self.y = 2 * self.size - self.y
            self.v_y = -self.v_y  # reverse velocity y-direction

    def move(self):
        self.x = self.x + self.v_x * dt
        self.y = self.y + self.v_y * dt


# check if the particles collided
def check_collision(p1, p2):
    s = (p2.x - p1.x) ** 2 + (p2.y - p1.y) ** 2  # s = square of distance between particles

    if s <= (p1.size + p2.size) ** 2 and s != 0:
        return True
    else:
        return False


# particle collision
def collide(p1, p2):
    s = (p2.x - p1.x) ** 2 + (p2.y - p1.y) ** 2  # s = square of distance between particles
    e1 = p2.x - p1.x
    e2 = p2.y - p1.y
    a = e1 * (p1.v_x - p2.v_x) + e2 * (p1.v_y - p2.v_y)  # numerator of lamda

    if a >= 0:
        lamda = a / s
        # new velocities after collision
        p1.v_x = int(p1.v_x - lamda * e1)
        p1.v_y = int(p1.v_y - lamda * e2)
        p2.v_x = int(p2.v_x + lamda * e1)
        p2.v_y = int(p2.v_y + lamda * e2)

    color_change(p1, p2)


# particle color change after collision
def color_change(p1, p2):
    if p2.color == color1 and p1.color == color1:
        randomizer = random.random()
        if randomizer <= color_factor:
            p2.color = color2
            p1.color = color2

    elif p2.color == color2 and p1.color == color2:
        randomizer = random.random()
        if randomizer <= color_factor:
            p2.color = color1
            p1.color = color1


def collider(particles_f, mode_f, t_iter_f):
    collision_count = 0
    for i, particle1 in enumerate(particles_f):
        for particle2 in particles[i + 1:]:
            if check_collision(particle1, particle2):
                collision_count = collision_count + 1
                colliding_particle = particle2
                for particle3 in particles[i + 1:]:
                    if check_collision(particle2, particle3):
                        collision_count = collision_count + 1
                        for particle4 in particles[i + 1:]:
                            if check_collision(particle3, particle4):
                                collision_count = collision_count + 1
                                for particle5 in particles[i + 1:]:
                                    if check_collision(particle4, particle5):
                                        collision_count = collision_count + 1
                                        for particle6 in particles[i + 1:]:
                                            if check_collision(particle5, particle6):
                                                collision_count = collision_count + 1
        if collision_count == 1:
            if mode_f == 1:
                t_iter_f = store(particle1, colliding_particle, t_iter_f, 1)  # store velocities before collision
                collide(particle1, colliding_particle)
                t_iter_f = store(particle1, colliding_particle, t_iter_f, 0)  # store velocities after collision
            elif mode_f == 2:
                collide(particle1, colliding_particle)
            elif mode_f == 3:
                table_check_reverse(colliding_particle, particle1, t_iter_f)
        collision_count = 0
    return t_iter_f


def move_and_display(particles_f):
        for particle_f in particles_f:
            particle_f.move()
            particle_f.wall_bounce()
            if display == 1:
                particle_f.display()


# reverse velocity
def reverse_velocity(particles_f):
    for p in particles_f:
        p.v_x = -p.v_x
        p.v_y = -p.v_y


# store velocities before and after collision
def store(p1, p2, t_iterator, before):
    if before == 1:
        reverse_table[t_iterator, 2] = -int(p1.v_x)
        reverse_table[t_iterator, 3] = -int(p1.v_y)
        reverse_table[t_iterator, 4] = -int(p2.v_x)
        reverse_table[t_iterator, 5] = -int(p2.v_y)
        reverse_table[t_iterator, 0] = p2.x - p1.x
        reverse_table[t_iterator, 1] = p2.y - p1.y

    elif before == 0:
        reverse_table[t_iterator, 6] = -int(p1.v_x)
        reverse_table[t_iterator, 7] = -int(p1.v_y)
        reverse_table[t_iterator, 8] = -int(p2.v_x)
        reverse_table[t_iterator, 9] = -int(p2.v_y)
        t_iterator = t_iterator + 1

    return t_iterator


def display_time(counter):
    # forward time
    if mode == 1:
        time_list.append(int(time.time() - start_time))
        timer = font.render(str(time_list[counter]), True, green, background_color)
        screen.blit(font.render("Time: ", True, white, background_color), (width - 150, 20))
        screen.blit(timer, (width - 95, 20))
        counter = counter + 1
    # reverse time
    else:
        counter = counter - 1
        if counter > -1:
            reverse_timer = font.render(str(time_list[counter]), True, red, background_color)
            screen.blit(reverse_timer, (width - 65, 20))
            screen.blit(font.render("Time: ", True, white, background_color), (width - 150, 20))
            screen.blit(font.render(str(time_list[rr]), True, green, background_color), (width - 95, 20))
        else:
            return counter
    return counter


def memory_store(frame_f, particles_f):

    for z in range(0, number_of_particles):
        memory[frame_f, z, 0] = int(particles_f[z].x)
        memory[frame_f, z, 1] = int(particles_f[z].y)
        memory[frame_f, z, 2] = particles_f[z].color


def table_check_reverse(colliding_particle_f, particle_f, t_iter_f):

    collision_check = [colliding_particle_f.x - particle_f.x,
                       colliding_particle_f.y - particle_f.y,
                       particle_f.v_x,
                       particle_f.v_y,
                       colliding_particle_f.v_x,
                       colliding_particle_f.v_y]

    for k in range(0, t_iter_f):
        table_check = [reverse_table[k, 0],
                       reverse_table[k, 1],
                       reverse_table[k, 6],
                       reverse_table[k, 7],
                       reverse_table[k, 8],
                       reverse_table[k, 9]]
        if np.array_equal(collision_check, table_check):
            particle_f.v_x = reverse_table[k, 2]
            particle_f.v_y = reverse_table[k, 3]
            colliding_particle_f.v_x = reverse_table[k, 4]
            colliding_particle_f.v_y = reverse_table[k, 5]
            color_change(particle_f, colliding_particle_f)
            break


# initialize particles
p_iter = 1
k = 1
while p_iter <= number_of_particles:
    for z in range(1, int(number_of_particles ** 0.5) + 1):
        x_init = 4 * z * particle_size + particle_size
        y_init = 4 * k * particle_size + particle_size
        v_x_init = v_initial * random.randint(0, 5)
        v_y_init = v_initial * random.randint(0, 5)
        particle = Particle(x_init, y_init, v_x_init, v_y_init, particle_size, color1)
        particles.append(particle)
        p_iter = p_iter + 1
    k = k + 1

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_f:  # press 'f' for forward motion
            mode = 1
            frame = 1
            start_time = time_elapsed = time.time()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:  # press 'r' for reversing velocities
            mode = 2
            reverse_once = 0
            rr = timer_counter - 1  # index at which time is reversed
            reverse_time = time.time()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_d:  # press 'd' for reversing motion from table
            mode = 3
            reverse_once = 0
            rr = timer_counter - 1  # index at which time is reversed
            reverse_time = time.time()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_m:  # press 'h' for reversing motion from memory
            mode = 4
            rev_frame = frame - 1
            rr = timer_counter - 1  # index at which time is reversed
            reverse_time = time.time()

    # refresh screen with background for every frame
    if time.time() - time_elapsed >= frame_rate:
        if time.time() - time_elapsed <= frame_rate + 1:
            screen.fill(background_color)
            display = 1
            time_elapsed = time.time()
        else:
            display = 0
    else:
        display = 0

    # Initial display of particles
    if mode == 0:
        for particle in particles:
            particle.display()
        memory_store(frame, particles)

    elif mode == 1:     # forward motion
        timer_counter = display_time(mode, timer_counter)       # display time

        if t_iter > len(reverse_table) - 10:  # break when reverse table length is about to be reached
            break

        t_iter = collider(particles, mode, t_iter)
        move_and_display(particles)
        memory_store(frame, particles)   # store positions in history table for reverse display through memory

    elif mode == 2:     # reverse velocities

        timer_counter = display_time(mode, timer_counter)       # display time

        if timer_counter < 0:    # stop animation when reverse time reaches 0
            pygame.time.wait(3000)
            running = False
            break

        if reverse_once == 0:
            reverse_velocity(particles)
            reverse_once = 1

        t_iter = collider(particles, mode, t_iter)
        move_and_display(particles)

    elif mode == 3:     # deterministic reverse with reverse_table
        timer_counter = display_time(mode, timer_counter)       # display time

        if timer_counter < 0:       # stop animation when reverse time reaches 0
            pygame.time.wait(3000)
            running = False
            break

        if reverse_once == 0:
            reverse_velocity(particles)
            reverse_once = 1

        t_iter = collider(particles, mode, t_iter)
        move_and_display(particles)

    else:       # reverse motion using memory
        timer_counter = display_time(mode, timer_counter)       # display time

        if rev_frame >= 0:
            for k in range(0, number_of_particles):
                if display == 1:
                    pygame.gfxdraw.aacircle(screen, memory[rev_frame, k, 0], memory[rev_frame, k, 1],
                                            particle_size, memory[rev_frame, k, 2])
                    pygame.gfxdraw.filled_circle(screen, memory[rev_frame, k, 0], memory[rev_frame, k, 1],
                                                 particle_size, memory[rev_frame, k, 2])
        else:
            pygame.time.wait(3000)
            running = False
            break

    if hist == 0:
        frame = frame + 1
    elif hist == 1:
        rev_frame = rev_frame - 1

    pygame.display.flip()


# 3. Input output
# 4. Stossahalantz
# 5. Multiple collision function
# Wall bounce optimize
# 6. Annotate code
# 7. Frame rate
# Historical reverse initial position error/time
