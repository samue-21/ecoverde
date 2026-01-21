from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CompanyConfig:
    nome: str
    cnpj: str
    endereco: str
    cidade_uf: str
    email: str
    telefone: str
    logo_path: str


COMPANY = CompanyConfig(
    nome="Ecoverde Jardinagem",
    cnpj="61.448.986/0001-51",
    endereco="Rua 6, 240 - Industrial, CEP 78635-000",
    cidade_uf="Água Boa - MT",
    email="ecoverdeJardinagem1@gmail.com",
    telefone="(66) 9641-7098",
    logo_path=r"assets\logo 4.png",
)
