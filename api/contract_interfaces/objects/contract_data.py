from dataclasses import dataclass
import datetime


@dataclass
class ContractData:
    id: int
    sha256hashsum: str
    timestamp: datetime.datetime

    @classmethod
    def from_tuple(cls, tuple):
        return ContractData(
            tuple[0],
            bytes(tuple[1]).hex(),
            datetime.datetime.fromtimestamp(tuple[2])
        )

    def to_raw_tuple(self):
        return (
            self.id,
            self.sha256hashsum,
            int(self.timestamp.timestamp())
        )


class TaskData(ContractData):
    ...


class SolutionData(ContractData):
    ...


class Argument(ContractData):
    ...


@dataclass
class JudgeVote(ContractData):
    verdict: bool
    judge_address: str = None

    @classmethod
    def from_tuple(cls, tuple):
        return JudgeVote(
            tuple[0],
            bytes(tuple[1]).hex(),
            datetime.datetime.fromtimestamp(tuple[2]),
            tuple[3],
            tuple[4],
        )

    def to_raw_tuple(self):
        return (
            self.verdict,
            self.id,
            self.sha256hashsum
        )


@dataclass
class ExecutorData:
    address: str
    was_chosen: bool

    @classmethod
    def from_tuple(cls, tuple):
        return ExecutorData(*tuple)


@dataclass
class MakeDealMoneyDistribution:
    price: int
    security_deposit: int
    marketplace_fee: int

    @classmethod
    def from_tuple(cls, tuple):
        return MakeDealMoneyDistribution(*tuple)
