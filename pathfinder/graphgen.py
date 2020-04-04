import pygame


def main( ):
    BLACK = pygame.Color('black')
    WHITE = pygame.Color('white')
    RED = pygame.Color('red')

    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("graph")

    done = False

    clock = pygame.time.Clock()

    mouse_position = (0, 0)
    lines = []
    new_line_start = None

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.MOUSEMOTION:
                print(event)
                mouse_position = event.pos
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not new_line_start:
                    new_line_start = event.pos
                else:
                    lines.append((new_line_start, event.pos))
                    new_line_start = None

        screen.fill(WHITE)

        pygame.draw.circle(screen, RED, mouse_position, 4)

        for line in lines:
            pygame.draw.line(screen, RED, line[0], line[1], 1)


        pygame.display.flip()

        clock.tick(20)

    pygame.quit()

if __name__ == "__main__":
    main( )