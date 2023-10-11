import requests
import datetime
import typing
import base64
from text_objects import TextData, Vote
from env_constants import JS_PYTHON_API
from .state_init import StateInit
from ton.money_utils import to_nano


class ContractAPI:
    def __init__(self, contract_address: str = None, api_url: str = JS_PYTHON_API):
        assert api_url is not None, f"JS_PYTHON_API param not set"
        self.__contract_address = contract_address
        self.__endpoint = api_url

    @property
    def contract_address(self) -> typing.Union[str, None]:
        return self.__contract_address

    def estimate_fee(self, body: str) -> int:
        payload = self.__pack_args(
            body=body,
        )
        response = self.__send_request(self.__APIMethods.ESTIMATE_FEE, payload)
        if response is None:
            return to_nano(0.35)
        fee = response["result"]
        if fee < to_nano(0.2):
            fee = to_nano(0.35)
        return fee

    def state_init(self) -> StateInit:
        response = self.__send_request(self.__APIMethods.STATE_INIT)
        return StateInit(response["address"], response["initial"], response["fee"])

    def constructor(self,
                    security_deposit_percent: int,
                    task_execution_time: datetime.timedelta,
                    text_data: TextData) -> str:
        payload = self.__pack_args(
            security_deposit_percent=security_deposit_percent,
            task_execution_time=task_execution_time,
            text_data=text_data
        )
        response = self.__send_request(self.__APIMethods.CONSTRUCTOR, payload)
        return response["body"]

    def add_task_execution_time(self, additional_time: datetime.timedelta) -> str:
        payload = self.__pack_args(
            additional_time=additional_time
        )
        response = self.__send_request(self.__APIMethods.ADD_TASK_EXECUTION_TIME, payload)
        return response["body"]

    def respond(self) -> str:
        response = self.__send_request(self.__APIMethods.RESPOND)
        return response["body"]

    def choose_executors(self, executors: typing.List[str]) -> str:
        payload = self.__pack_args(executors=executors)
        response = self.__send_request(self.__APIMethods.CHOOSE_EXECUTORS, payload)
        return response["body"]
    
    def accept_invitation(self) -> str:
        response = self.__send_request(self.__APIMethods.ACCEPT_INVITATION)
        return response["body"]

    def add_solution(self, solution_data: TextData) -> str:
        payload = self.__pack_args(solution_data=solution_data)
        response = self.__send_request(self.__APIMethods.ADD_SOLUTION, payload)
        return response["body"]
    
    def finish_execution(self) -> str:
        response = self.__send_request(self.__APIMethods.FINISH_EXECUTION)
        return response["body"]
    
    def accept_solution(self) -> str:
        response = self.__send_request(self.__APIMethods.ACCEPT_SOLUTION)
        return response["body"]

    def decline_solution(self, judgment_time: datetime.timedelta) -> str:
        payload = self.__pack_args(judgment_time=judgment_time)
        response = self.__send_request(self.__APIMethods.DECLINE_SOLUTION, payload)
        return response["body"]

    def add_argument(self, argument: TextData) -> str:
        payload = self.__pack_args(argument=argument)
        response = self.__send_request(self.__APIMethods.ADD_ARGUMENT, payload)
        return response["body"]
    
    def vote(self, vote: Vote) -> str:
        payload = self.__pack_args(vote=vote)
        response = self.__send_request(self.__APIMethods.VOTE, payload)
        return response["body"]

    def close_judgment(self):
        response = self.__send_request(self.__APIMethods.CLOSE_JUDGMENT)
        # return response["body"]

    # def __to_base64(self, src):
    #     return base64.b64encode(bytes.fromhex(src)).decode()

    def get_state(self) -> typing.Union[int, None]:
        response = self.__send_request(self.__APIMethods.GET_STATE)
        if response is None:
            return None
        return response["result"]

    def get_price(self) -> typing.Union[int, None]:
        response = self.__send_request(self.__APIMethods.GET_PRICE)
        if response is None:
            return None
        return int(response["result"])

    def get_security_deposit(self) -> typing.Union[int, None]:
        response = self.__send_request(self.__APIMethods.GET_SECURITY_DEPOSIT)
        if response is None:
            return None
        return int(response["result"])
    
    def get_task_execution_time(self) -> typing.Union[datetime.timedelta, None]:
        response = self.__send_request(self.__APIMethods.GET_TASK_EXECUTION_TIME)
        if response is None:
            return None
        return self.__parse_timedelta(response["result"])

    def get_customer(self) -> typing.Union[str, None]:
        response = self.__send_request(self.__APIMethods.GET_CUSTOMER)
        if response is None:
            return None
        return response["result"]
    
    def get_task_data(self) -> typing.Union[TextData, None]:
        response = self.__send_request(self.__APIMethods.GET_TASK_DATA)
        if response is None:
            return None
        return self.__parse_text_data(response["result"])
    
    def get_executor(self) -> typing.Union[str, None]:
        response = self.__send_request(self.__APIMethods.GET_EXECUTOR)
        if response is None:
            return None
        return response["result"]
    
    def get_solutions(self) -> typing.Union[typing.List[TextData], None]:
        response = self.__send_request(self.__APIMethods.GET_SOLUTIONS)
        if response is None:
            return None
        solutions = list()
        for solution_data in response["result"]:
            solutions.append(self.__parse_text_data(solution_data))
        return solutions

    def get_potential_executors(self) -> typing.Union[typing.List[str], None]:
        response = self.__send_request(self.__APIMethods.GET_POTENTIAL_EXECUTORS)
        if response is None:
            return None
        return response["result"]

    def get_chosen_executors(self) -> typing.Union[typing.List[str], None]:
        response = self.__send_request(self.__APIMethods.GET_CHOSEN_EXECUTORS)
        if response is None:
            return None
        return response["result"]
    
    def get_execution_time_end(self) -> typing.Union[datetime.datetime, None]:
        response = self.__send_request(self.__APIMethods.GET_EXECUTION_TIME_END)
        if response is None:
            return None
        return self.__parse_datetime(response["result"])

    def get_judgment_time_end(self) -> typing.Union[datetime.datetime, None]:
        response = self.__send_request(self.__APIMethods.GET_JUDGMENT_TIME_END)
        if response is None:
            return None
        return self.__parse_datetime(response["result"])

    def get_customer_arguments(self) -> typing.Union[typing.List[TextData], None]:
        return self.__get_arguments(self.__APIMethods.GET_CUSTOMER_ARGUMENTS)
    
    def get_executor_arguments(self) -> typing.Union[typing.List[TextData], None]:
        return self.__get_arguments(self.__APIMethods.GET_EXECUTOR_ARGUMENTS)

    def __get_arguments(self, method):
        response = self.__send_request(method)
        if response is None:
            return None
        arguments = list()
        for argument in response["result"]:
            arguments.append(self.__parse_text_data(argument))
        return arguments

    def get_num_votes(self) -> typing.Union[int, None]:
        response = self.__send_request(self.__APIMethods.GET_NUM_VOTES)
        if response is None:
            return None
        return response["result"]
    
    def get_votes(self) -> typing.Union[typing.List[Vote], None]:
        response = self.__send_request(self.__APIMethods.GET_VOTES)
        if response is None:
            return None
        votes = list()
        for vote in response["result"]:
            votes.append(self.__parse_vote_data(vote))
        return votes
    
    def is_customer(self, sender: str) -> typing.Union[bool, None]:
        args = self.__pack_args(sender=sender)
        response = self.__send_request(self.__APIMethods.IS_CUSTOMER, args)
        if response is None:
            return None
        return response["result"]
    
    def is_executor(self, sender: str) -> typing.Union[bool, None]:
        args = self.__pack_args(sender=sender)
        response = self.__send_request(self.__APIMethods.IS_EXECUTOR, args)
        if response is None:
            return None
        return response["result"]
    
    def is_judge(self, sender: str) -> typing.Union[bool, None]:
        args = self.__pack_args(sender=sender)
        response = self.__send_request(self.__APIMethods.IS_JUDGE, args)
        if response is None:
            return None
        return response["result"]

    def __pack_args(self, **args):
        response = dict()
        for key, value in args.items():
            if value is None:
                continue
            response[key] = self.__serialize_arg(value)
        return response

    def __serialize_arg(self, value):
        if isinstance(value, Vote):
            return value.to_dict()
        if isinstance(value, TextData):
            return value.to_dict()
        if isinstance(value, datetime.timedelta):
            return self.__serialize_timedelta(value)
        if isinstance(value, datetime.datetime):
            return self.__serialize_datetime(value)
        if isinstance(value, list):
            return self.__serialize_list(value)
        return value

    def __serialize_datetime(self, dt):
        return int(dt.timestamp())

    def __serialize_timedelta(self, td: datetime.timedelta):
        return int(td.total_seconds())

    def __serialize_list(self, obj):
        return [self.__serialize_arg(item) for item in obj]

    def __send_request(self, method: str, args = None):
        url = f"{self.__endpoint}/{method}"
        if args is None:
            args = dict()
        if self.__contract_address is not None:
            args.update(address=self.__contract_address)
        response = requests.post(url, json=args)
        if response.status_code != 200:
            return None
        result = response.json()
        if result["status"]:
            return None
        return result

    def __parse_datetime(self, source):
        return datetime.datetime.fromtimestamp(source)

    def __parse_timedelta(self, source):
        return datetime.timedelta(seconds=source)

    def __parse_text_data(self, source):
        timestamp = self.__parse_datetime(source["timestamp"])
        hash_bytes = int(source["hash"]).to_bytes(256 // 8, "big")
        hash_hex = hash_bytes.hex()
        return TextData(
            int(source["id"]),
            hash_hex,
            timestamp
        )

    def __parse_vote_data(self, source):
        timestamp = self.__parse_datetime(source["timestamp"])
        hash_bytes = int(source["hash"]).to_bytes(256 // 8, "big")
        hash_hex = hash_bytes.hex()
        return Vote(
            int(source["id"]),
            hash_hex,
            timestamp,
            source["vote"],
            source["judge"]
        )

    class __APIMethods:
        ESTIMATE_FEE = "estimate_fee"
        STATE_INIT = "state_init"
        CONSTRUCTOR = "constructor"
        ADD_TASK_EXECUTION_TIME = "add_task_execution_time"
        RESPOND = "respond"
        CHOOSE_EXECUTORS = "choose_executors"
        ACCEPT_INVITATION = "accept_invitation"
        ADD_SOLUTION = "add_solution"
        FINISH_EXECUTION = "finish_execution"
        ACCEPT_SOLUTION = "accept_solution"
        DECLINE_SOLUTION = "decline_solution"
        ADD_ARGUMENT = "add_argument"
        VOTE = "vote"
        CLOSE_JUDGMENT = "close_judgment"
        GET_STATE = "get_state"
        GET_PRICE = "get_price"
        GET_SECURITY_DEPOSIT = "get_security_deposit"
        GET_TASK_EXECUTION_TIME = "get_task_execution_time"
        GET_CUSTOMER = "get_customer"
        GET_TASK_DATA = "get_task_data"
        GET_EXECUTOR = "get_executor"
        GET_SOLUTIONS = "get_solutions"
        GET_POTENTIAL_EXECUTORS = "get_potential_executors"
        GET_CHOSEN_EXECUTORS = "get_chosen_executors"
        GET_EXECUTION_TIME_END = "get_execution_time_end"
        GET_JUDGMENT_TIME_END = "get_judgment_time_end"
        GET_CUSTOMER_ARGUMENTS = "get_customer_arguments"
        GET_EXECUTOR_ARGUMENTS = "get_executor_arguments"
        GET_NUM_VOTES = "get_num_votes"
        GET_VOTES = "get_votes"
        IS_CUSTOMER = "is_customer"
        IS_EXECUTOR = "is_executor"
        IS_JUDGE = "is_judge"
