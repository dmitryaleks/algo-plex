from abc import ABCMeta, abstractmethod

class Audit(metaclass=ABCMeta):

    @abstractmethod
    def log(self, msg):
        pass
