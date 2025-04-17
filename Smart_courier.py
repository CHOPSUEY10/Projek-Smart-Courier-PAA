import pygame
import random
import sys
import tkinter as tk
from tkinter import filedialog

# Inisialisasi Pygame
pygame.init()

# Konfigurasi layar
WIDTH = 800
HEIGHT = 600
TILE_SIZE = 30
GRID_WIDTH = WIDTH // TILE_SIZE
GRID_HEIGHT = HEIGHT // TILE_SIZE
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Smart Courier Demo")

# Warna
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Arah hadap
DIRECTIONS = {
    "UP": (0, -1),
    "RIGHT": (1, 0),
    "DOWN": (0, 1),
    "LEFT": (-1, 0)
}

# Tipe tile jalan
ROAD_TYPES = {
    "STRAIGHT": 0,       # Jalan lurus (vertikal atau horizontal)
    "TURN": 1,           # Tikungan (rotasi untuk 4 orientasi)
    "T_JUNCTION": 2,     # Simpang tiga (rotasi untuk 4 orientasi)
    "INTERSECTION": 3    # Simpang empat
}

# Orientasi untuk tipe jalan
ORIENTATIONS = {
    "VERTICAL": 0,       # 0 derajat
    "HORIZONTAL": 90,    # 90 derajat
    "UP": 0,             # T menghadap atas
    "RIGHT": 90,         # T menghadap kanan
    "DOWN": 180,         # T menghadap bawah
    "LEFT": 270,         # T menghadap kiri
    "TURN_TL": 0,        # Tikungan kiri atas
    "TURN_TR": 90,       # Tikungan kanan atas
    "TURN_BR": 180,      # Tikungan kanan bawah
    "TURN_BL": 270       # Tikungan kiri bawah
}

assets = {}
asset_names = [
    "road_straight",
    "road_turn",
    "road_t_junction",
    "road_intersection",
    "house_tile",
    "courier_car"
]

def load_assets_from_file_explorer():
    """
    Opens a file explorer dialog for each asset to select image files.
    Creates fallback surfaces if files are not selected or invalid.
    Returns a dictionary containing the loaded or fallback assets.
    """
    root = tk.Tk()
    root.withdraw()



    print("Please select an image file for each asset (or cancel for fallback).")
    
    for asset_name in asset_names:
        try:
            print(f"select the {asset_name} asset :")
            file_path = filedialog.askopenfilename(
                title=f"Select {asset_name} image",
                filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")]
            )
            if file_path:
                try:
                    assets[asset_name] = pygame.image.load(file_path)
                    if asset_name == "courier_car":
                        assets[asset_name] = pygame.transform.rotate(assets[asset_name], 90)
                    print(f"Loaded {asset_name} from {file_path}")
                except pygame.error as e:
                    print(f"Error loading {asset_name} from {file_path}: {e}. Using fallback.")
                    assets[asset_name] = create_fallback_surface(asset_name)
            else:
                print(f"No file selected for {asset_name}. Using fallback.")
                assets[asset_name] = create_fallback_surface(asset_name)
        except Exception as e:
            print(f"Error selecting file for {asset_name}: {e}. Using fallback.")
            assets[asset_name] = create_fallback_surface(asset_name)

    root.destroy()

    # Scale all assets to TILE_SIZE
    for key in assets:
        assets[key] = pygame.transform.scale(assets[key], (TILE_SIZE, TILE_SIZE))

    return assets


