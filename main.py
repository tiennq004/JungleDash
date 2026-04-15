import os
import random
import pygame
from pygame.locals import *

from objects import (
	World,
	Player,
	Button,
	Diamond,
	draw_lines,
	load_level,
	draw_text,
	sounds,
	sync_hud_score_pickup_world_rect,
	WIDTH,
	HEIGHT,
)
from hand_controller import HandGestureController

# Window setup
SIZE = WIDTH , HEIGHT
tile_size = 50

pygame.init()
# Use double buffering + hardware surface for smoother rendering.
win = pygame.display.set_mode(SIZE, pygame.HWSURFACE | pygame.DOUBLEBUF)
pygame.display.set_caption('DASH')
clock = pygame.time.Clock()
FPS = 60

intro_title_font = pygame.font.SysFont('Bauhaus 93', 48)
intro_text_font = pygame.font.SysFont('segoeui,arial', 24)
intro_hint_font = pygame.font.SysFont('segoeui,arial', 20, bold=True)
menu_font = pygame.font.SysFont('segoeui,arial', 28, bold=True)
menu_hint_font = pygame.font.SysFont('segoeui,arial', 22)
menu_item_font = pygame.font.SysFont('segoeui,arial', 24, bold=True)

INTRO_LINES = [
	"Trong một khu rừng cổ đại bị lãng quên, nơi bóng tối đang dần nuốt chửng mọi sự sống,",
	"những sinh vật kỳ lạ bắt đầu xuất hiện và phá vỡ sự yên bình vốn có.",
	"Không ai biết nguồn gốc của thế lực này... chỉ biết rằng bất kỳ ai bước vào đều không thể quay trở lại.",
	"",
	"Giữa lúc đó, một cái tên xuất hiện — Anh Liêm, một nhà thám hiểm trẻ mang trong mình",
	"lòng dũng cảm và quyết tâm bảo vệ quê hương.",
	"Không chờ đợi, không do dự, Anh Liêm bước vào khu rừng chết chóc, nơi mỗi bước đi đều là thử thách,",
	"mỗi sai lầm đều phải trả giá.",
	"",
	"Trên hành trình của mình, Anh Liêm sẽ phải vượt qua những cạm bẫy cổ xưa, chạy trốn khỏi những sinh vật",
	"bị tha hóa, và khám phá bí mật đằng sau bóng tối đang lan rộng.",
	"",
	"Liệu Anh Liêm có thể sống sót... hay sẽ trở thành một phần của khu rừng?",
	"",
	"Cuộc hành trình bắt đầu ngay bây giờ.",
]


def wrap_text(text, font, max_width):
	if not text:
		return [""]
	words = text.split()
	lines = []
	current = words[0]
	for word in words[1:]:
		candidate = current + " " + word
		if font.size(candidate)[0] <= max_width:
			current = candidate
		else:
			lines.append(current)
			current = word
	lines.append(current)
	return lines


def scale_cover(image, size):
	target_w, target_h = size
	src_w, src_h = image.get_size()
	scale = max(target_w / src_w, target_h / src_h)
	new_w = max(1, int(src_w * scale))
	new_h = max(1, int(src_h * scale))
	scaled = pygame.transform.smoothscale(image, (new_w, new_h))
	crop_x = (new_w - target_w) // 2
	crop_y = (new_h - target_h) // 2
	return scaled.subsurface((crop_x, crop_y, target_w, target_h)).copy()


