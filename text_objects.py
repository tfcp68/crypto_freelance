from dataclasses import dataclass
import datetime


@dataclass
class TextData:
    id: int
    hash: str
    timestamp: datetime.datetime

    @classmethod
    def from_tuple(cls, src):
        return TextData(
            src[0],
            bytes(src[1]).hex(),
            datetime.datetime.fromtimestamp(src[2])
        )

    def to_raw_tuple(self):
        return (
            self.id,
            self.hash,
            int(self.timestamp.timestamp())
        )

    def to_dict(self, hash_to_int: bool = True):
        return {
            "id": str(self.id),
            "hash": self.hash if not hash_to_int else self.__hash_int(),
            "timestamp": int(self.timestamp.timestamp())
        }

    def __hash_int(self):
        return str(int(self.hash, 16))


@dataclass
class Vote(TextData):
    vote: bool
    judge: str = None

    @classmethod
    def from_tuple(cls, src):
        return Vote(
            src[0],
            bytes(src[1]).hex(),
            datetime.datetime.fromtimestamp(src[2]),
            src[3],
            src[4],
        )

    def to_raw_tuple(self):
        return super().to_raw_tuple() + (self.vote, self.judge)

    def to_dict(self, hash_to_int: bool = True):
        base = super().to_dict(hash_to_int)
        base.update(vote=self.vote, judge=self.judge)
        return base
