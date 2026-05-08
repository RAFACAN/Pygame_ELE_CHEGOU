"""Entidades simples usadas durante a gameplay."""

import random

import pygame

from settings import display, sprites


class Player:
    """Representa a personagem controlada pelo jogador."""

    def __init__(self, screen_rect: pygame.Rect, image: pygame.Surface):
        self.screen_rect = screen_rect
        self.image = image
        self.rect = pygame.Rect(
            display.width // 2 - sprites.player_hitbox_size[0] // 2,
            display.height // 2 - sprites.player_hitbox_size[1] // 2,
            sprites.player_hitbox_size[0],
            sprites.player_hitbox_size[1],
        )
        self.speed = 8

    def move(self, keys, can_move=None) -> None:
        """Move a personagem respeitando os limites válidos do cenário.

        Args:
            keys: Estado atual das teclas fornecido pelo pygame.
            can_move: Callback opcional que valida a nova posição da hitbox.
        """
        move_x = 0
        move_y = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            move_x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            move_x += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            move_y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            move_y += self.speed

        previous_x = self.rect.x
        self.rect.x += move_x
        self.rect.clamp_ip(self.screen_rect)
        if can_move is not None and not can_move(self.rect):
            self.rect.x = previous_x

        previous_y = self.rect.y
        self.rect.y += move_y
        self.rect.clamp_ip(self.screen_rect)
        if can_move is not None and not can_move(self.rect):
            self.rect.y = previous_y

    def draw(self, screen: pygame.Surface) -> None:
        """Desenha o sprite alinhado à hitbox real da personagem."""
        screen.blit(
            self.image,
            (
                self.rect.x - sprites.player_draw_offset[0],
                self.rect.y - sprites.player_draw_offset[1],
            ),
        )


class Item:
    """Representa um item coletável posicionado no cenário."""

    def __init__(self, images: list[pygame.Surface], allowed_rects: list[pygame.Rect]):
        self.image = random.choice(images)
        spawn_rect = random.choice(allowed_rects)
        half_width = self.image.get_width() // 2
        half_height = self.image.get_height() // 2
        center_x = random.randint(spawn_rect.left + half_width, spawn_rect.right - half_width)
        center_y = random.randint(spawn_rect.top + half_height, spawn_rect.bottom - half_height)
        self.rect = self.image.get_rect(center=(center_x, center_y))

    def draw(self, screen: pygame.Surface) -> None:
        """Desenha o item na sua posição atual."""
        screen.blit(self.image, self.rect)
