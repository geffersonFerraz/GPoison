import asyncio
from fileinput import filename
from re import sub
from shelve import Shelf
import subprocess
import os
import sys
import requests
import json
import uuid
import pystray
from pystray import _gtk
import PIL.Image
import re
from datetime import date
import dateutil.parser
from pathlib import Path
import shutil


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


image = PIL.Image.open(resource_path("icon.png"))

##
# pyinstaller --onefile --add-data "icon.png:." GPoison.py --key
##


def getGatewayGPD0():
    result = subprocess.check_output(
        "ip route | grep gpd0 | awk '{print $3}'", shell=True).decode('utf-8')
    result = result.split('\n')
    if len(result) >= 1:
        result = result[0]
        return result
    else:
        sendMessage('VPN ainda não conectada!')
        return None


async def removeDefault(gatewayGpd0):
    if gatewayGpd0 != None:
        try:
            await subprocess.run(
                'sudo route del -net 0.0.0.0        gw {gateway} netmask 0.0.0.0       dev gpd0  > /dev/null 2>&1'.format(gateway=gatewayGpd0), shell=True)
        except:
            err = 1  # do nothing...
        try:
            await subprocess.run(
                'sudo route del -net 10.0.0.150        gw {gateway} netmask 255.255.255.255       dev gpd0  > /dev/null 2>&1'.format(gateway=gatewayGpd0), shell=True)
        except:
            err = 1  # do nothing...

        try:
            await subprocess.run(
                'sudo route del -net 10.0.0.151        gw {gateway} netmask 255.255.255.255       dev gpd0  > /dev/null 2>&1'.format(gateway=gatewayGpd0), shell=True)
        except:
            err = 1  # do nothing...
        print('Rotas default eliminadas. Continuando...')


async def getRoutes():
    # COLETA ROTAS GPD0 EXISTENTES
    try:
        routes = subprocess.check_output(
            'route -n -e | grep gpd0', shell=True).decode('utf-8')
        return routes.splitlines()
    except:
        sendMessage('Aguardando conexão da VPN.')


async def sudoTest():
    # TESTA SUDO
    try:
        if not 'SUDO_UID' in os.environ.keys():
            raise Exception('Execute com SUDO!')
    except:
        sendMessage('Execute a aplicação com SUDO')
        sys.exit(0)


async def seedAndDestroy():
    # LOCALIZA E FINALIZA PROCESSO DO GP
    try:
        try:
            await subprocess.Popen('kill $(pidof PanGPUI) > /dev/null 2>&1', shell=True)
            print('Processo PanGPUI finalizado. Continuando...')
        except:
            err = 0
    except:
        print('Processo não encontrado. Continuando...')


def justNumbers(string1):
    numsStr1 = re.sub('[^0-9]', '', string1)
    return int(numsStr1)


def calcSerial(jusNumber):
    Str1 = str(jusNumber)
    firstChar = Str1[0]
    today = date.today()
    dayIs = '{month}{day}'.format(
        month=int(today.strftime("%m")), day=int(today.strftime("%d")))
    result = Str1.replace(firstChar, dayIs, 1)
    return int(result)


async def sendNameWhoRun():
    urlServer = "https://gpoison.geff.ws/client"
    localSerial = getMachine_addr()
    # localSerial = '29RQ973BRCMJ0009N0073'
    # mock1 = '29RQ973BRCMJ0009N0073'
    # mock2 = '0xc91a509c6c35'
    # payload = json.dumps({"serial": mock1, "serial2": mock2})
    payload = json.dumps({"serial": localSerial})
    headers = {'Content-Type': 'application/json'}
    resultIs = ''
    try:
        response = requests.request(
            "GET", urlServer, headers=headers, data=payload)
        resultIs = json.loads(response.content.decode('utf-8'))['result']
        expireAt = json.loads(response.content.decode('utf-8'))['expireAt']
    except:
        err = 2

    if resultIs == '':
        sendMessage(
            'Falha ao conectar ao servidor de licença. Procure ajuda...')
        # sys.exit(0)
    else:
        print(resultIs)
        if resultIs > 0:
            myNum = justNumbers(localSerial)
            print(myNum)
            # myNum = justNumbers(mock1, mock2)
            mySer = calcSerial(myNum)
            print(mySer)
            if resultIs == mySer:
                xpto = dateutil.parser.isoparse(
                    expireAt).strftime("%d/%m/%Y, %H:%M:%S")
                sendMessage('Licença expira em: {data}'.format(data=xpto))
                return xpto
        sendMessage('Cliente não autorizado a executar. Procure ajuda...')
    return None


async def validatePanGPA():
    try:
        resultGpa = subprocess.check_output(
            'pidof PanGPA', shell=True).decode('utf-8')
        if resultGpa == '':
            raise Exception('Iniciando PanGPA...')
    except:
        await subprocess.run('/opt/paloaltonetworks/globalprotect/PanGPA start > /dev/null 2>&1', shell=True, user=os.getlogin())


async def runPanGPUI():
    try:
        await subprocess.Popen(['/opt/paloaltonetworks/globalprotect/PanGPUI', 'start', 'from-cli'], shell=True, user=os.getlogin())
    except:
        err = 1


def getIPListFileName():
    homeDir = os.path.expanduser('~')
    fullFile = "{dir}/GPoisonIPList.txt".format(dir=homeDir)
    return fullFile


def sendMessage(message):
    print(message)
    subprocess.Popen(['notify-send', message])


async def getIpList():
    fullFile = getIPListFileName()

    IPs = []
    try:
        with open(fullFile, "r") as f:
            IPs = f.readlines()
    except:
        open(fullFile, "w+")

    ipList = []
    for ip in IPs:
        ipList.append(str(ip).replace('\n', ''))

    return ipList


