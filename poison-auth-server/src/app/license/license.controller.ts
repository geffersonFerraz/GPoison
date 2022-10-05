import { Body, Controller, Get, Post, UseGuards } from '@nestjs/common';
import { JwtAuthGuard } from '../auth/guards/jwt-auth.guard';
import { IncrementLicense, ResultLicense } from './license.interface';
import { LicenseService } from './license.service';

@Controller()
export class LicenseController {
  constructor(private readonly licenseService: LicenseService) { }
  @UseGuards(JwtAuthGuard)
  @Post('/license')
  async extendLicense(@Body() postData: IncrementLicense): Promise<ResultLicense> {
    return this.licenseService.extendLicense(postData);
  }
}
