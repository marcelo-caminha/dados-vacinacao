"""Gera a versão reduzida do dataset usada no deploy.

O CSV original (~235 MB) passa do limite de 100 MB do GitHub. O dashboard
só usa algumas colunas, então este script mantém apenas elas e grava um
CSV compactado (gzip) em config.CSV_REDUZIDO_PATH.

Uso (a partir da pasta dash_vacinacao):
    python -m scripts.reduzir_dataset
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import config, data  # noqa: E402


def main() -> None:
    df = data.carregar_csv_original(config.CSV_PATH)
    df[config.COLUNAS_USADAS].to_csv(
        config.CSV_REDUZIDO_PATH, sep=config.CSV_SEP, index=False, encoding="utf-8"
    )
    tamanho_mb = config.CSV_REDUZIDO_PATH.stat().st_size / 1024**2
    print(f"{len(df)} linhas gravadas em {config.CSV_REDUZIDO_PATH.name} ({tamanho_mb:.1f} MB)")


if __name__ == "__main__":
    main()
