import pandas as pd
import streamlit as st


@st.cache_data
def load_and_clean_data(file):
  if file is None:
    # Dados de exemplo caso nenhum arquivo seja enviado
    return pd.DataFrame({
        "Categoria": ["A", "B", "C"] * 10,
        "Valor": range(30, 60),
    })

  # Leitura do CSV (com suporte a vírgula ou ponto e vírgula)
  try:
    df = pd.read_csv(file, encoding="utf-8")
    if len(df.columns) == 1:
      file.seek(0)
      df = pd.read_csv(file, sep=";", encoding="utf-8")
  except UnicodeDecodeError:
    file.seek(0)
    df = pd.read_csv(file, encoding="latin1")

  # --- TRADUÇÃO E FORMATAÇÃO DAS VARIÁVEIS PRINCIPAIS ---

  # 1. Salário Fixo (conversão para float)
  if "valorsaláriofixo" in df.columns:
    if df["valorsaláriofixo"].dtype == object:
      df["valorsalario_num"] = (
          df["valorsaláriofixo"].astype(str).str.replace(",", ".").astype(float)
      )
    else:
      df["valorsalario_num"] = df["valorsaláriofixo"].astype(float)

  # 2. Raça / Cor
  mapa_raca = {
      1: "Branca",
      2: "Preta",
      3: "Parda",
      4: "Não Informada / Outras",
      5: "Não Informada / Outras",
      6: "Não Informada",
      9: "Não Informada",
  }
  if "raçacor" in df.columns:
    df["raca_tratada"] = (
        df["raçacor"].map(mapa_raca).fillna("Não Informada / Outras")
    )

  # 3. Escolaridade (Grau de Instrução)
  mapa_instrucao = {
      1: "Analfabeto",
      2: "Fundamental Incompleto",
      3: "Fundamental Incompleto",
      4: "Fundamental Completo",
      5: "Médio Incompleto",
      6: "Médio Completo",
      7: "Médio Completo",
      8: "Superior Incompleto",
      9: "Superior Completo",
  }
  if "graudeinstrução" in df.columns:
    df["escolaridade_tratada"] = (
        df["graudeinstrução"].map(mapa_instrucao).fillna("Não Informada")
    )

  # 4. Setor Econômico (Seção CNAE)
  mapa_secao = {
      "G": "Comércio",
      "C": "Indústria",
      "N": "Serviços Administrativos",
      "F": "Construção Civil",
      "H": "Transporte e Logística",
      "I": "Alimentação e Alojamento",
      "Q": "Saúde e Serviços Sociais",
      "M": "Serviços Técnicos / Profissionais",
      "P": "Educação",
  }
  if "seção" in df.columns:
    df["setor_econ_tratado"] = (
        df["seção"].map(mapa_secao).fillna("Outros Setores")
    )

  return df 