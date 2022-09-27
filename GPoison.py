import asyncio
import subprocess
import os


async def removeDefault(gateway):
    # REMOVE ROTAS DEFAULT
    try:
        await subprocess.run(
            'sudo route del -net 0.0.0.0        gw {gateway} netmask 0.0.0.0       dev gpd0  > /dev/null 2>&1'.format(gateway=gateway), shell=True)
    except:
        err = 1  # do nothing...
    try:
        await subprocess.run(
            'sudo route del -net 10.0.0.150        gw {gateway} netmask 255.255.255.255       dev gpd0  > /dev/null 2>&1'.format(gateway=gateway), shell=True)
    except:
        err = 1  # do nothing...

    try:
        await subprocess.run(
            'sudo route del -net 10.0.0.151        gw {gateway} netmask 255.255.255.255       dev gpd0  > /dev/null 2>&1'.format(gateway=gateway), shell=True)
    except:
        err = 1  # do nothing...
    print('Rotas default eliminadas. Continuando...')


async def getRoutes():
    # COLETA ROTAS GPD0 EXISTENTES
    try:
        routes = subprocess.check_output(
            'sudo route -n -e | grep gpd0', shell=True).decode('utf-8')
        return routes.splitlines()
    except:
        print('VPN ainda não conectada...')


async def sudoTest():
    # TESTA SUDO
    try:
        if not 'SUDO_UID' in os.environ.keys():
            raise Exception('errow')
    except:
        print('Execute o script com SUDO')
        exit(0)


async def seedAndDestroy():
    # LOCALIZA E FINALIZA PROCESSO DO GP
    try:
        try:
            await subprocess.run('sudo kill $(pidof PanGPUI) > /dev/null 2>&1', shell=True)
            # await subprocess.run('sudo kill $(pidof PanGPA) > /dev/null 2>&1', shell=True)
            print('Processo PanGPUI finalizado. Continuando...')
        except:
            print('Falha ao finalizar Processo PanGPUI. Continuando...')
    except:
        print('Processo não encontrado. Continuando...')


async def poisoner(poisonIPs):
    await sudoTest()
    await seedAndDestroy()

    try:
        print('Iniciando GlobalProtect. Aguardando conexão...')
        # await subprocess.Popen('/opt/paloaltonetworks/globalprotect/PanGPA start > /dev/null 2>&1', shell=True, user=os.getlogin())
        await subprocess.Popen('/opt/paloaltonetworks/globalprotect/PanGPUI start from-cli > /dev/null 2>&1', shell=True, user=os.getlogin())
    except:
        err = 1

    routesLines = []
    while (not routesLines or len(routesLines) == 0):
        await asyncio.sleep(10)
        routesLines = await getRoutes()

    routesLines = await getRoutes()
    gateway = ''
    if routesLines and len(routesLines) > 0:
        for line in routesLines:
            if '0.0.0.0' in line:
                line = line.removeprefix('0.0.0.0         ')
                lineSlited = line.split()
                gateway = lineSlited[0]
                await removeDefault(gateway)

    for ip in poisonIPs:
        mask = ''
        ipSplit = ip.split('.')
        for part in ipSplit:
            if mask == '':
                mask = '255'
            else:
                if int(part) > 0:
                    mask = '{masks}.255'.format(masks=mask)
                else:
                    mask = '{masks}.0'.format(masks=mask)
        try:
            subprocess.run(
                'route add -net {ip}    gw {gateway} netmask {netmask}   dev gpd0 metric 600 > /dev/null 2>&1'.format(gateway=gateway, ip=ip, netmask=mask), shell=True)
        except:
            err = 1  # do nothing...

    print(''' 
      Special thanks to @panngo
    
 /$$    /$$ /$$$$$$$  /$$   /$$       /$$$$$$$  /$$$$$$$$  /$$$$$$  /$$$$$$$  /$$     /$$
| $$   | $$| $$__  $$| $$$ | $$      | $$__  $$| $$_____/ /$$__  $$| $$__  $$|  $$   /$$/
| $$   | $$| $$  \ $$| $$$$| $$      | $$  \ $$| $$      | $$  \ $$| $$  \ $$ \  $$ /$$/ 
|  $$ / $$/| $$$$$$$/| $$ $$ $$      | $$$$$$$/| $$$$$   | $$$$$$$$| $$  | $$  \  $$$$/  
 \  $$ $$/ | $$____/ | $$  $$$$      | $$__  $$| $$__/   | $$__  $$| $$  | $$   \  $$/   
  \  $$$/  | $$      | $$\  $$$      | $$  \ $$| $$      | $$  | $$| $$  | $$    | $$    
   \  $/   | $$      | $$ \  $$      | $$  | $$| $$$$$$$$| $$  | $$| $$$$$$$/    | $$    
    \_/    |__/      |__/  \__/      |__/  |__/|________/|__/  |__/|_______/     |__/                                                                                                 
''')


poisonTarget = ['35.0.0.0',
                '10.0.0.0'
                ]


async def main():
    await poisoner(poisonTarget)

if __name__ == '__main__':
    asyncio.run(main())