def getMachine_addr():

    os_type = sys.platform.lower()

    if "darwin" in os_type:
        command = "ioreg -l | grep IOPlatformSerialNumber"
    elif "win" in os_type:
        command = "wmic bios get serialnumber"
    elif "linux" in os_type:
        command = "dmidecode -s baseboard-serial-number"
    serial = os.popen(command).read().replace("\n", "").replace(
        "  ", "").replace(" ", "").replace('/', '').replace('\\', '')
    # print(serial)
    return serial


async def createNewRoutes(poisonIP, gatewayGpd0):
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
                'sudo route add -net {ip}    gw {gateway} netmask {netmask}   dev gpd0 metric 600 > /dev/null 2>&1'.format(gateway=gatewayGpd0, ip=ip, netmask=mask), shell=True)
        except:
            err = 1  # do nothing...
    try:
        subprocess.run(
            'sudo route add -net 10.0.0.151    gw {gateway} netmask 255.255.255.255 dev gpd0 metric 600 > /dev/null 2>&1'.format(gateway=gatewayGpd0), shell=True)
    except:
        err = 1  # do nothing...
    try:
        subprocess.run(
            'sudo route add -net 10.0.0.150    gw {gateway} netmask 255.255.255.255 dev gpd0 metric 600 > /dev/null 2>&1'.format(gateway=gatewayGpd0), shell=True)
    except:
        err = 1  # do nothing...


async def createDefaultRoutes():
    gatewayGpd0 = getGatewayGPD0()
    sendMessage('Aguarde...')
    try:
        subprocess.run(
            'sudo route add -net 0.0.0.0 gw {gateway} netmask 0.0.0.0   dev gpd0 metric 0 > /dev/null 2>&1'.format(gateway=gatewayGpd0), shell=True)
    except:
        err = 1  # do nothing...

    sendMessage('VPN full =(')


async def checkVPNConnected():
    routesLines = []
    while (not routesLines or len(routesLines) == 0):
        await asyncio.sleep(10)
        routesLines = await getRoutes()
    return routesLines


async def poisonerSub():
    sendMessage('Aguarde...')

    result = await sendNameWhoRun()
    if result != None:
        poisonIP = await getIpList()

        if len(poisonIP) == 0:
            sendMessage('Lista de IPs vazia. Preencha em "Lista de IPs"')
        else:
            await checkVPNConnected()
            gatewayGpd0 = getGatewayGPD0()
            await removeDefault(gatewayGpd0)
            await createNewRoutes(poisonIP, gatewayGpd0)
            sendMessage('VPN Splitada =)')


async def poisoner():
    await sudoTest()
    print('Validando processos do GlobalProtect')
    poisonIP = await getIpList()

    if len(poisonIP) == 0:
        sendMessage('Lista de IPs vazia. Preencha em "Lista de IPs"')
    else:
        await validatePanGPA()
        await seedAndDestroy()
        await runPanGPUI()
        await poisonerSub()


def on_run_vpn(icon, item):
    asyncio.run(poisoner())


def on_exit(icon, item):
    sys.exit(0)


def on_editIpList(icon, item):
    asyncio.run(getIpList())
    fileName = getIPListFileName()

    subprocess.run(
        'sudo gnome-terminal -x nano {file}'.format(file=fileName), shell=True)


def on_vpn_full(icon, item):
    asyncio.run(createDefaultRoutes())


def on_vpn_split(icon, item):
    asyncio.run(poisonerSub())


def on_valide_lic(icon, item):
    asyncio.run(sendNameWhoRun())


def on_client_info(icon, item):
    result = getMachine_addr()
    xMessage = '{S1}'.format(S1=result)
    try:
        requests.post(
            'https://api.telegram.org/token-expiradoU/sendMessage?chat_id=-1001851963351&text=Usuario: {msg}'.format(msg=xMessage))
    except:
        err = 1
    sendMessage(xMessage)


icon = pystray.Icon("GPoison", image, menu=pystray.Menu(
    pystray.MenuItem("Iniciar GlobalProtect", on_run_vpn),
    pystray.MenuItem("Split VPN", on_vpn_split),
    pystray.MenuItem("VPN Full", on_vpn_full),
    pystray.MenuItem("Lista de IPs", on_editIpList),
    pystray.MenuItem("Exibir Client Infos", on_client_info),
    pystray.MenuItem("Validar licenca", on_valide_lic),
    pystray.MenuItem("Exit", on_exit)
), kwargs=_gtk)


# if len(sys.argv) <= 1:
#     print('Olá, iniciarei a minha instalação...')
#     home = str(Path.home())
#     itsMe = (sys.argv[0]).replace('./', '')
#     file_name = os.getcwd() + os.sep + itsMe

#     itsSH = itsMe.replace('py', 'sh')
#     file_sh_name = os.getcwd() + os.sep + itsSH

#     file_icon_name = os.getcwd() + os.sep + 'icon.png'

#     f = open(file_sh_name, "w+")
#     f.writelines(['sudo {file} -run &'.format(file=file_name)])
#     f.close()

#     f = open("/usr/share/applications/gpoison.desktop", "w+")
#     f.writelines(['[Desktop Entry]\n',
#                  'Name=GPoison\n',
#                   'Type=Application\n',
#                   'Comment=GPoison Desktop\n',
#                   'GenericName=GPoison for Linux\n',
#                   'Exec=sudo sh {file}\n'.format(file=file_sh_name),
#                   'Icon={file}\n'.format(file=file_icon_name),
#                   'Terminal=true\n',
#                   'Categories=GNOME;GTK;Network;\n']
#                  )
#     f.close()

#     print('Processo finalizado, as próximas vezes voce pode abrir utilizando o atalho do seu S.O.')
#     sys.exit(0)


icon.run()
