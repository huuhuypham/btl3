import pygame
from pygame import mixer
import os
import random
import csv
import button

mixer.init()
pygame.init()


SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Shooter')

clock = pygame.time.Clock()
FPS = 60

GRAVITY = 0.75
SCROLL_THRESH = 200
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 21
MAX_LEVELS = 3
screen_scroll = 0
bg_scroll = 0
level = 0
start_game = False
start_intro = False
kill_value = 0

moving_left = False
moving_right = False
shoot = False
grenade = False
grenade_thrown = False
double_jump_on = True
sound_on = True

jump_fx = pygame.mixer.Sound('audio/jump.wav')
jump_fx.set_volume(0.05)
shot_fx = pygame.mixer.Sound('audio/shot.wav')
shot_fx.set_volume(0.05)
grenade_fx = pygame.mixer.Sound('audio/grenade.wav')
grenade_fx.set_volume(0.05)

start_img = pygame.image.load('img/start_btn.png').convert_alpha()
setting_img = pygame.image.load('img/option2_btn.png').convert_alpha()
exit_img = pygame.image.load('img/exit_btn.png').convert_alpha()
restart_img = pygame.image.load('img/restart_btn.png').convert_alpha()
pine_img = pygame.image.load('img/Background/pine.png').convert_alpha()
standard_width = start_img.get_width()
standard_height = start_img.get_height()
restart_button = button.Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, restart_img, 2)

show_setting_menu = False
# Load ảnh menu setting
setting_button_size = (180, 60)

doublejump_img = pygame.image.load('img/setting/Doublejump.png').convert_alpha()
sound_img = pygame.image.load('img/setting/Sound.png').convert_alpha()
on_img = pygame.image.load('img/setting/On.png').convert_alpha()
off_img = pygame.image.load('img/setting/Off.png').convert_alpha()

standard_size = (start_img.get_width(), start_img.get_height())

SETTING_BG = (180, 220, 255)  # Xanh nhạt dịu

doublejump_img = pygame.transform.scale(doublejump_img, setting_button_size)
sound_img = pygame.transform.scale(sound_img, setting_button_size)
on_img = pygame.transform.scale(on_img, setting_button_size)
off_img = pygame.transform.scale(off_img, setting_button_size)





# Scale setting_img và exit_img về kích thước chuẩn
setting_img = pygame.transform.scale(setting_img, (standard_width, standard_height))
exit_img = pygame.transform.scale(exit_img, (standard_width, standard_height))

mountain_img = pygame.image.load('img/Background/mountain.png').convert_alpha()
sky_img = pygame.image.load('img/Background/sky_cloud.png').convert_alpha()
img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f'img/Tile/{x}.png')
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)

boss_image_folder = 'img/boss2/Orc_Berserk'
animation_frame_counts = {
    'Attack_1': 4,
    'Attack_2': 5,
    'Attack_3': 2,
    'Dead': 4,
    'Hurt': 2,
    'Idle': 5,
    'Jump': 5,
    'Run': 6,
    'Run+Attack': 5,
    'Walk': 6
}
enemy_frame_counts = {
    'Idle': 5,
    'Run': 6,
    'Jump': 6,
    'Death': 5
}
soldier_standard_actions = ['Idle', 'Run', 'Jump', 'Death']

img_list_boss = []

for animation_name, frame_count in animation_frame_counts.items():
    temp_list = []
    animation_image = pygame.image.load(f'{boss_image_folder}/{animation_name}.png').convert_alpha()
    frame_width = animation_image.get_width() // frame_count
    frame_height = animation_image.get_height()
    for i in range(frame_count):
        img = animation_image.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
        img = pygame.transform.scale(img, (int(img.get_width() * 1.5), int(img.get_height() * 1.5)))  
        temp_list.append(img)
    img_list_boss.append(temp_list)

