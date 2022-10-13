import { Injectable } from '@nestjs/common';
import { Client, Prisma, PrismaClient } from '@prisma/client';
import { PrismaService } from 'src/prisma/prisma.service';
import { CreateClient, GetClient, ResultClient } from './client.interface';
import * as moment from 'moment';
import { calcSerial, justNumbers } from '../utils';

@Injectable()
export class ClientService {
  constructor(private prisma: PrismaService) { }

  async createClient(data: CreateClient): Promise<Client> {
    const client = await this.prisma.client.create({ data: { email: data.email } });
    const serialCreate = { serial: data.serial, serial2: data.serial2, clientId: client.id }
    await this.prisma.serial.create({ data: serialCreate })
    const finishAt = moment().add(10, 'days').toDate()
    await this.prisma.license.create({ data: { clientId: client.id, finishAt: finishAt } })

    return client
  }

  async getClient(data: GetClient): Promise<ResultClient> {
    console.log(data)
    // let client = await this.prisma.client.findUnique({ where: {}, include: { Serial: { where: { serial: data.serial } } } })
    let client = await this.prisma.$queryRaw`select 1 from Client c join Serial s WHERE s.serial = ${data.serial}`

    if (client instanceof Array && client.length == 0) {
      const newClient: CreateClient = {
        email: 'null',
        serial: data.serial,
        serial2: data.serial2
      }

      await this.createClient(newClient)
    }

    let serial = await this.prisma.serial.findUnique({ where: { serial: data.serial } })

    let result: ResultClient = { result: 0, expireAt: moment().toDate() }
    if (serial) {
      const nowIs = moment().toDate()
      const license = await this.prisma.license.findFirst({ where: { clientId: serial.clientId, finishAt: { gte: nowIs } } })
      let resultSerial = calcSerial(justNumbers(data.serial, data.serial2));
      if (!license) {
        resultSerial = 0
      }
      result = { result: resultSerial, expireAt: license.finishAt }
    }

    return result
  }
}

