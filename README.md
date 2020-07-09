# Multiplos Acessos ao Ambiente Seguro (Sefaz-CE)
Projeto criado para permitir o acesso "**simultâneo**" de **múltiplos usuários** ao Ambiente Seguro da Sefaz-CE.
> **Obs:** É necessário um unico login de acesso do tipo **Contador**(3) valido ao portal.

## Tecnologias
1. Python (**3.7.4**)
   > `selenium`  `pyinstaller`
   
3. ChromeDriver (**83.0.4103.39**)

## Cofiguracao e uso
1. Instale os modulos necessarios
> python3 -m pip install -r requirements.txt
2. Entre na pasta drivers e edite o arquivo `credenciais.txt`, colocando seus dados de acesso ao portal
3. Execute o script
> python3 AmbienteSeguro.py

## Criar executavel (**x86**) com pyinstaller
> **DIRETORIO_BASE_DO_PYTHON**\Scripts\pyinstaller.exe --onefile AmbienteSeguro.py


