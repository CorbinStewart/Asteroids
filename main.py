import pygame
from constants import *
from player import *

def main():
    print("Starting Asteroids!")
    print(f"Screen width: {SCREEN_WIDTH}")
    print(f"Screen height: {SCREEN_HEIGHT}")
    
    # Start the game
    pygame.init()
    
    # Set screen resolution
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    # Clock
    clock = pygame.time.Clock()

    dt = 0

    # Adding object groups
    updatable = pygame.sprite.Group()
    drawable = pygame.sprite.Group()
    
    # Adding player to groups
    Player.containers = (updatable, drawable)

    # Setting starting position
    x = SCREEN_WIDTH / 2
    y = SCREEN_HEIGHT / 2
    
    # Adding Player object
    player = Player(x, y)

    # Gameplay loop
    while True:
        #Close app window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

        # Set background colour    
        screen.fill("black")
        
        # Updating group postion
        updatable.update(dt)

        # Drawing the group position
        for spr in drawable:
            spr.draw(screen)

        pygame.display.flip()

        #Framerate
        dt = (clock.tick(60) / 1000)
    


if __name__ == "__main__":
    main()
    
