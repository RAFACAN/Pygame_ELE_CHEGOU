"""Loop principal e cenas do jogo Silêncio Doméstico."""

from collections import deque
from pathlib import Path

import pygame

from entities import Item, Player
from settings import assets, colors, display, gameplay, paths, scene, sprites


def load_audio() -> tuple[pygame.mixer.Sound | None, pygame.mixer.Sound | None]:
    """Carrega música e efeitos sonoros usados durante a partida."""
    try:
        pygame.mixer.music.load(paths.audio_dir / assets.music_file)
        pygame.mixer.music.set_volume(0.4)
        pygame.mixer.music.play(-1)

        step_sound = pygame.mixer.Sound(paths.audio_dir / assets.steps_sound)
        collect_sound = pygame.mixer.Sound(paths.audio_dir / assets.collect_sound)
        collect_sound.set_volume(0.3)
        return step_sound, collect_sound
    except (pygame.error, FileNotFoundError):
        print("Aviso: arquivos de áudio não encontrados.")
        return None, None


def load_asset(path_or_name: str | Path, size: tuple[int, int]) -> pygame.Surface:
    """Carrega uma imagem e a redimensiona para o tamanho solicitado."""
    try:
        asset_path = (
            path_or_name if isinstance(path_or_name, Path) else paths.images_dir / path_or_name
        )
        image = pygame.image.load(asset_path).convert_alpha()
        return pygame.transform.scale(image, size)
    except (pygame.error, FileNotFoundError):
        fallback = pygame.Surface(size, pygame.SRCALPHA)
        fallback.fill(colors.fallback_surface)
        return fallback


