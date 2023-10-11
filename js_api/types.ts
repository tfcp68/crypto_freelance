import * as ton from "ton-core";


export type TextData = {
    id: bigint,
    hash: bigint,
    timestamp: Date
}

export type VoteData = {
    id: bigint,
    hash: bigint,
    timestamp: Date,
    vote: boolean,
    judge?: ton.Address
}
