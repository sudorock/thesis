import pygame
from pygame import gfxdraw
import random
import time
import numpy as np


dt = float(input("Enter a value for dt (1 for default): "))
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
particle_size = 10
number_of_particles = 40
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

memory = np.zeros((10000, number_of_particles + 2, 3), dtype=object)  # store position and color in memory
frame = 0  # counter for history

rev_frame = 0  # iterator for reverse frame
# start_time = 0  # store time when 'f' is pressed
reverse_time = 0  # store time when 'r' is pressed

time_list = []  # stores time values in seconds
timer_counter = 0  # iterator for time_list
rr = 0  # flag to store index for time_list reversal when 'r' or 'h' is pressed

frame_rate = 0.03  # frame rate of display
time_elapsed = 0  # to store time elapsed for clock
display_flag = 0  # flag for display of particles according to frame rate

frame_time_ratio = 5.9  # number of program steps per minute

# number of particles in a certain state (occupation number)
occ_num_r = 0
# occ_num_r2 = 0
occ_num_b = 0
# occ_num_b2 = 0

interval = 12   # for calculating average value of actual number of processes
num_rr2bb = 0
num_bb2rr = 0
num_rr2bb_avg = 0


num_rr2bb_l = []
num_bb2rr_l = []

prev_time_counter = 0

# W list for r,r -> b,b
w_rr2bb = 0
w_rr2bb_l = []

# W list for b,b -> r,r
w_bb2rr = []

pause = False

running = True
pygame.init()
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Direction of Time')
screen.fill(background_color)
font = pygame.font.SysFont(None, 22, bold=True)


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

    s = (p2.x - p1.x) ** 2 + (p2.y - p1.y) ** 2  # square of distance between particles

    if s <= (p1.size + p2.size) ** 2 and s != 0:
        return True
    else:
        return False


# particle collision
def collide(p1, p2):
    global num_rr2bb
    
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

    p1_color = p1.color
    p2_color = p2.color
    color_change(p1, p2)
    if (p1_color == color1 and p2_color == color1) and (p1.color == color2 and p2.color == color2):
        num_rr2bb += 1
        # print(num_rr2bb," ", w_rr2bb)


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


def multiple_collision(c_particle, particles_f, c_count):
    for i, particle in enumerate(particles_f):
        if check_collision(c_particle, particle):
            c_count += multiple_collision(particle, particles_f[i + 1:], c_count)
    return c_count


def collider(t_iter_f):
    for i, particle in enumerate(particles):
        collision_count = 0
        for particle2 in particles:
            if check_collision(particle, particle2):
                collision_count += 1
                colliding_particle = particle2
                collision_count = multiple_collision(particle, particles[i + 1:], collision_count)
        if collision_count == 1:
            if mode == 1:
                t_iter_f = store(particle, colliding_particle, t_iter_f, 1)  # store velocities before collision
                collide(particle, colliding_particle)
                t_iter_f = store(particle, colliding_particle, t_iter_f, 0)  # store velocities after collision
            elif mode == 2:
                collide(particle, colliding_particle)
            elif mode == 3:
                table_check_reverse(colliding_particle, particle, t_iter_f)
    return t_iter_f


def move_and_display():
    if mode == 0:       # Initial display of particles
        for particle in particles:
            particle.display()
        memory_store()
    elif mode == 4:
        for k, p in enumerate(particles):
            if display_flag == 1:
                pygame.gfxdraw.aacircle(screen, memory[rev_frame, k, 0], memory[rev_frame, k, 1],
                                        particle_size, memory[rev_frame, k, 2])
                pygame.gfxdraw.filled_circle(screen, memory[rev_frame, k, 0], memory[rev_frame, k, 1],
                                             particle_size, memory[rev_frame, k, 2])
    else:
        for particle in particles:
            particle.move()
            particle.wall_bounce()
            if display_flag == 1:
                particle.display()