bullet_img = pygame.image.load('img/icons/bullet.png').convert_alpha()
bullet_img2 = pygame.image.load('img/icons/bullet2.png').convert_alpha()

grenade_img = pygame.image.load('img/icons/grenade.png').convert_alpha()
health_box_img = pygame.image.load('img/icons/health_box.png').convert_alpha()
ammo_box_img = pygame.image.load('img/icons/ammo_box.png').convert_alpha()
grenade_box_img = pygame.image.load('img/icons/grenade_box.png').convert_alpha()
item_boxes = {
    'Health'	: health_box_img,
    'Ammo'		: ammo_box_img,
    'Grenade'	: grenade_box_img
}

BG = (144, 201, 120)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
PINK = (235, 65, 54)

font = pygame.font.SysFont('Futura', 30)

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def draw_bg():
    screen.fill(BG)
    width = sky_img.get_width()
    for x in range(5):
        screen.blit(sky_img, ((x * width) - bg_scroll * 0.5, 0))
        screen.blit(mountain_img, ((x * width) - bg_scroll * 0.6, SCREEN_HEIGHT - mountain_img.get_height() - 200))
        screen.blit(pine_img, ((x * width) - bg_scroll * 0.8, SCREEN_HEIGHT - pine_img.get_height()))

def reset_level():
    enemy_group.empty()
    bullet_group.empty()
    grenade_group.empty()
    explosion_group.empty()
    item_box_group.empty()
    decoration_group.empty()
    water_group.empty()
    lava_group.empty()
    exit_group.empty()
    global kill_value
    kill_value = 0
    data = []
    for row in range(ROWS):
        r = [-1] * COLS
        data.append(r)
    return []

