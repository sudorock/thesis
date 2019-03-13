import pygame
from pygame import gfxdraw
import random
import time
import numpy as np

dt = float(input("Enter a value for dt (0.01 for default): "))
color_factor = 100  #float(input("Enter a value for Colour Change Determinancy (0 - 100): ")) / 100
corner = int(input("Enter 1 to start in Corner and if otherwise 0: "))

v_initial = float(input("Enter an initial value for velocity: "))  # initial velocity of particle
# background_color = (255, 255, 255)
background_color = (0, 0, 0)
(width, height) = (1300, 700)
red = (255, 0, 0)
green = (0, 255, 0)
# color1 = (255, 165, 80)  # orange
# color2 = (0, 0, 255)  # blue
color1 = (255, 0, 0)  # orange
color2 = (0, 75, 255)  # blue
black = (0, 0, 0)
grey = (255,255,0)
white = (255, 255, 255)
thickness = 1  # thickness of particle
particle_size = 15
number_of_particles = 30
particles = []

# deterministic reverse velocity reverse_table
reverse_table = np.zeros((10000, 10))  # reverse_table to store velocities
t_iter = 0  # iterator for the reverse_table

reverse = 0  # flag for reverse motion by reversing direction of velocities
forward = 0  # flag for forward motion
hist = 0  # flag for reverse motion from memory
reverse_once = 0  # flag to stop reversing velocities every time it enters reverse motion for loop
deterministic = 0  # use deterministic reverse_table for reversal

collision_count = 0  # counter for number of collisions

history = {}  # store position and color in memory
history_det = {}
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
        # pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size, self.thickness)
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
        # print("Position and Velocity  x: ", self.x, " y: ", self.y, " v_x: ", self.v_x, " v_y: ", self.v_y)
        self.x = self.x + self.v_x * dt
        self.y = self.y + self.v_y * dt


# check if the particles collided
def check_collision(p1, p2):
    s = (p2.x - p1.x) ** 2 + (p2.y - p1.y) ** 2  # s = square of distance between particles

    if s <= (p1.size + p2.size) ** 2 and s != 0:
        # print("Check Collision s: ", s, " Rx: ", (p1.x - p2.x), " Ry: ", (p1.y - p2.y))
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
        # print("Check Collision inside lambda s: ", s, " Rx: ", (p1.x - p2.x), " Ry: ", (p1.y - p2.y))
        # print("\n Before Lambda Rx: ", p1.x - p2.x, " Ry: ", p1.y - p2.y, " v1_x: ", p1.v_x, " v1_y: ", p1.v_y, " v2_x: ", p2.v_x, " v2_y: ", p2.v_y)
        # new velocities after collision
        p1.v_x = int(p1.v_x - lamda * e1)
        p1.v_y = int(p1.v_y - lamda * e2)
        p2.v_x = int(p2.v_x + lamda * e1)
        p2.v_y = int(p2.v_y + lamda * e2)
        # p1.v_x = p1.v_x - lamda * e1
        # p1.v_y = p1.v_y - lamda * e2
        # p2.v_x = p2.v_x + lamda * e1
        # p2.v_y = p2.v_y + lamda * e2
        # print("\n After Lambda Rx: ", p1.x - p2.x, " Ry: ", p1.y - p2.y, " v1_x: ", p1.v_x, " v1_y: ", p1.v_y, " v2_x: ", p2.v_x, " v2_y: ", p2.v_y)
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


# reverse velocity
def reverse_velocity(p):
    p.v_x = -p.v_x
    p.v_y = -p.v_y
    # print("Reverse Velocity point: x: ", p.x, " y: ", p.y, " v_x: ", p.v_x, " v_y: ", p.v_y)


# store velocities before and after collision
def store(p1, p2, t_iterator, before):
    if before == 1:
        # checker = [int(abs(particle2.x - particle.x)), int(abs(particle2.y - particle.y)),
        #            int(particle.v_x), int(particle.v_y), int(particle2.v_x), int(particle2.v_y)]
        # velocities before colllision
        reverse_table[t_iterator, 2] = -int(p1.v_x)
        reverse_table[t_iterator, 3] = -int(p1.v_y)
        reverse_table[t_iterator, 4] = -int(p2.v_x)
        reverse_table[t_iterator, 5] = -int(p2.v_y)
        # Difference of positions
        # reverse_table[t_iterator, 0] = int(abs(p2.x - p1.x))
        # reverse_table[t_iterator, 1] = int(abs(p2.y - p1.y))
        # reverse_table[t_iterator, 0] = abs(p2.x - p1.x)
        # reverse_table[t_iterator, 1] = abs(p2.y - p1.y)
        reverse_table[t_iterator, 0] = p2.x - p1.x
        reverse_table[t_iterator, 1] = p2.y - p1.y


    elif before == 0:
        reverse_table[t_iterator, 6] = -int(p1.v_x)
        reverse_table[t_iterator, 7] = -int(p1.v_y)
        reverse_table[t_iterator, 8] = -int(p2.v_x)
        reverse_table[t_iterator, 9] = -int(p2.v_y)
        t_iterator = t_iterator + 1

    return t_iterator