# reverse velocity
def reverse_velocity():
    for particle in particles:
        particle.v_x = -particle.v_x
        particle.v_y = -particle.v_y


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
    if mode == 1:       # forward time
        time_list.append(int(counter/frame_time_ratio))
        timer = font.render(str(time_list[counter]), True, green, background_color)
        screen.blit(font.render("Time: ", True, white, background_color), (width - 220, 20))
        screen.blit(timer, (width - 110, 20))
        counter = counter + 1
    elif mode == 2 or mode == 3 or mode == 4:       # reverse time
        counter = counter - 1
        if counter > -1:
            reverse_timer = font.render(str(time_list[counter]), True, red, background_color)
            screen.blit(reverse_timer, (width - 60, 20))
            screen.blit(font.render("Time: ", True, white, background_color), (width - 220, 20))
            screen.blit(font.render(str(time_list[rr]), True, green, background_color), (width - 110, 20))
        else:
            return counter
    return counter


def memory_store():
    if mode == 1:
        for i, pa in enumerate(particles):
            memory[frame, i, 0] = int(pa.x)
            memory[frame, i, 1] = int(pa.y)
            memory[frame, i, 2] = pa.color


def table_check_reverse(colliding_particle, particle, t_iter_f):
    global num_rr2bb
    collision_check = [colliding_particle.x - particle.x,
                       colliding_particle.y - particle.y,
                       particle.v_x,
                       particle.v_y,
                       colliding_particle.v_x,
                       colliding_particle.v_y]
    for k in range(0, t_iter_f):
        table_check = [reverse_table[k, 0],
                       reverse_table[k, 1],
                       reverse_table[k, 6],
                       reverse_table[k, 7],
                       reverse_table[k, 8],
                       reverse_table[k, 9]]
        if np.array_equal(collision_check, table_check):
            particle.v_x = reverse_table[k, 2]
            particle.v_y = reverse_table[k, 3]
            colliding_particle.v_x = reverse_table[k, 4]
            colliding_particle.v_y = reverse_table[k, 5]
            # color stuff
            p1_color = particle.color
            p2_color = colliding_particle.color
            color_change(particle, colliding_particle)
            if (p1_color == color1 and p2_color == color1) and (particle.color == color2 and colliding_particle.color == color2):
                num_rr2bb += 1
                # print(num_rr2bb, " ", w_rr2bb)
            break


def frame_display(time_elapsed_f):

    if time.time() - time_elapsed_f >= frame_rate:
        if time.time() - time_elapsed_f <= frame_rate + 1:
            screen.fill(background_color)
            time_elapsed_f = time.time()
            return 1, time_elapsed_f
        else:
            return 0, time_elapsed_f
    else:
        return 0, time_elapsed_f


# mem = []


def display_sza():
    w_avg = 0.0002      # estimated from a preliminary long run
    # Actual number of processes
    num_actual = font.render(str(round(num_rr2bb_avg, 3)), True, green, background_color)
    screen.blit(font.render("Actual(r,r|b,b): ", True, white, background_color), (width - 220, 40))
    screen.blit(num_actual, (width - 80, 40))
    # Expected number of processes
    expected = w_avg * (occ_num_r ** 2)
    num_expected = font.render(str(round(expected, 3)), True, green, background_color)
    screen.blit(font.render("W(r,r|b,b)*Nr*Nr: ", True, white, background_color), (width - 220, 60))
    screen.blit(num_expected, (width - 80, 60))
    # Number of red and Number of blue particles
    screen.blit(font.render("Nr: ", True, white, background_color), (width - 220, 80))
    n_r = font.render(str(occ_num_r), True, green, background_color)
    screen.blit(n_r, (width - 80, 80))
    screen.blit(font.render("Nb: ", True, white, background_color), (width - 220, 100))
    n_b = font.render(str(occ_num_b), True, green, background_color)
    screen.blit(n_b, (width - 80, 100))

    # print(num_rr2bb_avg, " ", expected)
    # mem.append(expected-num_rr2bb_avg)


