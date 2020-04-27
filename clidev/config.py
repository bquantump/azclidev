import os
import configparser
import clidev as cli


class Config:

    def __init__(self, config_path):
        with open(config_path, "r") as file:
            config_parser = configparser.RawConfigParser()
            config_parser.read_string(file.read())
            self.content = config_parser._sections
            self.config_path = config_path

    def __contains__(self, item):
        return item in self.content

    def __setitem__(self, key, value):
        self.content[key] = value
        
    def __getitem__(self, key):
        return self.content[key]

    def write(self):
        with open(self.config_path, "w") as file:
            config_parser = configparser.RawConfigParser()
            config_parser.read_dict(self.content)
            config_parser.write(file)
