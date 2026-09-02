from abc import ABC, abstractmethod


class TmpStorageRepositoryInterface(ABC):
    @abstractmethod
    def save_one(self, name: str, data):
        pass

    @abstractmethod
    def fetch_one(self, name: str):
        pass

    @abstractmethod
    def has(self, name: str) -> bool:
        pass

    @abstractmethod
    def remove_one(self, name: str):
        pass
