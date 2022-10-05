import { Module } from '@nestjs/common';
import { PrismaService } from 'src/prisma/prisma.service';
import { AuthModule } from '../auth/auth.module';
import { ClientController } from './client.controller';
import { ClientService } from './client.service';

@Module({
  imports: [AuthModule],
  controllers: [ClientController],
  providers: [ClientService, PrismaService],
})
export class ClientModule { }
