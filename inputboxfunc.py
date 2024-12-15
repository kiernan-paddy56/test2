import pygame

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
GREY = (128, 128, 128)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)



def input_box(screen, prompt):
    font = pygame.font.Font(None, 36)  # Default font, size 36
    input_rect = pygame.Rect(200, 300, 400, 50)  # Input box dimensions
    color_active = pygame.Color(MAGENTA)
    color_inactive = pygame.Color(CYAN)
    color = color_inactive
    active = False
    text = ""

    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None

            if event.type == pygame.MOUSEBUTTONDOWN:
                # Toggle active state if input box clicked
                if input_rect.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                color = color_active if active else color_inactive

            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        running = False  # Exit the input loop on Enter key
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]  # Remove last character
                    else:
                        text += event.unicode  # Append typed character

        # Clear screen and draw elements
        screen.fill((0, 0, 0))  # Black background
        text_surface = font.render(prompt + text, True, (255, 255, 255))
        pygame.draw.rect(screen, color, input_rect, 2)
        screen.blit(text_surface, (input_rect.x + 10, input_rect.y + 10))

        # Update display
        pygame.display.flip()
        clock.tick(30)

    return text  # Return the user input



