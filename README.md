# GPoison
Save when u want.

Run with python >= 3.10 

$ python3 GPoison.py

Add new ips to create a vpn route at object poisonTarget [], ex:

```
poisonTarget = ['35.0.0.0',
                '10.0.0.0'
                ]

```

Be happy!
thnks @panngo


para gerar binario: 

```

 pyinstaller --onefile --add-data "/home/gefferson/git-hub/GPoison/icon.png:./icon.png" --icon "/home/gefferson/git-hub/GPoison/icon.ico" GPoison.py

```
