import click
import subprocess

@click.command('seed:all')
def seed_all():
    commands = [
        ['flask', 'seed:scales'],
        ['flask', 'seed:players'],
        ['flask', 'seed:games']
    ]

    for cmd in commands:
        result = subprocess.call(cmd)
        if result != 0:
            print(f"Command {' '.join(cmd)} failed with return code {result}")
            break  # Optional: stop execution if a command fails

    else:
        print('All seeded')
