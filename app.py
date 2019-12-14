from infrastructure.file_system.configuration_file_reader import \
    ConfigurationFileReader
from concurrent.futures.thread import ThreadPoolExecutor
from importlib import import_module
import os


class App:
    CONFIGURATION_FILE_DIR: str = "configuration"
    CONFIGURATION_FILE_NAME: str = "app.conf.yml"
    CONFIGURATION_FILE_PATH: str = os.path.join(CONFIGURATION_FILE_DIR,
                                                CONFIGURATION_FILE_NAME)
    SCRAPPING_MODULE_PATH: str = "scrapping"
    CLASS_NAME: str

    @staticmethod
    def start():
        cfr: ConfigurationFileReader = ConfigurationFileReader(
            App.CONFIGURATION_FILE_PATH
        )

        app_configuration: {} = cfr.read()
        database_config: {} = app_configuration.get('database')

        robots_config: {} = app_configuration.get('robots')
        scheduling: [] = robots_config.get('scheduling')

        with ThreadPoolExecutor(max_workers=len(scheduling)) as executor:
            for task_k, task_v in scheduling.items():
                if True is task_v.get("enabled"):
                    scrapper_name: str = task_v.get('scrapper_name')

                    module_name: str = "{}.{}".format(
                        App.SCRAPPING_MODULE_PATH,
                        scrapper_name
                    )

                    module = import_module(module_name)

                    class_name = ""
                    for token in scrapper_name.split('_'):
                        class_name += token.capitalize()

                    _class = getattr(module, class_name)

                    scrapper_config: {} = {
                        'database_config': database_config,
                        'feed_endpoint': task_v.get('feed_endpoint')
                    }

                    scrapper_instance = _class(scrapper_config)
                    executor.submit(scrapper_instance.run)


if __name__ == "__main__":
    app: App = App()
    app.start()
