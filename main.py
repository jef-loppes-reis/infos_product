"""---"""
from os import system, path
from json import loads, dumps

from ecomm import Postgres
from psycopg import OperationalError
from pandas import DataFrame
from rich import print as rprint, print_json


class InfosProduct:

    with open(
        file=path.join(path.dirname(__file__), 'data/sql/query.sql'),
        mode='r',
        encoding='utf-8'
    ) as fp:
        _query_archive: str = fp.read()

    def __init__(self, codpro_sku: str) -> None:
        self._codpro_sku: str = codpro_sku


    def get_query(self, type_op_codpro: bool) -> str:
        _query: str = self._query_archive%('codpro', self._codpro_sku)
        _query = _query.replace(
            "WHERE produto.'codpro'",
            'WHERE produto.codpro'
        ) if type_op_codpro else _query.replace(
                "WHERE produto.'codpro'",
                'WHERE produto.num_fab'
            )

        return _query


    def re(self) -> DataFrame:
        """_summary_

        Args:
            query (str): _description_
            codpro (str): _description_

        Returns:
            str: _description_
        """
        with Postgres() as db:
            # Tentativa com CODPRO
            df_db: DataFrame = db.query(self.get_query(type_op_codpro=True))
            if not df_db.empty:
                df_aux: DataFrame = df_db.loc[0].copy()
                df_aux['tipo_anuncio'] = None
                df_aux['tipo_anuncio'] = 'CLASSICO' if df_aux.vl_total < 41 else 'PREMIUM'
                df_aux['oem'] = ', '.join(set(df_db.oem)) if len(df_db.oem) > 1 else ''
                return df_aux
            # Tentativa com NUM_FAB
            df_db: DataFrame = db.query(self.get_query(type_op_codpro=False))
            if not df_db.empty:
                df_aux: DataFrame = df_db.loc[0].copy()
                df_aux['tipo_anuncio'] = None
                df_aux['tipo_anuncio'] = 'CLASSICO' if df_aux.vl_total < 41 else 'PREMIUM'
                df_aux['oem'] = ', '.join(set(df_db.oem)) if len(df_db.oem) > 1 else ''
                return df_aux
            # Caso nada retorna vazio
            return DataFrame()


if __name__ == '__main__':
    # system('cls')

    while True:
        cod: str = input('\nDigite o CODPRO ou SKU: ').strip()
        try:
            infos_product: InfosProduct = InfosProduct(codpro_sku=cod)
            result: dict = infos_product.re().to_json()
            parsed: dict = loads(result)
            print_json(dumps(parsed, indent=4))
            rprint('[bright_yellow]Pressione ENTER para continuar...[/bright_yellow]')
            input()
        except OperationalError:
            rprint('[red3]Algo de errado, com a conexao com o BD. Tente novamente mais tarde ![/red3]')
            input('[bright_yellow]Precione ENTER para sair...[/bright_yellow]')
