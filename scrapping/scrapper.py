import abc


class Scrapper(abc.ABC):
    def run(self):
        raise NotImplementedError("Method run not implemented on new scrapper")
