import express from "express";
import * as functions from "./api_functions";


const app = express.Router();

app.post("/estimate_fee", functions.EstimateFee);
app.post("/state_init", functions.GetStateInit);
app.post("/constructor", functions.GetConstructorData);
app.post("/add_task_execution_time", functions.GetAddTaskExecutionTimeData);
app.post("/respond", functions.GetRespondData);
app.post("/choose_executors", functions.GetChooseExecutorsData);
app.post("/accept_invitation", functions.GetAcceptInvitationData);
app.post("/add_solution", functions.GetAddSolutionData);
app.post("/finish_execution", functions.GetFinishExecutionData);
app.post("/accept_solution", functions.GetAcceptSolutionData);
app.post("/decline_solution", functions.GetDeclineSolutionData);
app.post("/add_argument", functions.GetAddArgumentData);
app.post("/vote", functions.GetVoteData);
app.post("/close_judgment", functions.CloseJudgment);
app.post("/serialize_sender", functions.SerializeSender);
app.post("/get_state", functions.GetState);
app.post("/get_price", functions.GetPrice);
app.post("/get_security_deposit", functions.GetSecurityDeposit);
app.post("/get_task_execution_time", functions.GetTaskExecutionTime);
app.post("/get_customer", functions.GetCustomer);
app.post("/get_task_data", functions.GetTaskData);
app.post("/get_executor", functions.GetExecutor);
app.post("/get_solutions", functions.GetSolutions);
app.post("/get_potential_executors", functions.GetPotentialExecutors);
app.post("/get_chosen_executors", functions.GetChosenExecutors);
app.post("/get_execution_time_end", functions.GetExecutionTimeEnd);
app.post("/get_judgment_time_end", functions.GetJudgmentTimeEnd);
app.post("/get_customer_arguments", functions.GetCustomerArguments);
app.post("/get_executor_arguments", functions.GetExecutorArguments);
app.post("/get_num_votes", functions.GetNumVotes);
app.post("/get_votes", functions.GetVotes);
app.post("/is_customer", functions.GetIsCustomer);
app.post("/is_executor", functions.GetIsExecutor);
app.post("/is_judge", functions.GetIsJudge);
app.post("/", functions.index);

export = app;