def create_fallback_surface(asset_name):
    """
    Creates a fallback surface for the specified asset name.
    """
    surface = pygame.Surface((TILE_SIZE, TILE_SIZE))
    
    if asset_name == "road_straight":
        surface.fill((100, 100, 100))
        pygame.draw.line(surface, WHITE, (TILE_SIZE//2, 0), (TILE_SIZE//2, TILE_SIZE), 2)
    elif asset_name == "road_turn":
        surface.fill((100, 100, 100))
        pygame.draw.line(surface, WHITE, (TILE_SIZE//2, 0), (TILE_SIZE//2, TILE_SIZE//2), 2)
        pygame.draw.line(surface, WHITE, (TILE_SIZE//2, TILE_SIZE//2), (TILE_SIZE, TILE_SIZE//2), 2)
    elif asset_name == "road_t_junction":
        surface.fill((100, 100, 100))
        pygame.draw.line(surface, WHITE, (0, TILE_SIZE//2), (TILE_SIZE, TILE_SIZE//2), 2)
        pygame.draw.line(surface, WHITE, (TILE_SIZE//2, TILE_SIZE//2), (TILE_SIZE//2, 0), 2)
    elif asset_name == "road_intersection":
        surface.fill((100, 100, 100))
        pygame.draw.line(surface, WHITE, (TILE_SIZE//2, 0), (TILE_SIZE//2, TILE_SIZE), 2)
        pygame.draw.line(surface, WHITE, (0, TILE_SIZE//2), (TILE_SIZE, TILE_SIZE//2), 2)
    elif asset_name == "house_tile":
        surface.fill((150, 75, 0))
    elif asset_name == "courier_car":
        surface.fill(BLUE)
    
    return surface


# Kelas Kurir
class Courier:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.direction = "RIGHT"
        self.has_package = False
        self.moving = False
        self.path = []

    def move(self, dx, dy):
        new_x = self.x + dx
        new_y = self.y + dy
        if 0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT and grid[new_y][new_x] != 1:  # 1 = rumah/non-jalan
            self.x = new_x
            self.y = new_y

    def turn(self, new_direction):
        self.direction = new_direction

    def try_pickup(self, source_x, source_y):
        if self.x == source_x and self.y == source_y and not self.has_package:
            self.has_package = True
            return True
        return False

    def try_deliver(self, dest_x, dest_y):
        if self.x == dest_x and self.y == dest_y and self.has_package:
            self.has_package = False
            return True
        return False

    def follow_path(self):
        if self.path and self.moving:
            next_pos = self.path[0]
            dx, dy = next_pos[0] - self.x, next_pos[1] - self.y
            if dx > 0:
                self.turn("RIGHT")
            elif dx < 0:
                self.turn("LEFT")
            elif dy > 0:
                self.turn("DOWN")
            elif dy < 0:
                self.turn("UP")
            self.move(dx, dy)
            if (self.x, self.y) == next_pos:
                self.path.pop(0)

# Pathfinding (A* algorithm)
def a_star(start, goal):
    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    open_set = {start}
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}

    while open_set:
        current = min(open_set, key=lambda pos: f_score[pos])
        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path

        open_set.remove(current)
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            neighbor = (current[0] + dx, current[1] + dy)
            if 0 <= neighbor[0] < GRID_WIDTH and 0 <= neighbor[1] < GRID_HEIGHT and grid[neighbor[1]][neighbor[0]] != 1:
                tentative_g_score = g_score[current] + 1
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                    open_set.add(neighbor)
    return []

# Fungsi untuk menentukan jenis jalan dan orientasinya berdasarkan koneksi
def determine_road_type_and_orientation(x, y, grid):
    # Periksa arah mana yang terhubung dengan jalan
    connections = [0, 0, 0, 0]  # UP, RIGHT, DOWN, LEFT
    
    # Cek atas
    if y > 0 and grid[y-1][x] != 1:
        connections[0] = 1
    
    # Cek kanan
    if x < GRID_WIDTH-1 and grid[y][x+1] != 1:
        connections[1] = 1
    
    # Cek bawah
    if y < GRID_HEIGHT-1 and grid[y+1][x] != 1:
        connections[2] = 1
    
    # Cek kiri
    if x > 0 and grid[y][x-1] != 1:
        connections[3] = 1
    
    # Tentukan tipe jalan dan orientasi berdasarkan koneksi
    connection_sum = sum(connections)
    
    if connection_sum == 4:
        return ROAD_TYPES["INTERSECTION"], 0  # Simpang empat, tidak perlu rotasi
    
    elif connection_sum == 3:
        # Simpang tiga (T-junction)
        if connections[0] == 0:  # T menghadap bawah (tidak terhubung atas)
            return ROAD_TYPES["T_JUNCTION"], ORIENTATIONS["DOWN"]
        elif connections[1] == 0:  # T menghadap kiri (tidak terhubung kanan)
            return ROAD_TYPES["T_JUNCTION"], ORIENTATIONS["LEFT"]
        elif connections[2] == 0:  # T menghadap atas (tidak terhubung bawah)
            return ROAD_TYPES["T_JUNCTION"], ORIENTATIONS["UP"]
        else:  # connections[3] == 0, T menghadap kanan (tidak terhubung kiri)
            return ROAD_TYPES["T_JUNCTION"], ORIENTATIONS["RIGHT"]
    
    elif connection_sum == 2:
        # Cek apakah jalan lurus
        if connections[0] == 1 and connections[2] == 1:
            return ROAD_TYPES["STRAIGHT"], ORIENTATIONS["VERTICAL"]  # Jalan lurus vertikal
        elif connections[1] == 1 and connections[3] == 1:
            return ROAD_TYPES["STRAIGHT"], ORIENTATIONS["HORIZONTAL"]  # Jalan lurus horizontal
        
        # Tikungan
        elif connections[0] == 1 and connections[1] == 1:
            return ROAD_TYPES["TURN"], ORIENTATIONS["TURN_TR"]  # Tikungan kanan atas
        elif connections[0] == 1 and connections[3] == 1:
            return ROAD_TYPES["TURN"], ORIENTATIONS["TURN_TL"]  # Tikungan kiri atas
        elif connections[2] == 1 and connections[1] == 1:
            return ROAD_TYPES["TURN"], ORIENTATIONS["TURN_BR"]  # Tikungan kanan bawah
        elif connections[2] == 1 and connections[3] == 1:
            return ROAD_TYPES["TURN"], ORIENTATIONS["TURN_BL"]  # Tikungan kiri bawah
    
    elif connection_sum == 1:
        # Jalan buntu, gunakan tipe lurus dengan orientasi yang sesuai
        if connections[0] == 1:
            return ROAD_TYPES["STRAIGHT"], ORIENTATIONS["VERTICAL"]
        elif connections[1] == 1:
            return ROAD_TYPES["STRAIGHT"], ORIENTATIONS["HORIZONTAL"]
        elif connections[2] == 1:
            return ROAD_TYPES["STRAIGHT"], ORIENTATIONS["VERTICAL"]
        else:  # connections[3] == 1
            return ROAD_TYPES["STRAIGHT"], ORIENTATIONS["HORIZONTAL"]
    
    # Default jika tidak ada koneksi (tidak seharusnya terjadi)
    return ROAD_TYPES["INTERSECTION"], 0

# Generate tilemap peta jalan kota dengan simpang dan tikungan
def generate_map():
    # Inisialisasi grid (1 = blok perumahan/non-jalan)
    grid = [[1 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    
    # Buat grid jalan kota (horizontal dan vertikal)
    road_spacing_x = random.randint(5, 8)
    road_spacing_y = random.randint(5, 8)

    # Buat jalan horizontal utama
    for y in range(road_spacing_y, GRID_HEIGHT, road_spacing_y):
        if y < GRID_HEIGHT:  # Pastikan masih dalam grid
            for x in range(GRID_WIDTH):
                grid[y][x] = 0  # 0 = jalan

    # Buat jalan vertikal utama
    for x in range(road_spacing_x, GRID_WIDTH, road_spacing_x):
        if x < GRID_WIDTH:  # Pastikan masih dalam grid
            for y in range(GRID_HEIGHT):
                grid[y][x] = 0  # 0 = jalan

    # Tambahkan beberapa jalan terputus untuk variasi
    for _ in range(random.randint(3, 6)):
        if random.choice([True, False]):  # Jalan horizontal
            y = random.randint(0, GRID_HEIGHT - 1)
            start_x = random.randint(0, GRID_WIDTH - road_spacing_x)
            end_x = start_x + random.randint(road_spacing_x//2, road_spacing_x)
            end_x = min(end_x, GRID_WIDTH)
            for x in range(start_x, end_x):
                grid[y][x] = 0
        else:  # Jalan vertikal
            x = random.randint(0, GRID_WIDTH - 1)
            start_y = random.randint(0, GRID_HEIGHT - road_spacing_y)
            end_y = start_y + random.randint(road_spacing_y//2, road_spacing_y)
            end_y = min(end_y, GRID_HEIGHT)
            for y in range(start_y, end_y):
                grid[y][x] = 0

    # Tentukan tipe jalan dan orientasi untuk setiap tile jalan
    road_types = [[1 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    road_orientations = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if grid[y][x] == 0:  # Jika jalan
                road_type, road_orientation = determine_road_type_and_orientation(x, y, grid)
                road_types[y][x] = road_type
                road_orientations[y][x] = road_orientation
            else:
                road_types[y][x] = 1  # Non-jalan
                road_orientations[y][x] = 0  # Tidak ada orientasi

    return grid, road_types, road_orientations

# Posisi acak di jalan
def random_position():
    positions = []
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if grid[y][x] != 1:  # Bukan rumah (adalah jalan)
                positions.append((x, y))
    
    if not positions:
        # Fallback jika tidak ada posisi jalan yang valid
        return (0, 0)
    return random.choice(positions)

# Gambar peta
def draw_map():
    screen.fill(WHITE)
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if grid[y][x] != 1:  # Jalan
                road_type = road_types[y][x]
                road_orientation = road_orientations[y][x]
                
                # Pilih aset sesuai tipe jalan
                if road_type == ROAD_TYPES["STRAIGHT"]:
                    road_image = assets["road_straight"]
                elif road_type == ROAD_TYPES["TURN"]:
                    road_image = assets["road_turn"]
                elif road_type == ROAD_TYPES["T_JUNCTION"]:
                    road_image = assets["road_t_junction"]
                elif road_type == ROAD_TYPES["INTERSECTION"]:
                    road_image = assets["road_intersection"]
                else:
                    road_image = assets["road_intersection"]  # Default fallback
                
                # Rotasi gambar sesuai orientasi
                rotated_road = pygame.transform.rotate(road_image, road_orientation)
                
                # Menyesuaikan posisi setelah rotasi agar tetap berada di tengah tile
                rect = rotated_road.get_rect(center=((x * TILE_SIZE) + TILE_SIZE//2, 
                                                   (y * TILE_SIZE) + TILE_SIZE//2))
                screen.blit(rotated_road, rect)
            else:  # Blok perumahan
                screen.blit(assets["house_tile"], (x * TILE_SIZE, y * TILE_SIZE))
    
    # Gambar lokasi pengambilan (kuning) dan pengiriman (merah)
    pygame.draw.rect(screen, YELLOW, (source_x * TILE_SIZE, source_y * TILE_SIZE, TILE_SIZE, TILE_SIZE), 3)  # Garis tepi saja
    pygame.draw.rect(screen, RED, (dest_x * TILE_SIZE, dest_y * TILE_SIZE, TILE_SIZE, TILE_SIZE), 3)  # Garis tepi saja
    
    # Rotasi mobil kurir berdasarkan arahnya
    angle = 0
    if courier.direction == "UP":
        angle = 0
    elif courier.direction == "RIGHT":
        angle = 270
    elif courier.direction == "DOWN":
        angle = 180
    elif courier.direction == "LEFT":
        angle = 90
    
    rotated_car = pygame.transform.rotate(assets["courier_car"], angle)
    # Menghitung posisi yang disesuaikan untuk rotasi
    car_rect = rotated_car.get_rect(center=((courier.x * TILE_SIZE) + TILE_SIZE//2, 
                                          (courier.y * TILE_SIZE) + TILE_SIZE//2))
    screen.blit(rotated_car, car_rect)

    # Gambar tombol
    pygame.draw.rect(screen, BLACK, start_button)
    pygame.draw.rect(screen, BLACK, stop_button)
    pygame.draw.rect(screen, BLACK, randomize_button)
    pygame.draw.rect(screen, BLACK, generate_button)
    pygame.draw.rect(screen, BLACK, load_button)
    
    font = pygame.font.Font(None, 20)
    screen.blit(font.render("Start", True, WHITE), (start_button.x + 10, start_button.y + 5))
    screen.blit(font.render("Stop", True, WHITE), (stop_button.x + 10, stop_button.y + 5))
    screen.blit(font.render("Randomize", True, WHITE), (randomize_button.x + 10, randomize_button.y + 5))
    screen.blit(font.render("Generate Map", True, WHITE), (generate_button.x + 10, generate_button.y + 5))
    screen.blit(font.render("Loading Map", True, WHITE), (load_button.x + 10, load_button.y + 5))

    # Status paket
    status_text = "Carrying Package" if courier.has_package else "No Package"
    text = font.render(status_text, True, BLACK)
    screen.blit(text, (10, HEIGHT - 30))

# Inisialisasi peta
grid, road_types, road_orientations = generate_map()
source_x, source_y = random_position()
dest_x, dest_y = random_position()
while (dest_x, dest_y) == (source_x, source_y):
    dest_x, dest_y = random_position()
courier_x, courier_y = random_position()
courier = Courier(courier_x, courier_y)

# Tombol


# Loop utama
clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        start_button = pygame.Rect(WIDTH - 150, 10, 120, 40)
        stop_button = pygame.Rect(WIDTH - 150, 60, 120, 40)
        randomize_button = pygame.Rect(WIDTH - 150, 110, 120, 40)
        generate_button = pygame.Rect(WIDTH - 150, 160, 120, 40)
        load_button = pygame.Rect(WIDTH - 150, 210, 120, 40)

        # Gambar tombol
        pygame.draw.rect(screen, BLACK, start_button)
        pygame.draw.rect(screen, BLACK, stop_button)
        pygame.draw.rect(screen, BLACK, randomize_button)
        pygame.draw.rect(screen, BLACK, generate_button)
        pygame.draw.rect(screen, BLACK, load_button)
        
        font = pygame.font.Font(None, 20)
        screen.blit(font.render("Start", True, WHITE), (start_button.x + 10, start_button.y + 5))
        screen.blit(font.render("Stop", True, WHITE), (stop_button.x + 10, stop_button.y + 5))
        screen.blit(font.render("Randomize", True, WHITE), (randomize_button.x + 10, randomize_button.y + 5))
        screen.blit(font.render("Generate Map", True, WHITE), (generate_button.x + 10, generate_button.y + 5))
        screen.blit(font.render("Loading Map", True, WHITE), (load_button.x + 10, load_button.y + 5))


        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if start_button.collidepoint(event.pos):
                if not courier.has_package:
                    # Cari jalur ke sumber paket
                    courier.path = a_star((courier.x, courier.y), (source_x, source_y))
                    if not courier.path:
                        print("Tidak dapat menemukan jalur ke sumber paket!")
                    else:
                        courier.moving = True
                else:
                    courier.path = a_star((courier.x, courier.y), (dest_x, dest_y))
                    if not courier.path:
                        print("Tidak dapat menemukan jalur ke tujuan!")
                    else:
                        courier.moving = True
            elif stop_button.collidepoint(event.pos):
                courier.moving = False
                courier.path = []
            elif randomize_button.collidepoint(event.pos):
                source_x, source_y = random_position()
                dest_x, dest_y = random_position()
                while (dest_x, dest_y) == (source_x, source_y):
                    dest_x, dest_y = random_position()
                courier_x, courier_y = random_position()
                courier = Courier(courier_x, courier_y)
            elif generate_button.collidepoint(event.pos):
                grid, road_types, road_orientations = generate_map()
                source_x, source_y = random_position()
                dest_x, dest_y = random_position()
                while (dest_x, dest_y) == (source_x, source_y):
                    dest_x, dest_y = random_position()
                courier_x, courier_y = random_position()
                courier = Courier(courier_x, courier_y)
            elif load_button.collidepoint(event.pos):
                load_assets_from_file_explorer()
                print("successful loading the asset")


    # Update posisi kurir
    if courier.moving:
        courier.follow_path()
        # Periksa jika path kosong dan kurir sudah tiba di tujuan
        if not courier.path:
            if not courier.has_package and courier.x == source_x and courier.y == source_y:
                if courier.try_pickup(source_x, source_y):
                    print("Package picked up!")
                    # Setelah mengambil paket, tentukan rute ke tujuan
                    courier.path = a_star((courier.x, courier.y), (dest_x, dest_y))
                    if not courier.path:
                        print("Tidak dapat menemukan jalur ke tujuan!")
                        courier.moving = False
            elif courier.has_package and courier.x == dest_x and courier.y == dest_y:
                if courier.try_deliver(dest_x, dest_y):
                    print("Package delivered!")
                    courier.moving = False

    if assets and all(name in assets for name in asset_names):
        draw_map()
    pygame.display.flip()
    clock.tick(10)

pygame.quit()
sys.exit()