class Soldier(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo, grenades):
        pygame.sprite.Sprite.__init__(self)
        self.dead = False
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.ammo = ammo
        self.start_ammo = ammo
        self.gravity = 0.75  # Trọng lực
        self.jump_height = -12  # Lực nhảy
        self.shoot_cooldown = 0
        self.grenades = grenades
        self.health = 100
        self.max_health = self.health
        self.direction = 1
        self.vel_y = 0  # Vận tốc dọc
        self.jump = False
        self.in_air = False  # Đảm bảo kiểm tra trạng thái nhảy chính xác
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        self.move_counter = 0
        self.vision = pygame.Rect(0, 0, 150, 20)
        self.idling = False
        self.idling_counter = 0
        self.double_jump = False  # Biến để kiểm tra đã nhảy lần 2 hay chưa

        # Đọc file spritesheet cho các hành động của soldier
        char_folder = f'img/{self.char_type}'
        frame_counts_dict = None

        if self.char_type == 'player':
            frame_counts_dict = enemy_frame_counts
        elif self.char_type == 'enemy':
            frame_counts_dict = enemy_frame_counts

        if frame_counts_dict:
            for action_name in soldier_standard_actions:
                temp_list = []
                frame_count = frame_counts_dict.get(action_name)

                if frame_count and frame_count > 0:
                    spritesheet_path = f'{char_folder}/{action_name}.png'
                    try:
                        animation_image = pygame.image.load(spritesheet_path).convert_alpha()
                        frame_width = animation_image.get_width() // frame_count
                        frame_height = animation_image.get_height()

                        if frame_width <= 0:
                             raise ValueError(f"Chiều rộng frame tính ra <= 0. Kiểm tra số frame ({frame_count})?")

                        for i in range(frame_count):
                            img = animation_image.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
                            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                            cropped_img = img.subsurface(img.get_bounding_rect())

                            temp_list.append(cropped_img)

                    except FileNotFoundError:
                         print(f"Lỗi: Không tìm thấy file spritesheet '{spritesheet_path}' cho {self.char_type} action '{action_name}'")
                    except ValueError as e:
                         print(f"Lỗi: Số frame ({frame_count}) hoặc kích thước ảnh không hợp lệ cho action '{action_name}' tại '{spritesheet_path}'. Chi tiết: {e}")
                    except Exception as e:
                         print(f"Lỗi không xác định khi nạp spritesheet {self.char_type} '{action_name}': {e}")
                else:
                    print(f"Cảnh báo: Không tìm thấy/Không hợp lệ số frame cho {self.char_type} action '{action_name}'")

                self.animation_list.append(temp_list)

        else:
            print(f"Lỗi: char_type '{self.char_type}' không có frame_counts_dict được định nghĩa.")
            for _ in soldier_standard_actions:
                self.animation_list.append([])

        try:
            self.image = self.animation_list[self.action][self.frame_index]
        except IndexError:
            print(f"LỖI NGHIÊM TRỌNG: Không thể lấy ảnh ban đầu cho {self.char_type} action {self.action}. Nạp animation thất bại!")
            self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.image.fill(RED)

        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        self.update_animation()
        self.check_alive()
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self, moving_left, moving_right):
        screen_scroll = 0
        dx = 0
        dy = 0

        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        # Cơ chế nhảy
        if self.jump == True and self.in_air == False:
            self.vel_y = self.jump_height
            self.jump = False
            self.in_air = True
            self.double_jump = False  # Reset lại khi nhảy lần 2

        if self.jump == True and self.in_air == True and not self.double_jump:
            self.vel_y = self.jump_height  # Nhảy lần thứ hai
            self.jump = False
            self.double_jump = True

        # Áp dụng trọng lực
        self.vel_y += self.gravity
        if self.vel_y > 10:  # Giới hạn vận tốc rơi
            self.vel_y = 10

        dy += self.vel_y

        # Kiểm tra va chạm với các chướng ngại vật
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
                if self.char_type == 'enemy':
                    self.direction *= -1
                    self.move_counter = 0
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                if self.vel_y < 0:  # Khi đang nhảy lên
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                elif self.vel_y >= 0:  # Khi rơi xuống đất
                    self.vel_y = 0
                    self.in_air = False  # Đã chạm đất
                    dy = tile[1].top - self.rect.bottom

        # Kiểm tra va chạm với nước hoặc dung nham
        if pygame.sprite.spritecollide(self, water_group, False):
            self.health -= 0.5

        if pygame.sprite.spritecollide(self, lava_group, False):
            self.health -= 10    

        level_complete = False
        if pygame.sprite.spritecollide(self, exit_group, False):
            level_complete = True

        if self.rect.bottom > SCREEN_HEIGHT:
            self.health = 0

        # Kiểm tra di chuyển của player
        if self.char_type == 'player':
            if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                dx = 0

        self.rect.x += dx
        self.rect.y += dy

        # Kiểm tra cuộn màn hình
        if self.char_type == 'player':
            if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and bg_scroll < (world.level_length * TILE_SIZE) - SCREEN_WIDTH)\
                or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
                self.rect.x -= dx
                screen_scroll = -dx

        return screen_scroll, level_complete

    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20
            if self.char_type == 'player':
                from_player = True
            else:
                from_player = False
            bullet = Bullet(self.rect.centerx + ( 1* self.rect.size[0] * self.direction), self.rect.centery, self.direction, from_player)
            bullet_group.add(bullet)
            self.ammo -= 1
            shot_fx.play()

    def ai(self):
        if self.alive and player.alive:
            if self.idling == False and random.randint(1, 200) == 1:
                self.update_action(0)
                self.idling = True
                self.idling_counter = 50
            if self.vision.colliderect(player.rect):
                self.update_action(0)
                self.shoot()
            else:
                if self.idling == False:
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1)
                    self.move_counter += 1
                    self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)

                    if self.move_counter > TILE_SIZE:
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False

        self.rect.x += screen_scroll

    def update_animation(self):
        ANIMATION_COOLDOWN = 100
        self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0

    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.health <= 0 and not self.dead:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)
            self.dead = True
            global kill_value
            kill_value += 1
        if not self.in_air:
            self.double_jump = False  # Reset double jump khi chạm đất
            self.jump_count = 0


    def draw(self):
        # Giả sử self.rect đã chứa vị trí chính xác trên màn hình (đã bao gồm scroll)
        # do được cập nhật trong phương thức ai()
        base_draw_rect = self.rect

        # Tạo một bản sao để có thể sửa đổi cho việc vẽ
        final_draw_rect = base_draw_rect.copy()

        # Nếu soldier (enemy) đã chết, dịch chuyển vị trí vẽ xuống dưới
        if self.dead:
            final_draw_rect.y += TILE_SIZE  # <-- Dòng chính để hạ thấp xác enemy

        # Vẽ hình ảnh soldier tại vị trí cuối cùng đã tính toán
        screen.blit(pygame.transform.flip(self.image, self.flip, False), final_draw_rect)

        # Vẽ hình chữ nhật tầm nhìn (vision) cho mục đích debug (chỉ khi còn sống)
        # Giả sử self.vision đã ở đúng tọa độ màn hình vì nó được cập nhật
        # dựa trên self.rect trong phương thức ai().
        # if self.alive:
            #  pygame.draw.rect(screen, (0, 0, 255), self.vision, 2) # Giữ nguyên logic vẽ vision gốc, nhưng chỉ khi còn sống


