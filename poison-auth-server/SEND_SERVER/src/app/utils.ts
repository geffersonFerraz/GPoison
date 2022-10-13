import * as moment from 'moment';


export function justNumbers(string1, string2) {
    const numsStr1 = string1.replace(/[^0-9]/g, '');
    const numsStr2 = string2.replace(/[^0-9]/g, '');
    return parseInt(numsStr1) + parseInt(numsStr2);
}

export function calcSerial(jusNumber: number) {
    const Str1 = jusNumber.toString()
    const firstChar = Str1[0]
    const dayIs = moment().format('MD').toString()
    const result = Str1.replace(firstChar, dayIs)
    return parseInt(result)
}