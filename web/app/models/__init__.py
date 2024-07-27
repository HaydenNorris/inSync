import importlib
import pkgutil
import os

def import_all_models():
    # Directory containing the model files
    package_dir = os.path.dirname(__file__)

    # Iterate through all files in the directory
    for _, module_name, _ in pkgutil.iter_modules([package_dir]):
        if module_name == '__init__':
            continue
        importlib.import_module(f'app.models.{module_name}')
