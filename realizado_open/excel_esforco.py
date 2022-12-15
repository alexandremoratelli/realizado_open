import openpyxl
import pprint
from realizado.myconfig import myconfig


def get_colunas_realizado(letra_inicial, letra_final):
    alfabeto = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L',
                'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    #dif = alfabeto.index(letra_final) - alfabeto.index(letra_inicial)
    colunas = ""
    for i in range(alfabeto.index(letra_final) - alfabeto.index(letra_inicial) + 1):
        colunas = colunas + alfabeto[i]
    #print(f'Dif: {dif}')
    print(f'Colunas: {colunas}')
    return colunas


def get_lancamentos_planilha(arquivo_xlsx, sheet_name, nome_tabela, colunas_realizado):

    print('Abrindo planilha...')
    wb = openpyxl.load_workbook(arquivo_xlsx, data_only=True)
    sheet = wb[sheet_name]

    ref_tab_esforco = sheet.tables[nome_tabela].ref.split(":")

    linha_inicial = int(ref_tab_esforco[0][1:])
    linha_final = int(ref_tab_esforco[1][1:]) - 1

    row_list = []
    print('Lendo linhas da planilha...')
    for row in range(linha_inicial, linha_final + 1):
        # Each row in the spreadsheet has data for one census tract.
        dados_sheet = {}
        dados_list = []
        processar = True
        for nome_col in colunas_realizado:
            if nome_col == "A":
                processar = (
                    sheet[nome_col + str(row)].value != "S"
                    and sheet[nome_col + str(row)].value is not None
                )
            if processar:
                dados_sheet[nome_col +
                            str(row)] = sheet[nome_col + str(row)].value
                dados_list.append(sheet[nome_col + str(row)].value)

        if processar:
            row_list.append(dados_list)

    wb.close()
    return row_list


if __name__ == "__main__":
    row_list = get_lancamentos_planilha(
        myconfig.get_config("config.realizado.XLSX"),
        myconfig.get_config("config.planilha"),
        myconfig.get_config("config.tabela"),
        myconfig.get_config("config.colunas_realizado")
    )

    # Open a new text file and write the contents of countyData to it.
    print('Writing results...')
    with open('log/lancamentos.txt', 'w') as result_file:
        result_file.write(f'allData = {pprint.pformat(row_list)}')
    print('Done.')