def load_sheet_frames(
    path_or_name: str,
    frame_size: tuple[int, int],
    output_size: tuple[int, int],
) -> list[pygame.Surface]:
    """Recorta todos os frames horizontais de uma sprite sheet."""
    try:
        sheet = pygame.image.load(paths.images_dir / path_or_name).convert_alpha()
    except (pygame.error, FileNotFoundError):
        return [load_asset(path_or_name, output_size)]

    frame_width, frame_height = frame_size
    total_frames = max(1, sheet.get_width() // frame_width)
    frames: list[pygame.Surface] = []

    for index in range(total_frames):
        frame = sheet.subsurface((index * frame_width, 0, frame_width, frame_height)).copy()
        frames.append(pygame.transform.scale(frame, output_size))

    return frames


def color_distance(color_a: tuple[int, int, int], color_b: tuple[int, int, int]) -> int:
    """Calcula uma distância simples entre duas cores RGB."""
    return sum(abs(color_a[index] - color_b[index]) for index in range(3))


def scale_rect(rect: tuple[int, int, int, int]) -> pygame.Rect:
    """Converte um retângulo da escala da arte original para a janela atual."""
    source_x, source_y, source_width, source_height = rect
    scale_x = display.width / scene.source_size[0]
    scale_y = display.height / scene.source_size[1]
    return pygame.Rect(
        int(source_x * scale_x),
        int(source_y * scale_y),
        int(source_width * scale_x),
        int(source_height * scale_y),
    )


def build_walkable_rects() -> list[pygame.Rect]:
    """Cria retângulos-base usados para spawn de itens."""
    return [scale_rect(rect) for rect in scene.walkable_rects_source]


def scale_point(point: tuple[int, int]) -> tuple[int, int]:
    """Converte um ponto da escala original da arte para a resolução atual."""
    source_x, source_y = point
    scale_x = display.width / scene.source_size[0]
    scale_y = display.height / scene.source_size[1]
    return int(source_x * scale_x), int(source_y * scale_y)


def build_walkable_mask(background: pygame.Surface) -> pygame.Mask:
    """Gera uma máscara contínua de piso caminhável usando flood fill por cor.

    A máscara nasce a partir de pontos-semente posicionados em áreas válidas
    do piso. A partir desses pontos, o algoritmo expande para pixels com cor
    próxima, respeitando a tolerância definida em `Scene`.
    """
    width, height = background.get_size()
    mask = pygame.Mask((width, height), fill=False)
    tolerance = scene.walkable_color_tolerance

    for seed_point in scene.walkable_seed_points_source:
        seed_x, seed_y = scale_point(seed_point)
        if not (0 <= seed_x < width and 0 <= seed_y < height):
            continue

        seed_color = background.get_at((seed_x, seed_y))[:3]
        queue = deque([(seed_x, seed_y)])
        visited: set[tuple[int, int]] = set()

        while queue:
            x, y = queue.popleft()
            if (x, y) in visited:
                continue
            visited.add((x, y))

            if mask.get_at((x, y)):
                continue

            pixel_color = background.get_at((x, y))[:3]
            if color_distance(pixel_color, seed_color) > tolerance:
                continue

            mask.set_at((x, y), 1)

            if x > 0:
                queue.append((x - 1, y))
            if x < width - 1:
                queue.append((x + 1, y))
            if y > 0:
                queue.append((x, y - 1))
            if y < height - 1:
                queue.append((x, y + 1))

    return mask


def build_walkable_overlay(mask: pygame.Mask) -> pygame.Surface:
    """Cria o overlay de debug exibido ao pressionar `F1`."""
    overlay = pygame.Surface((display.width, display.height), pygame.SRCALPHA)
    mask_surface = mask.to_surface(
        setcolor=(80, 255, 120, 45),
        unsetcolor=(0, 0, 0, 0),
    )
    overlay.blit(mask_surface, (0, 0))
    return overlay


def find_player_start() -> tuple[int, int]:
    """Retorna o ponto inicial da personagem já escalado para a resolução atual."""
    return scale_point(scene.player_start_source)


def rect_is_walkable(rect: pygame.Rect, walkable_mask: pygame.Mask) -> bool:
    """Valida a hitbox da personagem contra a máscara de piso navegável."""
    points = (
        (rect.left + 1, rect.top + 1),
        (rect.right - 1, rect.top + 1),
        (rect.left + 1, rect.bottom - 1),
        (rect.right - 1, rect.bottom - 1),
    )
    return all(walkable_mask.get_at(point) for point in points)


def spawn_reachable_item(
    images: list[pygame.Surface],
    walkable_rects: list[pygame.Rect],
    walkable_mask: pygame.Mask,
    attempts: int = 40,
) -> Item | None:
    """Tenta posicionar um item apenas em locais alcançáveis pela personagem.

    Os retângulos de spawn servem como regiões candidatas. A validação final
    continua sendo feita contra a máscara de navegação para evitar itens
    presos em cantos inacessíveis.
    """
    for _ in range(attempts):
        item = Item(images, walkable_rects)
        if rect_is_walkable(item.rect, walkable_mask):
            return item
    return None


def draw_centered_lines(
    screen: pygame.Surface,
    font: pygame.font.Font,
    lines: list[str],
    start_y: int,
) -> None:
    """Desenha linhas centralizadas para as telas de mensagem."""
    for index, line in enumerate(lines):
        color = colors.red if "180" in line or "190" in line else colors.white
        text = font.render(line, True, color)
        x = display.width // 2 - text.get_width() // 2
        y = start_y + index * 70
        screen.blit(text, (x, y))


def draw_debug_overlay(
    screen: pygame.Surface,
    walkable_overlay: pygame.Surface,
    player: Player,
) -> None:
    """Mostra a máscara caminhável e a hitbox da personagem."""
    screen.blit(walkable_overlay, (0, 0))
    pygame.draw.rect(screen, (255, 80, 80), player.rect, width=3)
    pygame.draw.circle(screen, (255, 80, 80), player.rect.center, 4)


def main() -> None:
    """Inicializa o pygame, executa a gameplay e controla as cenas finais.

    O fluxo principal alterna entre quatro estados:

    - `jogando`: coleta de itens com tempo limitado;
    - `impacto`: aparição do agressor quando o tempo acaba;
    - `resgate`: chegada da polícia e troca para o agressor abatido;
    - `mensagem`: tela final com a mensagem social do projeto.
    """
    pygame.init()
    pygame.mixer.init()

    screen = pygame.display.set_mode((display.width, display.height))
    pygame.display.set_caption(display.title)
    clock = pygame.time.Clock()

    font = pygame.font.SysFont("Arial", 26, bold=True)
    big_font = pygame.font.SysFont("Arial", 72, bold=True)

    player_image = load_asset(assets.player_image, sprites.player_size)
    house_background = load_asset(assets.house_background, (display.width, display.height))
    aggressor_image = load_asset(assets.aggressor_image, sprites.aggressor_scene_size)
    aggressor_down_image = load_asset(assets.aggressor_down_image, sprites.aggressor_down_size)
    police_idle_frames = load_sheet_frames(
        assets.police_idle_sheet,
        sprites.police_officer_frame_size,
        sprites.police_officer_size,
    )
    police_walk_frames = load_sheet_frames(
        assets.police_walk_sheet,
        sprites.police_officer_frame_size,
        sprites.police_officer_size,
    )
    item_images = [load_asset(name, sprites.item_size) for name in assets.item_names]

    step_sound, collect_sound = load_audio()
    footsteps_enabled = False

    spawn_item_event = pygame.USEREVENT + 1
    pygame.time.set_timer(spawn_item_event, gameplay.spawn_interval_ms)
    light_mask = pygame.Surface((display.width, display.height), pygame.SRCALPHA)
    walkable_rects = build_walkable_rects()
    walkable_mask = build_walkable_mask(house_background)
    walkable_overlay = None

    player = Player(screen.get_rect(), player_image)
    player.rect.center = find_player_start()
    items_on_screen: list[Item] = []
    collected_items = 0
    start_ticks = pygame.time.get_ticks()
    state_started_at = start_ticks
    state = "jogando"
    ending = "fracasso"
    debug_walkable = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            if event.type == pygame.KEYDOWN and event.key == pygame.K_F1:
                debug_walkable = not debug_walkable
                if debug_walkable and walkable_overlay is None:
                    walkable_overlay = build_walkable_overlay(walkable_mask)

            if event.type == spawn_item_event and state == "jogando":
                if len(items_on_screen) + collected_items < gameplay.total_items:
                    item = spawn_reachable_item(item_images, walkable_rects, walkable_mask)
                    if item is not None:
                        items_on_screen.append(item)

        if state == "jogando":
            elapsed_seconds = (pygame.time.get_ticks() - start_ticks) / 1000
            remaining_time = max(0, gameplay.total_time - elapsed_seconds)

            player.move(
                pygame.key.get_pressed(),
                can_move=lambda rect: rect_is_walkable(rect, walkable_mask),
            )

            if remaining_time <= 10 and not footsteps_enabled:
                if step_sound:
                    step_sound.play(loops=-1)
                footsteps_enabled = True

            for item in items_on_screen[:]:
                if player.rect.colliderect(item.rect):
                    items_on_screen.remove(item)
                    collected_items += 1
                    if collect_sound:
                        collect_sound.play()

            screen.blit(house_background, (0, 0))
            for item in items_on_screen:
                item.draw(screen)
            player.draw(screen)
            if debug_walkable and walkable_overlay is not None:
                draw_debug_overlay(screen, walkable_overlay, player)

            progress = 1 - (remaining_time / gameplay.total_time)
            intensity = int(progress * 254)
            light_mask.fill((0, 0, 0, intensity))
            pygame.draw.circle(light_mask, (0, 0, 0, 0), player.rect.center, gameplay.light_radius)
            screen.blit(light_mask, (0, 0))

            timer_color = colors.red if remaining_time < 10 else colors.white
            timer_shadow = font.render(f"TEMPO: {int(remaining_time)}s", True, colors.black)
            timer_text = font.render(f"TEMPO: {int(remaining_time)}s", True, timer_color)
            items_text = font.render(
                f"ITENS: {collected_items}/{gameplay.total_items}",
                True,
                colors.white,
            )
            objective_text = font.render(
                "Recolha tudo antes que ele chegue.",
                True,
                colors.white,
            )
            screen.blit(timer_shadow, (18, 18))
            screen.blit(timer_text, (16, 16))
            screen.blit(items_text, (16, 54))
            screen.blit(objective_text, (16, 92))
            if debug_walkable:
                debug_text = font.render("DEBUG F1: verde = pode andar", True, colors.red)
                screen.blit(debug_text, (16, 130))

            if collected_items >= gameplay.total_items:
                pygame.mixer.music.stop()
                if step_sound:
                    step_sound.stop()
                state = "resgate"
                ending = "resgate"
                state_started_at = pygame.time.get_ticks()
            elif remaining_time <= 0:
                pygame.mixer.music.stop()
                if step_sound:
                    step_sound.stop()
                state = "impacto"
                ending = "fracasso"
                state_started_at = pygame.time.get_ticks()

        elif state == "impacto":
            screen.fill(colors.black)

            pos_x = display.width // 2 - aggressor_image.get_width() // 2
            pos_y = display.height // 2 - aggressor_image.get_height() // 2 + 40
            screen.blit(aggressor_image, (pos_x, pos_y))

            message = big_font.render("ELE CHEGOU.", True, colors.red)
            shadow = big_font.render("ELE CHEGOU.", True, colors.red_shadow)
            text_x = display.width // 2 - message.get_width() // 2
            text_y = pos_y - message.get_height() - 18
            screen.blit(shadow, (text_x + 5, text_y + 5))
            screen.blit(message, (text_x, text_y))

            if pygame.time.get_ticks() - state_started_at > scene.duration_ms:
                state = "mensagem"

        elif state == "resgate":
            screen.blit(house_background, (0, 0))

            elapsed = pygame.time.get_ticks() - state_started_at
            entry_progress = min(1.0, elapsed / scene.police_entry_ms)
            show_downed = elapsed >= scene.police_entry_ms + scene.downed_swap_delay_ms

            walk_frame = police_walk_frames[(elapsed // 120) % len(police_walk_frames)]
            idle_frame = police_idle_frames[0]

            if show_downed:
                downed_x = display.width // 2 - aggressor_down_image.get_width() // 2 + 70
                downed_y = display.height // 2 - aggressor_down_image.get_height() // 2 + 165
                screen.blit(aggressor_down_image, (downed_x, downed_y))
                aggressor_rect = pygame.Rect(
                    downed_x,
                    downed_y,
                    aggressor_down_image.get_width(),
                    aggressor_down_image.get_height(),
                )
            else:
                aggressor_x = display.width // 2 - aggressor_image.get_width() // 2 + 82
                aggressor_y = display.height // 2 - aggressor_image.get_height() // 2 + 145
                screen.blit(aggressor_image, (aggressor_x, aggressor_y))
                aggressor_rect = pygame.Rect(
                    aggressor_x,
                    aggressor_y,
                    aggressor_image.get_width(),
                    aggressor_image.get_height(),
                )

            left_target_x = aggressor_rect.left - idle_frame.get_width() + 72
            left_start_x = -idle_frame.get_width()
            left_x = int(left_start_x + entry_progress * (left_target_x - left_start_x))
            left_y = aggressor_rect.centery + 36
            left_rect = pygame.Rect(left_x, left_y, idle_frame.get_width(), idle_frame.get_height())

            right_target_x = aggressor_rect.right - 70
            right_start_x = display.width + idle_frame.get_width()
            right_x = int(right_start_x + entry_progress * (right_target_x - right_start_x))
            right_y = aggressor_rect.centery + 36

            left_sprite = idle_frame if elapsed >= scene.police_entry_ms else walk_frame
            right_sprite = pygame.transform.flip(
                idle_frame if elapsed >= scene.police_entry_ms else walk_frame,
                True,
                False,
            )
            screen.blit(left_sprite, left_rect.topleft)
            screen.blit(right_sprite, (right_x, right_y))

            message = big_font.render("POLICIA NO LOCAL.", True, colors.police_blue)
            shadow = big_font.render("POLICIA NO LOCAL.", True, colors.red_shadow)
            text_x = display.width // 2 - message.get_width() // 2
            text_y = 60
            screen.blit(shadow, (text_x + 5, text_y + 5))
            screen.blit(message, (text_x, text_y))

            subtitle = font.render(
                "A policia chegou, conteve e prendeu o agressor.",
                True,
                colors.white,
            )
            subtitle_x = display.width // 2 - subtitle.get_width() // 2
            screen.blit(subtitle, (subtitle_x, text_y + 92))

            if elapsed > scene.duration_ms:
                state = "mensagem"

        elif state == "mensagem":
            screen.fill(colors.black)
            if ending == "resgate":
                lines = [
                    "Voce conseguiu reunir o necessario a tempo.",
                    "A policia chegou e prendeu o agressor. Em emergencia, ligue 190.",
                    "Para denuncia e orientacao, ligue 180.",
                    "",
                    "Pressione ESC para sair.",
                ]
            else:
                lines = [
                    "A violencia domestica e uma corrida contra o tempo.",
                    "Em emergencia, ligue 190.",
                    "Para denuncia e orientacao, ligue 180.",
                    "",
                    "Pressione ESC para sair.",
                ]
            draw_centered_lines(screen, font, lines, display.height // 3)

            if pygame.key.get_pressed()[pygame.K_ESCAPE]:
                pygame.quit()
                raise SystemExit

        pygame.display.flip()
        clock.tick(display.fps)
