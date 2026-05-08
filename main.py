import pygame
import sys
import random

# --- CONFIGURAÇÕES INICIAIS ---
pygame.init()
pygame.mixer.init()
WIDTH, HEIGHT = 1200, 1000
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("60 Segundos - Sob Pressão")
clock = pygame.time.Clock()

# --- CARREGAMENTO DE ÁUDIO ---
def load_audio():
    try:
        # Música de fundo
        pygame.mixer.music.load("musica_fundo.mp3") 
        pygame.mixer.music.set_volume(0.4)
        pygame.mixer.music.play(-1)
        
        # Efeitos sonoros
        som_passos = pygame.mixer.Sound("passos.wav")
        som_coletar = pygame.mixer.Sound("coletar.wav")
        
        # --- AJUSTE DE VOLUME AQUI ---
        # Mude 0.3 para o valor que desejar (0.1 a 1.0)
        som_coletar.set_volume(0.3) 
        
        return som_passos, som_coletar
    except:
        print("Aviso: Arquivos de áudio não encontrados.")
        return None, None

som_passos, som_coletar = load_audio()
passos_ativos = False 

# --- CORES E FONTES ---
WHITE = (255, 255, 255)
RED = (180, 0, 0)
BLACK = (0, 0, 0)
font = pygame.font.SysFont("Arial", 32, bold=True)
big_font = pygame.font.SysFont("Arial", 90, bold=True)

# --- FUNÇÃO DE CARREGAMENTO DE ASSETS ---
def load_asset(name, size):
    try:
        img = pygame.image.load(name).convert_alpha()
        return pygame.transform.scale(img, size)
    except:
        surf = pygame.Surface(size)
        surf.fill((100, 100, 100)) 
        return surf

# Assets Visuais
img_player = load_asset("woman1.png", (100, 100))
img_bg = load_asset("cozinha1.png", (WIDTH, HEIGHT))
img_agressor = load_asset("agressor.png", (550, 750))

nomes_itens = ["talheres.png", "batedeira.png", "cafeteira.png", "torradeira.png","vassoura.png","chave.png"]
imagens_itens = [load_asset(nome, (60, 60)) for nome in nomes_itens]

# --- CONFIGURAÇÃO DO JOGO ---
SPAWN_ITEM = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_ITEM, 5000) 

RAIO_LUZ = 80 
light_mask = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

class Player:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH//2 - 30, HEIGHT//2 - 30, 60, 60)
        self.speed = 8
    def move(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.rect.x += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]: self.rect.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: self.rect.y += self.speed
        self.rect.clamp_ip(screen.get_rect())
    def draw(self):
        screen.blit(img_player, (self.rect.x - 20, self.rect.y - 20))

class Item:
    def __init__(self):
        self.image = random.choice(imagens_itens)
        self.rect = self.image.get_rect(center=(random.randint(60, WIDTH-60), random.randint(120, HEIGHT-60)))
    def draw(self):
        screen.blit(self.image, self.rect)

# Inicialização de Objetos
player = Player()
itens_na_tela = []
coletados = 0
total_para_vencer = 15
tempo_total = 60
start_ticks = pygame.time.get_ticks()
estado = "jogando"

# --- LOOP PRINCIPAL ---
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        
        if estado == "jogando" and event.type == SPAWN_ITEM:
            if len(itens_na_tela) + coletados < total_para_vencer:
                itens_na_tela.append(Item())

    if estado == "jogando":
        segundos_passados = (pygame.time.get_ticks() - start_ticks) / 1000
        tempo_restante = max(0, tempo_total - segundos_passados)
        
        player.move(pygame.key.get_pressed())
        if tempo_restante <= 10 and not passos_ativos:
            if som_passos: som_passos.play(loops=-1)
            passos_ativos = True

        for item in itens_na_tela[:]:
            if player.rect.colliderect(item.rect):
                itens_na_tela.remove(item)
                coletados += 1
                if som_coletar: som_coletar.play()

        screen.blit(img_bg, (0, 0))
        for item in itens_na_tela: item.draw()
        player.draw()

        progresso = 1 - (tempo_restante / tempo_total)
        intensidade = int(progresso * 254) 
        light_mask.fill((0, 0, 0, intensidade))
        pygame.draw.circle(light_mask, (0, 0, 0, 0), player.rect.center, RAIO_LUZ)
        screen.blit(light_mask, (0, 0))

        cor_timer = RED if tempo_restante < 10 else WHITE
        screen.blit(font.render(f"TEMPO: {int(tempo_restante)}s", True, BLACK), (22, 22)) 
        screen.blit(font.render(f"TEMPO: {int(tempo_restante)}s", True, cor_timer), (20, 20))
        screen.blit(font.render(f"ITENS: {coletados}/{total_para_vencer}", True, WHITE), (20, 65))

        if tempo_restante <= 0 or coletados >= total_para_vencer:
            pygame.mixer.music.stop()
            if som_passos: som_passos.stop()
            estado = "impacto"
            fim_timer = pygame.time.get_ticks()

    elif estado == "impacto":
        screen.fill(BLACK)
        
        pos_x = WIDTH // 2 - img_agressor.get_width() // 2
        pos_y = HEIGHT // 2 - img_agressor.get_height() // 2
        screen.blit(img_agressor, (pos_x, pos_y))
        
        # Texto "ELE CHEGOU" ACIMA da cabeça
        msg = big_font.render("ELE CHEGOU.", True, RED)
        sombra = big_font.render("ELE CHEGOU.", True, (40, 0, 0))
        
        txt_x = WIDTH // 2 - msg.get_width() // 2
        txt_y = pos_y - msg.get_height() - 20 
        
        screen.blit(sombra, (txt_x + 5, txt_y + 5))
        screen.blit(msg, (txt_x, txt_y))
        
        if pygame.time.get_ticks() - fim_timer > 4000:
            estado = "mensagem"

    elif estado == "mensagem":
        screen.fill(BLACK)
        linhas = [
            "A violência doméstica é uma corrida contra o tempo.",
            "NÃO SE CALE. DENUNCIE. LIGUE 180.",
            "",
            "Pressione ESC para sair."
        ]
        for i, linha in enumerate(linhas):
            cor = RED if "180" in linha else WHITE
            txt = font.render(linha, True, cor)
            screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//3 + i * 70))
        
        if pygame.key.get_pressed()[pygame.K_ESCAPE]:
            pygame.quit(); sys.exit()

    pygame.display.flip()
    clock.tick(60)