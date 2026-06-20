"""
services/auth_service.py
Cadastro, login e validação de usuários persistidos em data.json.
Sem dependência de Streamlit.
"""
import hashlib
import re
import secrets
from datetime import datetime

from core.persistence import _ler, _gravar

_EMAIL_RE = re.compile(r"^[\w.+-]+@[\w-]+\.[\w.-]+$")
_CONTA_RE = re.compile(r"^[a-zA-Z0-9_]{3,30}$")


def validar_conta(conta: str) -> str | None:
    conta = (conta or "").strip()
    if not _CONTA_RE.match(conta):
        return "Conta inválida. Use 3–30 caracteres (letras, números ou _)."
    return None


def validar_email(email: str) -> str | None:
    email = (email or "").strip().lower()
    if not email or not _EMAIL_RE.match(email):
        return "Informe um e-mail válido."
    return None


def validar_senha(senha: str) -> str | None:
    if not senha or len(senha) < 6:
        return "A senha deve ter no mínimo 6 caracteres."
    return None


def _hash_senha(senha: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        senha.encode("utf-8"),
        salt.encode("utf-8"),
        120_000,
    ).hex()
    return f"{salt}${digest}"


def _verificar_senha(senha: str, senha_hash: str) -> bool:
    try:
        salt, digest = senha_hash.split("$", 1)
    except ValueError:
        return False
    novo = hashlib.pbkdf2_hmac(
        "sha256",
        senha.encode("utf-8"),
        salt.encode("utf-8"),
        120_000,
    ).hex()
    return secrets.compare_digest(novo, digest)


def _normalizar_email(email: str) -> str:
    return email.strip().lower()


def _conta_em_uso(conta: str, email_atual: str = "") -> bool:
    conta_lower = conta.strip().lower()
    for email, usuario in _ler().get("usuarios", {}).items():
        if email == email_atual:
            continue
        if usuario.get("conta", "").lower() == conta_lower:
            return True
    return False


def cadastrar_usuario(conta: str, email: str, senha: str) -> tuple[dict | None, str | None]:
    """Registra um novo usuário. Retorna (usuario, erro)."""
    for validar, valor in (
        (validar_conta, conta),
        (validar_email, email),
        (validar_senha, senha),
    ):
        if err := validar(valor):
            return None, err

    email_norm = _normalizar_email(email)
    conta = conta.strip()

    if _conta_em_uso(conta):
        return None, "Esta conta já está em uso."

    dados = _ler()
    usuarios = dados.setdefault("usuarios", {})

    if email_norm in usuarios:
        return None, "Este e-mail já está cadastrado."

    usuarios[email_norm] = {
        "conta": conta,
        "email": email_norm,
        "senha_hash": _hash_senha(senha),
        "criado_em": datetime.now().isoformat(),
        "historico": [],
        "pendencias": {},
    }
    _gravar(dados)

    return _usuario_publico(usuarios[email_norm], email_norm), None


def autenticar_usuario(email: str, senha: str) -> tuple[dict | None, str | None]:
    """Valida e-mail e senha. Retorna (usuario, erro)."""
    if err := validar_email(email):
        return None, err
    if not senha:
        return None, "Informe sua senha."

    email_norm = _normalizar_email(email)
    usuario = _ler().get("usuarios", {}).get(email_norm)

    if not usuario or not _verificar_senha(senha, usuario.get("senha_hash", "")):
        return None, "E-mail ou senha incorretos."

    return _usuario_publico(usuario, email_norm), None


def _usuario_publico(usuario: dict, user_id: str) -> dict:
    return {
        "user_id": user_id,
        "conta": usuario.get("conta", ""),
        "email": usuario.get("email", user_id),
    }
