"""Configurações centrais do projeto Silêncio Doméstico."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Paths:
    """Expõe os diretórios base usados pelo jogo."""

    root_dir: Path = Path(__file__).resolve().parents[1]

    @property
    def assets_dir(self) -> Path:
        """Retorna a pasta raiz de assets."""
        return self.root_dir / "assets"

    @property
    def audio_dir(self) -> Path:
        """Retorna a pasta de áudio."""
        return self.assets_dir / "audio"

    @property
    def images_dir(self) -> Path:
        """Retorna a pasta de imagens em uso pelo jogo."""
        return self.assets_dir / "images"


@dataclass(frozen=True)
class Display:
    """Agrupa configurações da janela principal."""

    width: int = 1080
    height: int = 1080
    title: str = "Silêncio Doméstico"
    fps: int = 60


@dataclass(frozen=True)
class Gameplay:
    """Agrupa valores principais de jogabilidade."""

    total_items: int = 10
    total_time: int = 60
    spawn_interval_ms: int = 3000
    light_radius: int = 80


@dataclass(frozen=True)
class Colors:
    """Cores usadas na interface e nas cenas."""

    white: tuple[int, int, int] = (255, 255, 255)
    red: tuple[int, int, int] = (180, 0, 0)
    black: tuple[int, int, int] = (0, 0, 0)
    red_shadow: tuple[int, int, int] = (40, 0, 0)
    police_blue: tuple[int, int, int] = (40, 110, 220)
    fallback_surface: tuple[int, int, int] = (100, 100, 100)


@dataclass(frozen=True)
class Sprites:
    """Define tamanhos e offsets dos sprites usados em tela."""

    player_size: tuple[int, int] = (88, 88)
    player_hitbox_size: tuple[int, int] = (24, 24)
    player_draw_offset: tuple[int, int] = (32, 32)
    item_size: tuple[int, int] = (54, 54)
    aggressor_scene_size: tuple[int, int] = (210, 285)
    aggressor_down_size: tuple[int, int] = (210, 210)
    police_officer_size: tuple[int, int] = (170, 170)
    police_officer_frame_size: tuple[int, int] = (32, 32)


@dataclass(frozen=True)
class Scene:
    """Agrupa tempos e coordenadas da cena final e da navegação."""

    duration_ms: int = 6500
    police_entry_ms: int = 2600
    downed_swap_delay_ms: int = 900
    source_size: tuple[int, int] = (761, 768)
    player_start_source: tuple[int, int] = (184, 304)
    walkable_seed_points_source: tuple[tuple[int, int], ...] = (
        (220, 240),
        (205, 370),
        (332, 505),
        (142, 500),
        (193, 543),
        (274, 500),
        (334, 543),
        (205, 675),
        (398, 545),
        (522, 158),
        (575, 305),
        (575, 635),
        (565, 85),
        (575, 78),
    )
    walkable_color_tolerance: int = 54
    # Cada retângulo usa o formato (x, y, largura, altura)
    # na escala original da arte definida em `source_size`.
    walkable_rects_source: tuple[tuple[int, int, int, int], ...] = (
        (126, 151, 328, 178),
        (121, 324, 402, 84),
        (123, 454, 251, 112),
        (111, 606, 214, 166),
        (314, 607, 108, 66),
        (399, 515, 67, 157),
        (344, 512, 72, 58),
        (442, 118, 109, 125),
        (500, 29, 146, 90),
        (516, 214, 151, 176),
        (501, 382, 167, 171),
        (500, 547, 170, 170),
        (478, 219, 60, 74),
        (456, 258, 76, 82),
        (453, 344, 61, 74),
        (451, 490, 62, 65),
    )


@dataclass(frozen=True)
class Assets:
    """Define os nomes dos assets carregados em runtime."""

    player_image: str = "mulher.png"
    house_background: str = "fundo_casa.png"
    aggressor_image: str = "agressor.png"
    aggressor_down_image: str = "agressor_abatido.png"
    police_idle_sheet: str = "policial_parado.png"
    police_walk_sheet: str = "policial_andando.png"
    item_names: tuple[str, ...] = (
        "talheres.png",
        "batedeira.png",
        "cafeteira.png",
        "torradeira.png",
        "vassoura.png",
        "chave.png",
    )
    music_file: str = "musica_fundo.mp3"
    steps_sound: str = "passos.wav"
    collect_sound: str = "coletar.wav"


paths = Paths()
display = Display()
gameplay = Gameplay()
colors = Colors()
sprites = Sprites()
scene = Scene()
assets = Assets()
