import pygame
import sys
import math
import random
import os


# --- FUNÇÃO ESSENCIAL PARA O CAMINHO DO .EXE ---
def obter_caminho(caminho_relativo):
    if getattr(sys, 'frozen', False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, caminho_relativo)


# 1. Inicialização
pygame.init()
pygame.mixer.init()

# 2. Configurações de Tela
LARGURA, ALTURA = 800, 600
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Sobrevivência Zumbi - Uninter Final")

# 3. Cores
PRETO, BRANCO, VERDE, AMARELO, VERMELHO = (0, 0, 0), (255, 255, 255), (0, 255, 0), (255, 255, 0), (255, 0, 0)


# 4. Carregamento de Assets (Anti-Quadrado Branco/Preto)
def carregar_asset_limpo(caminho, cor_reserva):
    try:
        img_path = obter_caminho(caminho)
        temp_img = pygame.image.load(img_path).convert()
        # Remove a cor do fundo baseando-se no primeiro pixel
        cor_fundo = temp_img.get_at((0, 0))
        temp_img.set_colorkey(cor_fundo)
        return pygame.transform.scale(temp_img.convert_alpha(), (50, 50))
    except:
        res = pygame.Surface((50, 50), pygame.SRCALPHA)
        res.fill(cor_reserva)
        return res


IMG_PLAYER = carregar_asset_limpo("asset/jogador.png", VERDE)
IMG_ZUMBI = carregar_asset_limpo("asset/zumbi.png", VERMELHO)

try:
    IMG_CHAO = pygame.image.load(obter_caminho("asset/chao.jpg")).convert()
    IMG_CHAO = pygame.transform.scale(IMG_CHAO, (LARGURA, ALTURA))
except:
    IMG_CHAO = None

# --- SISTEMA DE ÁUDIO ---
som_tiro = som_morte = som_zumbi = None
volume_atual = 0.3
mutado = False

try:
    som_tiro = pygame.mixer.Sound(obter_caminho("asset/tiro.wav"))
    som_morte = pygame.mixer.Sound(obter_caminho("asset/morte.wav"))
    som_zumbi = pygame.mixer.Sound(obter_caminho("asset/zumbi.wav"))
    musica_path = obter_caminho("asset/som_fundo.mp3")
    if os.path.exists(musica_path):
        pygame.mixer.music.load(musica_path)
except:
    pass


def atualizar_volumes():
    vol = 0 if mutado else volume_atual
    try:
        pygame.mixer.music.set_volume(vol)
        if som_tiro: som_tiro.set_volume(vol)
        if som_morte: som_morte.set_volume(vol)
        if som_zumbi: som_zumbi.set_volume(vol)
    except:
        pass


