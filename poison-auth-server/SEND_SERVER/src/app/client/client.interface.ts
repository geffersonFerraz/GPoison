export interface CreateClient {
    email: string;
    serial: string;
    serial2: string;
}

export interface GetClient {
    serial: string;
    serial2: string;
}

export interface ResultClient {
    result: number,
    expireAt: Date
}