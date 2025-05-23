"""---"""
import signal
import sys
from json import dumps

from ecomm import Postgres
from psycopg import OperationalError
from pandas import DataFrame
from rich import print as rprint, print_json

from query import query_db

class InfosProduct:

    def __init__(self, codpro_sku: str) -> None:
        self._codpro_sku: str = codpro_sku

    def __definir_tarifa(self, valor: float) -> float:
        """
        definir_tarifa A regra e definiada com o valor do produto somado com a porcentagem 1.35504.
        Nao deve jogar somente o valor do "p_venda" Preco KAIZEN.

        Args:
            valor (float): Valor P_VENDA * 1.35504

        Returns:
            float: Taxa do produto.
        """
        if 0.48 <= valor < 6.25:
            return valor
        if 6.25 <= valor < 21.9:
            return 7.10
        if 21.9 <= valor < 42.61:
            return 7.39
        if 42.61 <= valor < 50.92:
            return 8.13
        return 0

    def __markup(self, tipo_anuncio: str = 'PREMIUM') -> float:
        match tipo_anuncio:
            case 'PREMIUM':
                return 1.35504
            case 'CLASSICO':
                return 1.27804
            case 'fulfillment':
                return 1.37504
            case 'gold_special_full':
                return 1.29804
            case _:
                return 1.35504

    def get_query(self, type_op_codpro: bool) -> str:
        _query: str = query_db % ('codpro', self._codpro_sku)
        _query = _query.replace(
            "WHERE produto.'codpro'",
            'WHERE produto.codpro'
        ) if type_op_codpro else _query.replace(
                "WHERE produto.'codpro'",
                'WHERE produto.num_fab'
            )
        return _query


    def re(self) -> dict:
        """_summary_

        Args:
            query (str): _description_
            codpro (str): _description_

        Returns:
            str: _description_
        """
        with Postgres() as db:
            df_db: DataFrame = db.query(self.get_query(type_op_codpro=bool(True) if self._codpro_sku.isnumeric() else False))
            if not df_db.empty:
                df_aux_data: dict = df_db.loc[[0]].squeeze().to_dict().copy()
                df_aux_data['vl_uni_siac'] = float(df_aux_data.get('vl_uni_siac', 0.0))
                df_aux_data['vl_total_siac'] = float(df_aux_data.get('vl_total_siac', 0.0))
                df_aux_data['tipo_anuncio'] = None
                df_aux_data['tipo_anuncio'] = 'CLASSICO' if df_aux_data.get('vl_total_siac', 0.0) < 41 else 'PREMIUM'
                df_aux_data['vl_ml'] = float(df_aux_data.get('vl_total_siac', 0.0)) * float(self.__markup(df_aux_data.get('tipo_anuncio', '')))
                df_aux_data['vl_ml'] = df_aux_data.get('vl_ml', 0.0) + self.__definir_tarifa(df_aux_data.get('vl_ml', 0.0))
                df_aux_data['vl_ml'] = round(df_aux_data.get('vl_ml', 0.0), 2)
                df_aux_data['oem'] = ', '.join(set(df_db.oem)) if not df_db.oem.loc[~df_db.oem.isna()].empty else '-'
                df_aux_data['codigo_barras'] = ', '.join(set(df_db.codigo_barras)) if not df_db.codigo_barras.loc[~df_db.codigo_barras.isna()].empty else '-'
                df_aux_data['sku'] = f'{df_db.multiplo.values[0]}X[{df_db.sku.values[0]}]' if int(df_db.multiplo.values[0]) > 1 else df_db.sku.values[0]
                return df_aux_data
            return {}

# Metodo Graceful Shutdown
SHUTDOWN_FLAG: bool = False

def signal_handler(sig, frame):
    global SHUTDOWN_FLAG
    rprint('[yellow]Recebido sinal para encerrar o programa. Finalizando...[/yellow]')
    SHUTDOWN_FLAG = True

if __name__ == '__main__':
    # Usp metodo Graceful Shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    while not SHUTDOWN_FLAG:
        try:
            cod: str = input('\nDigite o CODPRO ou SKU: ').strip()
            if SHUTDOWN_FLAG:
                break
            infos_product: InfosProduct = InfosProduct(codpro_sku=cod)
            result: dict = infos_product.re()
            print_json(dumps(result))
        except OperationalError:
            rprint('[red3]Algo de errado com a conexao com o BD. Tente novamente mais tarde ![/red3]')
        except KeyboardInterrupt:
            rprint('\n[yellow]Interrupção recebida pelo usuário. Finalizando...[/yellow]')
            break

    rprint('[green]Programa finalizado com sucesso.[/green]')
    sys.exit(0)
