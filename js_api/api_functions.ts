import {Request, Response} from "express";
import * as ton from "ton-core";
import openContract from "./open_contract";
import ContractDataBuilder from "./ContractDataBuilder";
import TimeDelta from "./TimeDelta";
import {TextData, VoteData} from "./types";
import {Cell} from "ton";
import initClient from "./init_client";
import loadContractBoc from "./load_contract_boc";
import {Address, beginCell} from "ton-core";
import closeContract from "./close_contract";

const data_builder = new ContractDataBuilder();

function sumFees(fees: {
    in_fwd_fee: number;
    storage_fee: number;
    gas_fee: number;
    fwd_fee: number;
}) {
    return fees.in_fwd_fee + fees.storage_fee + fees.gas_fee + fees.fwd_fee;
}

async function estimateTxFee(
    address: ton.Address,
    args: {
        body: Cell,
        state?: Cell
    }
) {
    const client = initClient();
    const data = args.state ? args.state : null;
    const estimated_fee = await client.estimateExternalMessageFee(
        address, {
            body: args.body,
            initCode: data ? loadContractBoc() : null,
            initData: data,
            ignoreSignature: false
        }
    )
    return sumFees(estimated_fee.source_fees);
}

export const EstimateFee = async (
    req: Request,
    res: Response
) => {
    try {
        const req_data = req.body;
        const address = Address.parse(req_data.address);
        const body = Cell.fromBase64(req_data.body);
        const fee = await estimateTxFee(
            address, {
                body: body
            }
        );
        return res.status(200).json({
            status: 0,
            result: fee
        })
    } catch (error) {
        console.log(error);
        return res.status(200).json({status: 1});
    }
}

function textDataToJSON(data: TextData) {
    return {
        id: data.id.toString(),
        hash: data.hash.toString(),
        timestamp: dateToInt(data.timestamp)
    };
}

export const GetStateInit = async (
    req: Request,
    res: Response
) => {
    try {
        const new_contract = openContract();
        const state_init = ton.beginCell().store(ton.storeStateInit(
            {code: new_contract.init?.code, data: new_contract.init?.data}
        )).endCell();
        const body = beginCell().endCell();
        let state: Cell;
        if (new_contract.init) {
            state = new_contract.init?.data;
        }
        else {
            state = beginCell().endCell();
        }
        const fee = await estimateTxFee(
            new_contract.address, {
                body: body,
                state: state
            }
        );
        return res.status(200).json({
            status: 0,
            initial: state_init.toBoc().toString("base64"),
            address: new_contract.address.toString(),
            fee: fee
        })
    } catch (error) {
        console.log(error);
        return res.status(200).json({status: 1});
    }
}

interface RequestTextData {
    id: string,
    hash: string,
    timestamp: number
}

function requestTextDataToTextData(data: RequestTextData): TextData {
    const timestamp = new Date(data.timestamp * 1000);
    return {
        id: BigInt(data.id),
        hash: BigInt(data.hash),
        timestamp: timestamp
    };
}

interface RConstructorData {
    security_deposit_percent: number,
    task_execution_time: number,
    text_data: RequestTextData
}

export const GetConstructorData = async (
    req: Request,
    res: Response
) => {
    try {
        const req_body: RConstructorData = req.body;
        const task_execution_time = TimeDelta.fromNumber(req_body.task_execution_time);
        const body = data_builder.buildConstructorData(
            req_body.security_deposit_percent,
            task_execution_time,
            requestTextDataToTextData(req_body.text_data)
        );
        return res.status(200).json({
            status: 0,
            body: body.toBoc().toString("base64"),
        });
    } catch (error) {
        console.log(error);
        return res.status(200).json({status: 1});
    }
};

interface RAddTaskExecutionTimeData {
    additional_time: number
}

export const GetAddTaskExecutionTimeData = async (
    req: Request,
    res: Response
) => {
    try {
        const req_body: RAddTaskExecutionTimeData = req.body;
        const additional_time = TimeDelta.fromNumber(req_body.additional_time);
        const body = data_builder.buildAddTaskExecutionTimeData(additional_time);
        return res.status(200).json({
            status: 0,
            body: body.toBoc().toString("base64")
        });
    } catch (error) {
        console.log(error);
        return res.status(200).json({status: 1});
    }
}

export const GetRespondData = async (
    req: Request,
    res: Response
) => {
    try {
        const body = data_builder.buildRespondData();
        return res.status(200).json({
            status: 0,
            body: body.toBoc().toString("base64")
        });
    } catch (error) {
        console.log(error);
        return res.status(200).json({status: 1});
    }
}

