import pygame
from pygame import mixer

mixer.init()
pygame.init()

# Game settings variables
double_jump_enabled = True
volume_level = 0.5
difficulty_level = 1  # Easy=0, Medium=1, Hard=2

# OptionMenu class to handle game settings
class OptionMenu():
    def __init__(self, x, y, width, height, options):
        self.rect = pygame.Rect(x, y, width, height)
        self.options = options  # Store options (button for each)
        self.selected_option = 0  # First option selected by default
        self.visible = False  # Initially, options menu is hidden

        # Create buttons for each option
        self.buttons = []
        for i, option in enumerate(self.options):
            button = Button(x + 50, y + 50 + (i * 60), option['image'], 1)  # Spacing between buttons
            self.buttons.append(button)

    def draw(self, surface):
        if self.visible:
            # Draw the background for the options menu
            pygame.draw.rect(surface, (0, 0, 0), self.rect)  # Black background for options menu
            for i, button in enumerate(self.buttons):
                if button.draw(surface):  # Check if button clicked
                    self.options[i]['action']()  # Execute associated action for button click

    def toggle(self):
        self.visible = not self.visible  # Toggle visibility of the option menu


# Actions for the options
def toggle_double_jump():
    global double_jump_enabled
    double_jump_enabled = not double_jump_enabled
    print("Double Jump is now", "enabled" if double_jump_enabled else "disabled")

def adjust_volume():
    global volume_level
    volume_level = (volume_level + 0.1) % 1.1  # Loop volume between 0.0 and 1.0
    mixer.music.set_volume(volume_level)
    print("Volume level is now", volume_level)

def change_difficulty():
    global difficulty_level
    difficulty_level = (difficulty_level + 1) % 3  # Toggle between 3 difficulty levels
    print("Difficulty level is now", ["Easy", "Medium", "Hard"][difficulty_level])


# Button class
class Button():
    def __init__(self, x, y, image, scale):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False

    def draw(self, surface):
        action = False

        # Get mouse position
        pos = pygame.mouse.get_pos()

        # Check mouseover and clicked conditions
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        # Draw button
        surface.blit(self.image, (self.rect.x, self.rect.y))

        return action


# Main game loop (simplified example)
def main():
    pygame.init()

    # Screen setup
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Option Menu Example")

    # Button images (replace with actual image files)
    double_jump_image = pygame.Surface((200, 50))
    double_jump_image.fill((0, 255, 0))  # Green for double jump

    volume_image = pygame.Surface((200, 50))
    volume_image.fill((0, 0, 255))  # Blue for volume

    difficulty_image = pygame.Surface((200, 50))
    difficulty_image.fill((255, 0, 0))  # Red for difficulty

    # Create option menu
    options = [
        {"image": double_jump_image, "action": toggle_double_jump},
        {"image": volume_image, "action": adjust_volume},
        {"image": difficulty_image, "action": change_difficulty},
    ]

    option_menu = OptionMenu(100, 100, 600, 400, options)

    # Main loop
    running = True
    while running:
        screen.fill((255, 255, 255))  # Fill the screen with white

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Draw the option menu when the player presses 'O'
        if pygame.key.get_pressed()[pygame.K_o]:
            option_menu.toggle()

        # Draw the option menu if it's visible
        option_menu.draw(screen)

        # Update the display
        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()