class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y, scale, speed):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.speed = speed
        self.health = 100
        self.dead = False
        self.max_health = self.health
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = img_list_boss
        self.frame_index = 0
        self.action = 5
        self.update_time = pygame.time.get_ticks()
        self.attack_cooldown = 0
        self.attacking = False
        self.vision = pygame.Rect(0, 0, 300, 20)
        self.scale=scale
        self.image = self.animation_list[self.action][self.frame_index]
        self.image = pygame.transform.scale(self.image, (int(self.image.get_width() * scale), int(self.image.get_height() * scale)))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.death_world_x = 0  # Thêm thuộc tính mới
        self.death_world_y = 0

        self.left_bound =  (x // TILE_SIZE - 5) * TILE_SIZE
        self.right_bound = (x // TILE_SIZE + 5) * TILE_SIZE

    def update(self):
        self.update_animation()
        self.check_alive()
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
            
    def draw_health_bar(self, surface):
        ratio=self.health/self.max_health
        bar_width=150
        bar_height=20
        bar_x=self.rect.centerx-bar_width//2
        bar_y=self.rect.top + 10
        pygame.draw.rect(surface,(0,0,0),(bar_x-1,bar_y-1,bar_width+2,bar_height+2))
        pygame.draw.rect(surface,(255,0,0),(bar_x,bar_y,bar_width,bar_height))
        pygame.draw.rect(surface,(0,255,0),(bar_x,bar_y,int(bar_width*ratio),bar_height))

    def move(self):
        dx = 0
        dy = 0
        if self.direction == 1:
            dx = self.speed
            self.flip = False
        else:
            dx = -self.speed
            self.flip = True
        absolute_x = self.rect.x + bg_scroll + dx
        if absolute_x < self.left_bound:
            self.direction = 1
            self.flip = False
            self.update_action(7)
            dx = self.speed
        elif absolute_x > self.right_bound:
            self.direction = -1
            self.flip = True
            self.update_action(7)
            dx = -self.speed
        self.rect.x += dx


    def ai(self):
        if self.alive and player.alive:
            vision_offset_x = 75
            self.vision.center = (self.rect.centerx + self.direction * vision_offset_x, self.rect.centery)

            if self.vision.colliderect(player.rect) and self.attack_cooldown == 0 and not self.attacking:
                self.attack()
                self.attack_cooldown = 120
            elif not self.attacking:
                if self.action == 5:
                    self.update_action(7)
                if self.action == 7 or self.action == 9:
                    self.move()

        if self.alive:
             self.rect.x += screen_scroll

    def attack(self):
        if not self.attacking:
            self.attacking = True
            attack_animation_index = random.choice([0, 1, 2])
            self.update_action(attack_animation_index)
            attack_range = 60
            attack_height = self.height * 0.8
            attack_y_offset = self.height * 0.1

            attack_hitbox_world = None
            if self.direction == 1:
                attack_hitbox_world = pygame.Rect(
                    self.rect.right,
                    self.rect.top + attack_y_offset,
                    attack_range,
                    attack_height
                )
            else:
                attack_hitbox_world = pygame.Rect(
                    self.rect.left - attack_range,
                    self.rect.top + attack_y_offset,
                    attack_range,
                    attack_height
                )

            if attack_hitbox_world:
                player_hitbox = getattr(player, 'hitbox', player.rect)
                if attack_hitbox_world.colliderect(player_hitbox):
                    if player.alive:
                        player_damage = 25
                        player.health -= player_damage

    def draw(self, surface):
        
    # Xác định vị trí vẽ dựa trên trạng thái sống/chết
        if self.alive:
            # Khi còn sống: vị trí tính theo scroll hiện tại
            draw_rect = self.rect.move(screen_scroll, 0)
        else:
            # Khi đã chết: tính vị trí dựa trên world position và bg_scroll
            draw_x = self.death_world_x - bg_scroll
            draw_rect = pygame.Rect(draw_x, self.death_world_y, self.width, self.height)

        # Vẽ boss
        surface.blit(pygame.transform.flip(self.image, self.flip, False), draw_rect)

        # Vẽ thanh máu (chỉ khi còn sống)
        if self.alive:
            
            ratio = self.health / self.max_health
            bar_width = 150
            bar_height = 10
            bar_x = draw_rect.centerx - bar_width // 2
            bar_y = draw_rect.top - 15
            
            # Vẽ background thanh máu
            pygame.draw.rect(surface, (0, 0, 0), (bar_x - 1, bar_y - 1, bar_width + 2, bar_height + 2))
            
            # Vẽ thanh máu hiện tại
            pygame.draw.rect(surface, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))
            pygame.draw.rect(surface, (0, 255, 0), (bar_x, bar_y, int(bar_width * ratio), bar_height))

        # Debug vision rect (chỉ khi còn sống)
        if self.alive : # SHOW_DEBUG là biến global bạn có thể định nghĩa
            vision_screen_rect = self.vision.move(screen_scroll, 0)
            pygame.draw.rect(surface, (0, 0, 255), vision_screen_rect, 2)
    


    def update_animation(self):
        ANIMATION_COOLDOWN = 150
        self.image = self.animation_list[self.action][self.frame_index]
        self.image = pygame.transform.scale(self.image, (int(self.image.get_width() * self.scale), int(self.image.get_height() * self.scale)))
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0
                if self.action in (0, 1, 2):
                    self.attacking = False
                    if self.vision.colliderect(player.rect) and self.attack_cooldown == 0:
                        self.attacking()
                    else:
                        self.update_action(7)
                elif self.action in (7, 9):
                    self.update_action(self.action)

    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.health <= 0 and not self.dead:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3) 
            self.dead = True
            self.death_world_x = self.rect.x - screen_scroll
            self.death_world_y = self.rect.y



