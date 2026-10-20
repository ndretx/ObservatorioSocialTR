import os
import urllib.request


def descarregar_caged_oficial():
  # URL oficial dos microdados do Novo CAGED (MTE)
  URL_FTP = "ftp://ftp.mtps.gov.br/pdet/microdados/NOVO%20CAGED/2024/202401/CAGEDMOV202401.7z"

  pasta_destino = "dados_brutos"
  os.makedirs(pasta_destino, exist_ok=True)
  caminho_arquivo = os.path.join(pasta_destino, "caged_bruto.7z")

  print(
      "🌐 Conectando ao FTP oficial do Ministério do Trabalho e Emprego"
      " (MTE)..."
  )
  print(
      "⏳ Baixando o arquivo oficial de microdados do Novo CAGED (isso pode"
      " levar alguns minutos)..."
  )

  try:
    urllib.request.urlretrieve(URL_FTP, caminho_arquivo)
    print(f"✅ Download concluído com sucesso!")
    print(f"💾 Arquivo bruto salvo em: {caminho_arquivo}")
  except Exception as e:
    print(f"⚠️ Erro ao descarregar os dados do FTP: {e}")


if __name__ == "__main__":
  descarregar_caged_oficial()