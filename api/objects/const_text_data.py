from dataclasses import dataclass

from api.utility import hash_text


@dataclass
class ConstTextData:
    id: int
    text: str

    def get_text_hashsum(self) -> str:
        return hash_text(self.text)

    @classmethod
    def null(cls):
        return cls(0, "")