class Water(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll

class World():
    def __init__(self):
        self.obstacle_list = []
        self.level_length = 0
    def process_data(self, data):
        if not data:
            return None, None   
        player = None
        health_bar = None

        self.level_length = len(data[0])

        boss_created = False
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0 and tile != 50:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    if tile >= 0 and tile <= 7:
                        self.obstacle_list.append(tile_data)
                    elif tile == 8:
                        lava = Lava(img, x * TILE_SIZE, y * TILE_SIZE)
                        lava_group.add(lava)
                    elif tile >= 9 and tile <= 10:
                        water = Water(img, x * TILE_SIZE, y * TILE_SIZE)
                        water_group.add(water)
                    elif tile >= 11 and tile <= 14:
                        decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
                        decoration_group.add(decoration)
                    elif tile == 15:
                        player = Soldier('player', x * TILE_SIZE, y * TILE_SIZE, 1, 5, 20, 5)
                        player.health += 300
                        health_bar = HealthBar(10, 10, player.health, player.health)
                    elif tile == 16:
                        enemy = Soldier('enemy', x * TILE_SIZE, y * TILE_SIZE, 1, 2, 20, 0)
                        enemy_group.add(enemy)
                    elif tile == 17:
                        item_box = ItemBox('Ammo', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 18:
                        item_box = ItemBox('Grenade', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 19:
                        item_box = ItemBox('Health', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 20 :  # Boss chết mới tạo exit
                        exit = Exit(img, x * TILE_SIZE, y * TILE_SIZE)
                        exit_group.add(exit)

                elif tile == 50 and not boss_created:
                        img = img_list_boss[5][0]
                        img_rect = img.get_rect()
                        img_rect.x = x * TILE_SIZE
                        img_rect.y = y * TILE_SIZE
                        tile_data = (img, img_rect)
                        boss = Boss(x * TILE_SIZE, y * TILE_SIZE, 1.5, 2)
                        enemy_group.add(boss)
                        boss_created = True

        return player, health_bar

    def draw(self):
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])

    def draw_ruler(self):
        pygame.draw.line(screen, WHITE, (0 - screen_scroll, 20), (self.level_length * TILE_SIZE - screen_scroll, 20))

        for i in range(0, self.level_length * TILE_SIZE + 1, 100):
            pygame.draw.line(screen, WHITE, (i - bg_scroll, 15), (i - bg_scroll, 25))
            if 0 <= i - bg_scroll <= SCREEN_WIDTH:
                draw_text(str(i), font, WHITE, i - bg_scroll, 0)

class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll

class Lava(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll

class Exit(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll

class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll
        if pygame.sprite.collide_rect(self, player):
            if self.item_type == 'Health':
                player.health += 25
                if player.health > 400:
                    player.health = 400
            elif self.item_type == 'Ammo':
                player.ammo += 15
            elif self.item_type == 'Grenade':
                player.grenades += 3
            self.kill()

class HealthBar():
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        self.health = health
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24))
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, from_player):
        pygame.sprite.Sprite.__init__(self)
        if from_player == True:
            self.speed = 6
        else:
            self.speed = 3
        self.image = bullet_img2
        self.image = pygame.transform.scale(self.image, (int(self.image.get_width() * 0.15), int(self.image.get_height() * 0.15)))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction
        self.from_player = from_player
    def update(self):
        self.rect.x += (self.direction * self.speed) + screen_scroll
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()
        if self.from_player: 
            for enemy in enemy_group:
                if pygame.sprite.spritecollide(enemy, bullet_group, False):
                    if enemy.alive:
                        enemy.health -= 60
                        self.kill()
        else:  # If the bullet is from the enemy, it damages the player
            if pygame.sprite.spritecollide(player, bullet_group, False):
                if player.alive:
                    player.health -= 5
                    self.kill()


class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.vel_y = -11
        self.speed = 7
        self.image = grenade_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.direction = direction

    def update(self):
        self.vel_y += GRAVITY
        dx = self.direction * self.speed
        dy = self.vel_y

        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                self.direction *= -1
                dx = self.direction * self.speed
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                self.speed = 0
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    dy = tile[1].top - self.rect.bottom	

        self.rect.x += dx + screen_scroll
        self.rect.y += dy

        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            grenade_fx.play()
            explosion = Explosion(self.rect.x, self.rect.y, 0.5)
            explosion_group.add(explosion)
            if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2 and \
                abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 2:
                player.health -= 50
            for enemy in enemy_group:
                if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2 and \
                    abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 2:
                    enemy.health -= 50

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1, 6):
            img = pygame.image.load(f'img/explosion/exp{num}.png').convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            self.images.append(img)
        self.frame_index = 0
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0

    def update(self):
        self.rect.x += screen_scroll

        EXPLOSION_SPEED = 4
        self.counter += 1

        if self.counter >= EXPLOSION_SPEED:
            self.counter = 0
            self.frame_index += 1
            if self.frame_index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame_index]

