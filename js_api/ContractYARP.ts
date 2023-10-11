import * as ton from "ton-core";
import TimeDelta from "./TimeDelta";
import { TextData, VoteData } from "./types";
import { Statuses, Sizes } from "./constants";
import ContractDataBuilder from "./ContractDataBuilder";
import { StateDependentGetMethodResult } from "./StateDependentGetMethodResult";


export default class ContractYARP implements ton.Contract {
    private data_builder = new ContractDataBuilder();
    private readonly min_fee = "0.05";

    public static deploy(
        code: ton.Cell,
        workchain: number = -1
    ): ContractYARP {
        const initial_data = ContractDataBuilder.buildInitialData();
        const contract_address = ton.contractAddress(
            workchain,
            {
                code: code,
                data: initial_data
            }
        );
        return new ContractYARP(contract_address, {code: code, data: initial_data});
    }

    public constructor(
        readonly address: ton.Address,
        readonly init?: {
            code: ton.Cell,
            data: ton.Cell
        }
    ) {}

    public async sendConstructor(
        provider: ton.ContractProvider,
        sender: ton.Sender,
        price: bigint | string,
        security_deposit_percent: number,
        task_execution_time: TimeDelta,
        text_data: TextData
    ) {
        const data = this.data_builder.buildConstructorData(
            security_deposit_percent,
            task_execution_time, 
            text_data
        );
        await provider.internal(
            sender,
            {
                value: price,
                body: data,
                bounce: false
            }
        );
    }

    public async sendAddTaskExecutionTime(
        provider: ton.ContractProvider,
        sender: ton.Sender,
        additional_time: TimeDelta
    ) {
        const data = this.data_builder.buildAddTaskExecutionTimeData(additional_time);
        await provider.internal(
            sender,
            {
                value: this.min_fee,
                body: data,
                bounce: false
            }
        );
    }

    public async sendRespond(
        provider: ton.ContractProvider,
        sender: ton.Sender
    ) {
        const data = this.data_builder.buildRespondData();
        await provider.internal(
            sender,
            {
                value: await this.getSecurityDeposit(provider),
                body: data,
                bounce: false
            }
        );
    }

    public async sendChooseExecutors(
        provider: ton.ContractProvider,
        sender: ton.Sender,
        executors: ton.Address[]
    ) {
        const data = this.data_builder.buildChooseExecutorsData(executors);
        await provider.internal(
            sender,
            {
                value: this.min_fee,
                body: data,
                bounce: false
            }
        );
    }

    public async sendAcceptInvitation(
        provider: ton.ContractProvider,
        sender: ton.Sender
    ) {
        const data = this.data_builder.buildAcceptInvitationData();
        await provider.internal(
            sender,
            {
                value: this.min_fee,
                body: data,
                bounce: false
            }
        );
    }

    public async sendAddSolution(
        provider: ton.ContractProvider,
        sender: ton.Sender,
        solution: TextData
    ) {
        const data = this.data_builder.buildAddSolutionData(solution);
        await provider.internal(
            sender,
            {
                value: this.min_fee,
                body: data,
                bounce: false
            }
        );
    }

    public async sendFinishExecution(
        provider: ton.ContractProvider,
        sender: ton.Sender
    ) {
        const data = this.data_builder.buildFinishExecutionData();
        await provider.internal(
            sender,
            {
                value: this.min_fee,
                body: data,
                bounce: false
            }
        );
    }

    public async sendAcceptSolution(
        provider: ton.ContractProvider,
        sender: ton.Sender
    ) {
        const data = this.data_builder.buildAcceptSolutionData();
        await provider.internal(
            sender,
            {
                value: this.min_fee,
                body: data,
                bounce: false
            }
        );
    }

    public async sendDeclineSolution(
        provider: ton.ContractProvider,
        sender: ton.Sender,
        judgment_time: TimeDelta
    ) {
        const data = this.data_builder.buildDeclineSolutionData(judgment_time);
        await provider.internal(
            sender,
            {
                value: this.min_fee,
                body: data,
                bounce: false
            }
        );
    }

    public async sendAddArgument(
        provider: ton.ContractProvider,
        sender: ton.Sender,
        argument: TextData
    ) {
        const data = this.data_builder.buildAddArgumentData(argument);
        await provider.internal(
            sender,
            {
                value: this.min_fee,
                body: data,
                bounce: false
            }
        );
    }

    public async sendVote(
        provider: ton.ContractProvider,
        sender: ton.Sender,
        vote: VoteData
    ) {
        const data = this.data_builder.buildVoteData(vote);
        await provider.internal(
            sender,
            {
                value: await this.getSecurityDeposit(provider),
                body: data,
                bounce: false
            }
        );
    }

