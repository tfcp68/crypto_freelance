import http from "http";
import express, { Express } from "express";
import morgan from "morgan";
import app from "./app";

const router: Express = express();

router.use(express.urlencoded({
    extended: false
}));
router.use(express.json());
router.use('/', app);

const http_server = http.createServer(router);
const PORT = 6666;
http_server.listen(PORT, () => console.log(`Running on port ${PORT}`));
