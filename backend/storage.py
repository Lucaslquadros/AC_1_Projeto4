"""
storage.py — a camada de armazenamento de arquivos (Azure Blob Storage).

O container é privado: `enviar_arquivo` grava e devolve a URL crua (sem
assinatura); `url_com_sas` gera, a cada resposta, um link temporário e
somente-leitura que o navegador consegue abrir.
"""

import os
from datetime import datetime, timedelta, timezone

from azure.storage.blob import (
    BlobSasPermissions,
    BlobServiceClient,
    ContentSettings,
    generate_blob_sas,
)
from dotenv import load_dotenv

load_dotenv()

CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
CONTAINER = os.getenv("AZURE_STORAGE_CONTAINER", "cartazes")

# Quanto tempo o link assinado vale. Curto de propósito: enquanto o link
# não expira, quem tiver a URL vê a imagem — e não há como revogá-la.
MINUTOS_DE_VALIDADE_DO_SAS = 60

_service_client: BlobServiceClient | None = None


def _servico() -> BlobServiceClient:
    global _service_client

    if not CONNECTION_STRING:
        raise RuntimeError(
            "AZURE_STORAGE_CONNECTION_STRING não está definida. "
            "Local: coloque no .env. No Azure: em Environment variables."
        )

    if _service_client is None:
        _service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)

    return _service_client


def _container_client():
    return _servico().get_container_client(CONTAINER)


def nome_do_cartaz(evento_id: int, extensao: str) -> str:
    """Nome de blob previsível, derivado do id."""
    return f"eventos/{evento_id}/cartaz{extensao}"


def enviar_arquivo(nome_do_blob: str, conteudo: bytes, content_type: str) -> str:
    """Grava o conteúdo no container e devolve a URL do blob (sem SAS)."""
    blob_client = _container_client().get_blob_client(nome_do_blob)

    blob_client.upload_blob(
        conteudo,
        overwrite=True,
        content_settings=ContentSettings(content_type=content_type),
    )

    return blob_client.url


def url_com_sas(url_do_blob: str) -> str:
    """Devolve a mesma URL com um SAS de leitura, válido por pouco tempo."""
    servico = _servico()
    prefixo = _container_client().url

    if not url_do_blob.startswith(prefixo):
        # URL de outra conta/container: assinar com a nossa chave não faz sentido.
        return url_do_blob

    nome_do_blob = url_do_blob[len(prefixo) :].lstrip("/")

    sas = generate_blob_sas(
        account_name=servico.account_name,
        container_name=CONTAINER,
        blob_name=nome_do_blob,
        account_key=servico.credential.account_key,
        permission=BlobSasPermissions(read=True),
        expiry=datetime.now(timezone.utc) + timedelta(minutes=MINUTOS_DE_VALIDADE_DO_SAS),
    )

    return f"{url_do_blob}?{sas}"
