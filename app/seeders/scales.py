import click

from app.models.Scale import Scale

@click.command('seed:scales')
def seed_scales():
    scales = [
        {'low': 'cold', 'high': 'hot'},
        {'low': 'small', 'high': 'big'},
        {'low': 'short', 'high': 'tall'},
        {'low': 'light', 'high': 'heavy'},
        {'low': 'soft', 'high': 'hard'},
        {'low': 'weak', 'high': 'strong'},
        {'low': 'slow', 'high': 'fast'},
        {'low': 'dull', 'high': 'sharp'},
        {'low': 'shallow', 'high': 'deep'},
        {'low': 'narrow', 'high': 'wide'},
        {'low': 'low', 'high': 'high'},
        {'low': 'poor', 'high': 'rich'},
        {'low': 'empty', 'high': 'full'},
        {'low': 'quiet', 'high': 'loud'},
        {'low': 'dark', 'high': 'bright'},
        {'low': 'smooth', 'high': 'rough'},
        {'low': 'clean', 'high': 'dirty'},
        {'low': 'simple', 'high': 'complex'},
        {'low': 'soft', 'high': 'hard'},
        {'low': 'sweet', 'high': 'sour'},
    ]

    for scale in scales:
        scale_exists = Scale.query.filter_by(low=scale['low'], high=scale['high'], created_by_id=None).first()
        if not scale_exists:
            new_scale = Scale(low=scale['low'], high=scale['high'])
            new_scale.save()

    print('Scales seeded')
