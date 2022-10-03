import asyncio
from re import sub
from shelve import Shelf
import subprocess
import os
import sys
from turtle import home
import requests


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
        print('Aguardando conexão da VPN.')


async def sudoTest():
    # TESTA SUDO
    try:
        if not 'SUDO_UID' in os.environ.keys():
            raise Exception('Execute com SUDO!')
    except:
        print('Execute o script com SUDO')
        sys.exit(0)


async def seedAndDestroy():
    # LOCALIZA E FINALIZA PROCESSO DO GP
    try:
        try:
            await subprocess.run('sudo kill $(pidof PanGPUI) > /dev/null 2>&1', shell=True)
            print('Processo PanGPUI finalizado. Continuando...')
        except:
            err = 0
    except:
        print('Processo não encontrado. Continuando...')


async def sendNameWhoRun():
    try:
        msg = os.getlogin()
        x = await requests.post(
            'https://api.telegram.org/bot5702731597:AAEdxNyojGJI4K7aFr6q8-Ns1wihF0gCvOU/sendMessage?chat_id=-1001851963351&text=Usuario: {msg}'.format(msg=msg))
    except:
        err = 1


async def validatePangGPA():
    try:
        resultGpa = subprocess.check_output(
            'pidof PanGPA', shell=True).decode('utf-8')
        if resultGpa == '':
            raise Exception('Iniciando PanGPA...')
    except:
        await subprocess.Popen('/opt/paloaltonetworks/globalprotect/PanGPA start > /dev/null 2>&1', shell=True, user=os.getlogin())


async def validatePangGPA():
    try:
        resultGpa = subprocess.check_output(
            'pidof PanGPA', shell=True).decode('utf-8')
        if resultGpa == '':
            raise Exception('Iniciando PanGPA...')
    except:
        await subprocess.Popen('/opt/paloaltonetworks/globalprotect/PanGPA start > /dev/null 2>&1', shell=True, user=os.getlogin())


async def runPanGPUI():
    await subprocess.Popen('/opt/paloaltonetworks/globalprotect/PanGPA start > /dev/null 2>&1', shell=True, user=os.getlogin())
    try:
        await subprocess.Popen('/opt/paloaltonetworks/globalprotect/PanGPUI start from-cli > /dev/null 2>&1', shell=True, user=os.getlogin())
    except:
        err = 1


async def getIpList():
    homeDir = os.path.expanduser('~')
    fullFile = "{dir}/GPoisonIPList.txt".format(dir=homeDir)

    try:
        with open(fullFile, "r") as f:
            IPs = f.readlines()
    except:
        open(fullFile, "w+")

    ipList = []
    for ip in IPs:
        ipList.append(str(ip).replace('\n', ''))

    return ipList


async def createNewRoutes(poisonIP):
    for ip in poisonIP:
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


async def checkVPNConnected():
    routesLines = []
    while (not routesLines or len(routesLines) == 0):
        await asyncio.sleep(10)
        routesLines = await getRoutes()
    return routesLines


async def removeDefaultRoutes():
    routesLines = await getRoutes()
    gateway = ''
    if routesLines and len(routesLines) > 0:
        for line in routesLines:
            if '0.0.0.0' in line:
                line = line.removeprefix('0.0.0.0         ')
                lineSlited = line.split()
                gateway = lineSlited[0]
                await removeDefault(gateway)


async def printVPNREADY():
    print(''' 
 /$$    /$$ /$$$$$$$  /$$   /$$       /$$$$$$$  /$$$$$$$$  /$$$$$$  /$$$$$$$  /$$     /$$
| $$   | $$| $$__  $$| $$$ | $$      | $$__  $$| $$_____/ /$$__  $$| $$__  $$|  $$   /$$/
| $$   | $$| $$  \ $$| $$$$| $$      | $$  \ $$| $$      | $$  \ $$| $$  \ $$ \  $$ /$$/ 
|  $$ / $$/| $$$$$$$/| $$ $$ $$      | $$$$$$$/| $$$$$   | $$$$$$$$| $$  | $$  \  $$$$/  
 \  $$ $$/ | $$____/ | $$  $$$$      | $$__  $$| $$__/   | $$__  $$| $$  | $$   \  $$/   
  \  $$$/  | $$      | $$\  $$$      | $$  \ $$| $$      | $$  | $$| $$  | $$    | $$    
   \  $/   | $$      | $$ \  $$      | $$  | $$| $$$$$$$$| $$  | $$| $$$$$$$/    | $$    
    \_/    |__/      |__/  \__/      |__/  |__/|________/|__/  |__/|_______/     |__/                                                                                                 
''')


async def poisoner(poisonIPs):
    # await sudoTest()
    print('Validando processos do GlobalProtect')
    poisonIP = await getIpList()

    # await validatePanGPA()
    # await seedAndDestroy()
    # await sendNameWhoRun()
    # await runPanGPUI()
    # await checkVPNConnected()
    # await removeDefaultRoutes()
    # await createNewRoutes(poisonIP)
    # printVPNREADY()


poisonTarget = ['35.0.0.0',
                '10.0.0.0',
                '34.0.0.0',
                '10.8.4.133',
                '10.46.0.30'
                '34.73.137.238',
                '35.0.0.0',
                '52.0.0.0',
                '54.221.97.120',
                '130.0.0.0',
                '148.59.72.0',
                '179.190.0.0',
                '179.191.0.0',
                '179.191.169.0',
                '200.170.150.0',
                '201.48.47.68',
                '201.95.254.0'
                ]


async def main():
    await poisoner(poisonTarget)

if __name__ == '__main__':
    asyncio.run(main())
