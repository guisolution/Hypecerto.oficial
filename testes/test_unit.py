"""TESTES UNITÁRIOS — services/auth_service.py, schemas.py, config.py"""
import time, pytest
from datetime import timedelta
from jose import jwt
from fastapi import HTTPException
from pydantic import ValidationError
from app.services import auth_service as A
from app.schemas.schemas import SignupRequest, LoginRequest
from app.config import settings

# ---- Hash de senha
def test_U01_hash_nao_e_texto_plano():
    h = A.hash_password("Senha123"); assert h != "Senha123" and h.startswith("$2")
def test_U02_hash_com_salt_unico():
    assert A.hash_password("Senha123") != A.hash_password("Senha123")
def test_U03_verify_ok_e_falha():
    h = A.hash_password("Senha123"); assert A.verify_password("Senha123", h) and not A.verify_password("senha123", h)
def test_U04_bcrypt_trunca_72_bytes_VULN():
    """Senhas que diferem só após o byte 72 são equivalentes (truncamento silencioso do bcrypt)."""
    base = "A1" + "x"*70
    h = A.hash_password(base + "AAAA")
    assert A.verify_password(base + "ZZZZ", h) is True   # <- comportamento indesejado documentado

# ---- JWT
def test_U05_token_roundtrip():
    t = A.create_access_token({"sub": "7"}); assert A.decode_token(t)["sub"] == "7"
def test_U06_token_expirado_rejeitado():
    t = A.create_access_token({"sub": "1"}, expires_delta=timedelta(seconds=-1))
    with pytest.raises(HTTPException) as e: A.decode_token(t)
    assert e.value.status_code == 401
def test_U07_token_adulterado_rejeitado():
    t = A.create_access_token({"sub": "1"}); bad = t[:-3] + ("AAA" if not t.endswith("AAA") else "BBB")
    with pytest.raises(HTTPException): A.decode_token(bad)
def test_U08_alg_none_rejeitado():
    import base64, json
    b = lambda d: base64.urlsafe_b64encode(json.dumps(d).encode()).rstrip(b"=").decode()
    forged = f'{b({"alg":"none","typ":"JWT"})}.{b({"sub":"1","exp":9999999999})}.'
    with pytest.raises(HTTPException): A.decode_token(forged)
def test_U09_expiracao_padrao_7_dias_RISCO():
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 10080   # 7 dias, sem refresh/revogação
def test_U10_secret_key_padrao_previsivel_VULN():
    """Sem .env, SECRET_KEY é um valor público -> qualquer um forja tokens."""
    assert settings.SECRET_KEY == "dev-secret-key-change-in-production"
    forged = jwt.encode({"sub": "1", "exp": time.time()+3600}, "dev-secret-key-change-in-production", algorithm="HS256")
    assert A.decode_token(forged)["sub"] == "1"            # aceito pelo serviço

# ---- Schemas
def test_U11_signup_senhas_diferentes_rejeitadas():
    with pytest.raises(ValidationError): SignupRequest(nome="a", email="a@b.com", password="x", confirmPassword="y")
def test_U12_email_invalido_rejeitado():
    with pytest.raises(ValidationError): LoginRequest(email="nao-e-email", password="x")
def test_U13_sem_politica_de_senha_no_backend_VULN():
    s = SignupRequest(nome="a", email="a@b.com", password="1", confirmPassword="1"); assert s.password == "1"
def test_U14_nome_vazio_aceito_VULN():
    assert SignupRequest(nome="", email="a@b.com", password="1", confirmPassword="1").nome == ""
def test_U15_sem_limite_tamanho_nome():
    assert len(SignupRequest(nome="x"*100000, email="a@b.com", password="1", confirmPassword="1").nome) == 100000