def actual_processes():
    global num_rr2bb_avg, prev_time_counter
    if mode == 1:
        if timer_counter - prev_time_counter == interval:
            num_rr2bb_avg = sum(num_rr2bb_l[-interval:]) / interval
            prev_time_counter = timer_counter
    else:
        if prev_time_counter - timer_counter == interval:
            num_rr2bb_avg = sum(num_rr2bb_l[-interval:]) / interval
            prev_time_counter = timer_counter


def pause_program(pause_f):
    while pause_f:
        for pause_event in pygame.event.get():
            if pause_event.type == pygame.KEYUP and pause_event.key == pygame.K_p:
                return False


# initialize particles
p_iter = 1
w = 1
while p_iter <= number_of_particles:
    for z in range(1, int(number_of_particles ** 0.5) + 1):
        x_init = 4 * z * particle_size + particle_size
        y_init = 4 * w * particle_size + particle_size
        v_x_init = v_initial * random.randint(0, 5)
        v_y_init = v_initial * random.randint(0, 5)
        particle_init = Particle(x_init, y_init, v_x_init, v_y_init, particle_size, color1)
        particles.append(particle_init)
        p_iter = p_iter + 1
    w += 1

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            pause = False
            if event.key == pygame.K_f:  # press 'f' for forward motion
                mode = 1
                # start_time = time_elapsed = time.time()
            if event.key == pygame.K_i:  # press 'i' for reversing velocities
                mode = 2
                reverse_once = 0
                rr = timer_counter - 1  # index at which time is reversed
                reverse_time = time.time()
            if event.key == pygame.K_d:  # press 'd' for reversing motion from table
                mode = 3
                reverse_once = 0
                rr = timer_counter - 1  # index at which time is reversed
                reverse_time = time.time()
            if event.key == pygame.K_m:  # press 'm' for reversing motion from memory
                mode = 4
                rev_frame = frame - 1
                rr = timer_counter - 1  # index at which time is reversed
                reverse_time = time.time()
        if event.type == pygame.KEYUP and event.key == pygame.K_p:
            pause = True

    pause = pause_program(pause)

    screen.fill(background_color)

    # reset values at every program step
    num_rr2bb = 0
    num_bb2rr = 0
    occ_num_r = 0
    occ_num_b = 0

    # display_flag, time_elapsed = frame_display(time_elapsed)     # refresh screen with background for every frame
    display_flag = 1
    timer_counter = display_time(timer_counter)  # display time

    if mode != 4 and timer_counter < 0:  # stop animation when reverse time reaches 0
        pygame.time.wait(5000)
        running = False
        break
    elif mode == 4 and rev_frame == -1:
        pygame.time.wait(5000)
        running = False
        break

    if t_iter > len(reverse_table) - 10:  # break when reverse table length is about to be reached
        break

    if mode == 2 or mode == 3:     # reverse velocities
        if reverse_once == 0:
            reverse_velocity()
            reverse_once = 1

    t_iter = collider(t_iter)

    # Estimate Actual processes for every interval
    actual_processes()

    # Estimate occupation numbers at every frame
    for Particle in particles:
        if Particle.color == color1:
            occ_num_r += 1
        elif Particle.color == color2:
            occ_num_b += 1

    num_rr2bb_l.append(num_rr2bb)
    w_rr2bb = num_rr2bb/occ_num_r**2
    w_rr2bb_l.append(w_rr2bb)

    # print(timer_counter, "W: :",w_rr2bb, "OccNum: ", occ_num_r)

    display_sza()
    move_and_display()  # move_and_display(particles)
    memory_store()  # store positions in history table for reverse display through memory

    if mode == 1:
        frame = frame + 1
    elif mode == 4:
        rev_frame = rev_frame - 1

    pygame.display.flip()

# print(sum(w_rr2bb_l))
# print(time_list[-1])
# print("Avg W: ", sum(w_rr2bb_l)/timer_counter)
