from ecomm_postgres import PostgresConnection as Postgres
from pandas import DataFrame
from services.query import query_db

class ProcessInfosProduct:

    def __init__(self, codpro_sku: str) -> None:
        self._codpro_sku: str = codpro_sku

    def __definir_tarifa(self, valor: float, tipo_anuncio: str) -> float:
        __result: float = 0.0
        match tipo_anuncio:
            case 'CLASSICO':
                if 0.01 <= valor < 19.00:
                    __result = 0
                elif 19.00 <= valor < 21.90:
                    __result = 7.10
                elif 21.90 <= valor < 42.62:
                    __result = 7.38
                elif 42.62 <= valor <= 71.33:
                    __result = 7.67
                elif 71.33 < valor:
                    __result = 0
                else:
                    raise ValueError(f"Caso Inesperado. Recebemos preço base vezes markup igual a {valor}")
            
            case 'PREMIUM':
                
                if 0.01 <= valor < 19.00:
                    __result = 0
                elif 19.00 <= valor < 21.47:
                    __result = 7.53
                elif 21.47 <= valor < 42.17:
                    __result = 7.83
                elif 42.17 <= valor <= 71.86:
                    __result = 8.13
                elif 71.86 < valor:
                    __result = 0
                else:
                    raise ValueError(f"Caso Inesperado. Recebemos preço base vezes markup igual a {valor}")

            case _:
                raise ValueError(f"Caso Inesperado. Recebemos preço base vezes markup igual a {valor}")
        return __result

    def __markup(self, tipo_anuncio: str = 'PREMIUM', logistic_type: str = 'cross_docking') -> float:
        __result: float = 0.0
        match tipo_anuncio:
            case 'PREMIUM': # Premium
                match logistic_type:
                    case 'cross_docking':
                        __result = 1.35504
                    case 'fulfillment':
                        __result = 1.37504
                    case _:
                        __result = 1.35504
            case 'CLASSICO': # Classico
                match logistic_type:
                    case 'cross_docking':
                        __result = 1.27804
                    case 'fulfillment':
                        __result = 1.29804
                    case _:
                        __result = 1.27804
            case _:
                raise ValueError(f"Caso Inesperado. Recebemos tipo de anuncio igual a {tipo_anuncio} e tipo de logistico igual a {logistic_type}")
        return __result

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
        with Postgres() as db:
            df_db: DataFrame = db.run_command(self.get_query(type_op_codpro=bool(True) if self._codpro_sku.isnumeric() else False))
            if not df_db.empty:
                df_aux_data: dict = df_db.loc[[0]].squeeze().to_dict().copy()
                df_aux_data['vl_uni_siac'] = float(df_aux_data.get('vl_uni_siac', 0.0))
                df_aux_data['vl_total_siac'] = float(df_aux_data.get('vl_total_siac', 0.0))
                df_aux_data['tipo_anuncio'] = None
                df_aux_data['tipo_anuncio'] = 'CLASSICO' if df_aux_data.get('vl_total_siac', 0.0) < 41 else 'PREMIUM'
                df_aux_data['vl_ml'] = float(df_aux_data.get('vl_total_siac', 0.0)) * float(self.__markup(
                    tipo_anuncio=df_aux_data.get('tipo_anuncio', ''),
                    logistic_type=df_aux_data.get('logistic_type', 'cross_docking')
                ))
                df_aux_data['vl_ml'] = df_aux_data.get('vl_ml', 0.0) + self.__definir_tarifa(
                    df_aux_data.get('vl_ml', 0.0),
                    df_aux_data.get('tipo_anuncio', '')
                )
                df_aux_data['vl_ml'] = round(df_aux_data.get('vl_ml', 0.0), 2)
                df_aux_data['oem'] = ', '.join(set(df_db.oem)) if not df_db.oem.loc[~df_db.oem.isna()].empty else '-'
                df_aux_data['codigo_barras'] = ', '.join(set(df_db.codigo_barras)) if not df_db.codigo_barras.loc[~df_db.codigo_barras.isna()].empty else '-'
                df_aux_data['sku'] = f'{df_db.multiplo.values[0]}X[{df_db.sku.values[0]}]' if int(df_db.multiplo.values[0]) > 1 else df_db.sku.values[0]
                return df_aux_data
            return {}
