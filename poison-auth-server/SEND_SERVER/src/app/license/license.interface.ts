export interface IncrementLicense {
    serial: string;
    serial2: string;
    days: number;
}

export interface ResultLicense {
    result: number,
    expireAt: Date
}