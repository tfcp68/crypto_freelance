import {Cell} from "ton";
import fs from "fs";
import {CONTRACT_BOC_PATH} from "./constants";

export default function loadContractBoc() {
    return Cell.fromBoc(fs.readFileSync(CONTRACT_BOC_PATH))[0];
}