interface RChooseExecutorsData {
    executors: string[]
}

export const GetChooseExecutorsData = async (
    req: Request,
    res: Response
) => {
    try {
        const data: RChooseExecutorsData = req.body;
        let executors: ton.Address[] = [];
        data.executors.forEach((addr) => {
            executors.push(ton.Address.parse(addr));
        });
        const body = data_builder.buildChooseExecutorsData(executors);
        return res.status(200).json({
            status: 0,
            body: body.toBoc().toString("base64")
        });
    } catch (error) {
        console.log(error);
        return res.status(200).json({status: 1});
    }
}

export const GetAcceptInvitationData = async (
    req: Request,
    res: Response
) => {
    try {
        const body = data_builder.buildAcceptInvitationData();
        return res.status(200).json({
            status: 0,
            body: body.toBoc().toString("base64")
        });
    } catch (error) {
        console.log(error);
        return res.status(200).json({status: 1});
    }
}

interface RAddSolutionData {
    solution_data: RequestTextData
}

export const GetAddSolutionData = async (
    req: Request,
    res: Response
) => {
    try {
        const data: RAddSolutionData = req.body;
        const body = data_builder.buildAddSolutionData(requestTextDataToTextData(data.solution_data));
        return res.status(200).json({
            status: 0,
            body: body.toBoc().toString("base64")
        });
    } catch (error) {
        console.log(error);
        return res.status(200).json({status: 1});
    }
}

export const GetFinishExecutionData = async (
    req: Request,
    res: Response
) => {
    try {
        const body = data_builder.buildFinishExecutionData();
        return res.status(200).json({
            status: 0,
            body: body.toBoc().toString("base64")
        });
    } catch (error) {
        console.log(error);
        return res.status(200).json({status: 1});
    }
}

export const GetAcceptSolutionData = async (
    req: Request,
    res: Response
) => {
    try {
        const body = data_builder.buildAcceptSolutionData();
        return res.status(200).json({
            status: 0,
            body: body.toBoc().toString("base64")
        });
    } catch (error) {
        console.log(error);
        return res.status(200).json({status: 1});
    }
}

interface RDeclineSolutionData {
    judgment_time: number
}

export const GetDeclineSolutionData = async (
    req: Request,
    res: Response
) => {
    try {
        const req_body: RDeclineSolutionData = req.body;
        const judgment_time = TimeDelta.fromNumber(req_body.judgment_time);
        const body = data_builder.buildDeclineSolutionData(judgment_time);
        return res.status(200).json({
            status: 0,
            body: body.toBoc().toString("base64")
        });
    } catch (error) {
        console.log(error);
        return res.status(200).json({status: 1});
    }
}

interface RAddArgumentData {
    argument: RequestTextData
}

export const GetAddArgumentData = async (
    req: Request,
    res: Response
) => {
    try {
        const req_body: RAddArgumentData = req.body;
        const body = data_builder.buildAddArgumentData(requestTextDataToTextData(req_body.argument));
        return res.status(200).json({
            status: 0,
            body: body.toBoc().toString("base64")
        });
    } catch (error) {
        console.log(error);
        return res.status(200).json({status: 1});
    }
}

interface RequestVoteData {
    id: string,
    hash: string,
    timestamp: number,
    vote: boolean
}

function requestVoteDataToVoteData(data: RequestVoteData): VoteData {
    return {
        id: BigInt(data.id),
        hash: BigInt(data.hash),
        timestamp: new Date(data.timestamp * 1000),
        vote: data.vote
    };
}

interface RVoteData {
    vote: RequestVoteData
}

export const GetVoteData = async (
    req: Request,
    res: Response
) => {
    try {
        const data: RVoteData = req.body;
        const body = data_builder.buildVoteData(requestVoteDataToVoteData(data.vote));
        return res.status(200).json({
            status: 0,
            body: body.toBoc().toString("base64")
        });
    } catch (error) {
        console.log(error);
        return res.status(200).json({status: 1});
    }
}

export const CloseJudgment = async (
    req: Request,
    res: Response
) => {
    try {
        const req_body = req.body;
        const address = Address.parse(req_body.address);
        const body = data_builder.buildCloseJudgmentData();
        const fee = ton.toNano("0.35");
        await closeContract(address, body, fee);
        return res.status(200).json({
            status: 0,
            // body: body.toBoc().toString("base64")
        });
    } catch (error) {
        console.log(error);
        return res.status(200).json({status: 1});
    }
}

