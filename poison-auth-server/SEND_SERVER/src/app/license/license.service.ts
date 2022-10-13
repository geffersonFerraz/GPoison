import { Injectable } from '@nestjs/common';
import { PrismaService } from 'src/prisma/prisma.service';
import { IncrementLicense, ResultLicense } from './license.interface';
import * as moment from 'moment';
import { ResultClient } from '../client/client.interface';
import { calcSerial, justNumbers } from '../utils';

@Injectable()
export class LicenseService {
  constructor(private prisma: PrismaService) { }

  async extendLicense(data: IncrementLicense): Promise<ResultLicense> {
    const serial = await this.prisma.serial.findUnique({ where: { serial: data.serial } })
    let license = await this.prisma.license.findFirst({ where: { clientId: serial.clientId } })
    const newExpiration = moment(license.finishAt).add(5, 'days').toDate()
    await this.prisma.license.updateMany({ where: { clientId: serial.clientId }, data: { finishAt: newExpiration } })
    license = await this.prisma.license.findFirst({ where: { clientId: serial.clientId } })

    let resultSerial = calcSerial(justNumbers(data.serial, data.serial2));
    if (!license) {
      resultSerial = 0
    }
    const result: ResultLicense = { result: resultSerial, expireAt: license.finishAt }
    return result
  }
}
