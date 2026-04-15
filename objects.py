import os
import pickle
import random
import pygame
from pygame import mixer
from pygame.locals import *

SIZE = WIDTH , HEIGHT= 1152, 648
tile_size = 50
# Scroll: level wider than the window by this many tiles (~1 screen edge). Camera follows the player.
SCROLL_EXTRA_COLS = 10

pygame.font.init()
score_font = pygame.font.SysFont('Bauhaus 93', 30)

WHITE = (255,255,255)
BLUE = (30, 144, 255)

# load sounds
mixer.init()

class _SilentSound:
	def play(self):
		pass

	def set_volume(self, _volume):
		pass


def _load_sound_safe(path, volume=0.5):
	if os.path.isfile(path):
		try:
			snd = pygame.mixer.Sound(path)
			snd.set_volume(volume)
			return snd
		except pygame.error:
			pass
	return _SilentSound()


def _scale_by_height(image, target_h):
	"""Scale sprite by height while preserving original aspect ratio."""
	src_w, src_h = image.get_size()
	if src_h <= 0:
		return image.copy()
	scale = target_h / src_h
	target_w = max(1, int(src_w * scale))
	return pygame.transform.smoothscale(image, (target_w, int(target_h)))


def _fit_to_frame(image, frame_size):
	"""Place sprite in fixed-size transparent frame (bottom-aligned)."""
	frame_w, frame_h = frame_size
	surf = pygame.Surface((frame_w, frame_h), pygame.SRCALPHA)
	x = (frame_w - image.get_width()) // 2
	y = frame_h - image.get_height()
	surf.blit(image, (x, y))
	return surf


def _load_image_with_fallback(*paths):
	"""Load first existing image path; fallback to visible player sprite."""
	for path in paths:
		if os.path.isfile(path):
			return pygame.image.load(path)
	default_path = 'player/walk1.png'
	if os.path.isfile(default_path):
		return pygame.image.load(default_path)
	return pygame.Surface((32, 48), pygame.SRCALPHA)


def _pick_background_music_path():
	"""Always use sounds/music.mp3 for background music."""
	path = os.path.join('sounds', 'music.mp3')
	if os.path.isfile(path):
		return path
	return None


def start_background_music():
	path = _pick_background_music_path()
	if path is None:
		legacy = 'sounds/Ballad for Olivia.mp3'
		if os.path.isfile(legacy):
			path = legacy
	if path is None:
		return
	try:
		pygame.mixer.music.load(path)
		pygame.mixer.music.set_volume(0.35)
		pygame.mixer.music.play(-1, 0.0, 800)
	except pygame.error:
		pass


start_background_music()

diamond_fx = _load_sound_safe('sounds/341695__projectsu012__coins-1.wav', 0.5)
jump_fx = _load_sound_safe('sounds/jump.wav', 0.5)
dead_fx = _load_sound_safe('sounds/406113__daleonfire__dead.wav', 0.5)
power_fx = _load_sound_safe('sounds/kamehameha_1.mp3', 0.7)
sounds = [diamond_fx, ]


