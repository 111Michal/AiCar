import pygame
import math
from utils import scale_image
from utils import blit_rotate_center

GRASS = scale_image(pygame.image.load("imgs/grass.jpg"), 2.5)
TRACK = scale_image(pygame.image.load("imgs/track.png"), 0.9)
TRACK_BORDER = scale_image(pygame.image.load("imgs/track-border-zmieniony.png"), 0.9)
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER)
FINISH = pygame.image.load("imgs/finish.png")
FINISH_MASK = pygame.mask.from_surface(FINISH)
FINISH_POSITION = (130, 250)
RED_CAR = scale_image(pygame.image.load("imgs/red-car.png"), 0.55)
GREEN_CAR = scale_image(pygame.image.load("imgs/green-car.png"), 0.55)

pygame.display.set_caption("Racing Game!")


class AbstractCar:  # klasa do samochodzika
    def __init__(self, max_vel, rotation_vel, IMG, START_POS):
        # self.win = win
        # self.images = images
        self.img = IMG
        self.width = self.img.get_width()
        self.height = self.img.get_height()
        self.x_res, self.y_res = START_POS
        self.max_vel = max_vel
        self.vel = 0
        self.rotation_vel = rotation_vel
        self.angle = 0
        self.x, self.y = START_POS
        self.center = (self.x + self.width / 2, self.y + self.height / 2)
        self.acceleration = 0.1
        self.alive = True  # Boolean To Check If Car is Crashed
        self.distance = 0
        # czujniki
        self.sensors = []
        self.sensor_max_distance = 300

    def get_reward(self):
        # Calculate Reward (Maybe Change?)
        # return self.distance / 50.0
        return self.distance / (self.width / 2)

    def is_alive(self):
        # Basic Alive Function
        return self.alive

    def draw_radar(self, win):
        for radar in self.sensors:
            position = radar[0]
            pygame.draw.line(win, (255, 255, 255), self.center, position, 1)

    def check_sensor(self, sensor_angle):
        length = 0
        x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + sensor_angle))) * length)
        y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + sensor_angle))) * length)

        # While We Don't Hit BORDER_COLOR AND length < 300 (just a max) -> go further and further
        while not TRACK_BORDER.get_at((x, y)) == (255, 0, 0) and length < self.sensor_max_distance:
            length = length + 1
            x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + sensor_angle))) * length)
            y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + sensor_angle))) * length)

        # Calculate Distance To Border And Append To Radars List
        dist = int(math.sqrt(math.pow(x - self.center[0], 2) + math.pow(y - self.center[1], 2)))
        self.sensors.append([(x, y), dist])

    def update_radars(self):
        self.sensors.clear()
        self.center = (self.x + self.width / 2, self.y + self.height / 2)
        # od 0 do 225 stopni co 45 stopni ustal radary
        for d in range(0, 225, 45):
            self.check_sensor(d)

    def get_data(self):
        # distances_array = []
        # for sensor in self.sensors:
        #     dist = sensor[1]
        #     distances_array.append(dist)
        #
        # distances_array[0] - self.width / 2,
        # distances_array[1] - (self.width / 2) / (math.cos(math.radians(45))),
        # distances_array[2] - self.height / 2,
        # distances_array[3] - (self.width / 2) / (math.cos(math.radians(45))),
        # distances_array[4] - self.width / 2
        #
        # return distances_array
        radars = self.sensors
        return_values = [0, 0, 0, 0, 0]
        for i in range(2, len(radars), 1):
            return_values[2] = radars[2][1] - self.height / 2
            break
        for i in range(0, len(radars), 4):
            return_values[i] = radars[i][1] - self.width / 2
        for i in range(1, len(radars), 2):
            return_values[i] = radars[i][1] - (self.width / 2) / (math.cos(math.radians(45)))

        return return_values

    def rotate(self, left=False, right=False):
        if left:
            self.angle += self.rotation_vel
        elif right:
            self.angle -= self.rotation_vel

    def move_forward(self):
        self.vel = min(self.vel + self.acceleration, self.max_vel)
        self.move()

    def move_backward(self):
        self.vel = max(self.vel - self.acceleration, -self.max_vel / 2)
        self.move()

    def move(self):
        radians = math.radians(self.angle)
        vertical = math.cos(radians) * self.vel
        horizontal = math.sin(radians) * self.vel
        self.x -= horizontal
        self.y -= vertical

    def collide(self, mask, x=0, y=0):
        car_mask = pygame.mask.from_surface(self.img)
        offset = (int(self.x - x), int(self.y - y))
        poi = mask.overlap(car_mask, offset)
        return poi

    def reset(self):
        self.x, self.y = self.x_res, self.y_res
        self.angle = 0
        self.vel = 0
        self.distance = 0

    def reduce_speed(self):
        self.vel = max(self.vel - self.acceleration / 2, 0)
        self.move()

    # def move_player(self):
    #     # obsluga klawiszy
    #     keys = pygame.key.get_pressed()
    #     moved = False
    #     if keys[pygame.K_a]:
    #         self.rotate(left=True)
    #     if keys[pygame.K_d]:
    #         self.rotate(right=True)
    #     if keys[pygame.K_w]:
    #         moved = True
    #         self.move_forward()
    #     if keys[pygame.K_s]:
    #         moved = True
    #         self.move_backward()
    #     if not moved:
    #         self.reduce_speed()

    def move_player(self, left, right, straight):
        # keys = pygame.key.get_pressed()
        moved = False
        if left:
            self.rotate(left=True)
        if right:
            self.rotate(right=True)
        if straight:
            moved = True
            self.move_forward()
        if not moved:
            self.reduce_speed()

    def handle_collision(self):
        self.alive = True
        if self.collide(TRACK_BORDER_MASK) is not None:
            self.alive = False
            # self.reset()
            # print("crash")

        player_finish_poi_collide = self.collide(FINISH_MASK, *FINISH_POSITION)
        if player_finish_poi_collide is not None:
            if player_finish_poi_collide[1] == 0:
                # self.reset()
                self.alive = False
                # print("crash")
            else:
                # self.reset()
                print("finish")

    def draw(self, win):  # rysowanie obiektow

        blit_rotate_center(win, self.img, (self.x, self.y), self.angle)
        #self.draw_radar(win)


def draw_game(win, images):  # rysowanie obiektow
    for img, pos in images:
        win.blit(img, pos)
