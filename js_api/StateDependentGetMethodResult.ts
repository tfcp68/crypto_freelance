export class StateDependentGetMethodResult<T> {
    constructor(
        readonly status: number,
        readonly result?: T
    ) {}
}