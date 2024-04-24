"""---"""
from os import system
from json import loads, dumps

from ecomm import Postgres
from print_cores import Cores

QUERY = '''
SELECT
	produto.produto as titulo,
	produto.codpro as codigo_interno,
    produto.codpro as sku,
	tb_multiplo.multiplo,
	ROUND(prd_tipo.p_venda * 1.35504, 2) as vl_uni,
	ROUND(prd_tipo.p_venda * 1.35504 * tb_multiplo.multiplo::int, 2) as vl_total,
	ROUND(tb_estoque.estoque::int / tb_multiplo.multiplo::int)::int as estoque,
	prd_gtin.cd_barras as codigo_barras,
	original.num_orig as oem
FROM "D-1".produto

INNER JOIN (SELECT codpro, CASE WHEN produto.embala = 0 THEN 1 ELSE produto.embala END as multiplo FROM "D-1".produto) as tb_multiplo
ON produto.codpro = tb_multiplo.codpro

LEFT JOIN "D-1".prd_tipo
ON produto.codpro = prd_tipo.codpro

LEFT JOIN (SELECT codpro, SUM(estoque) as estoque FROM "H-1".prd_loja GROUP BY codpro) as tb_estoque
ON produto.codpro = tb_estoque.codpro

LEFT JOIN "D-1".prd_gtin
ON produto.codpro = prd_gtin.cd_produto

LEFT JOIN "D-1".original
ON produto.num_orig = original.nu_origina

WHERE produto.codpro = '%s'
ORDER BY dt_cadast DESC
'''

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
        if df_aux.multiplo > 1:
            df_aux['sku'] = f'{df_aux.multiplo}X[{df_aux.codigo_interno}]'
        print(df_aux.vl_total)
        df_aux['tipo_anuncio'] = 'CLASSICO' if df_aux.vl_total < 41 else 'PREMIUM'
        try:
            df_aux['oem'] = ', '.join(set(df_db.oem)) if len(df_db.oem) > 1 else ''
        except TypeError:
            df_aux['oem'] = ''
    return df_aux


if __name__ == '__main__':
    system('cls')
    while True:
        cod = input(f'\n{Cores.SUBLINHADO}Digite o CODPRO (Codigo interno do produto):{Cores.RESET} ').strip()
        if cod.isnumeric():
            try:
                result = re(QUERY, cod).to_json()
                parsed = loads(result)
                print('')
                print(dumps(parsed, indent=4))
                input(f'\n{Cores.VERDE_CLARO}Pressione qualquer tecla para continuar...{Cores.RESET}')
            except KeyError:
                system('cls')
                print(f'\n{Cores.AMARELO}Codigo do produto nao encontrado!{Cores.RESET}')