# loading images
dead_img = pygame.image.load('assets/ghost.png')
game_over_img = pygame.image.load('assets/gover.png')
game_over_img = pygame.transform.scale(game_over_img, (300,250))
game_over_rect = game_over_img.get_rect(center=(WIDTH//2, HEIGHT//2 - HEIGHT//6))

# creates background
class World:
	def __init__(self, win, data, groups):
		self.tile_list  = []
		self.win = win
		self.groups = groups

		tiles = []
		for t in sorted(os.listdir('tiles/'), key=lambda s: int(s[:-4])):
			tile = pygame.image.load('tiles/' + t)
			tiles.append(tile)

		row_count = 0
		for row in data:
			col_count = 0
			for col in row:
				if col > 0:
					if col in range(1,14) or col == 18:
						# dirt blocks
						img = pygame.transform.scale(tiles[col-1], (tile_size, tile_size))
						rect = img.get_rect()
						rect.x = col_count * tile_size
						rect.y = row_count * tile_size
						tile = (img, rect)
						self.tile_list.append(tile)

					if col == 14:
						# bush
						bush = Forest('bush',col_count * tile_size, row_count * tile_size + tile_size // 2)
						self.groups[2].add(bush)

					if col == 15:
						# lava
						lava = Fluid('lava_flow', col_count * tile_size, row_count * tile_size + tile_size // 2)
						self.groups[1].add(lava)
					if col == 16:
						lava = Fluid('lava_still', col_count * tile_size, row_count * tile_size)
						self.groups[1].add(lava)
					
					if col == 17:
						# diamond
						diamond = Diamond(col_count * tile_size, row_count * tile_size)
						self.groups[3].add(diamond)
					if col == 19:
						# water block
						water = Fluid('water_flow', col_count * tile_size, row_count * tile_size + tile_size // 2)
						self.groups[1].add(water)
					if col == 20:
						# water block
						water = Fluid('water_still', col_count * tile_size, row_count * tile_size)
						self.groups[1].add(water)
					if col == 21:
						# tree
						tree = Forest('tree', (col_count-1) * tile_size + 10, (row_count-2) * tile_size + 5)
						self.groups[2].add(tree)
					if col == 22:
						# mushroom
						mushroom = Forest('mushroom', col_count * tile_size, row_count * tile_size + tile_size // 4)
						self.groups[2].add(mushroom)
					if col == 23:
						# bee
						bee = Bee(col_count * tile_size, row_count * tile_size)
						self.groups[4].add(bee)
					if col == 24:
						#Gate blocks
						gate = ExitGate(col_count * tile_size - tile_size//4, row_count * tile_size - tile_size//4)
						self.groups[5].add(gate)
					if col == 25:
						#Side moving platform
						platform = MovingPlatform('side', col_count * tile_size, row_count * tile_size)
						self.groups[6].add(platform)
					if col == 26:
						#top moving platform
						platform = MovingPlatform('up', col_count * tile_size, row_count * tile_size)
						self.groups[6].add(platform)
					if col == 27:
						#flower
						flower = Forest('flower', (col_count) * tile_size, row_count * tile_size)
						self.groups[2].add(flower)
					if col == 28:
						# bridge
						bridge = Bridge((col_count-2) * tile_size + 10, row_count * tile_size + tile_size // 4)
						self.groups[7].add(bridge)
					if col == 29:
						#Slime
						slime = Slime(col_count * tile_size - 10, row_count * tile_size + tile_size // 4)
						self.groups[4].add(slime)


				col_count += 1
			row_count += 1

		self.world_pixel_width = WIDTH
		for tile in self.tile_list:
			self.world_pixel_width = max(self.world_pixel_width, tile[1].right)
		for g in self.groups:
			for s in g:
				if getattr(s, 'hud_screen_anchor', False):
					continue
				self.world_pixel_width = max(self.world_pixel_width, s.rect.right)
		self.world_pixel_width = int(max(WIDTH, self.world_pixel_width)) + 48

	def draw(self, scroll_x=0):
		sx = int(scroll_x)
		for tile in self.tile_list:
			self.win.blit(tile[0], (tile[1].x - sx, tile[1].y))

# -------------------------------------------------------------------------------------------------
#											 Creates Player
class Player:
	def __init__(self, win, pos, world, groups):
		self.reset(win, pos, world, groups)

	def _collision_rect(self, x=None, y=None):
		"""Compact hitbox so character can pass tight spaces."""
		if x is None:
			x = self.rect.x
		if y is None:
			y = self.rect.y
		return pygame.Rect(
			int(x + self.hitbox_offset_x),
			int(y + self.hitbox_offset_y),
			int(self.hitbox_w),
			int(self.hitbox_h),
		)

	def update(self, pressed_keys, game_over, level_won, game_won, scroll_x=0):
		dx = 0
		dy = 0
		walk_cooldown = 3
		col_threshold = 20
		moving_horiz = False


		if not game_over and not game_won:
			now = pygame.time.get_ticks()
			if pressed_keys[K_x] and now - self.last_shot_ms >= self.shot_cooldown_ms:
				self.spawn_player_bullet()
				self.last_shot_ms = now
				power_fx.play()

			if pressed_keys[K_UP] and not self.jumped and not self.in_air:
				self.vel_y = -15
				jump_fx.play()
				self.jumped = True
			if pressed_keys[K_UP] == False:
				self.jumped = False

			if pressed_keys[K_LEFT]:
				dx -= 5
				self.direction = -1
				moving_horiz = True
			if pressed_keys[K_RIGHT]:
				dx += 5
				self.direction = 1
				moving_horiz = True


			# add gravity
			self.vel_y += 1
			if self.vel_y > 10:
				self.vel_y = 10
			dy += self.vel_y

			# check for collision
			self.in_air = True
			cur_hitbox = self._collision_rect()
			next_hitbox_x = self._collision_rect(self.rect.x + dx, self.rect.y)
			next_hitbox_y = self._collision_rect(self.rect.x, self.rect.y + dy)
			for tile in self.world.tile_list:
				# check for collision in x direction
				if tile[1].colliderect(next_hitbox_x):
					dx = 0
					next_hitbox_x = self._collision_rect(self.rect.x + dx, self.rect.y)
					
				# check for collision in y direction
				if tile[1].colliderect(next_hitbox_y):
					# check if below the ground
					if self.vel_y < 0:
						dy = tile[1].bottom - cur_hitbox.top
						self.vel_y = 0
					elif self.vel_y >= 0:
						dy = tile[1].top - cur_hitbox.bottom
						self.vel_y = 0
						self.in_air = False
					next_hitbox_y = self._collision_rect(self.rect.x, self.rect.y + dy)

			player_hitbox_now = self._collision_rect()
			for water in self.groups[0]:
				if player_hitbox_now.colliderect(water.rect):
					game_over = True
					break
			for hazard in self.groups[1]:
				if player_hitbox_now.colliderect(hazard.rect):
					game_over = True
					break
			for enemy in self.groups[4]:
				if not getattr(enemy, 'can_hurt', True):
					continue
				if player_hitbox_now.colliderect(enemy.rect):
					game_over = True
					break
			if len(self.groups) > 8:
				for bullet in list(self.groups[8]):
					if player_hitbox_now.colliderect(bullet.rect):
						bullet.kill()
						game_over = True
						break

			# temp = self
			# temp = temp.rect.x + 20
			# if pygame.sprite.spritecollide(temp, self.groups[5], False):
			# 	level_won = True
			for gate in self.groups[5]:
				if gate.rect.colliderect(self._collision_rect(self.rect.x - tile_size//2, self.rect.y)):
					level_won = True

			if game_over:
				dead_fx.play()

			# check for collision with moving platform
			for platform in self.groups[6]:
				next_hitbox_x = self._collision_rect(self.rect.x + dx, self.rect.y)
				next_hitbox_y = self._collision_rect(self.rect.x, self.rect.y + dy)
				# collision in x direction
				if platform.rect.colliderect(next_hitbox_x):
					dx = 0

				# collision in y direction
				if platform.rect.colliderect(next_hitbox_y):
					# check if below platform
					if abs((player_hitbox_now.top + dy) - platform.rect.bottom) < col_threshold:
						self.vel_y = 0
						dy = (platform.rect.bottom - player_hitbox_now.top)

					# check if above platform
					elif abs((player_hitbox_now.bottom + dy) - platform.rect.top) < col_threshold:
						self.rect.y = platform.rect.top - self.hitbox_h - self.hitbox_offset_y - 1
						self.in_air = False
						dy = 0
					# move sideways with the platform
					if platform.move_x:
						self.rect.x += platform.move_direction

			for bridge in self.groups[7]:
				next_hitbox_x = self._collision_rect(self.rect.x + dx, self.rect.y)
				next_hitbox_y = self._collision_rect(self.rect.x, self.rect.y + dy)
				# collision in x direction
				if (bridge.rect.colliderect(next_hitbox_x) and
							(bridge.rect.bottom < player_hitbox_now.bottom + 5)):
					dx = 0

				# collision in y direction
				if bridge.rect.colliderect(next_hitbox_y):
					if abs((player_hitbox_now.top + dy) - bridge.rect.bottom) < col_threshold:
						self.vel_y = 0
						dy = (bridge.rect.bottom - player_hitbox_now.top)

					# check if above platform
					elif abs((player_hitbox_now.bottom + dy) - bridge.rect.bottom) < 8:
						self.rect.y = bridge.rect.bottom - self.hitbox_h - self.hitbox_offset_y - 12
						self.in_air = False
						dy = 0




			# updating player position
			self.rect.x += dx
			self.rect.y += dy
			# if self.rect.x == self.width:
			# 	self.rect.x = self.width
			max_x = self.world.world_pixel_width - self.width
			if self.rect.x >= max_x:
				self.rect.x = max_x
			if self.rect.x <= 0:
				self.rect.x = 0

			# Animation state with character sprites in player/
			if self.in_air:
				if moving_horiz:
					self.counter += 1
					if self.counter > walk_cooldown:
						self.counter = 0
						self.index = (self.index + 1) % len(self.walk_right)
					self.image = self.walk_right[self.index] if self.direction == 1 else self.walk_left[self.index]
				else:
					self.image = self.jump_right if self.direction == 1 else self.jump_left
			elif moving_horiz:
				self.counter += 1
				if self.counter > walk_cooldown:
					self.counter = 0
					self.index = (self.index + 1) % len(self.walk_right)
				self.image = self.walk_right[self.index] if self.direction == 1 else self.walk_left[self.index]
			else:
				self.counter = 0
				self.index = 0
				self.image = self.idle_right if self.direction == 1 else self.idle_left

			self.update_player_bullets()

		elif game_over:
			self.image = dead_img
			if self.rect.top > 0:
				self.rect.y -= 5

			self.win.blit(game_over_img, game_over_rect)

		# displaying player on window (world coords → screen with camera)
		sx = int(scroll_x)
		for bullet in self.player_bullets:
			self.win.blit(bullet.image, (bullet.rect.x - sx, bullet.rect.y))
		self.win.blit(self.image, (self.rect.x - sx, self.rect.y))
		# pygame.draw.rect(self.win, (255, 255, 255), self.rect, 1)
	
		return game_over, level_won

	def reset(self, win, pos, world, groups):
		x, y  = pos
		self.win = win
		self.world = world
		self.groups = groups

		# Tune character size smaller so tight gaps are passable.
		base_h = 68
		legacy_walk = [f'player/walk{i}.png' for i in range(1, 7)]
		frame_size = (78, base_h + 4)

		self.idle_right = _fit_to_frame(
			_scale_by_height(_load_image_with_fallback(legacy_walk[0]), base_h),
			frame_size,
		)
		self.idle_left = pygame.transform.flip(self.idle_right, True, False)
		self.jump_right = _fit_to_frame(
			_scale_by_height(_load_image_with_fallback(legacy_walk[1]), base_h),
			frame_size,
		)
		self.jump_left = pygame.transform.flip(self.jump_right, True, False)

		move_1 = _fit_to_frame(
			_scale_by_height(_load_image_with_fallback(legacy_walk[2]), base_h),
			frame_size,
		)
		move_2 = _fit_to_frame(
			_scale_by_height(_load_image_with_fallback(legacy_walk[3]), base_h),
			frame_size,
		)
		self.walk_right = [move_1, move_2]
		self.walk_left = [pygame.transform.flip(img, True, False) for img in self.walk_right]

		self.index = 0
		self.counter = 0
		self.player_bullets = []
		self.shot_cooldown_ms = 230
		self.last_shot_ms = -self.shot_cooldown_ms

		self.image = self.idle_right
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.width = self.image.get_width()
		self.height = self.image.get_height()
		self.hitbox_w = max(28, int(self.width * 0.46))
		self.hitbox_h = max(38, int(self.height * 0.62))
		self.hitbox_offset_x = (self.width - self.hitbox_w) // 2
		self.hitbox_offset_y = self.height - self.hitbox_h - 2
		self.direction = 1
		self.vel_y = 0
		self.jumping = False
		self.jumped = False
		self.in_air = True

	def spawn_player_bullet(self):
		bullet = PlayerBullet(self.rect.centerx, self.rect.centery + 4, self.direction)
		self.player_bullets.append(bullet)

	def update_player_bullets(self):
		for bullet in list(self.player_bullets):
			bullet.update()
			if bullet.rect.right < 0 or bullet.rect.left > self.world.world_pixel_width or bullet.exceeded_range():
				self.player_bullets.remove(bullet)
				continue
			hit_wall = False
			for tile in self.world.tile_list:
				if tile[1].colliderect(bullet.rect):
					hit_wall = True
					break
			if hit_wall:
				self.player_bullets.remove(bullet)
				continue
			for enemy in list(self.groups[4]):
				if getattr(enemy, 'is_defeated', False):
					continue
				if bullet.rect.colliderect(enemy.rect):
					if hasattr(enemy, 'defeat'):
						enemy.defeat()
					else:
						enemy.kill()
					self.player_bullets.remove(bullet)
					break


class PlayerBullet(pygame.sprite.Sprite):
	def __init__(self, x, y, direction):
		super().__init__()
		surf = pygame.Surface((22, 8), pygame.SRCALPHA)
		pygame.draw.ellipse(surf, (120, 230, 255), surf.get_rect())
		pygame.draw.ellipse(surf, (230, 250, 255), surf.get_rect().inflate(-8, -3))
		self.image = surf
		self.rect = self.image.get_rect(center=(int(x), int(y)))
		self.vx = 14 * (1 if direction >= 0 else -1)
		self.start_x = self.rect.x
		self.max_range_px = WIDTH // 4

	def update(self):
		self.rect.x += self.vx

	def exceeded_range(self):
		return abs(self.rect.x - self.start_x) >= self.max_range_px

class MovingPlatform(pygame.sprite.Sprite):
	def __init__(self, type_, x, y):
		super(MovingPlatform, self).__init__()

		img = pygame.image.load('assets/moving.png')
		self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y

		direction = random.choice([-1,1])
		self.move_direction = direction
		self.move_counter = 0
		self.move_x = 0
		self.move_y = 0

		if type_ == 'side':
			self.move_x = 1
		elif type_ == 'up':
			self.move_y = 1

	def update(self):
		self.rect.x += self.move_direction * self.move_x
		self.rect.y += self.move_direction * self.move_y
		self.move_counter += 1
		if abs(self.move_counter) >= 50:
			self.move_direction *= -1
			self.move_counter *= -1

class Bridge(pygame.sprite.Sprite):
	def __init__(self, x, y):
		super(Bridge, self).__init__()

		img = pygame.image.load('tiles/28.png')
		self.image = pygame.transform.scale(img, (5*tile_size + 20, tile_size))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y


class Fluid(pygame.sprite.Sprite):
	def __init__(self, type_, x, y):
		super(Fluid, self).__init__()

		if type_ == 'water_flow':
			img = pygame.image.load('tiles/19.png')
			self.image = pygame.transform.scale(img, (tile_size, tile_size // 2 + tile_size // 4))
		if type_ == 'water_still':
			img = pygame.image.load('tiles/20.png')
			self.image = pygame.transform.scale(img, (tile_size, tile_size))
		elif type_ == 'lava_flow':
			img = pygame.image.load('tiles/15.png')
			self.image = pygame.transform.scale(img, (tile_size, tile_size // 2 + tile_size // 4))
		elif type_ == 'lava_still':
			img = pygame.image.load('tiles/16.png')
			self.image = pygame.transform.scale(img, (tile_size, tile_size))

		
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y

class ExitGate(pygame.sprite.Sprite):
	def __init__(self, x, y):
		super(ExitGate, self).__init__()
		
		img_list = [f'assets/gate{i+1}.png' for i in range(4)]
		self.gate_open = pygame.image.load('assets/gate5.png')
		self.image = pygame.image.load(random.choice(img_list))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.width = self.image.get_width()
		self.height = self.image.get_height()

	def update(self, player):
		if player.rect.colliderect(self.rect.x , self.rect.y, self.width, self.height):
			self.image = self.gate_open


class Forest(pygame.sprite.Sprite):
	def __init__(self, type_, x, y):
		super(Forest, self).__init__()

		if type_ == 'bush':
			img = pygame.image.load('tiles/14.png')
			self.image = pygame.transform.scale(img, (tile_size, int(tile_size * 0.50)))

		if type_ == 'tree':
			img = pygame.image.load('tiles/21.png')
			self.image = pygame.transform.scale(img, (3*tile_size, 3 * tile_size))

		if type_ == 'mushroom':
			img = pygame.image.load('tiles/22.png')
			self.image = pygame.transform.scale(img, (int(tile_size * 0.80), int(tile_size * 0.80)))

		if type_ == 'flower':
			img = pygame.image.load('tiles/27.png')
			self.image = pygame.transform.scale(img, (2*tile_size, tile_size))

		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y

class Diamond(pygame.sprite.Sprite):
	def __init__(self, x, y, hud_screen_anchor=False):
		super(Diamond, self).__init__()

		img_list = [f'assets/d{i+1}.png' for i in range(4)]
		img = pygame.image.load(random.choice(img_list))
		self.image = pygame.transform.scale(img, (tile_size, tile_size))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.hud_screen_anchor = hud_screen_anchor


class Bee(pygame.sprite.Sprite):
	def __init__(self, x, y):
		super(Bee, self).__init__()

		img = pygame.image.load('tiles/23.png')
		self.img_left = pygame.transform.scale(img, (48,48))
		self.img_right = pygame.transform.flip(self.img_left, True, False)
		self.image = self.img_left
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y

		self.pos = self.rect.y
		self.dx = 3
		self.can_hurt = True
		self.is_defeated = False
		self.defeat_started_ms = 0
		self.defeat_duration_ms = 650
		self.ghost_image = pygame.transform.smoothscale(dead_img, self.rect.size)
		self.shoot_cooldown_ms = 5000
		self.last_shot_ms = pygame.time.get_ticks()

	def update(self, player, bullet_group=None, world_w=None):
		if self.is_defeated:
			self.rect.y -= 2
			if pygame.time.get_ticks() - self.defeat_started_ms >= self.defeat_duration_ms:
				self.kill()
			return

		if self.rect.x >= player.rect.x:
			self.image = self.img_left
		else:
			self.image = self.img_right

		if self.rect.y >= self.pos:
			self.dx *= -1
		if self.rect.y <= self.pos - tile_size * 3:
			self.dx *= -1

		self.rect.y += self.dx
		if bullet_group is not None and world_w is not None:
			now = pygame.time.get_ticks()
			if now - self.last_shot_ms >= self.shoot_cooldown_ms:
				self.last_shot_ms = now
				dir_x = -1 if self.rect.centerx > player.rect.centerx else 1
				dist = max(1, abs(player.rect.centerx - self.rect.centerx))
				vx = 6 * dir_x
				vy = max(-2.2, min(2.2, (player.rect.centery - self.rect.centery) / max(60, dist / 2)))
				bullet_group.add(EnemyBullet(self.rect.centerx, self.rect.centery, vx, vy))

	def defeat(self):
		if self.is_defeated:
			return
		self.is_defeated = True
		self.can_hurt = False
		self.defeat_started_ms = pygame.time.get_ticks()
		self.image = self.ghost_image

class EnemyBullet(pygame.sprite.Sprite):
	def __init__(self, x, y, vx, vy):
		super().__init__()
		surf = pygame.Surface((14, 10), pygame.SRCALPHA)
		pygame.draw.ellipse(surf, (220, 40, 40), surf.get_rect())
		pygame.draw.ellipse(surf, (120, 10, 10), surf.get_rect().inflate(-4, -3))
		self.image = surf
		self.rect = self.image.get_rect(center=(int(x), int(y)))
		self.vx = vx
		self.vy = vy
		self.start_x = self.rect.x
		self.max_range_px = WIDTH // 4

	def update(self, world_w):
		self.rect.x += int(self.vx)
		self.rect.y += int(self.vy)
		m = 120
		exceeded_range = abs(self.rect.x - self.start_x) >= self.max_range_px
		if exceeded_range or self.rect.right < -m or self.rect.left > world_w + m or self.rect.bottom < -m or self.rect.top > HEIGHT + m:
			self.kill()


class Slime(pygame.sprite.Sprite):
	def __init__(self, x, y):
		super(Slime, self).__init__()

		img = pygame.image.load('tiles/29.png')
		self.img_left = pygame.transform.scale(img, (int(1.2*tile_size), tile_size//2 + tile_size//4))
		self.img_right = pygame.transform.flip(self.img_left, True, False)
		self.imlist = [self.img_left, self.img_right]
		self.index = 0

		self.image = self.imlist[self.index]
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y

		self.move_direction = -1
		self.move_counter = 0
		self.can_hurt = True
		self.is_defeated = False
		self.defeat_started_ms = 0
		self.defeat_duration_ms = 650
		self.ghost_image = pygame.transform.smoothscale(dead_img, self.rect.size)
		self.shoot_cooldown_ms = 5000
		self.last_shot_ms = pygame.time.get_ticks()

	def update(self, player, bullet_group=None, world_w=None):
		if self.is_defeated:
			self.rect.y -= 2
			if pygame.time.get_ticks() - self.defeat_started_ms >= self.defeat_duration_ms:
				self.kill()
			return

		self.rect.x += self.move_direction
		self.move_counter += 1
		if abs(self.move_counter) >= 50:
			self.index = (self.index + 1) % 2
			self.image = self.imlist[self.index]
			self.move_direction *= -1
			self.move_counter *= -1
		if bullet_group is not None and world_w is not None:
			now = pygame.time.get_ticks()
			if now - self.last_shot_ms >= self.shoot_cooldown_ms:
				self.last_shot_ms = now
				dir_x = -1 if self.rect.centerx > player.rect.centerx else 1
				vx = 5 * dir_x
				bullet_group.add(EnemyBullet(self.rect.centerx, self.rect.centery - 6, vx, 0))

	def defeat(self):
		if self.is_defeated:
			return
		self.is_defeated = True
		self.can_hurt = False
		self.defeat_started_ms = pygame.time.get_ticks()
		self.image = self.ghost_image

class Button(pygame.sprite.Sprite):
	def __init__(self, img, scale, x, y):
		super(Button, self).__init__()

		self.image = pygame.transform.scale(img, scale)
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y

		self.clicked = False

	def draw(self, win):
		action = False
		pos = pygame.mouse.get_pos()
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] and not self.clicked:
				action = True
				self.clicked = True

			if not pygame.mouse.get_pressed()[0]:
				self.clicked = False

		win.blit(self.image, self.rect)
		return action


# -------------------------------------------------------------------------------------------------
#											 Custom Functions
def draw_lines(win):
	for row in range(HEIGHT // tile_size + 1):
		pygame.draw.line(win, WHITE, (0, tile_size*row), (WIDTH, tile_size*row), 2)
	for col in range(WIDTH // tile_size):
		pygame.draw.line(win, WHITE, (tile_size*col, 0), (tile_size*col, HEIGHT), 2)

def pad_rows_for_horizontal_scroll(data):
	"""
	Widen each row slightly for scrolling. Only repeats solid terrain (1–13, 18);
	empty / sky rows extend with air (0). Never fills sky with dirt.
	"""
	if not data:
		return data
	base_cols = max(len(row) for row in data)
	target = max(base_cols, WIDTH // tile_size + SCROLL_EXTRA_COLS)
	out = []
	for row in data:
		r = list(row)
		while len(r) < base_cols:
			r.append(0)
		if len(r) >= target:
			out.append(r[:target])
			continue
		ext = 0
		for c in reversed(r):
			if c == 0:
				continue
			if c in range(1, 14) or c == 18:
				ext = c
			break
		r.extend([ext] * (target - len(r)))
		out.append(r)
	return out


def sync_hud_score_pickup_world_rect(sprite, scroll_x):
	"""Keeps the score gem pinned to the top-right of the *window* while using world coords for collisions."""
	if getattr(sprite, 'hud_screen_anchor', False):
		sprite.rect.x = int(scroll_x) + WIDTH - 3 * tile_size
		sprite.rect.y = tile_size // 2


def load_level(level):
	def _read_level(level_no):
		game_level = f'levels/level{level_no}_data'
		if not os.path.exists(game_level):
			return None
		with open(game_level, 'rb') as f:
			return pickle.load(f)

	def _merge_two_levels(left_data, right_data):
		if right_data is None:
			return left_data

		left_rows = len(left_data)
		right_rows = len(right_data)
		left_cols = max(len(row) for row in left_data) if left_data else 0
		right_cols = max(len(row) for row in right_data) if right_data else 0
		total_rows = max(left_rows, right_rows)
		merged = []

		for row_idx in range(total_rows):
			left_row = list(left_data[row_idx]) if row_idx < left_rows else [0] * left_cols
			right_row = list(right_data[row_idx]) if row_idx < right_rows else [0] * right_cols

			if len(left_row) < left_cols:
				left_row.extend([0] * (left_cols - len(left_row)))
			if len(right_row) < right_cols:
				right_row.extend([0] * (right_cols - len(right_row)))

			# Keep only the final gate at the end of merged map.
			left_row = [0 if c == 24 else c for c in left_row]
			merged.append(left_row + right_row)

		return merged

	data = _read_level(level)
	if data is None:
		return None

	next_data = _read_level(level + 1)
	data = _merge_two_levels(data, next_data)
	return pad_rows_for_horizontal_scroll(data)

def draw_text(win, text, pos):
	img = score_font.render(text, True, BLUE)
	win.blit(img, pos)
