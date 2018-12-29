import pygame
import random
import time


dt = float(input("Enter a value for dt: "))
v_initial = 1000
color_factor = float(input("Enter a value for Colour Change Determinancy (0 - 100): "))/100
background_color = (255, 255, 255)
(width, height) = (1300, 700)
green = (0, 255, 0)
red = (255, 0, 0)
color1 = (255, 165, 80)  # orange
color2 = (0, 0, 255)  # blue
black = (0, 0, 0)
corner = int(input("Enter 1 to start in Corner and if otherwise 0: "))
thickness = 1


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


def reverse_velocity(p):
    p.v_x = -p.v_x
    p.v_y = -p.v_y


def check_collision(p1, p2):
    s = (p2.x - p1.x) ** 2 + (p2.y - p1.y) ** 2  # s = square of distance between particles

    if s < (p1.size + p2.size) ** 2:
        return True


def collide(p1, p2):
    s = (p2.x - p1.x) ** 2 + (p2.y - p1.y) ** 2  # s = square of distance between particles
    e1 = p2.x - p1.x
    e2 = p2.y - p1.y
    a = e1 * (p1.v_x - p2.v_x) + e2 * (p1.v_y - p2.v_y)  # numerator of lamda

    if a >= 0:
        lamda = a / s

        # new velocities after collision
        p1.v_x = p1.v_x - lamda * e1
        p1.v_y = p1.v_y - lamda * e2
        p2.v_x = p2.v_x + lamda * e1
        p2.v_y = p2.v_y + lamda * e2

    color_change(p1, p2)


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
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size, self.thickness)

    def wall_bounce(self):

        # collision with right wall
        if self.x >= width - self.size:       # if particle has moved beyond right wall
            self.x = 2 * (width - self.size) - self.x
            self.v_x = -self.v_x      # reverse velocity x-direction

        # collision with left wall
        if self.x <= self.size:  # if particle has moved beyond left wall
            self.x = 2 * self.size - self.x
            self.v_x = -self.v_x  # reverse velocity x-direction

        # collision with bottom wall
        if self.y >= height - self.size:      # if particle has moved beyond bottom wall
            self.y = 2 * (height - self.size) - self.y       #
            self.v_y = -self.v_y      # reverse velocity y-direction

        # collision with top wall
        if self.y <= self.size:       # if particle has moved beyond top wall
            self.y = 2 * self.size - self.y
            self.v_y = -self.v_y    # reverse velocity y-direction

    def move(self):
        self.x = self.x + self.v_x * dt
        self.y = self.y + self.v_y * dt


pygame.init()
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Direction of Time')
screen.fill(background_color)
font = pygame.font.SysFont(None, 22)

particle_size = 10
number_of_particles = 50
particles = []

# initialize particles

if corner == 1:  # User input to start in corner
    j = 1
    k = 1
    while j <= number_of_particles:
        for z in range(1, int(number_of_particles ** 0.5) + 1):
            x_init = 4 * z * particle_size + particle_size * (random.random() - 0.5)
            y_init = 4 * k * particle_size + particle_size * (random.random() - 0.5)
            v_x_init = v_initial * (random.random() - 0.5)
            v_y_init = v_initial * (random.random() - 0.5)
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

running = True

reverse = 0
forward = 0
hist = 0
reverse_once = 0    # flag to stop reversing velocities every time it enters reverse motion for loop

collision_count = 0

history = {}    # store position and color in memory
frame = 0   # counter for history

j = 0   # iterator for reverse frame
start_time = 0  # store time when 'f' is pressed
reverse_time = 0    # store time when 'r' is pressed

time_list = []  # stores time values in seconds
r = 0   # iterator for time_list
rr = 0  # flag to store index for time_list reversal when 'r' or 'h' is pressed

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_f:    # press 'f' for forward motion
            forward = 1
            reverse = 0
            frame = 0
            start_time = time.time()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:    # press 'r' for reversing velocities
            reverse = 1
            forward = 0
            reverse_once = 0
            rr = r - 1  # index at which time is reversed
            reverse_time = time.time()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_h:    # press 'h' for reversing motion from memory
            reverse = 0
            forward = 0
            hist = 1
            j = frame - 1
            rr = r - 1

    screen.fill(background_color)   # refresh screen with background for every frame

    # Initial display of particles

    if forward == 0 and reverse == 0 and hist == 0:
        for particle in particles:
            particle.display()

    # forward motion

    if forward == 1 and reverse == 0 and hist == 0:
        for i, particle in enumerate(particles):
            particle.move()
            particle.wall_bounce()
            for particle2 in particles[i + 1:]:
                if check_collision(particle, particle2):
                    collision_count = collision_count + 1
                    colliding_particle = particle2
            if collision_count == 1:
                collide(particle, colliding_particle)
            collision_count = 0
            particle.display()

        for z in range(0, number_of_particles + 1):
            history[frame, z, 0] = particles[z].x
            history[frame, z, 1] = particles[z].y
            history[frame, z, 2] = particles[z].color

        time_list.append(int(time.time() - start_time))
        timer = font.render("Time: " + str(time_list[r]), True, black, background_color)
        screen.blit(timer, (width - 150, 20))
        r = r + 1

    # reverse velocities

    if reverse == 1 and forward == 0 and hist == 0:
        r = r - 1
        # stop animation when reverse time reaches 0
        if (time.time() - reverse_time == reverse_time - start_time) or r == -1:
            pygame.time.wait(10000)
            running = False

        if reverse_once == 0:
            for particle in particles:
                reverse_velocity(particle)
                reverse_once = 1
        for i, particle in enumerate(particles):
            particle.move()
            particle.wall_bounce()
            for particle2 in particles[i + 1:]:
                if check_collision(particle, particle2):
                    collision_count = collision_count + 1
                    colliding_particle = particle2
            if collision_count == 1:
                collide(particle, colliding_particle)
            collision_count = 0
            particle.display()

        # display reverse time
        reverse_timer = font.render(str(time_list[r]), True, red, background_color)
        screen.blit(reverse_timer, (width - 80, 20))
        screen.blit(font.render("Time: " + str(time_list[rr]), True, black, background_color), (width - 150, 20))

    # reverse motion using memory

    if reverse == 0 and forward == 0 and hist == 1:

        r = r - 1
        # stop animation when reverse flag becomes 0 or when index for history becomes 0
        if r == -1 or j == -1:
            pygame.time.wait(10000)
            running = False

        for k in range(0, number_of_particles + 1):
            pygame.draw.circle(screen, history[j, k, 2], (int(history[j, k, 0]), int(history[j, k, 1])), particle_size, thickness)

        # display reverse time
        reverse_timer = font.render(str(time_list[r]), True, red, background_color)
        screen.blit(reverse_timer, (width - 80, 20))
        screen.blit(font.render("Time: " + str(time_list[rr]), True, black, background_color), (width - 150, 20))

    if hist == 0:
        frame = frame + 1
    elif hist == 1:
        j = j - 1

    pygame.display.flip()
