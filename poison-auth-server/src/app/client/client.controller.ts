import { Body, Controller, Get, Post, UseGuards } from '@nestjs/common';
import { ClientService } from './client.service';
import { Client as ClientModel } from '@prisma/client';
import { CreateClient, GetClient, ResultClient } from './client.interface';
import { JwtAuthGuard } from '../auth/guards/jwt-auth.guard';
@Controller()
export class ClientController {
  constructor(private readonly clientService: ClientService) { }


  @Get('/client')
  async getClient(@Body() postData: GetClient): Promise<ResultClient> {
    console.log(postData)
    return this.clientService.getClient(postData);
  }

  @UseGuards(JwtAuthGuard)
  @Post('/client')
  async postClient(@Body() postData: CreateClient): Promise<ClientModel> {
    return this.clientService.createClient(postData);
  }
}