def draw_intro(surface):
	surface.blit(bg1, (0, 0))
	overlay = pygame.Surface(SIZE, pygame.SRCALPHA)
	overlay.fill((0, 0, 0, 150))
	surface.blit(overlay, (0, 0))

	panel_rect = pygame.Rect(45, 30, WIDTH - 90, HEIGHT - 65)
	panel = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
	panel.fill((8, 16, 24, 180))
	surface.blit(panel, panel_rect.topleft)
	pygame.draw.rect(surface, (120, 180, 140), panel_rect, 2, border_radius=10)

	title_img = intro_title_font.render("Jungle Dash", True, (255, 221, 110))
	surface.blit(title_img, (WIDTH // 2 - title_img.get_width() // 2, panel_rect.y + 16))

	text_x = panel_rect.x + 26
	max_width = panel_rect.width - 52
	text_bottom = panel_rect.bottom - 68
	text_font = intro_text_font
	text_line_h = 32
	paragraph_gap = 6
	blank_gap = 16

	for size in range(24, 15, -1):
		candidate_font = pygame.font.SysFont('segoeui,arial', size)
		line_h = max(24, size + 8)
		total_h = 0
		for paragraph in INTRO_LINES:
			if paragraph == "":
				total_h += blank_gap
			else:
				total_h += len(wrap_text(paragraph, candidate_font, max_width)) * line_h + paragraph_gap
		start_y = panel_rect.y + 92
		if start_y + total_h <= text_bottom:
			text_font = candidate_font
			text_line_h = line_h
			break

	y = panel_rect.y + 92
	for paragraph in INTRO_LINES:
		if paragraph == "":
			y += blank_gap
			continue
		for line in wrap_text(paragraph, text_font, max_width):
			line_img = text_font.render(line, True, (245, 245, 245))
			surface.blit(line_img, (text_x, y))
			y += text_line_h
		y += paragraph_gap

	hint = "Nhan phim bat ky hoac click chuot de tiep tuc"
	hint_img = intro_hint_font.render(hint, True, (180, 255, 180))
	surface.blit(hint_img, (WIDTH // 2 - hint_img.get_width() // 2, panel_rect.bottom - 34))


def draw_background(surface, image):
	# Fill first so no bottom seam appears on any display scaling.
	surface.fill((186, 236, 255))
	bg_x = (WIDTH - image.get_width()) // 2
	bg_y = HEIGHT - image.get_height()
	surface.blit(image, (bg_x, bg_y))


class GestureKeys:
	def __init__(self):
		self.state = {
			K_UP: False,
			K_SPACE: False,
			K_x: False,
			K_LEFT: False,
			K_RIGHT: False,
		}

	def set_controls(self, controls):
		keyboard = pygame.key.get_pressed()
		jump = controls.get("jump", False) or keyboard[K_UP] or keyboard[K_SPACE]
		power = controls.get("power", False) or keyboard[K_x]
		left = controls.get("left", False) or keyboard[K_LEFT]
		right = controls.get("right", False) or keyboard[K_RIGHT]
		self.state[K_UP] = jump
		self.state[K_SPACE] = jump
		self.state[K_x] = power
		self.state[K_LEFT] = left
		self.state[K_RIGHT] = right

	def __getitem__(self, key):
		return self.state.get(key, False)


# background images
bg1 = scale_cover(pygame.image.load('assets/BG1.png'), SIZE)
bg2 = scale_cover(pygame.image.load('assets/BG2.png'), SIZE)
bg = bg1
sun = pygame.transform.smoothscale(pygame.image.load('assets/sun.png'), (96, 96))
jungle_dash = pygame.image.load('assets/jungle dash.png')
you_won = pygame.image.load('assets/won.png')


# loading level 1
level = 1
max_level = len(os.listdir('levels/'))
level_step = 2
stage_starts = list(range(1, max_level + 1, level_step))
selected_stage_idx = 0
data = load_level(level)

player_pos = (10, 340)


# creating world & objects
water_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
forest_group = pygame.sprite.Group()
diamond_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
enemies_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()
bridge_group = pygame.sprite.Group()
enemy_bullet_group = pygame.sprite.Group()
groups = [water_group, lava_group, forest_group, diamond_group, enemies_group, exit_group, platform_group,
			bridge_group, enemy_bullet_group]
world = World(win, data, groups)
player = Player(win, player_pos, world, groups)

hud_score_pickup = None


def add_hud_score_pickup():
	global hud_score_pickup
	hud_score_pickup = Diamond(0, tile_size // 2, hud_screen_anchor=True)
	diamond_group.add(hud_score_pickup)


add_hud_score_pickup()

# creating buttons
play= pygame.image.load('assets/play.png')
replay = pygame.image.load('assets/replay.png')
home = pygame.image.load('assets/home.png')
exit = pygame.image.load('assets/exit.png')
setting = pygame.image.load('assets/setting.png')

play_btn = Button(play, (128, 64), WIDTH//2 - WIDTH // 16, HEIGHT//2)
replay_btn  = Button(replay, (45,42), WIDTH//2 - 110, HEIGHT//2 + 20)
home_btn  = Button(home, (45,42), WIDTH//2 - 20, HEIGHT//2 + 20)
exit_btn  = Button(exit, (45,42), WIDTH//2 + 70, HEIGHT//2 + 20)


# function to reset a level
def reset_level(level):
	global cur_score
	cur_score = 0

	data = load_level(level)
	if data:
		for group in groups:
			group.empty()
		world = World(win, data, groups)
		player.reset(win, player_pos, world, groups)
		add_hud_score_pickup()
	return world


def draw_sprite_group_with_scroll(surface, group, scroll_x):
	sx = int(scroll_x)
	for spr in group:
		surface.blit(spr.image, (spr.rect.x - sx, spr.rect.y))


def get_stage_ui_items():
	items = []
	box_w = 92
	box_h = 74
	gap_x = 22
	gap_y = 18
	cols = 3
	rows = (len(stage_starts) + cols - 1) // cols
	total_w = cols * box_w + (cols - 1) * gap_x
	total_h = rows * box_h + (rows - 1) * gap_y
	start_x = WIDTH // 2 - total_w // 2
	start_y = HEIGHT // 2 + 10 - total_h // 2
	for idx, _start_level in enumerate(stage_starts):
		row = idx // cols
		col = idx % cols
		label = f"{idx + 1}"
		rect = pygame.Rect(
			start_x + col * (box_w + gap_x),
			start_y + row * (box_h + gap_y),
			box_w,
			box_h,
		)
		items.append((rect, label))
	return items


def start_selected_stage(reset_score=True):
	global level, world, main_menu, game_over, level_won, game_won, score, selecting_stage, bg
	level = stage_starts[selected_stage_idx]
	world = reset_level(level)
	main_menu = False
	selecting_stage = False
	game_over = False
	level_won = False
	game_won = False
	if reset_score:
		score = 0
	bg = random.choice([bg1, bg2])

score = 0
cur_score = 0

main_menu = True
selecting_stage = False
show_intro = True
game_over = False
level_won = False
game_won = False
running = True
hand_controller = HandGestureController()
gesture_keys = GestureKeys()
while running:
	for event in pygame.event.get():
		if event.type == QUIT:
			running = False
		if show_intro and event.type in (KEYDOWN, MOUSEBUTTONDOWN):
			show_intro = False
		if (not show_intro) and main_menu and selecting_stage and event.type == KEYDOWN:
			if event.key == K_LEFT:
				selected_stage_idx = (selected_stage_idx - 1) % len(stage_starts)
			elif event.key == K_RIGHT:
				selected_stage_idx = (selected_stage_idx + 1) % len(stage_starts)
			elif event.key == K_UP:
				selected_stage_idx = (selected_stage_idx - 3) % len(stage_starts)
			elif event.key == K_DOWN:
				selected_stage_idx = (selected_stage_idx + 3) % len(stage_starts)
			elif K_1 <= event.key <= K_9:
				num = event.key - K_0
				if 1 <= num <= len(stage_starts):
					selected_stage_idx = num - 1
			elif event.key == K_RETURN:
				start_selected_stage()
			elif event.key == K_ESCAPE:
				selecting_stage = False
		if (not show_intro) and main_menu and selecting_stage and event.type == MOUSEBUTTONDOWN and event.button == 1:
			for idx, (rect, _label) in enumerate(get_stage_ui_items()):
				if rect.collidepoint(event.pos):
					selected_stage_idx = idx
					start_selected_stage()
		if (not show_intro) and (not main_menu) and game_over and event.type == KEYDOWN:
			if event.key == K_r:
				score -= cur_score
				world = reset_level(level)
				game_over = False
			elif event.key == K_h:
				game_over = True
				main_menu = True
				selecting_stage = True
				bg = bg1

	controls = hand_controller.get_controls()
	gesture_keys.set_controls(controls)

	scroll_x = 0
	if not main_menu and data:
		scroll_x = player.rect.centerx - WIDTH // 2
		max_scroll = max(0, world.world_pixel_width - WIDTH)
		scroll_x = int(max(0, min(scroll_x, max_scroll)))
	if hud_score_pickup is not None:
		sync_hud_score_pickup_world_rect(hud_score_pickup, scroll_x)

	# displaying background & sun image
	draw_background(win, bg)
	win.blit(sun, (40, 40))
	world.draw(scroll_x)
	for group in groups:
		draw_sprite_group_with_scroll(win, group, scroll_x)

	# drawing grid
	# draw_lines(win)

	if show_intro:
		draw_intro(win)

	elif main_menu:
		win.blit(jungle_dash, (WIDTH//2 - WIDTH//8, HEIGHT//4))
		if not hand_controller.available:
			draw_text(win, hand_controller.status_message, (WIDTH//2 - 200, HEIGHT//2 - 40))

		if not selecting_stage:
			play_game = play_btn.draw(win)
			if play_game:
				selecting_stage = True
		else:
			stage_text = "Chon man"
			stage_img = menu_font.render(stage_text, True, (240, 248, 255))
			win.blit(stage_img, (WIDTH // 2 - stage_img.get_width() // 2, HEIGHT // 2 - 82))

			hint_text = "Nhan 1-6 hoac click de vao man"
			hint_img = menu_hint_font.render(hint_text, True, (200, 235, 210))
			win.blit(hint_img, (WIDTH // 2 - hint_img.get_width() // 2, HEIGHT // 2 - 48))

			for idx, (rect, label) in enumerate(get_stage_ui_items()):
				selected = idx == selected_stage_idx
				fill = (55, 110, 85, 220) if selected else (24, 45, 60, 190)
				item_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
				item_surf.fill(fill)
				win.blit(item_surf, rect.topleft)
				border_color = (180, 255, 180) if selected else (120, 150, 170)
				pygame.draw.rect(win, border_color, rect, 2, border_radius=8)
				text_img = menu_item_font.render(label, True, (245, 245, 245))
				win.blit(text_img, (rect.centerx - text_img.get_width() // 2, rect.centery - text_img.get_height() // 2))

	else:
		
		if not game_over and not game_won:
			for enemy in enemies_group:
				enemy.update(player, enemy_bullet_group, world.world_pixel_width)
			enemy_bullet_group.update(world.world_pixel_width)
			platform_group.update()
			exit_group.update(player)
			if pygame.sprite.spritecollide(player, diamond_group, True):
				sounds[0].play()
				cur_score += 1
				score += 1	
			draw_text(win, f'{score}', ((WIDTH//tile_size - 2) * tile_size, tile_size//2 + 10))
			
		game_over, level_won = player.update(gesture_keys, game_over, level_won, game_won, scroll_x)

		if game_over and not game_won:
			replay = replay_btn.draw(win)
			home = home_btn.draw(win)
			choice_hint = menu_hint_font.render("R: Choi lai man   |   H: Ve chon man", True, (240, 240, 240))
			win.blit(choice_hint, (WIDTH // 2 - choice_hint.get_width() // 2, HEIGHT // 2 + 80))

			if replay:
				score -= cur_score
				world = reset_level(level)
				game_over = False
			if home:
				game_over = True
				main_menu = True
				selecting_stage = True
				bg = bg1

		if level_won:
			score += cur_score
			cur_score = 0
			level_won = False
			next_stage_idx = selected_stage_idx + 1
			if next_stage_idx < len(stage_starts):
				selected_stage_idx = next_stage_idx
				start_selected_stage(reset_score=False)
			else:
				game_won = True
				bg = bg1

		if game_won:
			win.blit(you_won, (WIDTH//4, HEIGHT // 4))
			replay = replay_btn.draw(win)
			home = home_btn.draw(win)

			if replay:
				score = 0
				world = reset_level(level)
				game_over = False
				game_won = False
			if home:
				main_menu = True
				selecting_stage = False
				game_over = False
				game_won = False

	pygame.display.flip()
	clock.tick(FPS)

pygame.quit()
hand_controller.close()