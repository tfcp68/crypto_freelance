FROM node:16-slim

ENV CONTRACT_BOC_PATH="./Contract.boc"

COPY js_api /api
WORKDIR /api

RUN npm i

COPY ton_contracts/boc/Contract.boc Contract.boc

EXPOSE 6666
CMD ["npx", "ts-node", "server.ts"]
