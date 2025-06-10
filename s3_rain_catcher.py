import pygame
import sys
import random
import os
from pygame.locals import *

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
LIGHT_BLUE = (173, 216, 230)
ORANGE = (255, 165, 0)
DARK_ORANGE = (255, 140, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)

# Game parameters
BUCKET_WIDTH = 80
BUCKET_HEIGHT = 80
RAINDROP_SIZE = 15
RAINDROP_SPEED_MIN = 2
RAINDROP_SPEED_MAX = 6
RAINDROP_FREQUENCY = 30  # Lower is more frequent
GAME_DURATION = 60  # seconds

class S3RainCatcher:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("S3 Rain Catcher")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 24)
        
        # Load S3 bucket image from file
        try:
            # Load the image and scale it to the desired size
            original_img = pygame.image.load("s3.png")
            self.bucket_img = pygame.transform.scale(original_img, (BUCKET_WIDTH, BUCKET_HEIGHT))
        except pygame.error:
            # Fallback to creating the image if file can't be loaded
            print("Could not load s3.png, using fallback image")
            self.bucket_img = self.create_s3_bucket_image()
        
        self.reset_game()
    
    def create_s3_bucket_image(self):
        """Create an S3 bucket icon"""
        surf = pygame.Surface((BUCKET_WIDTH, BUCKET_HEIGHT), pygame.SRCALPHA)
        
        # Draw the main bucket body (orange)
        bucket_rect = pygame.Rect(5, 15, BUCKET_WIDTH - 10, BUCKET_HEIGHT - 15)
        pygame.draw.rect(surf, ORANGE, bucket_rect, border_radius=5)
        
        # Draw the bucket top rim (darker orange)
        rim_rect = pygame.Rect(0, 10, BUCKET_WIDTH, 10)
        pygame.draw.rect(surf, DARK_ORANGE, rim_rect, border_radius=3)
        
        # Draw the AWS S3 logo text
        logo_font = pygame.font.SysFont(None, 28)
        logo_text = logo_font.render("S3", True, WHITE)
        text_rect = logo_text.get_rect(center=(BUCKET_WIDTH//2, BUCKET_HEIGHT//2))
        surf.blit(logo_text, text_rect)
        
        # Draw water level indicator lines
        for i in range(1, 4):
            y_pos = bucket_rect.bottom - (i * bucket_rect.height // 4)
            pygame.draw.line(surf, DARK_ORANGE, 
                            (bucket_rect.left + 5, y_pos),
                            (bucket_rect.right - 5, y_pos), 2)
        
        return surf
    
    def create_raindrop_image(self):
        """Create a raindrop image"""
        surf = pygame.Surface((RAINDROP_SIZE, RAINDROP_SIZE), pygame.SRCALPHA)
        
        # Draw a blue teardrop shape
        pygame.draw.circle(surf, LIGHT_BLUE, (RAINDROP_SIZE//2, RAINDROP_SIZE//2), RAINDROP_SIZE//2)
        
        return surf
    
    def reset_game(self):
        self.bucket_x = SCREEN_WIDTH // 2 - BUCKET_WIDTH // 2
        self.bucket_y = SCREEN_HEIGHT - BUCKET_HEIGHT - 20
        self.raindrops = []
        self.score = 0
        self.water_level = 0  # 0 to 100
        self.game_over = False
        self.start_time = pygame.time.get_ticks()
        self.time_left = GAME_DURATION
        self.raindrop_img = self.create_raindrop_image()
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                return False
            
            if event.type == KEYDOWN:
                if event.key == K_r and self.game_over:
                    self.reset_game()
        
        # Move bucket with keyboard
        keys = pygame.key.get_pressed()
        if keys[K_LEFT] and self.bucket_x > 0:
            self.bucket_x -= 5
        if keys[K_RIGHT] and self.bucket_x < SCREEN_WIDTH - BUCKET_WIDTH:
            self.bucket_x += 5
        
        return True
    
    def update(self):
        if self.game_over:
            return
        
        # Update time left
        current_time = pygame.time.get_ticks()
        elapsed_seconds = (current_time - self.start_time) // 1000
        self.time_left = max(0, GAME_DURATION - elapsed_seconds)
        
        if self.time_left <= 0:
            self.game_over = True
            return
        
        # Create new raindrops randomly
        if random.randint(1, RAINDROP_FREQUENCY) == 1:
            raindrop_x = random.randint(0, SCREEN_WIDTH - RAINDROP_SIZE)
            raindrop_y = -RAINDROP_SIZE
            raindrop_speed = random.uniform(RAINDROP_SPEED_MIN, RAINDROP_SPEED_MAX)
            self.raindrops.append([raindrop_x, raindrop_y, raindrop_speed])
        
        # Update raindrops position and check for collisions
        for drop in self.raindrops[:]:
            drop[1] += drop[2]  # Move the raindrop down
            
            # Check if raindrop is caught by bucket
            if (self.bucket_x < drop[0] < self.bucket_x + BUCKET_WIDTH and
                self.bucket_y < drop[1] < self.bucket_y + BUCKET_HEIGHT):
                self.score += 1
                self.water_level = min(100, self.water_level + 2)  # Increase water level
                self.raindrops.remove(drop)
            
            # Remove raindrops that fall off the screen
            elif drop[1] > SCREEN_HEIGHT:
                self.raindrops.remove(drop)
    
    def draw(self):
        # Draw background
        self.screen.fill(WHITE)
        
        # Draw clouds
        for i in range(3):
            cloud_x = (i * SCREEN_WIDTH // 3) + random.randint(-20, 20)
            cloud_y = 50 + random.randint(-10, 10)
            self.draw_cloud(cloud_x, cloud_y)
        
        # Draw raindrops
        for drop in self.raindrops:
            self.screen.blit(self.raindrop_img, (drop[0], drop[1]))
        
        # Draw bucket with water level
        self.draw_bucket_with_water()
        
        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, BLACK)
        self.screen.blit(score_text, (20, 20))
        
        # Draw water level
        water_text = self.font.render(f"Water: {self.water_level}%", True, BLUE)
        self.screen.blit(water_text, (20, 60))
        
        # Draw time left
        time_text = self.font.render(f"Time: {self.time_left}s", True, BLACK)
        self.screen.blit(time_text, (SCREEN_WIDTH - 150, 20))
        
        # Draw game over message
        if self.game_over:
            game_over_text = self.font.render("Game Over!", True, BLACK)
            restart_text = self.small_font.render("Press R to restart", True, BLACK)
            
            game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20))
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20))
            
            self.screen.blit(game_over_text, game_over_rect)
            self.screen.blit(restart_text, restart_rect)
            
            # Draw final score
            final_score_text = self.font.render(f"Final Score: {self.score}", True, BLACK)
            final_score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 60))
            self.screen.blit(final_score_text, final_score_rect)
        
        pygame.display.flip()
    
    def draw_cloud(self, x, y):
        """Draw a simple cloud"""
        for i in range(3):
            pygame.draw.circle(self.screen, GRAY, (x + i*20, y), 20)
        pygame.draw.circle(self.screen, GRAY, (x + 20, y - 10), 25)
    
    def draw_bucket_with_water(self):
        """Draw the bucket with current water level"""
        # Draw the bucket
        self.screen.blit(self.bucket_img, (self.bucket_x, self.bucket_y))
        
        # Draw water inside the bucket based on water level
        if self.water_level > 0:
            water_height = (BUCKET_HEIGHT - 25) * self.water_level / 100
            water_rect = pygame.Rect(
                self.bucket_x + 10, 
                self.bucket_y + BUCKET_HEIGHT - 10 - water_height,
                BUCKET_WIDTH - 20, 
                water_height
            )
            pygame.draw.rect(self.screen, LIGHT_BLUE, water_rect, border_radius=3)
    
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = S3RainCatcher()
    game.run()