    public async sendCloseJudgment(
        provider: ton.ContractProvider,
        sender: ton.Sender
    ) {
        const data = this.data_builder.buildCloseJudgmentData();
        await provider.internal(
            sender,
            {
                value: this.min_fee,
                body: data,
                bounce: false
            }
        );
    }

    public async getState(
        provider: ton.ContractProvider
    ): Promise<number> {
        const { stack } = await provider.get("get_state", []);
        return stack.readNumber();
    }

    public async getPrice(
        provider: ton.ContractProvider
    ): Promise<bigint> {
        const { stack } = await provider.get("get_price", []);
        return stack.readBigNumber();
    }

    public async getSecurityDeposit(
        provider: ton.ContractProvider
    ): Promise<bigint> {
        const { stack } = await provider.get("get_security_deposit", []);
        return stack.readBigNumber();
    }

    public async getTaskExecutionTime(
        provider: ton.ContractProvider
    ): Promise<TimeDelta> {
        const { stack } = await provider.get("get_task_execution_time", []);
        const task_execution_time = stack.readNumber();
        return TimeDelta.fromNumber(task_execution_time);
    }

    public async getCustomer(
        provider: ton.ContractProvider
    ): Promise<ton.Address> {
        const { stack } = await provider.get("get_customer", []);
        const customer = stack.readCell().asSlice();
        return customer.loadAddress();
    }

    public async getTaskData(
        provider: ton.ContractProvider
    ): Promise<TextData> {
        const { stack } = await provider.get("get_task_data", []);
        const task_id = stack.readBigNumber();
        const task_hash = stack.readBigNumber();
        const task_timestamp = new Date(stack.readNumber());
        return {
            id: task_id,
            hash: task_hash,
            timestamp: task_timestamp
        };
    }

    public async getExecutor(
        provider: ton.ContractProvider
    ): Promise<StateDependentGetMethodResult<ton.Address>> {
        const { stack } = await provider.get("get_executor", []);
        const result = stack.readCell().asSlice();
        const status = result.loadUint(Sizes.STATUS);
        if (status != Statuses.OK) 
            return {status, };
        const executor = result.loadRef().asSlice().loadAddress();
        return {
            status: Statuses.OK,
            result: executor
        };
    }

    public async getSolutions(
        provider: ton.ContractProvider
    ): Promise<StateDependentGetMethodResult<TextData[]>> {
        const { stack } = await provider.get("get_solutions", []);
        const result = stack.readCell().asSlice();
        const status = result.loadUint(Sizes.STATUS);
        if (status != Statuses.OK)
            return {status, };
        const solutions_slice = result.loadRef().asSlice();
        return {
            status: Statuses.OK,
            result: this.__parseTextData(solutions_slice)
        };
    }

    public async getPotentialExecutors(
        provider: ton.ContractProvider
    ): Promise<StateDependentGetMethodResult<ton.Address[]>> {
        const { stack } = await provider.get("get_potential_executors", []);
        const result = stack.readCell().asSlice();
        const status = result.loadUint(Sizes.STATUS);
        if (status != Statuses.OK)
            return {status, };
        const potential_executors = result.loadRef().asSlice();
        return {
            status: Statuses.OK,
            result: this.__parseExecutors(potential_executors)
        };
    }

    public async getChosenExecutors(
        provider: ton.ContractProvider
    ): Promise<StateDependentGetMethodResult<ton.Address[]>> {
        const { stack } = await provider.get("get_chosen_executors", []);
        const result = stack.readCell().asSlice();
        const status = result.loadUint(Sizes.STATUS);
        if (status != Statuses.OK)
            return {status, };
        const chosen_executors = result.loadRef().asSlice();
        return {
            status: Statuses.OK,
            result: this.__parseExecutors(chosen_executors)
        };
    }

    private __parseExecutors(slice: ton.Slice): ton.Address[] {
        let result: ton.Address[] = [];
        while (slice.remainingRefs != 0) {
            let executor = slice.loadRef().asSlice().loadAddress();
            result.push(executor);
            slice = slice.loadRef().asSlice();
        }
        return result;
    }

    public async getExecutionTimeEnd(
        provider: ton.ContractProvider
    ): Promise<StateDependentGetMethodResult<Date>> {
        const { stack } = await provider.get("get_execution_time_end", []);
        const result = stack.readCell().asSlice();
        const status = result.loadUint(Sizes.STATUS);
        if (status != Statuses.OK)
            return {status, };
        const execution_time_end = result.loadUint(Sizes.TIME);
        return {
            status: Statuses.OK,
            result: new Date(execution_time_end * 1000)
        };
    }

