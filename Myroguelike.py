import pygame
import os
import sys
import datetime
import random


MAP_FILE = "level1.map"


def loadCharacterSpritesheet(filename, xRes, yRes, xNum, yNum, xScale=1, yScale=1, colorkey=None, d_x=0, d_y=0, d_x1=0,
                             d_y1=0):
    file = pygame.image.load(filename).convert()
    output = []
    for i in range(0, yNum):
        images = []
        for x in range(xNum):
            rect = pygame.Rect((xRes * x + d_x, yRes * i + d_y, xRes + d_x1, yRes + d_y1))
            image = pygame.Surface(rect.size).convert()
            image.blit(file, (0, 0), rect)
            if colorkey is not None:
                if colorkey == -1:
                    colorkey = image.get_at((0, 0))
                image.set_colorkey(colorkey, pygame.RLEACCEL)
            image = pygame.transform.scale(image, (xRes * xScale, yRes * yScale))
            #  pygame.image.save(image, f'{i}_{x}_{os.path.basename(filename)}')
            images.append((image, image.get_rect()))
        output.extend(images)
    return output


def loadSpritesheet(filename, xRes, yRes, xNum, yNum, xScale=1, yScale=1, colorkey=None, d_x=0, d_y=0, d_x1=0, d_y1=0):
    file = pygame.image.load(filename).convert()
    output = []
    for i in range(0, yNum):
        images = []
        for x in range(xNum):
            rect = pygame.Rect((xRes * x + d_x, yRes * i + d_y, xRes + d_x1, yRes + d_y1))
            image = pygame.Surface(rect.size).convert()
            image.blit(file, (0, 0), rect)
            if colorkey is not None:
                if colorkey == -1:
                    colorkey = image.get_at((0, 0))
                image.set_colorkey(colorkey, pygame.RLEACCEL)
            image = pygame.transform.scale(image, (xRes * xScale, yRes * yScale))
            #  pygame.image.save(image, f'{i}_{x}_{os.path.basename(filename)}')
            images.append((image, image.get_rect()))
        output.extend(images)
    return output


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    if color_key is not None:
        image = pygame.image.load(fullname).convert()
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = pygame.image.load(fullname).convert_alpha()
    return image


pygame.init()
WIDTH, HEIGHT = 850, 600
screen_size = (WIDTH, HEIGHT)
screen = pygame.display.set_mode(screen_size)

FPS = 50

TILE_IMAGES = {
    'wall': [load_image('wall.png'), load_image('wall.png'), load_image('wall2.png')],
    'empty': [load_image('floor.png'), load_image('floor.png'),
              load_image('floor1.png'), load_image('floor2.png'), load_image('floor3.png'), load_image('floor4.png')],
    'void': [load_image('void.png')]
}
PLAYER_IMAGES = [
    loadCharacterSpritesheet('data/Hero_sprites/Idle.png', 140, 140, 11, 1, 0.357, 0.357, -1, 40, 30, -80, -80),
    loadCharacterSpritesheet('data/Hero_sprites/Attack.png', 140, 140, 8, 1, 0.357, 0.357, -1)]
ENEMY_IMAGES = {
    'spearman_not_arm': load_image('Enemies/Skeleton_Spearman Not Armored2.png', -1),
    'skeleton_mage': load_image('Enemies/Skeleton_Mage Not Hooded2.png', -1),
    'mag_ball': load_image('Enemies/mag_ball.png', -1)
}
TILE_WIDTH = TILE_HEIGHT = 50
HEARTS_IMAGES = [load_image('heart.png'), load_image('empty_heart.png')]
TRAPS_IMAGES = {
    'fire': [loadSpritesheet('data/Traps/Fire_Trap.png', 32, 41, 14, 1, 1.5, 1.5, -1, 0, 13)],
    'spike': [loadSpritesheet('data/Traps/Spike_Trap.png', 32, 41, 14, 1, 1.5, 1.5, -1, 0, 0)],
    'pit': [[[load_image('Traps/Pit_trap_Spikes2.png')]]]
}
TREASURE_IMAGES = [loadSpritesheet('data/Treasure+/chest.png', 40, 40, 4, 1, 1, 1, -1)]
ALL_TILES = []
ALL_ENEMIES = []
ALL_TRAPS = []
ALL_CHESTS = []
ALL_MAG_BALLS = []


class SpriteGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()

    def get_event(self, event):
        for sprite in self:
            sprite.get_event(event)


class Sprite(pygame.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)
        self.rect = None

    def get_event(self, event):
        pass


class Tile(Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(sprite_group)
        self.tile_type = tile_type
        self.true_image = random.choice(TILE_IMAGES[self.tile_type])
        self.image = TILE_IMAGES['void'][0]
        self.rect = self.image.get_rect().move(
            TILE_WIDTH * pos_x, TILE_HEIGHT * pos_y)
        self.init_pos = (self.rect.x, self.rect.y)
        self.is_visible = False


class Trap(Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(trap_group)
        self.num_fire_sprite = 0
        self.num_spike_sprite = 0
        self.num_push_sprite = 0
        self.tile_type = tile_type
        self.true_image = TRAPS_IMAGES[self.tile_type][0][0][0]
        self.image = TILE_IMAGES['void'][0]
        self.rect = self.image.get_rect().move(
            TILE_WIDTH * pos_x, TILE_HEIGHT * pos_y)
        self.init_pos = (self.rect.x, self.rect.y)
        self.is_visible = False


class Player(Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(hero_group)
        self.image = PLAYER_IMAGES[0][0][0]
        self.direction = 'right'
        self.rect = self.image.get_rect().move(
            TILE_WIDTH * pos_x, TILE_HEIGHT * pos_y)
        self.tile_pos = (pos_x, pos_y)
        self.health = 5
        self.attacking = False
        self.num_attack_sprite = 0
        self.num_idle_sprite = 0

    def move(self, x, y):
        if not camera.check_viewpoint(x, y):
            camera.dx -= (x - self.tile_pos[0])
            camera.dy -= (y - self.tile_pos[1])

            camera.centre_x += (x - self.tile_pos[0])
            camera.centre_y += (y - self.tile_pos[1])

            for sprite in sprite_group:
                camera.apply(sprite)
            for sprite in enemy_group:
                camera.enemy_apply(sprite)
            for sprite in trap_group:
                camera.apply(sprite)
            for sprite in treasure_group:
                camera.apply(sprite)
        self.tile_pos = (x, y)
        for sprite in hero_group:
            camera.hero_apply(sprite)


class HealthBar(Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(heart_group)
        self.image = HEARTS_IMAGES[0]
        self.rect = self.image.get_rect().move(
            TILE_WIDTH * pos_x, TILE_HEIGHT * pos_y)
        self.init_pos = (pos_x, pos_y)
        self.isfull = True


class Enemy(Sprite):
    def __init__(self, enemy_type, pos_x, pos_y, route, hp):
        super().__init__(enemy_group)
        self.true_image = ENEMY_IMAGES[enemy_type]
        self.image = TILE_IMAGES['void'][0]
        self.rect = self.image.get_rect().move(
            TILE_WIDTH * pos_x, TILE_HEIGHT * pos_y)
        self.abs_pos = [self.rect.x, self.rect.y]
        self.route = route
        self.route_index = 0
        self.hp = hp
        self.is_visible = False

    def move(self):
        current_direction = self.route[self.route_index]
        if current_direction == 1:
            self.abs_pos[0] -= 1 * TILE_WIDTH
        elif current_direction == 2:
            self.abs_pos[1] -= 1 * TILE_HEIGHT
        elif current_direction == 3:
            self.abs_pos[0] += 1 * TILE_WIDTH
        elif current_direction == 4:
            self.abs_pos[1] += 1 * TILE_WIDTH
        self.route_index = (self.route_index + 1) % len(self.route)
        for sprite in enemy_group:
            camera.enemy_apply(sprite)


class RangeEnemy(Sprite):
    def __init__(self, enemy_type, pos_x, pos_y, direction, hp):
        super().__init__(enemy_group)
        self.true_image = ENEMY_IMAGES[enemy_type]
        self.image = TILE_IMAGES['void'][0]
        self.rect = self.image.get_rect().move(
            TILE_WIDTH * pos_x, TILE_HEIGHT * pos_y)
        self.abs_pos = [self.rect.x, self.rect.y]
        self.hp = hp
        self.is_visible = False
        self.direction = direction
        ALL_MAG_BALLS.append(MagicBall(pos_x, pos_y, direction))

    def move(self):
        pass

    #def shot(self):
    #    MagicBall


class MagicBall(Sprite):
    def __init__(self, pos_x, pos_y, direction):
        super().__init__(enemy_group)
        self.true_image = ENEMY_IMAGES['mag_ball']
        self.image = TILE_IMAGES['void'][0]
        self.rect = self.image.get_rect().move(
            TILE_WIDTH * pos_x, TILE_HEIGHT * pos_y)
        self.abs_pos = [self.rect.x, self.rect.y]
        self.start_pos = [pos_x * TILE_WIDTH, pos_y * TILE_HEIGHT]
        self.is_visible = False
        self.direction = direction
        self.iteration = 0

    def move(self):
        if self.iteration == 5:
            self.iteration = 0
            self.abs_pos = self.start_pos[:]
        elif self.direction == 'left':
            self.abs_pos[0] -= 1 * TILE_WIDTH
        elif self.direction == 'up':
            self.abs_pos[1] -= 1 * TILE_HEIGHT
        elif self.direction == 'right':
            self.abs_pos[0] += 1 * TILE_WIDTH
        elif self.direction == 'down':
            self.abs_pos[1] += 1 * TILE_WIDTH
        for sprite in enemy_group:
            camera.enemy_apply(sprite)
        self.iteration += 1


class Treasure(Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(treasure_group)
        self.true_image = TREASURE_IMAGES[0][0][0]
        self.image = TILE_IMAGES['void'][0]
        self.rect = self.image.get_rect().move(
            TILE_WIDTH * pos_x + 5, TILE_HEIGHT * pos_y + 5)
        self.init_pos = (self.rect.x, self.rect.y)
        self.is_visible = False


class Camera:
    def __init__(self, hero):
        self.dx = 0
        self.dy = 0
        self.centre_x = hero.tile_pos[0]
        self.centre_y = hero.tile_pos[1]
        self.view_point_width = 4
        self.view_point_height = 4

    def check_viewpoint(self, x, y):
        if self.centre_x - self.view_point_width // 2 < x < self.centre_x + self.view_point_width // 2 \
                and self.centre_y - self.view_point_height // 2 < y < self.centre_y + self.view_point_height // 2:
            return True
        return False

    def apply(self, obj):
        obj.rect.x = obj.init_pos[0] + self.dx * TILE_WIDTH
        obj.rect.y = obj.init_pos[1] + self.dy * TILE_HEIGHT

    def enemy_apply(self, obj):
        obj.rect.x = obj.abs_pos[0] + self.dx * TILE_WIDTH
        obj.rect.y = obj.abs_pos[1] + self.dy * TILE_HEIGHT

    def hero_apply(self, obj):
        obj.rect.x = obj.tile_pos[0] * TILE_WIDTH + self.dx * TILE_WIDTH
        obj.rect.y = obj.tile_pos[1] * TILE_HEIGHT + self.dy * TILE_HEIGHT

    def update(self, target):
        self.dx = 0
        self.dy = 0


player = None
running = True
clock = pygame.time.Clock()
sprite_group = SpriteGroup()
hero_group = SpriteGroup()
enemy_group = SpriteGroup()
heart_group = SpriteGroup()
trap_group = SpriteGroup()
treasure_group = SpriteGroup()


def clear_groups():
    global sprite_group, hero_group, enemy_group, heart_group, trap_group, treasure_group
    sprite_group = SpriteGroup()
    hero_group = SpriteGroup()
    enemy_group = SpriteGroup()
    heart_group = SpriteGroup()
    trap_group = SpriteGroup()
    treasure_group = SpriteGroup()


def terminate():
    pygame.quit()
    sys.exit()


def check_button_click(btn, pos):
    if btn[0] < pos[0] < btn[0] + btn[2] and btn[1] < pos[1] < btn[1] + btn[3]:
        return True
    return False


class TextObj:
    def __init__(self, text, x, y, font_size, color, is_center=False, btn_size=None):
        self.string_rendered, self.font = None, None
        self.text = text
        self.font_size = font_size
        self.color = color
        self.x, self.y = x, y
        self.is_center = is_center
        self.text_render()
        if btn_size is None:
            self.button_rect = (self.rect.x, self.rect.y, self.rect.width, self.rect.height)
        else:
            self.button_rect = btn_size

    def text_render(self):
        self.font = pygame.font.Font('data/mael1.ttf', self.font_size)
        self.string_rendered = self.font.render(self.text, True, self.color)
        self.rect = self.string_rendered.get_rect()
        if not self.is_center:
            self.rect.x = self.x
        else:
            self.rect.centerx = self.x
        self.rect.top = self.y
        screen.blit(self.string_rendered, self.rect)

    def change_color(self, color):
        self.color = color
        self.string_rendered.set_colorkey(self.color)
        self.string_rendered = self.font.render(self.text, True, self.color)
        screen.blit(self.string_rendered, self.rect)

    def change_text(self, text):
        self.text = text
        self.string_rendered = self.font.render(self.text, True, self.color)
        screen.blit(self.string_rendered, self.rect)


def start_screen():
    fon = pygame.transform.scale(load_image('start_screen.jpg'), screen_size)
    screen.blit(fon, (0, 0))

    TextObj("ROGUELIKE", WIDTH // 2, 180, 100, pygame.Color('black'), True)
    start_btn = TextObj("NEW GAME", WIDTH // 2, 300, 40, pygame.Color('black'), True)
    settings_btn = TextObj("SETTINGS", WIDTH // 2, 360, 35, pygame.Color('black'), True)
    while True:
        for event in pygame.event.get():
            on_start_btn = check_button_click(start_btn.button_rect, pygame.mouse.get_pos())
            on_settings_btn = check_button_click(settings_btn.button_rect, pygame.mouse.get_pos())
            if event.type == pygame.QUIT:
                terminate()
            elif on_start_btn:
                start_btn.change_color(pygame.Color('white'))
                if event.type == pygame.MOUSEBUTTONDOWN:
                    clear_groups()
                    restart()
                    return
            elif on_settings_btn:
                settings_btn.change_color(pygame.Color('white'))
                if event.type == pygame.MOUSEBUTTONDOWN:
                    settings()
            if not on_start_btn:
                start_btn.change_color(pygame.Color('black'))
            if not on_settings_btn:
                settings_btn.change_color(pygame.Color('black'))

        pygame.display.flip()
        clock.tick(FPS)


def settings():
    global SOUND_VOLUME, EFFECT_VOLUME
    back_ground_image = load_image('pause_background.jpg')
    fon = pygame.transform.scale(back_ground_image, (375, 483))
    screen.blit(fon, (WIDTH // 2 - 187, HEIGHT // 2 - 241))
    TextObj("ROGUELIKE", WIDTH // 2, 140, 70, pygame.Color('black'), True)
    TextObj("SETTINGS", WIDTH // 2, 220, 60, pygame.Color('red'), True)
    TextObj("VOLUME", WIDTH // 2, 270, 60, pygame.Color('black'), True)
    minus_btn = TextObj("-", WIDTH // 2 - 100, 300, 120, pygame.Color('black'), True)
    plus_btn = TextObj("+", WIDTH // 2 + 100, 300, 120, pygame.Color('black'), True)
    #  leave_btn = TextObj("+", WIDTH // 2 + 100, 300, 120, pygame.Color('black'), True)
    # status_volume = TextObj(str(SOUND_VOLUME * 100), WIDTH // 2, 330, 70, pygame.Color('black'), True)
    while True:
        for event in pygame.event.get():
            on_minus_btn = check_button_click(minus_btn.button_rect, pygame.mouse.get_pos())
            on_plus_btn = check_button_click(plus_btn.button_rect, pygame.mouse.get_pos())
            if event.type == pygame.QUIT:
                terminate()
            elif on_minus_btn:
                minus_btn.change_color(pygame.Color('white'))
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if SOUND_VOLUME > 0:
                        SOUND_VOLUME -= 0.01
                        # status_volume.chacge_text(str(SOUND_VOLUME * 100))
                    pygame.mixer.music.set_volume(SOUND_VOLUME)

            elif on_plus_btn:
                plus_btn.change_color(pygame.Color('white'))
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if SOUND_VOLUME < 0.1:
                        SOUND_VOLUME += 0.01
                    pygame.mixer.music.set_volume(SOUND_VOLUME)

            if not on_plus_btn:
                plus_btn.change_color(pygame.Color('black'))
            if not on_minus_btn:
                minus_btn.change_color(pygame.Color('black'))

        pygame.display.flip()
        clock.tick(FPS)


def game_over():
    back_ground_image = load_image('game_over.jpg')
    fon = pygame.transform.scale(back_ground_image,
                                 (back_ground_image.get_rect()[2] + 120, back_ground_image.get_rect()[3] + 120))
    screen.blit(fon, (WIDTH // 2 - (back_ground_image.get_rect()[2] + 120) // 2,
                      HEIGHT // 2 - (back_ground_image.get_rect()[3] + 120) // 2))
    TextObj("ROGUELIKE", WIDTH // 2, 140, 70, pygame.Color('black'), True)
    TextObj(" GAME OVER", WIDTH // 2, 220, 60, pygame.Color('red'), True)
    again_btn = TextObj("NEW GaME", WIDTH // 2, 300, 40, pygame.Color('black'), True)
    settings_btn = TextObj("SETTINGS", WIDTH // 2, 360, 40, pygame.Color('black'), True)
    menu_btn = TextObj("MEIN MENU", WIDTH // 2, 420, 40, pygame.Color('black'), True)

    while True:
        for event in pygame.event.get():
            on_again_btn = check_button_click(again_btn.button_rect, pygame.mouse.get_pos())
            on_settings_btn = check_button_click(settings_btn.button_rect, pygame.mouse.get_pos())
            on_menu_btn = check_button_click(menu_btn.button_rect, pygame.mouse.get_pos())
            if event.type == pygame.QUIT:
                terminate()
            elif on_again_btn:
                again_btn.change_color(pygame.Color('white'))
                if event.type == pygame.MOUSEBUTTONDOWN:
                    return 1
            elif on_settings_btn:
                settings_btn.change_color(pygame.Color('white'))
                if event.type == pygame.MOUSEBUTTONDOWN:
                    settings()
            elif on_menu_btn:
                menu_btn.change_color(pygame.Color('white'))
                if event.type == pygame.MOUSEBUTTONDOWN:
                    return 2
            if not on_again_btn:
                again_btn.change_color(pygame.Color('black'))
            if not on_menu_btn:
                menu_btn.change_color(pygame.Color('black'))
            if not on_settings_btn:
                settings_btn.change_color(pygame.Color('black'))
        pygame.display.flip()
        clock.tick(FPS)


def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: list(x.ljust(max_width, '&')), level_map))


MAGE_CAST_DIRECTIONS = ['down', 'down', 'down', 'down', 'right', 'right', 'up', 'down', 'up', 'up',
                        'up', 'up', 'up', 'up', 'up', 'up']
MAGE_CAST_DIRECTION_INDEX = 0


def generate_level(level):
    global MAGE_CAST_DIRECTION_INDEX
    new_player, x, y, slime = None, None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                ALL_TILES.append(Tile('empty', x, y))
            elif level[y][x] == '#':
                ALL_TILES.append(Tile('wall', x, y))
            elif level[y][x] == '&':
                ALL_TILES.append(Tile('void', x, y))
            elif level[y][x] == 'c':
                ALL_TILES.append(Tile('empty', x, y))
                ALL_CHESTS.append(Treasure(x, y))
                level[y][x] = "#"
            elif level[y][x] == 'f':
                ALL_TILES.append(Tile('empty', x, y))
                ALL_TRAPS.append(Trap('fire', x, y))
                level[y][x] = "."
            elif level[y][x] == 's':
                ALL_TILES.append(Tile('empty', x, y))
                ALL_TRAPS.append(Trap('spike', x, y))
                level[y][x] = "."
            elif level[y][x] == 'p':
                ALL_TILES.append(Tile('empty', x, y))
                ALL_TRAPS.append(Trap('pit', x, y))
                level[y][x] = "."
            elif level[y][x] == '@':
                ALL_TILES.append(Tile('empty', x, y))
                new_player = Player(x, y)
                level[y][x] = "."
            elif level[y][x] == '1':
                ALL_TILES.append(Tile('empty', x, y))
                ALL_ENEMIES.append(Enemy('spearman_not_arm', x, y, (1, 4, 3, 2), 3))
                level[y][x] = "."
            elif level[y][x] == 'r':
                ALL_TILES.append(Tile('empty', x, y))
                ALL_ENEMIES.append(RangeEnemy('skeleton_mage', x, y,
                                              MAGE_CAST_DIRECTIONS[MAGE_CAST_DIRECTION_INDEX], 3))
                level[y][x] = "."
                MAGE_CAST_DIRECTION_INDEX += 1
    MAGE_CAST_DIRECTION_INDEX = 0
    return new_player, x, y


def move(hero, movement):
    x, y = hero.tile_pos
    if movement == "up":
        if y > 0 and level_map[y - 1][x] == ".":
            hero.move(x, y - 1)
    elif movement == "down":
        if y < max_y - 1 and level_map[y + 1][x] == ".":
            hero.move(x, y + 1)
    elif movement == "left":
        if hero.direction == 'right':
            hero.direction = 'left'
            hero.image = pygame.transform.flip(hero.image, True, False)
        if x > 0 and level_map[y][x - 1] == ".":
            hero.move(x - 1, y)
    elif movement == "right":
        if hero.direction == 'left':
            hero.direction = 'right'
            hero.image = pygame.transform.flip(hero.image, True, False)
        if x < max_x - 1 and level_map[y][x + 1] == ".":
            hero.move(x + 1, y)


VISIBLE_RADIUS = 3


def set_tiles_visible(hero):
    for tile in ALL_TILES:
        if not tile.is_visible:
            if hero.tile_pos[0] * TILE_WIDTH - VISIBLE_RADIUS * \
                    TILE_WIDTH < tile.init_pos[0] < hero.tile_pos[0] * \
                    TILE_WIDTH + VISIBLE_RADIUS * TILE_WIDTH and hero.tile_pos[1] * \
                    TILE_HEIGHT - VISIBLE_RADIUS * TILE_WIDTH < tile.init_pos[1] < hero.tile_pos[1] * \
                    TILE_HEIGHT + VISIBLE_RADIUS * TILE_WIDTH:
                tile.is_visible = True
                tile.image = tile.true_image
    for trap in ALL_TRAPS:
        if not trap.is_visible:
            if hero.tile_pos[0] * TILE_WIDTH - VISIBLE_RADIUS * \
                    TILE_WIDTH < trap.init_pos[0] < hero.tile_pos[0] * \
                    TILE_WIDTH + VISIBLE_RADIUS * TILE_WIDTH and hero.tile_pos[1] * \
                    TILE_HEIGHT - VISIBLE_RADIUS * TILE_WIDTH < trap.init_pos[1] < hero.tile_pos[1] * \
                    TILE_HEIGHT + VISIBLE_RADIUS * TILE_WIDTH:
                trap.is_visible = True
                trap.image = trap.true_image
    for chest in ALL_CHESTS:
        if not chest.is_visible:
            if hero.tile_pos[0] * TILE_WIDTH - VISIBLE_RADIUS * \
                    TILE_WIDTH < chest.init_pos[0] < hero.tile_pos[0] * \
                    TILE_WIDTH + VISIBLE_RADIUS * TILE_WIDTH and hero.tile_pos[1] * \
                    TILE_HEIGHT - VISIBLE_RADIUS * TILE_WIDTH < chest.init_pos[1] < hero.tile_pos[1] * \
                    TILE_HEIGHT + VISIBLE_RADIUS * TILE_WIDTH:
                chest.is_visible = True
                chest.image = chest.true_image


def set_enemies_visible(hero):
    for enemy in ALL_ENEMIES:
        for tile in ALL_TILES:
            if tile.init_pos[0] // TILE_WIDTH == enemy.abs_pos[0] // TILE_WIDTH and tile.init_pos[1] // TILE_WIDTH == \
                    enemy.abs_pos[1] // TILE_WIDTH:
                if tile.is_visible:
                    enemy.is_visible = True
                    enemy.image = enemy.true_image
                else:
                    enemy.is_visible = False
                    enemy.image = TILE_IMAGES['void'][0]
    for ball in ALL_MAG_BALLS:
        for tile in ALL_TILES:
            if tile.init_pos[0] // TILE_WIDTH == ball.abs_pos[0] // TILE_WIDTH and tile.init_pos[1] // TILE_WIDTH == \
                    ball.abs_pos[1] // TILE_WIDTH:
                if tile.is_visible:
                    ball.is_visible = True
                    ball.image = ball.true_image
                else:
                    ball.is_visible = False
                    ball.image = TILE_IMAGES['void'][0]


def restart():
    global level_map, hero, max_x, max_y, camera, iteration_time, iteration_time1, iteration_time_f_trap, \
        iteration_time_attack, iteration_time_idle, iteration_time_spike_trap, iteration_time_mag_ball, hearts
    screen.fill(pygame.Color("black"))
    level_map = load_level(MAP_FILE)
    hero, max_x, max_y = generate_level(level_map)
    camera = Camera(hero)
    iteration_time = iteration_time1 = iteration_time_f_trap = iteration_time_attack = \
        iteration_time_idle = iteration_time_spike_trap = iteration_time_mag_ball = datetime.datetime.now()
    hearts = [HealthBar(2, 0), HealthBar(1.5, 0),
              HealthBar(1, 0), HealthBar(0.5, 0), HealthBar(0, 0)]
    set_tiles_visible(hero)
    set_enemies_visible(hero)


class Timer:
    def __init__(self, time):
        self.time = time
        self.timer = TextObj(f"{time}", WIDTH - 90, 5, 70, pygame.Color('orange'), True)

    def tick(self):
        self.timer.change_text("4:00")

SOUND_VOLUME = 0.05
EFFECT_VOLUME = 1
pygame.mixer.music.load('data/Sounds/soundtrack1.mp3')
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(SOUND_VOLUME)
level_map = load_level(MAP_FILE)
hero, max_x, max_y = generate_level(level_map)
camera = Camera(hero)
iteration_time = iteration_time1 = iteration_time_attack = iteration_time_idle \
    = iteration_time_f_trap = iteration_time_spike_trap = iteration_time_mag_ball = datetime.datetime.now()
hearts = [HealthBar(2, 0), HealthBar(1.5, 0),
          HealthBar(1, 0), HealthBar(0.5, 0), HealthBar(0, 0)]
set_tiles_visible(hero)
set_enemies_visible(hero)
start_screen()
timer = Timer()
while running:
    now = datetime.datetime.now()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                move(hero, "up")
            elif event.key == pygame.K_DOWN:
                move(hero, "down")
            elif event.key == pygame.K_LEFT:
                move(hero, "left")
            elif event.key == pygame.K_RIGHT:
                move(hero, "right")
            elif event.key == pygame.K_SPACE and not hero.attacking:
                hero.attacking = True
            set_tiles_visible(hero)
        #    if pygame.key.get_pressed():
        # if pygame.key.get_pressed()[pygame.K_UP]:
        #    move(hero, "up")
        # elif pygame.key.get_pressed()[pygame.K_DOWN]:
        #    move(hero, "down")
        # elif pygame.key.get_pressed()[pygame.K_LEFT]:
        #    move(hero, "left")
        # elif pygame.key.get_pressed()[pygame.K_RIGHT]:
        #    move(hero, "right")
        # elif pygame.key.get_pressed()[pygame.K_SPACE]:
        #    if hero.direction == 'right':
        #        pass
        #
        #    else:
        #        pass
        # set_tiles_visible(hero)
    if pygame.sprite.spritecollideany(hero, enemy_group):
        for heart in hearts:
            if heart.isfull:
                if (now - iteration_time1).total_seconds() >= 1:
                    iteration_time1 = now
                    heart.isfull = False
                    heart.image = HEARTS_IMAGES[1]
                    hero.health -= 1
                    break
    collided_trap = pygame.sprite.spritecollideany(hero, trap_group)
    if collided_trap:
        if collided_trap.tile_type == 'fire':
            if 7 <= collided_trap.num_fire_sprite <= 9:
                for heart in hearts:
                    if heart.isfull:
                        heart.isfull = False
                        heart.image = HEARTS_IMAGES[1]
                        hero.health -= 1
                        break
        elif collided_trap.tile_type == 'spike':
            if 7 <= collided_trap.num_spike_sprite <= 12:
                for heart in hearts:
                    if heart.isfull:
                        heart.isfull = False
                        heart.image = HEARTS_IMAGES[1]
                        hero.health -= 1
                        break
        elif collided_trap.tile_type == 'pit':
            for heart in hearts:
                if heart.isfull:
                    heart.isfull = False
                    heart.image = HEARTS_IMAGES[1]
                    hero.health -= 1
                    break
    if hero.attacking:
        if (now - iteration_time_attack).total_seconds() >= 0.15:
            iteration_time_attack = now
            if hero.direction == 'right':
                hero.image = PLAYER_IMAGES[1][hero.num_attack_sprite][0]
            else:
                hero.image = pygame.transform.flip(PLAYER_IMAGES[1][hero.num_attack_sprite][0], True, False)
            hero.num_attack_sprite = (hero.num_attack_sprite + 1) % 6
            if hero.num_attack_sprite == 0:
                hero.attacking = False
                hero.image = PLAYER_IMAGES[0][0][0]
    if not hero.attacking:
        if (now - iteration_time_idle).total_seconds() >= 0.1:
            iteration_time_idle = now
            if hero.direction == 'right':
                hero.image = PLAYER_IMAGES[0][hero.num_idle_sprite][0]
            else:
                hero.image = pygame.transform.flip(PLAYER_IMAGES[0][hero.num_idle_sprite][0], True, False)
            hero.num_idle_sprite = (hero.num_idle_sprite + 1) % 11
    if (now - iteration_time_f_trap).total_seconds() >= 0.2:
        iteration_time_f_trap = now
        for trap in ALL_TRAPS:
            if trap.tile_type == 'fire':
                trap.num_fire_sprite = (trap.num_fire_sprite + 1) % 14
                if trap.is_visible and trap.tile_type == 'fire':
                    trap.image = TRAPS_IMAGES[trap.tile_type][0][trap.num_fire_sprite][0]
    if (now - iteration_time_spike_trap).total_seconds() >= 0.2:
        iteration_time_spike_trap = now
        for trap in ALL_TRAPS:
            if trap.tile_type == 'spike':
                trap.num_spike_sprite = (trap.num_spike_sprite + 1) % 13
                if trap.is_visible:
                    trap.image = TRAPS_IMAGES[trap.tile_type][0][trap.num_spike_sprite][0]
    if (now - iteration_time).total_seconds() >= 1:
        iteration_time = now
        for enemy in ALL_ENEMIES:
            enemy.move()
    if (now - iteration_time_mag_ball).total_seconds() >= 1:
        iteration_time_mag_ball = now
        for ball in ALL_MAG_BALLS:
            ball.move()
    if hero.health == 0:
        hearts[-1].isfull = False
        hearts[-1].image = HEARTS_IMAGES[1]
        heart_group.draw(screen)
        pygame.display.flip()
        res = game_over()
        if res == 1:
            clear_groups()
            restart()
        elif res == 2:
            start_screen()
    set_enemies_visible(hero)
    screen.fill(pygame.Color("black"))
    sprite_group.draw(screen)
    hero_group.draw(screen)
    enemy_group.draw(screen)
    trap_group.draw(screen)
    treasure_group.draw(screen)
    heart_group.draw(screen)
    timer.timer.text_render()
    clock.tick(FPS)
    pygame.display.flip()
pygame.quit()
