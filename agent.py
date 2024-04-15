import pygame

import game
from game import GRASS, TRACK, FINISH, FINISH_POSITION, TRACK_BORDER, AbstractCar, GREEN_CAR
import neat

# FPS = 60
# WIDTH = TRACK.get_width()
# HEIGHT = TRACK.get_height()
#
# WIN = pygame.display.set_mode((WIDTH, HEIGHT))  # do poprawy
#
# run = True  # do wiecznej petli
# clock = pygame.time.Clock()  # fpsy na kazdym kompie tak samo
# images = [(GRASS, (0, 0)), (TRACK, (0, 0)), (FINISH, FINISH_POSITION), (TRACK_BORDER, (0, 0))]
# player_car = AbstractCar(4, 4, GREEN_CAR, (168, 200))
#
# # eventy gry
# while run:
#     clock.tick(FPS)
#
#     game.draw_game(WIN,images)
#     player_car.draw(WIN)
#
#     pygame.display.update()
#
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             run = False
#             break
#
#     player_car.move_player()
#     dupa = player_car.get_data()
#     print(dupa)
#     player_car.handle_collision()
#     player_car.update_radars()
# pygame.quit()


FPS = 60
WIDTH = TRACK.get_width()
HEIGHT = TRACK.get_height()

images = [(GRASS, (0, 0)), (TRACK, (0, 0)), (FINISH, FINISH_POSITION), (TRACK_BORDER, (0, 0))]
current_generation = 0  # Generation counter


def run_simulation(genomes, config):
    # Empty Collections For Nets and Cars
    nets = []
    cars = []

    # Initialize PyGame And The Display
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    # For All Genomes Passed Create A New Neural Network
    for i, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        g.fitness = 0

        cars.append(AbstractCar(4, 4, GREEN_CAR, (168, 200)))

    # Clock Settings
    # Font Settings & Loading Map
    clock = pygame.time.Clock()
    # generation_font = pygame.font.SysFont("Arial", 30)
    # alive_font = pygame.font.SysFont("Arial", 20)
    # game_map = pygame.image.load('map4.png').convert()  # Convert Speeds Up A Lot

    global current_generation
    current_generation += 1

    # Simple Counter To Roughly Limit Time (Not Good Practice)
    counter = 0

    run = True
    while run:
        # Exit On Quit Event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

        # For Each Car Get The Acton It Takes
        for i, car in enumerate(cars):
            output = nets[i].activate(car.get_data())
            choice = output.index(max(output))
            if choice == 0:
                # car.angle += 10  # Left
                car.move_player(True, False, False)
            elif choice == 1:
                # car.angle -= 10  # Right
                car.move_player(False, True, False)
            else:
                car.move_player(False, False, True)


            # else:
            #    if car.speed < car.max_speed:
            #        car.speed += 1  # Speed Up

        # Check If Car Is Still Alive
        # Increase Fitness If Yes And Break Loop If Not
        still_alive = 0
        for i, car in enumerate(cars):
            if car.is_alive():
                still_alive += 1
                car.handle_collision()
                car.distance += car.vel
                car.update_radars()
                genomes[i][1].fitness += car.get_reward()

        if still_alive == 0:
            break

        counter += 1
        if counter == 30 * 40:  # Stop After About 20 Seconds
            break

        # Draw Map And All Cars That Are Alive
        # screen.blit(game_map, (0, 0))
        game.draw_game(screen, images)

        for car in cars:
            if car.is_alive():
                car.draw(screen)

        # Display Info
        # text = generation_font.render("Generation: " + str(current_generation), True, (0, 0, 0))
        # text_rect = text.get_rect()
        # text_rect.center = (900, 450)
        # screen.blit(text, text_rect)
        #
        # text = alive_font.render("Still Alive: " + str(still_alive), True, (0, 0, 0))
        # text_rect = text.get_rect()
        # text_rect.center = (900, 490)
        # screen.blit(text, text_rect)
        #
        pygame.display.flip()
        clock.tick(60)  # 60 FPS


if __name__ == "__main__":
    # Load Config
    config_path = "./config.txt"
    config = neat.config.Config(neat.DefaultGenome,
                                neat.DefaultReproduction,
                                neat.DefaultSpeciesSet,
                                neat.DefaultStagnation,
                                config_path)

    # Create Population And Add Reporters
    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)

    # Run Simulation For A Maximum of 1000 Generations
    population.run(run_simulation, 1000)
