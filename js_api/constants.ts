export class States {
    public static readonly NULL = 0;
    public static readonly MAKE_DEAL = 1;
    public static readonly EXECUTION = 2;
    public static readonly JUDGMENT = 3;
    public static readonly CLOSED = 4;
    public static readonly CLOSED_AFTER_JUDGMENT = 5;
}

export class Sizes {
    public static readonly VOTE = 2;
    public static readonly STATE = 4;
    public static readonly PERCENT = 8;
    public static readonly OP = 16;
    public static readonly STATUS = 16;
    public static readonly TIME = 32;
    public static readonly QUANTITY = 32;
    public static readonly COIN = 120;
    public static readonly ID = 256;
    public static readonly HASH = 256;
}

export class Statuses {
    public static readonly OK = 0;
    public static readonly ALREADY_CONSTRUCTED = 0x1001;
    public static readonly MESSAGE_ERROR = 0x1002;
    public static readonly ACCESS_DENIED = 0x1003;
    public static readonly UNKNOWN_METHOD = 0x1004;
    public static readonly TOO_LOW_CONTRACT_PRICE = 0x1005;
    public static readonly TOO_LOW_TASK_EXECUTION_TIME = 0x1006;
    public static readonly TOO_LOW_JUDGMENT_TIME = 0x1007;
    public static readonly ALREADY_RESPONDED = 0x1008;
    public static readonly VALUE_ERROR = 0x1009;
    public static readonly ALREADY_VOTED = 0x1010;
    public static readonly WRONG_STATE = 0x1011;
}

export class Operators {
    public static readonly CONSTRUCTOR = 0;
    public static readonly ADD_TASK_EXECUTION_TIME = 1;
    public static readonly RESPOND = 2;
    public static readonly CHOOSE_EXECUTORS = 3;
    public static readonly ACCEPT_INVITATION = 4;
    public static readonly ADD_SOLUTION = 5;
    public static readonly FINISH_EXECUTION = 6;
    public static readonly ACCEPT_SOLUTION = 7;
    public static readonly DECLINE_SOLUTION = 8;
    public static readonly ADD_ARGUMENT = 9;
    public static readonly VOTE = 10;
    public static readonly CLOSE_JUDGMENT = 11;
}

export const API_ENDPOINT = "https://testnet.toncenter.com/api/v2/jsonRPC";
export const API_KEY = "58fd60709aa0a35db5f69364a67642142aad9153acde7e0f281a2edffc12eb57";
// export const CONTRACT_BOC_PATH = "../ton_contracts/boc/Contract.boc";
export const CONTRACT_BOC_PATH = String(process.env.CONTRACT_BOC_PATH);