export const SerializeSender = async (
    req: Request,
    res: Response
) => {
    try {
        const sender = ton.Address.parse(req.body.sender);
        const body = data_builder.buildSenderData(sender);
        return res.status(200).json({
            status: 0,
            boc: ton.serializeTuple(body).toBoc().toString("base64")
        });
    } catch (error) {
        console.log(error);
        return res.status(200).json({status: 1});
    }
}

export const GetState = async (
    req: Request,
    res: Response
) => {
    try {
        const address = ton.Address.parse(req.body.address);
        const contract = openContract(address);
        return res.status(200).json({
            status: 0,
            result: await contract.getState()
        });
    } catch (error) {
        console.log(error);
        return res.status(200).json({status: 1});
    }
}

export const GetPrice = async (
    req: Request,
    res: Response
) => {
    try {
        const address = ton.Address.parse(req.body.address);
        const contract = openContract(address);
        return res.status(200).json({
            status: 0,
            result: (await contract.getPrice()).toString()
        });
    } catch (error) {
        console.log(error);
        return res.status(200).json({status: 1});
    }
}

export const GetSecurityDeposit = async (
    req: Request,
    res: Response
) => {
    try {
        const address = ton.Address.parse(req.body.address);
        const contract = openContract(address);
        return res.status(200).json({
            status: 0,
            result: (await contract.getSecurityDeposit()).toString()
        });
    } catch (error) {
        console.log(error);
        return res.status(200).json({status: 1});
    }
}

export const GetTaskExecutionTime = async (
    req: Request,
    res: Response
) => {
    try {
        const address = ton.Address.parse(req.body.address);
        const contract = openContract(address);
        return res.status(200).json({
            status: 0,
            result: (await contract.getTaskExecutionTime()).toNumber()
        });
    } catch (error) {
        console.log(error);
        return res.status(200).json({status: 1});
    }
}

export const GetCustomer = async (
    req: Request,
    res: Response
) => {
    try {
        const address = ton.Address.parse(req.body.address);
        const contract = openContract(address);
        return res.status(200).json({
            status: 0,
            result: (await contract.getCustomer()).toString()
        });
    } catch (error) {
        console.log(error);
        return res.status(200).json({status: 1});
    }
}

function dateToInt(date: Date): number {
    return date.getTime() / 1000 | 0;
}

export const GetTaskData = async (
    req: Request,
    res: Response
) => {
    try {
        const address = ton.Address.parse(req.body.address);
        const contract = openContract(address);
        const task_data = await contract.getTaskData();
        return res.status(200).json({
            status: 0,
            result: textDataToJSON(task_data)
        });
    } catch (error) {
        console.log(error);
        return res.status(200).json({status: 1});
    }
}

export const GetExecutor = async (
    req: Request,
    res: Response
) => {
    try {
        const address = ton.Address.parse(req.body.address);
        const contract = openContract(address);
        const executor = await contract.getExecutor();
        return res.status(200).json({
            status: executor.status,
            result: executor.result?.toString()
        });
    } catch (error) {
        console.log(error);
        return res.status(200).json({status: 1});
    }
}

export const GetSolutions = async (
    req: Request,
    res: Response
) => {
    try {
        const address = ton.Address.parse(req.body.address);
        const contract = openContract(address);
        const solutions = await contract.getSolutions();
        return res.status(200).json({
            status: solutions.status,
            result: solutions.result?.map(textDataToJSON)
        });
    } catch (error) {
        console.log(error);
        return res.status(200).json({status: 1});
    }
}

export const GetPotentialExecutors = async (
    req: Request,
    res: Response
) => {
    try {
        const address = ton.Address.parse(req.body.address);
        const contract = openContract(address);
        const potential_executors = await contract.getPotentialExecutors();
        return res.status(200).json({
            status: potential_executors.status,
            result: potential_executors.result?.map((addr) => {
                return addr.toString();
            })
        });
    } catch (error) {
        console.log(error);
        return res.status(200).json({status: 1});
    }
}

export const GetChosenExecutors = async (
    req: Request,
    res: Response
) => {
    try {
        const address = ton.Address.parse(req.body.address);
        const contract = openContract(address);
        const chosen_executors = await contract.getChosenExecutors();
        return res.status(200).json({
            status: chosen_executors.status,
            result: chosen_executors.result?.map((addr) => {
                return addr.toString()
            })
        });
    } catch (error) {
        console.log(error);
        return res.status(200).json({status: 1});
    }
}