    public async getJudgmentTimeEnd(
        provider: ton.ContractProvider
    ): Promise<StateDependentGetMethodResult<Date>> {
        const { stack } = await provider.get("get_judgment_time_end", []);
        const result = stack.readCell().asSlice();
        const status = result.loadUint(Sizes.STATUS);
        if (status != Statuses.OK)
            return {status, };
        const judgment_time_end = result.loadUint(Sizes.TIME);
        return {
            status: Statuses.OK,
            result: new Date(judgment_time_end * 1000)
        };
    }

    public async getCustomerArguments(
        provider: ton.ContractProvider
    ): Promise<StateDependentGetMethodResult<TextData[]>> {
        const { stack } = await provider.get("get_customer_arguments", []);
        const result = stack.readCell().asSlice();
        const status = result.loadUint(Sizes.STATUS);
        if (status != Statuses.OK)
            return {status, };
        const customer_arguments = result.loadRef().asSlice();
        return {
            status: Statuses.OK,
            result: this.__parseTextData(customer_arguments)
        };
    }

    public async getExecutorArguments(
        provider: ton.ContractProvider
    ): Promise<StateDependentGetMethodResult<TextData[]>> {
        const { stack } = await provider.get("get_executor_arguments", []);
        const result = stack.readCell().asSlice();
        const status = result.loadUint(Sizes.STATUS);
        if (status != Statuses.OK)
            return {status, };
        const executor_arguments = result.loadRef().asSlice();
        return {
            status: Statuses.OK,
            result: this.__parseTextData(executor_arguments)
        };
    }

    private __parseTextData(slice: ton.Slice): TextData[] {
        let result: TextData[] = [];
        while (slice.remainingRefs != 0) {
            let solution = slice.loadRef().asSlice();
            const solution_id = solution.loadUintBig(Sizes.ID);
            const solution_hash = solution.loadUintBig(Sizes.HASH);
            const solution_timestamp = new Date(solution.loadUint(Sizes.TIME) * 1000);
            result.push({
                id: solution_id,
                hash: solution_hash,
                timestamp: solution_timestamp
            });
            slice = slice.loadRef().asSlice();
        }
        return result
    }

    public async getNumVotes(
        provider: ton.ContractProvider
    ): Promise<StateDependentGetMethodResult<number>> {
        const { stack } = await provider.get("get_num_votes", []);
        const result = stack.readCell().asSlice();
        const status = result.loadUint(Sizes.STATUS);
        if (status != Statuses.OK)
            return {status, };
        const num_votes = result.loadUint(Sizes.QUANTITY);
        return {
            status: Statuses.OK,
            result: num_votes
        };
    }

    public async getVotes(
        provider: ton.ContractProvider
    ): Promise<StateDependentGetMethodResult<VoteData[]>> {
        const { stack } = await provider.get("get_votes", []);
        const result = stack.readCell().asSlice();
        const status = result.loadUint(Sizes.STATUS);
        if (status != Statuses.OK)
            return {status, };
        const votes = result.loadRef().asSlice();
        return {
            status: Statuses.OK,
            result: this.__parseVotes(votes)
        };
    }

    private __parseVotes(slice: ton.Slice): VoteData[] {
        let result: VoteData[] = [];
        while (slice.remainingRefs != 0) {
            let vote_data = slice.loadRef().asSlice();
            const vote_id = vote_data.loadUintBig(Sizes.ID);
            const vote_hash = vote_data.loadUintBig(Sizes.HASH);
            const vote_timestamp = new Date(vote_data.loadUint(Sizes.TIME) * 1000);
            const vote_value = vote_data.loadUint(Sizes.VOTE) == -1;
            const judge = vote_data.loadRef().asSlice().loadAddress();
            result.push({
                id: vote_id,
                hash: vote_hash,
                timestamp: vote_timestamp,
                vote: vote_value,
                judge: judge
            });
            slice = slice.loadRef().asSlice();
        }
        return result
    }

    public async getIsCustomer(
        provider: ton.ContractProvider,
        sender: ton.Address
    ): Promise<boolean> {
        const args = this.data_builder.buildSenderData(sender);
        const { stack } = await provider.get("is_customer", args);
        return stack.readNumber() === 1;
    }

    public async getIsExecutor(
        provider: ton.ContractProvider,
        sender: ton.Address
    ): Promise<boolean> {
        const args = this.data_builder.buildSenderData(sender);
        const { stack } = await provider.get("is_executor", args);
        return stack.readNumber() !== 0;
    }

    public async getIsJudge(
        provider: ton.ContractProvider,
        sender: ton.Address
    ): Promise<boolean> {
        const args = this.data_builder.buildSenderData(sender);
        const { stack } = await provider.get("is_judge", args);
        return stack.readNumber() !== 0;
    }
}
