"""---"""
import signal
import sys
from json import dumps

from psycopg import OperationalError
from rich import print as rprint, print_json

from base.process import ProcessInfosProduct

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
            infos_product: ProcessInfosProduct = ProcessInfosProduct(codpro_sku=cod)
            result: dict = infos_product.re()
            rprint("=-="*40)
            rprint(f"[crimson3]Informações do produto {cod} obtidas com sucesso.[/crimson3]")
            print_json(dumps(result))
            rprint("=-="*40)
        except OperationalError as e:
            rprint(f'[red3]Algo de errado com a conexao com o BD. Tente novamente mais tarde ![/red3] {e}')
            rprint(f'[red3]{e}[/red3]')
        except KeyboardInterrupt:
            rprint('\n[yellow]Interrupção recebida pelo usuário. Finalizando...[/yellow]')
            break
