import { Cell, Address } from "ton-core";
import ContractYARP from "./ContractYARP";
import initClient from "./init_client";
import loadContractBoc from "./load_contract_boc";

export default function openContract(address?: Address) {
	const client = initClient();
	const contract_boc = loadContractBoc();
	const contract_ = address ? new ContractYARP(address) : ContractYARP.deploy(contract_boc);
	return client.open(contract_);
}