export const GetExecutionTimeEnd = async (
    req: Request,
    res: Response
) => {
    try {
        const address = ton.Address.parse(req.body.address);
        const contract = openContract(address);
        const execution_time_end = await contract.getExecutionTimeEnd();
        return res.status(200).json({
            status: execution_time_end.status,
            result: execution_time_end.result ? dateToInt(execution_time_end.result) : null
        });
    } catch (error) {
        console.log(error);
        return res.status(200).json({status: 1});
    }
}

export const GetJudgmentTimeEnd = async (
    req: Request,
    res: Response
) => {
    try {
        const address = ton.Address.parse(req.body.address);
        const contract = openContract(address);
        const judgment_time_end = await contract.getJudgmentTimeEnd();
        return res.status(200).json({
            status: judgment_time_end.status,
            result: judgment_time_end.result ? dateToInt(judgment_time_end.result) : null
        });
    } catch (error) {
        console.log(error);
        return res.status(200).json({status: 1});
    }
}

export const GetCustomerArguments = async (
    req: Request,
    res: Response
) => {
    try {
        const address = ton.Address.parse(req.body.address);
        const contract = openContract(address);
        const customer_arguments = await contract.getCustomerArguments();
        return res.status(200).json({
            status: customer_arguments.status,
            result: customer_arguments.result?.map(textDataToJSON)
        });
    } catch (error) {
        console.log(error);
        return res.status(200).json({status: 1});
    }
}

export const GetExecutorArguments = async (
    req: Request,
    res: Response
) => {
    try {
        const address = ton.Address.parse(req.body.address);
        const contract = openContract(address);
        const executor_arguments = await contract.getExecutorArguments();
        return res.status(200).json({
            status: executor_arguments.status,
            result: executor_arguments.result?.map(textDataToJSON)
        });
    } catch (error) {
        console.log(error);
        return res.status(200).json({status: 1});
    }
}

export const GetNumVotes = async (
    req: Request,
    res: Response
) => {
    try {
        const address = ton.Address.parse(req.body.address);
        const contract = openContract(address);
        const num_votes = await contract.getNumVotes();
        return res.status(200).json({
            status: num_votes.status,
            result: num_votes.result
        });
    } catch (error) {
        console.log(error);
        return res.status(200).json({status: 1});
    }
}

function voteDataToJSON(data: VoteData) {
    return {
        id: data.id.toString(),
        hash: data.hash.toString(),
        timestamp: dateToInt(data.timestamp),
        vote: data.vote,
        judge: data.judge?.toString()
    };
}

export const GetVotes = async (
    req: Request,
    res: Response
) => {
    try {
        const address = ton.Address.parse(req.body.address);
        const contract = openContract(address);
        const votes = await contract.getVotes();
        return res.status(200).json({
            status: votes.status,
            result: votes.result?.map(voteDataToJSON)
        });
    } catch (error) {
        console.log(error);
        return res.status(200).json({status: 1});
    }
}

export const GetIsCustomer = async (
    req: Request,
    res: Response
) => {
    try {
        const sender = ton.Address.parse(req.body.sender);
        const address = ton.Address.parse(req.body.address);
        const contract = openContract(address);
        return res.status(200).json({
            status: 0,
            result: await contract.getIsCustomer(sender)
        });
    } catch (error) {
        console.log(error);
        return res.status(200).json({status: 1});
    }
}

export const GetIsExecutor = async (
    req: Request,
    res: Response
) => {
    try {
        const sender = ton.Address.parse(req.body.sender);
        const address = ton.Address.parse(req.body.address);
        const contract = openContract(address);
        return res.status(200).json({
            status: 0,
            result: await contract.getIsExecutor(sender)
        });
    } catch (error) {
        console.log(error);
        return res.status(200).json({status: 1});
    }
}

export const GetIsJudge = async (
    req: Request,
    res: Response
) => {
    try {
        const sender = ton.Address.parse(req.body.sender);
        const address = ton.Address.parse(req.body.address);
        const contract = openContract(address);
        return res.status(200).json({
            status: 0,
            result: await contract.getIsJudge(sender)
        });
    } catch (error) {
        console.log(error);
        return res.status(200).json({status: 1});
    }
}

export const index = async (
    req: Request,
    res: Response
) => {
    try {
        return res.status(200).json({
            status: 0,
            result: "Hello, world!"
        });
    } catch (error) {
        console.log(error);
        return res.status(200).json({status: 1});
    }
}