def display_time(fwd, counter):
    # forward time
    if fwd == 1:
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
            # screen.blit(font.render("Time: " + str(time_list[rr]), True, red, background_color), (width - 150, 20))
            screen.blit(font.render("Time: ", True, white, background_color), (width - 150, 20))
            screen.blit(font.render(str(time_list[rr]), True, green, background_color), (width - 95, 20))
        else:
            return counter
    return counter

pos = {}
c_count = 0
c_count2 = 0
disp_once = 0
total_collision_count = 0
# initialize particles
if corner == 1:
    j = 1
    k = 1
    while j <= number_of_particles:
        for z in range(1, int(number_of_particles ** 0.5) + 1):
            x_init = 4 * z * particle_size + particle_size  #* int((random.random() - 0.5))
            y_init = 4 * k * particle_size + particle_size  #* int((random.random() - 0.5))
            # x_init = z * particle_size + particle_size  # * int((random.random() - 0.5))
            # y_init = 1.5*k * particle_size + particle_size
            # v_x_init = v_initial
            # v_y_init = 0
            v_x_init = v_initial * random.randint(0, 5)
            v_y_init = v_initial * random.randint(0, 5)
            pos[j] = (x_init, y_init)
            # print("Initial Position: ", j, " ", pos[j])
            particle = Particle(x_init, y_init, v_x_init, v_y_init, particle_size, color1)
            particles.append(particle)
            j = j + 1
        k = k + 1
