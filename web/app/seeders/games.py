import random

import click

from app.models.Game import Game
from app.models.Player import Player

@click.command('seed:games')
def seed_games():
    players = Player.query.limit(20).all()
    for game in range(10):
        host = random.choice(players)
        game = Game.create(host, host.name)
        players_in_game = [host.id]
        for _ in range(2):
            player = random.choice(players)
            while player.id in players_in_game:
                player = random.choice(players)
            game.add_player(player, player.name)
            players_in_game.append(player.id)

    print('Games seeded')
