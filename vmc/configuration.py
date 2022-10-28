#!/usr/bin/env python3

from os.path import exists
from yaml import safe_load, safe_dump, YAMLError

class Configuration(dict):
    filename: str = ''

    def __setitem__(self, key, value) -> None:
        super().__setitem__(key, value)
        with open(self.filename, 'w') as file:
            safe_dump(dict(self), file)

    def __init__(self, filename: str, defaults: dict = {}) -> None:
        self.filename = filename
        if exists(self.filename):
            with open(self.filename, 'r') as file:
                try:
                    defaults.update(safe_load(file))
                except YAMLError as error:
                    raise ValueError("Invalid configuration file given.", error)
        super().__init__(defaults)
