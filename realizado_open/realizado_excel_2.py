
import json
import getpass
import datetime
from tkinter import E
import excel_esforco
from myconfig import myconfig
from locale import LC_NUMERIC
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.select import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def logar(arquivo_json, arquivo_txt, lancamento):
    # loga informacoes em arquivo formato JSON
    with open(arquivo_json, 'a') as f:
        json.dump(lancamento, f, indent=4)
        f.write("\n")
    f.close()

    # loga informacoes em arquivo formato TXT
    with open(arquivo_txt, 'a') as f:
        salvar_log(f, lancamento)
    f.close()


def salvar_log(f, lancamento):
    f.write(f'{lancamento["log"]["datahora"]}')
    f.write(myconfig.get_config("config.separador_dados_txt"))
    f.write(f'{lancamento["log"]["mensagem"]}')
    f.write(f'{lancamento["log"]["retorno"]}')
    f.write(myconfig.get_config("config.separador_dados_txt"))
    f.write(f'data: {lancamento["lancamento"]["data"]}')
    f.write(myconfig.get_config("config.separador_dados_txt"))
    f.write(f'inicio: {lancamento["lancamento"]["inicio"]}')
    f.write(myconfig.get_config("config.separador_dados_txt"))
    f.write(f'fim: {lancamento["lancamento"]["fim"]}')
    f.write(myconfig.get_config("config.separador_dados_txt"))
    f.write(f'projeto: {lancamento["lancamento"]["projeto"]}')
    f.write(myconfig.get_config("config.separador_dados_txt"))
    f.write(f'atividade: {lancamento["lancamento"]["atividade"]}')
    f.write("\n")


row_list = excel_esforco.get_lancamentos_planilha(
    myconfig.get_config("config.realizado.XLSX"),
    myconfig.get_config("config.planilha"),
    myconfig.get_config("config.tabela"),
    myconfig.get_config("config.colunas_realizado")
)


# recupera usuário e senha do arquivo de configuraçãp
service_user = myconfig.get_config("config.service_user")
service_pwd = myconfig.get_config("config.service_pwd")

# solicita a digitação do usuário e senha
print("Usuário: ")
service_user = input()
service_pwd = getpass.getpass()


print(f'Qtd lançamentos encontrados: {len(row_list) - 1}')

# inicializa componentes e abre tela de realizado, que manda para o login
driver = webdriver.Chrome()
driver.maximize_window()
driver.implicitly_wait(5)
driver.get(myconfig.get_config("config.url_service"))

# recupera campos para login
username = driver.find_element(by=By.NAME, value="P101_USERNAME")
pwd = driver.find_element(by=By.NAME, value="P101_PASSWORD")
conectar = driver.find_element(by=By.ID, value="P101_LOGIN")

# informa dados de login
username.send_keys(service_user)
pwd.send_keys(service_pwd)
conectar.click()

line_count = 0
sucesso_count = 0
erro_count = 0