else:
    for i in range(1, number_of_particles + 1):
        x_init = 2 * particle_size + (width - 4 * particle_size) * random.random()
        y_init = 2 * particle_size - (height - 4 * particle_size) * random.random()
        v_x_init = v_initial * (random.random() - 0.5)
        v_y_init = v_initial * (random.random() - 0.5)
        particle = Particle(x_init, y_init, v_x_init, v_y_init, particle_size, color1)
        particles.append(particle)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_f:  # press 'f' for forward motion
            forward = 1
            reverse = 0
            frame = 0
            start_time = time_elapsed = time.time()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:  # press 'r' for reversing velocities
            reverse = 1
            forward = 0
            reverse_once = 0
            rr = timer_counter - 1  # index at which time is reversed
            reverse_time = time.time()
            # print("Velocity reversed: \n \n")
        if event.type == pygame.KEYDOWN and event.key == pygame.K_h:  # press 'h' for reversing motion from memory
            reverse = 0
            forward = 0
            hist = 1
            rev_frame = frame - 1
            rr = timer_counter - 1  # index at which time is reversed
            reverse_time = time.time()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_d:  # press 'd' for reversing motion from table
            reverse = 0
            forward = 0
            hist = 0
            reverse_once = 0
            deterministic = 1
            print("Velocity reversed \n")
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
    if forward == 0 and reverse == 0 and hist == 0 and deterministic == 0:
        for particle in particles:
            particle.display()

    # if t_iter % 10 == 0 and t_iter != 0:
    #     reverse_once = 0
    #     reverse = 1
    #     forward = 0

    # forward motion
    if forward == 1 and reverse == 0 and hist == 0:

        # display time
        timer_counter = display_time(forward, timer_counter)

        if t_iter > len(reverse_table) - 10:  # break when reverse table length is about to be reached
            break

        for i, particle in enumerate(particles):
            for particle2 in particles[i + 1:]:
                if check_collision(particle, particle2):
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
                t_iter = store(particle, colliding_particle, t_iter, 1)  # store velocities before collision
                collide(particle, colliding_particle)
                t_iter = store(particle, colliding_particle, t_iter, 0)  # store velocities before collision
                collision_data = [colliding_particle.x - particle.x,
                                   colliding_particle.y - particle.y,
                                   particle.v_x, particle.v_y, colliding_particle.v_x,
                                   colliding_particle.v_y]
                print(t_iter-1, " Collision recorded ", "Rec Table data: ", reverse_table[t_iter-1], "Actual data: ", collision_data)
                # print(t_iter)
            elif collision_count > 1:
                print("------Multiple collision:", collision_count)

            collision_count = 0
            particle.move()
            particle.wall_bounce()
            if display == 1:
                particle.display()

        # store positions in history table for reverse display through memory
        # for z in range(0, number_of_particles + 1):
        #     history[frame, z, 0] = particles[z].x
        #     history[frame, z, 1] = particles[z].y
        #     history[frame, z, 2] = particles[z].color

    # reverse velocities
    if reverse == 1 and forward == 0 and hist == 0:

        # display time
        timer_counter = display_time(forward, timer_counter)

        # if t_iter > len(reverse_table) - 10:  # break when reverse table length is about to be reached
        #     break

        # stop animation when reverse time reaches 0
        if (time.time() - reverse_time == reverse_time - start_time) or timer_counter == -1:
            pygame.time.wait(10000)
            running = False
            break

        if reverse_once == 0:
            for particle in particles:
                reverse_velocity(particle)
                reverse_once = 1

        for i, particle in enumerate(particles):
            for particle2 in particles[i + 1:]:
                if check_collision(particle, particle2):
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
                # t_iter = store(particle, colliding_particle, t_iter, 1)  # store velocities before collision
                collide(particle, colliding_particle)
                # t_iter = store(particle, colliding_particle, t_iter, 0)  # store velocities before collision
                # print(t_iter)
            collision_count = 0
            particle.move()
            particle.wall_bounce()
            if display == 1:
                particle.display()

    # reverse motion using memory
    if reverse == 0 and forward == 0 and hist == 1:

        # display time
        timer_counter = display_time(forward, timer_counter)

        # stop animation when reverse flag becomes 0 or when index for history becomes 0
        if timer_counter == -1 or rev_frame == -1:
            pygame.time.wait(10000)
            running = False

        for k in range(0, number_of_particles + 1):
            if display == 1:
                pygame.draw.circle(screen, history[rev_frame, k, 2],
                                   (int(history[rev_frame, k, 0]), int(history[rev_frame, k, 1])),
                                   particle_size, thickness)

    # deterministic reverse with reverse_table
    if forward == 0 and reverse == 0 and hist == 0 and deterministic == 1:

        # # display time
        timer_counter = display_time(forward, timer_counter)
        #
        # # stop animation when reverse time reaches 0

        # time.time() - reverse_time == reverse_time - start_time) or
        if timer_counter < 0:
            # for particle in particles:
                # print("Final Position: ", particle.x, " ", particle.y)
            pygame.time.wait(3000)
            running = False
            break

        if reverse_once == 0:
            for particle in particles:
                reverse_velocity(particle)
                reverse_once = 1

        for i, particle in enumerate(particles):
            for particle2 in particles[i + 1:]:
                if check_collision(particle, particle2):
                    # compare with reverse_table and change velocities
                    collision_count = collision_count + 1
                    colliding_particle = particle2
                    for particle3 in particles[i + 1:]:
                        if check_collision(particle2, particle3):
                            collision_count = collision_count + 1
                            for particle4 in particles[i + 1:]:
                                if check_collision(particle3, particle4):
                                    collision_count = collision_count + 1
            if collision_count == 1:
                # collision_check = [int(particle.v_x), int(particle.v_y), int(particle2.v_x), int(particle2.v_y)]
                collision_check = [colliding_particle.x - particle.x,
                                   colliding_particle.y - particle.y,
                                   particle.v_x, particle.v_y, colliding_particle.v_x,
                                   colliding_particle.v_y]
                # collision_check = [int(abs(colliding_particle.x - particle.x)), int(abs(colliding_particle.y - particle.y)),
                #                    int(particle.v_x), int(particle.v_y), int(colliding_particle.v_x), int(colliding_particle.v_y)]
                c_count += 1

                for k in range(0, t_iter):
                    # table_check1 = [reverse_table[k, 6], reverse_table[k, 7],
                    #                 reverse_table[k, 8], reverse_table[k, 9]]
                    # table_check2 = [reverse_table[k, 2], reverse_table[k, 3],
                    #                 reverse_table[k, 4], reverse_table[k, 5]]
                    table_check1 = [reverse_table[k, 0], reverse_table[k, 1], reverse_table[k, 6], reverse_table[k, 7],
                                    reverse_table[k, 8], reverse_table[k, 9]]
                    table_check2 = [reverse_table[k, 0], reverse_table[k, 1], reverse_table[k, 2], reverse_table[k, 3],
                                    reverse_table[k, 4], reverse_table[k, 5]]
                    # print(collision_check, " ", table_check1, " ", table_check2)
                    # if there is a corresponding row for collision with v1 and v2, then change to w1 and w2
                    if np.array_equal(collision_check, table_check1):
                        particle.v_x           = reverse_table[k, 2]
                        particle.v_y           = reverse_table[k, 3]
                        colliding_particle.v_x = reverse_table[k, 4]
                        colliding_particle.v_y = reverse_table[k, 5]
                        color_change(particle, colliding_particle)
                        c_count2 += 1
                        print(k, " Collision found  ", "Actual data: ", collision_check, "Table data: ", table_check1,
                              "reversed to:", table_check2)
                        break

                    # if there is a corresponding row for collision with w1 and w2, then change to v1 and v2
                    # elif np.array_equal(collision_check, table_check2):
                    #     particle.v_x = reverse_table[k, 6]
                    #     particle.v_y = reverse_table[k, 7]
                    #     colliding_particle.v_x = reverse_table[k, 8]
                    #     colliding_particle.v_y = reverse_table[k, 9]
                    #     color_change(particle, colliding_particle)
                    #     c_count2 += 1
                    #     print("Collision found 2:  ", "Actual data: ", collision_check, "Table data: ", table_check2, "reversed to:", table_check1)

                if disp_once != c_count - c_count2:
                    # screen.fill(background_color)
                    # colliding_particle.display()
                    # colliding_particle.display()
                    # pygame.time.wait(5000)
                    print("c_count - c_count2:",c_count - c_count2, "c_count:", c_count, "c_count2:", c_count2,
                          " Collision not found in table for: ", collision_check)
                    # particle.v_x = reverse_table[k-1, 2]
                    # particle.v_y = reverse_table[k-1, 3]
                    # colliding_particle.v_x = reverse_table[k-1, 4]
                    # colliding_particle.v_y = reverse_table[k-1, 5]
                    # collide(colliding_particle, particle)
                    disp_once = c_count - c_count2
                    # screen.fill(background_color)
                    # particle.display()
                    # particle2.display()
                    # pygame.draw.circle(screen, colliding_particle.color, (int(colliding_particle.x), int(colliding_particle.y)), colliding_particle.size, 0)
                    # pygame.draw.circle(screen, particle.color, (int(particle.x), int(particle.y)), particle.size, 0)
                    # time.sleep(3)
                    # break
            elif collision_count > 1:
                print("------Multiple collision:", collision_count)
            collision_count = 0


            particle.move()
            particle.wall_bounce()
            if display == 1:
                particle.display()
            # screen.blit(font.render("c_ctr: " + str(k), True, white, background_color),
            #             (width - 150, 50))
    if hist == 0:
        frame = frame + 1
    elif hist == 1:
        rev_frame = rev_frame - 1

    pygame.display.flip()


