import click

from app.models.Player import Player
from werkzeug.security import generate_password_hash

@click.command('seed:players')
def seed_players():
    players = [
        {'name': 'Hayden', 'email': 'hayden@email.com', 'password': 'password'},
        {'name': 'Jordan', 'email': 'Jordan@email.com', 'password': 'password'},
        {'name': 'Koba', 'email': 'koba@email.com', 'password': 'password'},
        {'name': 'Chase', 'email': 'chase@email.com', 'password': 'password'},
        {'name': 'Mia', 'email': 'mia@email.com', 'password': 'password'},
        {'name': 'Christine', 'email': 'christine@email.com', 'password': 'password'},
        {'name': 'Igor', 'email': 'igor@email.com', 'password': 'password'},
        {'name': 'Sam', 'email': 'sam@email.com', 'password': 'password'},
        {'name': 'Casey', 'email': 'casey@email.com', 'password': 'password'},
        {'name': 'Tom', 'email': 'tom@email.com', 'password': 'password'},
        {'name': 'Michael', 'email': 'michael@email.com', 'password': 'password'},
        {'name': 'Angus', 'email': 'angus@email.com', 'password': 'password'},
    ]

    for player in players:
        player_exists = Player.query.filter_by(email=player['email']).first()
        if not player_exists:
            new_player = Player(name=player['name'], email=player['email'], password=generate_password_hash(player['password']))
            new_player.save()

    print('Players seeded')