# --- MENU INICIAL DETALHADO ---
def menu():
    while True:
        tela.fill(PRETO)
        f_tit = pygame.font.SysFont('Arial', 45, True).render("SOBREVIVÊNCIA ZUMBI", True, VERDE)
        f_op = pygame.font.SysFont('Arial', 25).render("1 - MODO FÁCIL  |  2 - MODO DIFÍCIL", True, BRANCO)

        controles = [
            "CONTROLES:",
            "W, A, S, D - Movimentar",
            "ESPAÇO - Atirar",
            "P - Pausar Jogo | M - Mudo",
            "+ e -  - Ajustar Volume"
        ]

        tela.blit(f_tit, (LARGURA // 2 - f_tit.get_width() // 2, 80))
        tela.blit(f_op, (LARGURA // 2 - f_op.get_width() // 2, 180))

        y = 300
        for linha in controles:
            cor = AMARELO if "CONTROLES" in linha else BRANCO
            txt = pygame.font.SysFont('Arial', 20, "CONTROLES" in linha).render(linha, True, cor)
            tela.blit(txt, (LARGURA // 2 - txt.get_width() // 2, y))
            y += 35

        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_1: return "facil"
                if e.key == pygame.K_2: return "dificil"


relogio = pygame.time.Clock()

# --- LOOP PRINCIPAL ---
while True:
    dif = menu()
    px, py = 400, 300
    balas, zumbis = [], [[100, 100, 2.0]]
    pontos, jogando, pausado, angulo_p = 0, True, False, 0
    timer_spawn, freq_spawn = 0, 90

    try:
        pygame.mixer.music.play(-1)
    except:
        pass
    atualizar_volumes()

    while jogando:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_p: pausado = not pausado
                if ev.key == pygame.K_m:
                    mutado = not mutado
                    atualizar_volumes()
                if ev.key == pygame.K_KP_PLUS or ev.key == pygame.K_EQUALS:
                    volume_atual = min(1.0, volume_atual + 0.1);
                    atualizar_volumes()
                if ev.key == pygame.K_KP_MINUS or ev.key == pygame.K_MINUS:
                    volume_atual = max(0.0, volume_atual - 0.1);
                    atualizar_volumes()
                if ev.key == pygame.K_SPACE and not pausado:
                    if som_tiro: som_tiro.play()
                    rad = math.radians(angulo_p)
                    balas.append([pygame.Rect(px - 4, py - 4, 8, 8), math.cos(rad) * 10, -math.sin(rad) * 10])

        if not pausado:
            # Lógica de Horda (Modo Difícil)
            if dif == "dificil":
                timer_spawn += 1
                if timer_spawn > freq_spawn:
                    sx, sy = random.choice([(0, random.randint(0, 600)), (800, random.randint(0, 600))])
                    zumbis.append([sx, sy, 2.0 + (pontos * 0.05)])
                    timer_spawn = 0
                    freq_spawn = max(30, 90 - (pontos // 2))

            teclas = pygame.key.get_pressed()
            dx, dy = 0, 0
            if teclas[pygame.K_a]: dx -= 5; angulo_p = 180
            if teclas[pygame.K_d]: dx += 5; angulo_p = 0
            if teclas[pygame.K_w]: dy -= 5; angulo_p = 90
            if teclas[pygame.K_s]: dy += 5; angulo_p = 270
            px += dx;
            py += dy
            px = max(25, min(LARGURA - 25, px));
            py = max(25, min(ALTURA - 25, py))

            for b in balas[:]:
                b[0].x += b[1];
                b[0].y += b[2]
                if not tela.get_rect().colliderect(b[0]): balas.remove(b)

            for z in zumbis[:]:
                dist_x, dist_y = px - z[0], py - z[1]
                dist = math.hypot(dist_x, dist_y)
                if dist > 0:
                    z[0] += (dist_x / dist) * z[2];
                    z[1] += (dist_y / dist) * z[2]

                rz = pygame.Rect(z[0] - 20, z[1] - 20, 40, 40)
                for b in balas[:]:
                    if rz.colliderect(b[0]):
                        pontos += 1
                        if som_zumbi: som_zumbi.play()
                        if z in zumbis: zumbis.remove(z)
                        if b in balas: balas.remove(b)
                        if dif == "facil": zumbis.append([random.choice([0, 800]), random.choice([0, 600]), 2.0])
                        break
                if rz.colliderect(pygame.Rect(px - 20, py - 20, 40, 40)):
                    if som_morte: som_morte.play()
                    jogando = False

        # --- DESENHO ---
        if IMG_CHAO:
            tela.blit(IMG_CHAO, (0, 0))
        else:
            tela.fill((40, 40, 40))

        for b in balas: pygame.draw.circle(tela, AMARELO, b[0].center, 5)

        p_rot = pygame.transform.rotate(IMG_PLAYER, angulo_p)
        tela.blit(p_rot, p_rot.get_rect(center=(px, py)))

        for z in zumbis:
            ang_z = math.degrees(math.atan2(-(py - z[1]), px - z[0]))
            z_rot = pygame.transform.rotate(IMG_ZUMBI, ang_z + 90)
            tela.blit(z_rot, z_rot.get_rect(center=(z[0], z[1])))

        # HUD COMPLETO
        f = pygame.font.SysFont('Arial', 18, True)
        tela.blit(f.render(f"PONTOS: {pontos}", True, BRANCO), (20, 20))
        vol_info = f"VOLUME: {int(volume_atual * 100)}% {'(MUDO)' if mutado else ''}"
        tela.blit(f.render(vol_info, True, AMARELO), (20, 45))
        if pausado:
            txt_p = pygame.font.SysFont('Arial', 50, True).render("PAUSADO", True, BRANCO)
            tela.blit(txt_p, (LARGURA // 2 - txt_p.get_width() // 2, ALTURA // 2 - 25))

        pygame.display.flip()
        relogio.tick(60)