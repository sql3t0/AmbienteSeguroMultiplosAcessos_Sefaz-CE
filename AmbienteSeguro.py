# -*- coding: utf-8 -*-
import os
import sys
import time
import pickle
import psutil
import warnings
import selenium
from selenium import webdriver
from selenium.webdriver.support.ui import Select

warnings.filterwarnings('ignore')
# GLOBAL VALUES
DRIVER_PATH 	 = "./driver/chromedriver.exe"
COOKIE_PATH 	 = "./driver/cookies.pkl"
CREDENCIAIS_PATH = "./driver/credenciais.txt" # O formato do arquivo deve seguir o layout ( CPF:SENHA:TIPO ) em uma unica linha, separando os valores por ':'

def info(txt, breakline=True):
	if breakline:
		sys.stdout.write(txt+'\n')
	else:
		sys.stdout.write(txt)

def error(e):
	print(e)
	exc_type, exc_obj, exc_tb = sys.exc_info()
	fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
	print(exc_type, fname, exc_tb.tb_lineno)

def ForceCloseApp():
	PROCNAME = "chromedriver.exe"
	for proc in psutil.process_iter():
		if proc.name() == PROCNAME:
			proc.kill()

	PROCNAME = "AmbienteSeguro.exe"
	for proc in psutil.process_iter():
		if proc.name() == PROCNAME:
			proc.kill()

def save_cookies(browser):
	info('[>] Salvando Cookies...')
	try:
		pickle.dump(browser.get_cookies(), open(COOKIE_PATH,"wb"))
		info('[+] Cookies salvo com sucesso.')
	except Exception as e:
		error(e)

def readCookies(browser):
	info('[>] Carregando cookies no chrome...')
	try:
		browser.delete_all_cookies()
		cookies = pickle.load(open(COOKIE_PATH, "rb"))
		for cookie in cookies:
			browser.add_cookie(cookie)
		
		info('[+] Cookies carregados com sucesso.')
	except Exception as e:
		error(e)

	return browser

def submitForm(browser,inputIds, values, phanton):
	try:
		iduser , idsenha, idtipo, idbt  = inputIds
		vuser , vsenha, vtipo = values
		if phanton:
			info('[>] Ghost Login...')
		else:
			info('[>] Chrome Login...')

		fuser  = browser.find_element_by_id(iduser)
		fuser.clear()
		fuser.send_keys(vuser)
		fsenha = browser.find_element_by_id(idsenha)
		fsenha.clear()
		fsenha.send_keys(vsenha)
		ftipo  = Select(browser.find_element_by_id(idtipo))
		ftipo.select_by_value(vtipo)
		browser.find_element_by_id(idbt).send_keys(u'\ue007') #unicode for enter key
	except Exception as e:
		error(e)

def login(browser, phanton=False):
	status = False
	try:
		CPF, SENHA , TIPO = open(CREDENCIAIS_PATH).read().strip().split(':')
		URL_Login = 'https://servicos.sefaz.ce.gov.br/internet/AcessoSeguro/servicosenha/logarusuario/login.asp'
		URL_Loged = 'https://servicos.sefaz.ce.gov.br/internet/acessoSeguro/ServicoSenha/LogarUsuario/cweb2003.asp'
		browser.get(URL_Login)
		submitForm(browser, ['txtUsuario','txtSenha','cboTipoUsuario','btEntrar'],[CPF,SENHA,TIPO], phanton)
		body = browser.find_element_by_tag_name('body').text
		# print(body)
		if 'O usuário já está logado no sistema.' in body:
			info('[!] Outro usuario jah logado !')
			browser = readCookies(browser)
			try:
				browser.get(URL_Loged)
				if 'Clique aqui para voltar ao menu de Serviços.' in browser.find_element_by_tag_name('body').text:
					status = True
			except selenium.common.exceptions.UnexpectedAlertPresentException as e:
				info('[!] Outro usuario logado fora do App !')
				browser.execute_script("alert('[!] Outro usuario logado fora do App !');")
				time.sleep(3)
				status = False
				pass
		else:
			info('[+] Login realizado com sucesso.')
			save_cookies(browser)
			status = True

		return browser, status	
	except Exception as e:
		error(e)
		return False