print("Actual Collisions: ",c_count, " Collisions found in table: ", c_count2)

# #check for duplicate rows in stored reverse_table
# delete_rows = []

# print(reverse_table, "\n \n \n")
# for i in range(0, len(reverse_table)):
#     for j in range(0, i):
#         if np.array_equal(reverse_table[i],reverse_table[j]):
#             if reverse_table[i].all():
#                 print(reverse_table[i])
#             delete_rows.append(j)
#
#
# reverse_table = np.delete(reverse_table, delete_rows, axis=0)


# for i in range(0, len(reverse_table)):
#     if not reverse_table[i].any():
#         delete_rows.append(i)
#
#
# reverse_table = np.delete(reverse_table, delete_rows, axis=0)

# print(reverse_table, "\n \n \n")

# for i in range(0, len(reverse_table)):
#     for j in range(0, i):
#         if np.array_equal(reverse_table[i],reverse_table[j]):
#                 # print("yes",reverse_table[i],"  ", reverse_table[j], i," ", j)
#                 reverse_table[k, 2] = reverse_table[k, 2] + 1
#                 reverse_table[k, 3] = reverse_table[k, 3] - 1
#                 reverse_table[k, 4] = reverse_table[k, 4] - 1
#                 reverse_table[k, 5] = reverse_table[k, 5] + 1


# save reverse_table as .txt
np.savetxt('tabledump.txt', reverse_table, fmt='%d', delimiter=',')

# '%1.0f'

# #delete duplicate rows
# for i in range(0, len(delete_rows)):
#     reverse_table = np.delete(reverse_table, delete_rows[i], axis=0)

# reversal during collision
# sticking particles

# loadtxt

# wall probelm reflection

# process is indeterministic causes irreversibility