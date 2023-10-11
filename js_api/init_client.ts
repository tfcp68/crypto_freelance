import * as ton from "ton";
import {API_ENDPOINT, API_KEY} from "./constants";

export default function initClient() {
    return new ton.TonClient({
        endpoint: API_ENDPOINT,
        apiKey: API_KEY
    });
}
