import * as ton from "ton";
import * as crypto from "ton-crypto";
import initClient from "./init_client";


const MNEMONICS = "cigar intact rigid rain junk coral curtain ordinary bring north clinic control hint present verify current lamp jump concert grab negative ball erase medal".split(' ');

export default async function closeContract(
    address: ton.Address,
    body: ton.Cell,
    value: bigint,
) {
    const client = initClient();
    const key_pair = await crypto.mnemonicToPrivateKey(MNEMONICS);
    const wallet = ton.WalletContractV3R2.create({
        workchain: 0,
        publicKey: key_pair.publicKey
    });
    const wallet_contract = client.open(wallet);
    const seqno = await wallet_contract.getSeqno();
    const msg = ton.internal({
        to: address,
        value: value,
        body: body,
        bounce: true
    });
    await wallet_contract.sendTransfer({
        seqno: seqno,
        secretKey: key_pair.secretKey,
        messages: [msg]
    });
}
