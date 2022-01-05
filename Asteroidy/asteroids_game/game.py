import pygame
from pygame import Color
from pygame.mixer import music
from utils import load_sprite, get_random_position, print_text

from models import Spaceship, Asteroid, Shotgun, Shield

import random


class Asteroidy:
    MIN_ASTEROID_DISTANCE = 300

    def __init__(self):
        self._init_pygame()
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((1600, 900))
        self.background = load_sprite("space", False)
        self.startbg = load_sprite("start", False)
        self.message = ""
        self.message_color = Color("red")
        self.asteroids = []
        self.bullets = []
        self.score = 0
        self.spaceship = Spaceship((800, 450), self.bullets.append)
        self.count = 1
        self.menu_mode = True
        self.game_over = False
        #self.upgrades = [self._get_random_upgrade()]
        self.upgrades = [Shield(get_random_position(self.screen), self.spaceship)]
        self._asteroid_spawn(amount=4)
        music.load("assets/sounds/soundtrack.wav")
        music.set_volume(0.1)
        music.play(-1, fade_ms=1000)

    def _init_pygame(self):
        pygame.init()
        pygame.display.set_caption("Asteroidy")

    # main menu
    def menu(self):
        while self.menu_mode:
            self.screen.blit(self.startbg, (0, 0))
            pygame.display.flip()
            for event in pygame.event.get():
                # exiting the game
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    quit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    self.menu_mode = False
                    self.main_loop()

    # spawning asteroids
    def _asteroid_spawn(self, amount: int):
        for _ in range(amount):
            while True:
                position = get_random_position(self.screen)
                if position.distance_to(self.spaceship.position) > self.MIN_ASTEROID_DISTANCE:
                    break
            self.asteroids.append(Asteroid(position, self.asteroids.append))

    def _get_random_upgrade(self):
        upgrade_list = {
            1: Shield(get_random_position(self.screen), self.spaceship),
            2: Shotgun(get_random_position(self.screen), self.spaceship)
        }
        return upgrade_list[random.randint(1, 2)]

    def _handle_input(self):
        for event in pygame.event.get():
            # exiting the game
            if self.game_over:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    self._restart()
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                quit()

            # shooting
            elif self.game_over is False and self.spaceship and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.spaceship.shoot()

        # moving the spaceship
        is_key_pressed = pygame.key.get_pressed()
        if self.spaceship:
            if is_key_pressed[pygame.K_RIGHT]:
                self.spaceship.rotate(clockwise=True)
            elif is_key_pressed[pygame.K_LEFT]:
                self.spaceship.rotate(clockwise=False)
            if is_key_pressed[pygame.K_UP]:
                self.spaceship.accelerate()

    def _process_game_logic(self):
        for game_object in self._get_game_objects():
            game_object.move(self.screen)
        self.count += 1
        if self.count > 10000:
            self.count = 1
        if self.count % 500 == 0:
            self._asteroid_spawn(1 + self.score // 500)

        if len(self.asteroids) == 0:
            self._asteroid_spawn(2)
        if len(self.upgrades) == 0:
            if self.count % 4000 == 0:
                self.upgrades.append(self._get_random_upgrade())

        # destroying spaceship when it hits asteroids
        # game over
        if self.spaceship:
            for asteroid in self.asteroids:
                if asteroid.collides_with(self.spaceship):
                    # self.spaceship = None
                    if self.spaceship.destroy(game=self):
                        self._game_loss()
                    self.asteroids.remove(asteroid)
                    break

        # destroying asteroid when it hits bullet
        for bullet in self.bullets[:]:

            for asteroid in self.asteroids[:]:
                if asteroid.collides_with(bullet):
                    self.asteroids.remove(asteroid)
                    self.bullets.remove(bullet)
                    if asteroid.size == 3:
                        self.score += 10
                    elif asteroid.size == 2:
                        self.score += 20
                    else:
                        self.score += 30
                    asteroid.split()
                    break

        # getting the upgrade
        for bullet in self.bullets[:]:
            for upgrade in self.upgrades[:]:
                if upgrade.collides_with(bullet):
                    upgrade.destroy()
                    self.upgrades.remove(upgrade)
                    self.bullets.remove(bullet)
                    break

        # removing bullets that are outside of the map
        for bullet in self.bullets[:]:
            if not self.screen.get_rect().collidepoint(bullet.position):
                self.bullets.remove(bullet)
        # winning the game
        # if not self.asteroids and self.spaceship:
        #     self.message_color = "green"
        #     self.message = "You won!"
        #     self.game_over = True

    def _game_loss(self):
        self.message = "You lost! Press Enter to restart!"
        self.game_over = True
        music.pause()

        # game restart

    def _restart(self):
        if self.game_over:
            self.spaceship = Spaceship((800, 450), self.bullets.append)
            self.game_over = False
            self.message = ""
            self.asteroids.clear()
            self.bullets.clear()
            self.upgrades.clear()
            self.score = 0
            self._asteroid_spawn(amount=4)
            music.unpause()

    def _draw(self):

        self.screen.blit(self.background, (0, 0))

        print_text(self.screen, "Score = " + str(self.score), 10, 10, 48, False, (255, 255, 255))

        if self.spaceship:
            temp = "Lives = " + str(self.spaceship.lives)
            temp2 = "Shotgun = " + str(self.spaceship.shotgunRemaining)
        else:
            temp = "Lives = 0"
            temp2 = "Shotgun = 0 "

        print_text(self.screen, temp, 10, 50, 48, False, (255, 255, 255))
        print_text(self.screen, temp2, 10, 100, 48, False, (255, 255, 255))

        for game_object in self._get_game_objects():
            game_object.draw(self.screen)

        if self.message:
            print_text(self.screen, self.message, 50, 50, 64, True, self.message_color)

        pygame.display.flip()
        self.clock.tick(60)

    def _get_game_objects(self):
        game_objects = [*self.asteroids, *self.bullets, *self.upgrades]
        if self.spaceship:
            game_objects.append(self.spaceship)
        return game_objects

        # game

    def main_loop(self):
        while True:
            # handle input outside of if, so that it's possible to quit and restart the game
            self._handle_input()
            if not self.game_over:
                self._process_game_logic()
                self._draw()