# itera cada linha de lançamento da lista de linhas recuperadas da planilha
for linha in row_list:
    if line_count > 0:

        print(f'Data do lançamento: {linha[1]}')

        # referência para janela atual
        janela_atual = driver.window_handles[0]

        try:
            # dicionario com dados do lancamento
            lancamento = {
                "lancamento": {
                    "data": datetime.datetime.strftime(linha[1], "%d/%m/%Y"),
                    "inicio": datetime.time.strftime(linha[2], "%H:%M")[:2]
                    + datetime.time.strftime(linha[2], "%H:%M")[3:5],
                    "fim": datetime.time.strftime(linha[3], "%H:%M")[:2]
                    + datetime.time.strftime(linha[3], "%H:%M")[3:5],
                    "projeto": linha[4],
                    "atividade": linha[5],
                    "descricao": linha[6],
                }
            }
        except Exception as e:
            # adiciona informacoes do alert para o log de erros
            lancamento = {
                "log": {
                    "datahora": datetime.datetime.now().strftime(
                        "%Y/%m/%d %H:%M:%S.%f"
                    ),
                    "mensagem": f"ERRO ao carregar lançamento número: {str(line_count)}",
                    "retorno": f"Verifique o lançamento número: {str(line_count)}",
                },
                "lancamento": {
                    "data": datetime.datetime.now().strftime("%d/%m/%Y"),
                    "inicio": datetime.datetime.now().strftime("%H:%M"),
                    "fim": datetime.datetime.now().strftime("%H:%M"),
                    "projeto": f"Verifique o lançamento número: {str(line_count)}",
                    "atividade": f"Verifique o lançamento número: {str(line_count)}",
                    "descricao": f"Verifique o lançamento número: {str(line_count)}",
                },
            }

            # regista informacoes no log de erros
            logar(myconfig.get_config("config.log_erro_json"), myconfig.get_config(
                "config.log_erro_txt"), lancamento)
            erro_count += 1
            line_count += 1
            continue

        print(f'Lancamento: {lancamento["lancamento"]}')

        dia_lanc = lancamento["lancamento"]["data"].split("/")[0]

        # lança apenas os dias indicados (data inicial e final) ou um único dia
        # if int(dia_lanc) >= 26 and int(dia_lanc) <= 27:
        if int(dia_lanc) == 4:

            # driver.implicitly_wait(15)
            inicio = driver.find_element(by=By.NAME, value="P100_HORINICIO")
            data = driver.find_element(by=By.NAME, value="P100_DATAESFORCO")

            if data.get_attribute("value") != lancamento["lancamento"]["data"]:
                # envia a data
                actions = ActionChains(driver)
                actions.send_keys_to_element(
                    data, Keys.HOME + Keys.DELETE * 11)
                actions.send_keys_to_element(
                    data, lancamento["lancamento"]["data"])
                actions.perform()
                driver.implicitly_wait(10)
                driver.switch_to.window(janela_atual)

            inicio.click()

            # recupera campos do realizado
            descricao = driver.find_element(by=By.NAME, value="P100_DESCRICAO")
            projeto_element = driver.find_element(
                By.NAME, 'P100_PROJETOUSUARIO')
            projeto = Select(projeto_element)
            # seleciona o projeto do lançamento
            # caso não exista, volta para o início do for
            try:
                projeto.select_by_value(lancamento["lancamento"]["projeto"])
            except Exception as e:
                lancamento["log"] = {
                    "datahora": datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f"),
                    "mensagem": "ERRO: Projeto não encontrado: ",
                    "retorno": ""
                }

                # regista erro no log de erros
                logar(myconfig.get_config("config.log_erro_json"), myconfig.get_config(
                    "config.log_erro_txt"), lancamento)

                # inicio.clear()
                # fim.clear()
                erro_count += 1
                line_count += 1
                continue

            # driver.implicitly_wait(2)
            atividade_element = driver.find_element(
                By.NAME, 'P100_SEQORDEMSERVICO')
            atividade = Select(atividade_element)

            data = driver.find_element(by=By.NAME, value="P100_DATAESFORCO")
            salvar = driver.find_element(by=By.ID, value="B788316930202301159")

            inicio = driver.find_element(by=By.NAME, value="P100_HORINICIO")
            # driver.implicitly_wait(15)
            inicio.clear()
            # verifica se o valor da hora de início no formulário é igual
            # ao valor da hora de início da planilha e só sai do loop quando forem iguais.
            # Motivo: existe uma validação javascript que complica demais a inserção do valor correto
            # while inicio.get_attribute("value") == "" or inicio.get_attribute("value") == "00:00":
            while (inicio.get_attribute("value")[:2] + inicio.get_attribute("value")[3:]) != lancamento["lancamento"]["inicio"]:
                driver.implicitly_wait(1)
                inicio.send_keys(lancamento["lancamento"]["inicio"])

            fim = driver.find_element(by=By.NAME, value="P100_HORFIM")
            # driver.implicitly_wait(15)
            fim.clear()
            # verifica se o valor da hora fim no formulário é igual
            # ao valor da hora fim da planilha e só sai do loop quando forem iguais.
            # Motivo: existe uma validação javascript que complica demais a inserção do valor correto
            # while fim.get_attribute("value") == "" or fim.get_attribute("value") == "00:00":
            while (fim.get_attribute("value")[:2] + fim.get_attribute("value")[3:]) != lancamento["lancamento"]["fim"]:
                driver.implicitly_wait(1)
                fim.send_keys(lancamento["lancamento"]["fim"])

            # driver.implicitly_wait(5)

            # driver.implicitly_wait(15)
            descricao.clear()
            while descricao.get_attribute("value") != lancamento["lancamento"]["descricao"]:
                descricao.send_keys(lancamento["lancamento"]["descricao"])

            # driver.implicitly_wait(15)

            # seleciona a atividade do lançamento
            # caso não exista, volta para o início do for
            try:
                atividade.select_by_value(
                    str(lancamento["lancamento"]["atividade"]))
            except Exception as e:
                lancamento["log"] = {
                    "datahora": datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f"),
                    "mensagem": "ERRO: Atividade não encontrada: ",
                    "retorno": ""
                }

                # regista erro no log de erros
                logar(myconfig.get_config("config.log_erro_json"), myconfig.get_config(
                    "config.log_erro_txt"), lancamento)

                erro_count += 1
                line_count += 1
                continue

            # driver.implicitly_wait(20)

            # verifica se algum alerta foi lançado
            # Sim - gera log com msg do alerta e daodos que o causaram
            try:
                # salva os dados
                salvar.click()
                WebDriverWait(driver, 2).until(EC.alert_is_present())
                # switch_to.alert for switching to alert and accept
                alert = driver.switch_to.alert
                text = alert.text
                alert.accept()

                # adiciona informacoes do alert para o log de erros
                lancamento["log"] = {
                    "datahora": datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f"),
                    "mensagem": "ERRO: Alert disparado: ",
                    "retorno": text
                }

                # regista informacoes no log de erros
                logar(myconfig.get_config("config.log_erro_json"), myconfig.get_config(
                    "config.log_erro_txt"), lancamento)
                erro_count += 1
                # driver.implicitly_wait(100)

            except TimeoutException:
                # print("alert does not Exist in page")
                lancamento["log"] = {
                    "datahora": datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f"),
                    "mensagem": "Sucesso!",
                    "retorno": "TimeOutException"
                }
                # registra sucesso no log de sucesso
                logar(myconfig.get_config("config.log_sucesso_json"), myconfig.get_config(
                    "config.log_sucesso_txt"), lancamento)
                sucesso_count = sucesso_count + 1

                # driver.implicitly_wait(5)

    line_count += 1


print(f'Total de lançamentos processados: {line_count - 1}')
print(f'Sucesso: {sucesso_count}')
print(f'Erro: {erro_count}')
if erro_count > 0:
    print(f'Log de erros: {myconfig.get_config("config.log_erro_txt")}')
# print(f'Configuracoes: {configuracoes}')

driver.implicitly_wait(100)
driver.close()
driver.quit()
