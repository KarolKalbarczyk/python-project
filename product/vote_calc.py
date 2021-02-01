from abc import ABC, abstractmethod



class VoteCalc(ABC):

    def __init__(self, calc = None):
        self.__wrapped = calc

    @abstractmethod
    def _get_multiplier(self, user):
        return 1

    def calculate(self, user):
        if self.__wrapped is None:
            return  self._get_multiplier(user)

        return self._get_multiplier(user) * self.__wrapped._get_multiplier(user)
