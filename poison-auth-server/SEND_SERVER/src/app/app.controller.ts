import { Controller, Get, Header, HttpCode, HttpStatus, Redirect, Res, Response, StreamableFile, UseGuards } from '@nestjs/common';
import * as fs from 'node:fs'
import * as path from 'node:path';
import { AppService } from './app.service';
import { JwtAuthGuard } from './auth/guards/jwt-auth.guard';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) { }
  @Redirect('https://gpoison.gefferson.com.br', 301)
  @Get()
  getHello() {

  }
}