def phantonBrownser(browser, empresa):
	try:
		if empresa:
			info('\r[>] Selecionando empresa...', False)
			browser.get("https://servicos.sefaz.ce.gov.br/internet/acessoSeguro/EMPRESASDOCPF/CWeb2010.Asp?SSE=1")
			try:
				browser.execute_script(empresa)
				info('\r[+] Empresa Selecioanda com sucesso.', False)
			except selenium.common.exceptions.UnexpectedAlertPresentException as e:
				# error(e)
				pass
	except Exception as e:
		error(e)
		pass

def setEmpOnLocalStorage(browser, storageKEY):
	try:

		if 'CWeb2010.Asp'.upper() in browser.current_url.upper():
			info('\r[>] Injetando JS para salvar empresa selecionada...', False)
			browser.execute_script("for(var i=0; i<document.links.length; i++) { if(document.links[i].href.includes('javascript:submete')){ document.links[i].setAttribute('onclick',\"localStorage.setItem('%s',this.href.replace('javascript:',''))\"); }}"%storageKEY)
	except Exception as e:
		# error(e)
		pass

def toggleBody(browser, value):
	try:
		browser.execute_script(f'document.body.style.display = "{value}";')
	except Exception as e:
		# error(e)
		pass

if __name__ == '__main__':
	try:
		storageKEY = os.environ['username'].upper().strip()

		# Opcoes do browserChrome
		info('[>] Iniciando Chrome Driver...')
		options = webdriver.ChromeOptions()
		options.add_argument('--log-level=3')
		options.add_argument('--disable-gpu')
		options.add_argument('--use-gl=desktop')
		options.add_argument("--disable-infobars")
		options.add_argument("--disable-extensions")
		options.add_argument("--proxy-bypass-list=*")
		options.add_argument("--proxy-server='direct://'")
		options.add_argument("--ignore-certificate-errors")
		options.add_experimental_option('excludeSwitches', ['enable-logging'])
		browserChrome = webdriver.Chrome(options=options, executable_path=DRIVER_PATH, service_args=["--silent",])

		# Opcoes do ghostBrowser
		info('[>] Iniciando Ghost Driver...')
		gOptions = webdriver.ChromeOptions()
		options.add_argument('--headless')
		ghostBrowser = webdriver.Chrome(options=options, executable_path=DRIVER_PATH, service_args=["--silent",])


		browserChrome, status = login(browserChrome)
		if status:
			toggleBody(browserChrome,'none')
			ghostBrowser, status = login(ghostBrowser, 1)
			toggleBody(browserChrome,'block')
			# Checando se o usuario irah fechar o browserChrome no botao [X]
			url = browserChrome.current_url
			while True:
				setEmpOnLocalStorage(browserChrome, storageKEY)
				try:
					empresa = browserChrome.execute_script("return localStorage.getItem('%s');"%storageKEY)
					if browserChrome.current_url != url:
						info('\r[>] Nova URL carregada: ', False )
						toggleBody(browserChrome,'none') #hidden body
						url = browserChrome.current_url
						info(browserChrome.current_url)
						phantonBrownser(ghostBrowser, empresa)
						browserChrome.refresh()
						toggleBody(browserChrome,'block') #display body
				except selenium.common.exceptions.WebDriverException as e:
					info('\n[>] Encerrando Ghost Browser...')
					ghostBrowser.quit()
					# error(e)
					# pass
					break
			
			info('[>] Encerrando Chrome Browser...')
			ForceCloseApp()
		else:
			info('[>] Encerrando a aplicacao...')
			ghostBrowser.quit()
			browserChrome.quit()

	except Exception as e:
		error(e)
