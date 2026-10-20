import os
import pandas as pd
import py7zr


def processar_microdados_tres_rios():
  COD_TRES_RIOS = 330600  # Código IBGE de Três Rios - RJ
  caminho_7z = "dados_brutos/caged_bruto.7z"
  pasta_temp = "dados_brutos/temp_caged"
  pasta_saida = "dados_tratados"

  if not os.path.exists(caminho_7z):
    print(
        f"⚠️ Arquivo {caminho_7z} não encontrado! Execute o 'coleta_oficial.py'"
        " primeiro."
    )
    return

  print("📦 Descompactando microdados oficiais do Novo CAGED...")
  with py7zr.SevenZipFile(caminho_7z, mode="r") as archive:
    archive.extractall(path=pasta_temp)

  # Localizar o arquivo .txt / .csv descompactado
  arquivos_encontrados = [
      os.path.join(pasta_temp, f)
      for f in os.listdir(pasta_temp)
      if f.endswith((".txt", ".csv"))
  ]

  if not arquivos_encontrados:
    print("⚠️ Nenhum arquivo .txt ou .csv encontrado na extração.")
    return

  arquivo_extraido = arquivos_encontrados[0]

  print("⚡ Lendo o arquivo de microdados (isso pode levar alguns segundos)...")
  # Leitura segura com Pandas (tentando separador ponto-e-vírgula ou vírgula)
  try:
    df = pd.read_csv(
        arquivo_extraido,
        sep=";",
        encoding="utf-8",
        low_memory=False,
        on_bad_lines="skip",
    )
  except Exception:
    df = pd.read_csv(
        arquivo_extraido,
        sep=",",
        encoding="utf-8",
        low_memory=False,
        on_bad_lines="skip",
    )

  # Padronizar nomes das colunas (remover espaços, colocar minúsculas)
  df.columns = [col.lower().strip() for col in df.columns]

  print(f"📋 Colunas disponíveis no arquivo: {list(df.columns)[:10]} ...")

  # Identificar dinamicamente a coluna de município (evita erro de acentuação)
  coluna_mun = None
  for col in df.columns:
    if "municipio" in col or "município" in col or col == "mun":
      coluna_mun = col
      break

  if not coluna_mun:
    print(
        "⚠️ Não foi possível encontrar a coluna de município automaticamente."
    )
    print(f"Colunas presentes: {list(df.columns)}")
    return

  print(
      f"🔍 Coluna de município identificada com sucesso: '{coluna_mun}'"
  )

  # Filtrar estritamente pelo código de Três Rios
  df_tr = df[df[coluna_mun] == COD_TRES_RIOS].copy()

  print(
      f"🎉 Encontradas {len(df_tr)} movimentações reais de emprego em Três"
      " Rios!"
  )

  if len(df_tr) == 0:
    print(
        "⚠️ O filtro retornou 0 registros. Verifique se o código do município"
        " bate com o formato da base."
    )
    return

  # Mapeamento dos códigos oficiais do MTE / CAGED
  mapa_sexo = {1: "Masculino", 3: "Feminino", 9: "Não Identificado"}
  mapa_raca = {
      1: "Branca",
      2: "Preta",
      3: "Parda",
      4: "Amarela",
      5: "Indígena",
      6: "Não Informada",
      9: "Não Identificado",
  }

  # Mapear colunas se existirem
  for col_sexo in ["sexo", "c_sexo"]:
    if col_sexo in df_tr.columns:
      df_tr["sexo_desc"] = df_tr[col_sexo].map(mapa_sexo)
      break

  for col_raca in ["racacor", "raca_cor", "raçacor"]:
    if col_raca in df_tr.columns:
      df_tr["raca_desc"] = df_tr[col_raca].map(mapa_raca)
      break

  # Salvar base tratada completa de Três Rios
  os.makedirs(pasta_saida, exist_ok=True)
  caminho_csv_tr = os.path.join(
      pasta_saida, "caged_microdados_tres_rios.csv"
  )
  df_tr.to_csv(caminho_csv_tr, index=False, encoding="utf-8-sig")

  # Processar salário se a coluna existir
  coluna_salario = None
  for c in [
      "valorsalariofixo",
      "valor_salario_fixo",
      "salario",
      "saláriofixo",
  ]:
    if c in df_tr.columns:
      coluna_salario = c
      break

  if coluna_salario and "sexo_desc" in df_tr.columns and "raca_desc" in df_tr.columns:
    # Tratar vírgula por ponto se for string
    if df_tr[coluna_salario].dtype == object:
      df_tr[coluna_salario] = (
          df_tr[coluna_salario]
          .astype(str)
          .str.replace(",", ".")
          .astype(float)
      )

    painel_disparidade = (
        df_tr.groupby(["sexo_desc", "raca_desc"])
        .agg(
            salario_medio=(coluna_salario, "mean"),
            total_movimentacoes=(coluna_salario, "count"),
        )
        .reset_index()
    )

    caminho_painel = os.path.join(
        pasta_saida, "disparidade_salarial_tres_rios.csv"
    )
    painel_disparidade.to_csv(caminho_painel, index=False, encoding="utf-8-sig")

    print("\n📊 PAINEL REAL DE DISPARIDADE SALARIAL EM TRÊS RIOS:")
    print("=" * 65)
    print(painel_disparidade.to_string(index=False))
    print("=" * 65)

  print(f"\n💾 Arquivos salvos com sucesso na pasta: {pasta_saida}/")


if __name__ == "__main__":
  processar_microdados_tres_rios()