class ScreenFade():
    def __init__(self, direction, colour, speed):
        self.direction = direction
        self.colour = colour
        self.speed = speed
        self.fade_counter = 0

    def fade(self):
        fade_complete = False
        self.fade_counter += self.speed
        if self.direction == 1:
            pygame.draw.rect(screen, self.colour, (0 - self.fade_counter, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.colour, (SCREEN_WIDTH // 2 + self.fade_counter, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.colour, (0, 0 - self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
            pygame.draw.rect(screen, self.colour, (0, SCREEN_HEIGHT // 2 +self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT))
        if self.direction == 2:
            pygame.draw.rect(screen, self.colour, (0, 0, SCREEN_WIDTH, 0 + self.fade_counter))
        if self.fade_counter >= SCREEN_WIDTH:
            fade_complete = True
        return fade_complete

intro_fade = ScreenFade(1, BLACK, 4)
death_fade = ScreenFade(2, PINK, 4)
# start_button = button.Button(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 - 150, start_img, 1)
# exit_button = button.Button(SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2 + 150, exit_img, 1)
# setting_button = button.Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, setting_img, 1)   # Đặt nút Setting bên dưới nút Restart
button_spacing = 150  # Khoảng cách giữa các nút
start_y = SCREEN_HEIGHT // 2 - 200  # Vị trí y của nút đầu tiên

# Khởi tạo các nút
start_button = button.Button(
    SCREEN_WIDTH // 2 - standard_width // 2,  # Căn giữa trục x
    start_y, 
    start_img, 
    1
)

setting_button = button.Button(
    SCREEN_WIDTH // 2 - standard_width // 2, 
    start_y + button_spacing,  # Thêm khoảng cách
    setting_img, 
    1
)

exit_button = button.Button(
    SCREEN_WIDTH // 2 - standard_width // 2, 
    start_y + 2 * button_spacing,  # Thêm khoảng cách x2
    exit_img, 
    1
)


enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

world_data = []
for row in range(ROWS):
    r = [-1] * COLS
    world_data.append(r)
with open(f'level{level}_data.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    world_data = []
    for row in reader:
        world_data.append([int(tile) for tile in row])

world = World()
player, health_bar = world.process_data(world_data)

run = True
while run:

    clock.tick(FPS)

    if not start_game and not show_setting_menu:
        screen.fill(BG)
        if start_button.draw(screen):
            start_game = True
            start_intro = True
        if exit_button.draw(screen):
            run = False
        if setting_button.draw(screen):
            show_setting_menu = True

    # ========== MENU SETTING ==========
    elif show_setting_menu:
    # Kích thước từng cột và hàng
        col_width = SCREEN_WIDTH // 2
        row_height = SCREEN_HEIGHT // 2

        # Scale ảnh theo kích thước từng khung
        label_size = (col_width - 40, row_height - 40)
        toggle_size = (col_width - 40, row_height - 40)

        doublejump_scaled = pygame.transform.scale(doublejump_img, label_size)
        sound_scaled = pygame.transform.scale(sound_img, label_size)
        on_scaled = pygame.transform.scale(on_img, toggle_size)
        off_scaled = pygame.transform.scale(off_img, toggle_size)

        # Vẽ giao diện chia 2x2
        screen.blit(doublejump_scaled, (20, 20))
        screen.blit(on_scaled if double_jump_on else off_scaled, (col_width + 20, 20))

        screen.blit(sound_scaled, (20, row_height + 20))
        screen.blit(on_scaled if sound_on else off_scaled, (col_width + 20, row_height + 20))


    
    else:
        draw_bg()
        world.draw()
        world.draw_ruler()
        if player and health_bar:
            health_bar.draw(player.health)
            player.update()
            player.draw()

        draw_text('AMMO: ', font, BLACK, 10, 35)
        for x in range(player.ammo):
            screen.blit(bullet_img, (90 + (x * 10), 40))
        draw_text('GRENADES: ', font, BLACK, 10, 60)
        for x in range(player.grenades):
            screen.blit(grenade_img, (135 + (x * 15), 60))

        kill_img = font.render(str(kill_value), True, pygame.Color('black'))
        draw_text('KILL: ', font, RED, 610, 40)
        screen.blit(kill_img, (690 , 40))
        level_img = font.render(str(level), True, pygame.Color('black'))
        draw_text('LEVEL: ', font, GREEN, 610, 10)
        if level == 0:
            draw_text('TUTORIAL', font, BLACK, 695, 10)
        elif level >= 0 and level <= 3:
            screen.blit(level_img, (690, 10))




        for enemy in enemy_group:
            enemy.ai()
            enemy.update()
            if isinstance(enemy, Boss):
                enemy.draw(screen)
                if not enemy.alive:  # Chỉ vẽ exit khi boss chết
                    # Nếu boss chết, vẽ exit

                    exit_group.draw(screen)
                    level_complete = True


            else:
                enemy.draw()        

        bullet_group.update()
        grenade_group.update()
        explosion_group.update()
        item_box_group.update()
        decoration_group.update()
        water_group.update()
        lava_group.update()
        exit_group.update()
        bullet_group.draw(screen)
        grenade_group.draw(screen)
        explosion_group.draw(screen)
        item_box_group.draw(screen)
        decoration_group.draw(screen)
        water_group.draw(screen)
        lava_group.draw(screen)

        if start_intro == True:
            if intro_fade.fade():
                start_intro = False
                intro_fade.fade_counter = 0

        if player.alive:
            if shoot:
                player.shoot()
            elif grenade and grenade_thrown == False and player.grenades > 0:
                grenade = Grenade(player.rect.centerx + (0.5 * player.rect.size[0] * player.direction),\
                             player.rect.top, player.direction)
                grenade_group.add(grenade)
                player.grenades -= 1
                grenade_thrown = True
            if player.in_air:
                player.update_action(2)
            elif moving_left or moving_right:
                player.update_action(1)
            else:
                player.update_action(0)
            screen_scroll, level_complete = player.move(moving_left, moving_right)
            bg_scroll -= screen_scroll
            if level_complete:
                start_intro = True
                level += 1
                bg_scroll = 0
                world_data = reset_level()
         

                if level <= MAX_LEVELS:
                    with open(f'level{level}_data.csv', newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        world_data = []
                        for row in reader:
                            world_data.append([int(tile) for tile in row])
                    world = World()
                    player, health_bar = world.process_data(world_data)
        else:
            screen_scroll = 0
            if death_fade.fade():
                if restart_button.draw(screen):
                    death_fade.fade_counter = 0
                    start_intro = True
                    bg_scroll = 0
                    kill_value = 0
                    world_data = reset_level()
                    with open(f'level{level}_data.csv', newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        world_data = []
                        for row in reader:
                            world_data.append([int(tile) for tile in row])
                    world = World()
                    player, health_bar = world.process_data(world_data)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_SPACE:
                shoot = True
            if event.key == pygame.K_q:
                grenade = True
            if event.key == pygame.K_w and player.alive:
                player.jump = True
                jump_fx.play()
            if event.key == pygame.K_ESCAPE:
                run = False

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_SPACE:
                shoot = False
            if event.key == pygame.K_q:
                grenade = False
                grenade_thrown = False

    pygame.display.update()

pygame.quit()
