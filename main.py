"""---"""
from os import system
from json import loads, dumps

from ecomm import Postgres

QUERY = '''
SELECT
	produto.produto as titulo,
	produto.codpro as codigo_interno,
    produto.codpro as sku,
	tb_multiplo.multiplo,
	ROUND(prd_tipo.p_venda * 1.35504, 2) as vl_uni,
	ROUND(prd_tipo.p_venda * 1.35504 * tb_multiplo.multiplo::int, 2) as vl_total,
	ROUND(tb_estoque.estoque / tb_multiplo.multiplo::int) as estoque,
	prd_gtin.cd_barras as codigo_barras,
	original.num_orig as original
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
ON produto.codpro = original.codpro

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
        if df_aux.multiplo > 1:
            df_aux['sku'] = f'{df_aux.multiplo}X[{df_aux.codigo_interno}]'
        try:
            df_aux['original'] = ', '.join(set(df_db.original)) if len(df_db.original) > 1 else ''
        except TypeError:
            df_aux['original'] = ''
    return df_aux


if __name__ == '__main__':
    system('cls')
    while True:
        cod = input('\nDigite o CODPRO (Codigo interno do produto): ').strip()
        if cod.isnumeric():
            result = re(QUERY, cod).to_json()
            parsed = loads(result)
            print(dumps(parsed, indent=4))
            input('\nPressione qualquer tecla para continuar...')

        system('cls')
