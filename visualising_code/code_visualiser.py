import pygame
import sys

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Colors
WHITE, BLACK, BLUE, GREEN, RED = (255,255,255), (0,0,0), (0,0,255), (0,255,0), (255,0,0)

# Blocks (RAM, IN, OUT, ALU)
blocks = {
    "IN": pygame.Rect(100, 250, 80, 80),
    "RAM": pygame.Rect(300, 100, 100, 80),
    "ALU": pygame.Rect(500, 250, 100, 80),
    "OUT": pygame.Rect(700, 250, 80, 80)
}

# State
selected_command = None
selected_source = None
selected_dest = None
bit_packets = []

class BitPacket:
    def __init__(self, start, end):
        self.x, self.y = start
        self.end = end
        self.speed = 3
    
    def update(self):
        dx, dy = self.end[0]-self.x, self.end[1]-self.y
        dist = (dx**2 + dy**2)**0.5
        if dist > self.speed:
            self.x += self.speed * dx/dist
            self.y += self.speed * dy/dist
            return False
        return True
    
    def draw(self, screen):
        pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), 8)

# Main loop
while True:
    screen.fill(WHITE)

    # Draw blocks
    for name, rect in blocks.items():
        pygame.draw.rect(screen, BLUE, rect, border_radius=10)
        font = pygame.font.SysFont(None, 24)
        screen.blit(font.render(name, True, WHITE), (rect.x+10, rect.y+30))

    # Draw bit packets
    for packet in bit_packets[:]:
        done = packet.update()
        packet.draw(screen)
        if done:
            bit_packets.remove(packet)

    # Event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                selected_command = "LOAD"
            elif event.key == pygame.K_2:
                selected_command = "ADD"
            elif event.key == pygame.K_3:
                selected_command = "STORE"
            elif event.key == pygame.K_RETURN and selected_source and selected_dest:
                start = blocks[selected_source].center
                end = blocks[selected_dest].center
                bit_packets.append(BitPacket(start, end))
                print(f"Command {selected_command}: {selected_source} -> {selected_dest}")
                selected_source, selected_dest, selected_command = None, None, None
            elif event.key == pygame.K_i:
                selected_source = "IN"
            elif event.key == pygame.K_r:
                selected_source = "RAM"
            elif event.key == pygame.K_a:
                selected_dest = "ALU"
            elif event.key == pygame.K_o:
                selected_dest = "OUT"

    pygame.display.flip()
    clock.tick(60)
