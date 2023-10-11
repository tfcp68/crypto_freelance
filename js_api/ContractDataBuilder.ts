import * as ton from "ton-core";
import TimeDelta from "./TimeDelta";
import { TextData, VoteData } from "./types";
import { States, Sizes, Statuses, Operators } from "./constants";


export default class ContractDataBuilder {
    public static buildInitialData(): ton.Cell {
        return ton.beginCell()
               .storeUint(States.NULL, Sizes.STATE)
               .storeUint(ContractDataBuilder.__getInitialState(), 64)
               .endCell();
    }

    private static __getInitialState(): number {
        const date = new Date();
        return Number(date.getTime());
    }

    public buildConstructorData(
        security_deposit_percent: number,
        task_execution_time: TimeDelta,
        text_data: TextData
    ): ton.Cell {
        const text_data_cell = ton.beginCell()
                               .storeUint(text_data.id, Sizes.ID)
                               .storeUint(text_data.hash, Sizes.HASH)
                               .storeUint(this.__timestampToInt(text_data.timestamp), Sizes.TIME)
                               .endCell();
        const data = ton.beginCell()
                     .storeUint(Operators.CONSTRUCTOR, Sizes.OP)
                     .storeUint(security_deposit_percent, Sizes.PERCENT)
                     .storeUint(task_execution_time.toNumber(), Sizes.TIME)
                     .storeRef(text_data_cell)
                     .endCell();
        return data;
    }

    private __timestampToInt(timestamp: Date): number {
        return (timestamp.getTime() / 1000 | 0);
    }

    public buildAddTaskExecutionTimeData(
        additional_time: TimeDelta
    ): ton.Cell {
        return ton.beginCell()
               .storeUint(Operators.ADD_TASK_EXECUTION_TIME, Sizes.OP)
               .storeUint(additional_time.toNumber(), Sizes.TIME)
               .endCell();
    }

    public buildRespondData(): ton.Cell {
        return ton.beginCell()
               .storeUint(Operators.RESPOND, Sizes.OP)
               .endCell();
    }

    public buildChooseExecutorsData(
        executors: ton.Address[]
    ): ton.Cell {
        const executors_data = this.__addressArrayToList(executors);
        return ton.beginCell()
               .storeUint(Operators.CHOOSE_EXECUTORS, Sizes.OP)
               .storeRef(executors_data)
               .endCell();
    }

    private __addressArrayToList(addresses: ton.Address[]): ton.Cell {
        let result = ton.beginCell().endCell();
        addresses.forEach((address) => {
            result = ton.beginCell()
                     .storeRef(
                        ton.beginCell()
                        .storeAddress(address)
                        .endCell()
                     )
                     .storeRef(result)
                     .endCell();
        });
        return result;
    }

    public buildAcceptInvitationData(): ton.Cell {
        return ton.beginCell()
               .storeUint(Operators.ACCEPT_INVITATION, Sizes.OP)
               .endCell();
    }

    public buildAddSolutionData(
        solution: TextData
    ): ton.Cell {
        const solution_data = ton.beginCell()
                              .storeUint(solution.id, Sizes.ID)
                              .storeUint(solution.hash, Sizes.HASH)
                              .storeUint(this.__timestampToInt(solution.timestamp), Sizes.TIME)
                              .endCell();
        return ton.beginCell()
               .storeUint(Operators.ADD_SOLUTION, Sizes.OP)
               .storeRef(solution_data)
               .endCell();
    }

    public buildFinishExecutionData(): ton.Cell {
        return ton.beginCell()
               .storeUint(Operators.FINISH_EXECUTION, Sizes.OP)
               .endCell();
    }

    public buildAcceptSolutionData(): ton.Cell {
        return ton.beginCell()
               .storeUint(Operators.ACCEPT_SOLUTION, Sizes.OP)
               .endCell();
    }

    public buildDeclineSolutionData(
        judgment_time: TimeDelta
    ): ton.Cell {
        return ton.beginCell()
               .storeUint(Operators.DECLINE_SOLUTION, Sizes.OP)
               .storeUint(judgment_time.toNumber(), Sizes.TIME)
               .endCell();
    }

    public buildAddArgumentData(
        argument: TextData
    ): ton.Cell {
        const argument_data = ton.beginCell()
                              .storeUint(argument.id, Sizes.ID)
                              .storeUint(argument.hash, Sizes.HASH)
                              .storeUint(this.__timestampToInt(argument.timestamp), Sizes.TIME)
                              .endCell();
        return ton.beginCell()
               .storeUint(Operators.ADD_ARGUMENT, Sizes.OP)
               .storeRef(argument_data)
               .endCell();
    }

    public buildVoteData(
        vote: VoteData
    ): ton.Cell {
        const vote_data = ton.beginCell()
                          .storeUint(vote.id, Sizes.ID)
                          .storeUint(vote.hash, Sizes.HASH)
                          .storeUint(this.__timestampToInt(vote.timestamp), Sizes.TIME)
                          .storeInt(vote.vote ? -1 : 0, Sizes.VOTE)
                          .endCell();
        return ton.beginCell()
               .storeUint(Operators.VOTE, Sizes.OP)
               .storeRef(vote_data)
               .endCell();
    }

    public buildCloseJudgmentData(): ton.Cell {
        return ton.beginCell()
               .storeUint(Operators.CLOSE_JUDGMENT, Sizes.OP)
               .endCell();
    }

    public buildSenderData(sender: ton.Address): ton.TupleItem[] {
        const data = ton.beginCell().storeAddress(sender).endCell();
        const tuple_builder = new ton.TupleBuilder()
        tuple_builder.writeCell(data);
        const args = tuple_builder.build();
        return args;
    }
}
