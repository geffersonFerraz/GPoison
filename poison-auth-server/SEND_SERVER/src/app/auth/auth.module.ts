import { Module } from '@nestjs/common';
import { JwtModule } from '@nestjs/jwt';
import { jwtConstants } from './constants';
import { JwtStrategy } from './strategies/jwt.strategy';

@Module({
    imports: [JwtModule.register({
        secret: jwtConstants.secret,
        signOptions: { expiresIn: '1h' },
    }),],
    providers: [JwtStrategy],
    controllers: [],
})
export class AuthModule { }