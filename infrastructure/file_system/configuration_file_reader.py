import yaml


class ConfigurationFileReader:
    READ_MODE = 'r'

    def __init__(self, configuration_file_path: str):
        self.__configuration_file_path = configuration_file_path

    def read(self):
        with open(self.__configuration_file_path, self.READ_MODE) as stream:
            try:
                configuration: {} = yaml.safe_load(stream)
                return configuration
            except yaml.YAMLError as exc:
                print(exc)
