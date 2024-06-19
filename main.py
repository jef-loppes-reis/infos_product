"""---"""
from os import system, path
from json import loads, dumps

from ecomm import Postgres
from print_cores import Cores


def re(query:str, codpro:str) -> str:
    """_summary_

    Args:
        query (str): _description_
        codpro (str): _description_

    Returns:
        str: _description_
    """
    with Postgres() as db:
        df_db = db.query(query%codpro)
        df_aux = df_db.loc[0].copy()
        df_aux['tipo_anuncio'] = None
        # if df_aux.multiplo > 1:
        #     df_aux['sku'] = f'{df_aux.multiplo}X[{df_aux.codigo_interno}]'
        df_aux['tipo_anuncio'] = 'CLASSICO' if df_aux.vl_total < 41 else 'PREMIUM'
        try:
            df_aux['oem'] = ', '.join(set(df_db.oem)) if len(df_db.oem) > 1 else ''
        except TypeError:
            df_aux['oem'] = ''
    return df_aux


if __name__ == '__main__':
    system('cls')

    path_here = path.dirname(__file__)

    with open(path.join(path_here, 'data/sql/', 'query.sql'), 'r', encoding='utf-8') as fp:
        QUERY = fp.read()

    while True:
        cod = input(f'\n{Cores.SUBLINHADO}Digite o CODPRO (Codigo interno do produto):{Cores.RESET} ').strip()
        if cod.isnumeric():
            try:
                print('\nCarregando...')
                result = re(QUERY, cod).to_json()
                system('cls')
                parsed = loads(result)
                for title, item in parsed.items():
                    print(f'{Cores.ITALICO}{Cores.SUBLINHADO}{title.upper()}{Cores.RESET}: {item}')
                # print(dumps(parsed, indent=4))
                input(f'\n{Cores.VERDE_CLARO}Pressione qualquer tecla para continuar...{Cores.RESET}')
            except KeyError:
                system('cls')
                print(f'\n{Cores.AMARELO}Codigo do produto nao encontrado!{Cores.RESET}')
