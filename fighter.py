import pygame

class Fighter():
    def __init__(self, player, x, y, flip, data, sprite_sheet, animation_steps, sound):
        self.player = player
        self.size = data[0]
        self.image_scale = data[1]
        self.offset = data[2]
        self.flip = flip
        self.animation_list = self.load_images(sprite_sheet, animation_steps)
        self.action = 0 #0:idle #1:run #2:jump #3:attack #4:attack2 #5:hit #6:death
        self.frame_index = 0
        self.image = self.animation_list[self.action][self.frame_index]
        self.update_time = pygame.time.get_ticks()
        self.rect = pygame.Rect((x, y, 80, 180))
        self.vel_y = 0
        self.running = False
        self.jump = False
        self.attacking = False
        self.attack_type = 0
        self.attack_cooldown = 0
        self.attack_sound = sound
        self.hit = False
        self.health = 100
        self.alive = True


    def load_images(self, sprite_sheet, animation_steps):
        # Extract images from the sprite sheet
        animation_list = []
        for y, animation in enumerate(animation_steps):
            temp_img_list = []
            for x in range(animation):
                # Calculate the coordinates for the subsurface
                subsurface_x = x * self.size
                subsurface_y = y * self.size
                # Check if the subsurface rectangle is within the sprite sheet dimensions
                if subsurface_x + self.size <= sprite_sheet.get_width() and subsurface_y + self.size <= sprite_sheet.get_height():
                    temp_img = sprite_sheet.subsurface(subsurface_x, subsurface_y, self.size, self.size)
                    temp_img_list.append(
                        pygame.transform.scale(temp_img, (self.size * self.image_scale, self.size * self.image_scale)))
                else:
                    print(f"Subsurface rectangle outside surface area at ({subsurface_x}, {subsurface_y})")
            animation_list.append(temp_img_list)
        return animation_list

    def move(self, screen_width, screen_height, surface, target, round_over):
        SPEED = 10
        GRAVITY = 2
        JUMP_VELOCITY = 30  # Adjust this value to control jump height
        dx = 0
        dy = 0
        self.running = False
        self.attack_type = 0

        # Get keypresses
        keys = pygame.key.get_pressed()

        if self.alive and round_over == False:
            # Control player 1
            if self.player == 1:
                if keys[pygame.K_a]:
                    dx = -SPEED
                    self.running = True
                if keys[pygame.K_d]:
                    dx = +SPEED
                    self.running = True
                if keys[pygame.K_w] and not self.jump:
                    self.vel_y = -JUMP_VELOCITY  # Adjust jump velocity here
                    self.jump = True
                if keys[pygame.K_r] or keys[pygame.K_t]:
                    self.attack(target)
                    if keys[pygame.K_r]:
                        self.attack_type = 1
                    if keys[pygame.K_t]:
                        self.attack_type = 2

            # Control player 2
            elif self.player == 2:
                if keys[pygame.K_LEFT]:
                    dx = -SPEED
                    self.running = True
                if keys[pygame.K_RIGHT]:
                    dx = +SPEED
                    self.running = True
                if keys[pygame.K_UP] and not self.jump:
                    self.vel_y = -JUMP_VELOCITY  # Adjust jump velocity here
                    self.jump = True
                if keys[pygame.K_KP1] or keys[pygame.K_KP2]:
                    self.attack(target)
                    if keys[pygame.K_KP1]:
                        self.attack_type = 1
                    if keys[pygame.K_KP2]:
                        self.attack_type = 2

        # Apply gravity
        self.vel_y += GRAVITY
        dy += self.vel_y

        # Ensure player stays on screen
        if self.rect.left + dx < 0:
            dx = -self.rect.left
        if self.rect.right + dx > screen_width:
            dx = screen_width - self.rect.right
        if self.rect.bottom + dy > screen_height - 110:
            self.vel_y = 0
            self.jump = False
            dy = screen_height - 110 - self.rect.bottom

        # Ensure players face each other
        if target.rect.centerx > self.rect.centerx:
            self.flip = False
        else:
            self.flip = True

        # Ensure attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        # Update player position
        self.rect.x += dx
        self.rect.y += dy

    #handle animation upadtes
    def update(self):
        # Check if the player is alive
        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.update_action(6)  # Set the death animation
        elif self.hit:
            self.update_action(5)  # Set the hit animation
        elif self.attacking:
            if self.attack_type == 1:
                self.update_action(3)  # Set the first attack animation
            elif self.attack_type == 2:
                self.update_action(4)  # Set the second attack animation
        elif self.jump:
            self.update_action(2)  # Set the jump animation
        elif self.running:
            self.update_action(1)  # Set the run animation
        else:
            self.update_action(0)  # Set the idle animation

        animation_cooldown = 50
        # Update image
        self.image = self.animation_list[self.action][self.frame_index]
        # Check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()
            # Check if the animation is finished
            if self.frame_index >= len(self.animation_list[self.action]):
                # If the player is dead, then end the animation
                if not self.alive:
                    self.frame_index = len(self.animation_list[self.action]) - 1
                else:
                    self.frame_index = 0
                # Check if an attack was executed
                if self.action == 3 or self.action == 4:
                    self.attacking = False
                    self.attack_cooldown = 20
                # Check if damage was taken
                if self.action == 5:
                    self.hit = False
                    # If the player was in the middle of an attack, then stop the attack
                    self.attacking = False
                    self.attack_cooldown = 20

    def attack(self, target):
        if self.attack_cooldown == 0:
            #excute attack
            self.attacking = True
            self.attack_sound.play()
            attacking_rect = pygame.Rect(self.rect.centerx - (2 * self.rect.width * self.flip), self.rect.y, 2 * self.rect.width, self.rect.height)
            if attacking_rect.colliderect(target.rect):
                target.health -= 5
                target.hit = True
                self.attack_cooldown = 20


    def update_action(self, new_action):
        #check if new action is different to the previous one
        if new_action != self.action:
            self.action = new_action
            #update animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def draw(self, surface):
        img = pygame.transform.flip(self.image, self.flip, False)
        surface.blit(img, (self.rect.x - (self.offset[0]*self.image_scale), self.rect.y - (self.offset[1] * self.image_scale)))
