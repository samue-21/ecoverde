from sqlalchemy import (
    Column, Integer, String, Date, DateTime, Text, ForeignKey
)
from sqlalchemy.orm import relationship
from datetime import datetime
from database.db import Base

class ClienteFornecedor(Base):
    __tablename__ = 'cliente_fornecedor'

    id = Column(Integer, primary_key=True)
    nome = Column(String(120), nullable=False)
    contato = Column(String(120))
    telefone = Column(String(40))
    endereco = Column(String(200))
    documento = Column(String(20))  # CPF ou CNPJ
    tipo = Column(String(20))  # Cliente ou Fornecedor

    contratos = relationship(
        'Contrato',
        back_populates='cliente',
        cascade='all, delete-orphan'
    )


class Contrato(Base):
    __tablename__ = 'contrato'

    id = Column(Integer, primary_key=True)
    titulo = Column(String(120), nullable=False)

    cliente_id = Column(
        Integer,
        ForeignKey('cliente_fornecedor.id'),
        nullable=False
    )

    tipo = Column(String(30))  # Anual, Temporário, Por serviço
    data_inicio = Column(Date)
    data_fim = Column(Date)

    arquivo = Column(String(200))  # Caminho do PDF/texto
    status = Column(String(20))

    cliente = relationship(
        'ClienteFornecedor',
        back_populates='contratos'
    )

    historico = relationship(
        'HistoricoAlteracao',
        back_populates='contrato',
        cascade='all, delete-orphan'
    )


class ModeloContrato(Base):
    __tablename__ = 'modelo_contrato'

    id = Column(Integer, primary_key=True)
    tipo = Column(String(30), nullable=False)
    conteudo = Column(Text, nullable=False)


class HistoricoAlteracao(Base):
    __tablename__ = 'historico_alteracao'

    id = Column(Integer, primary_key=True)

    contrato_id = Column(
        Integer,
        ForeignKey('contrato.id'),
        nullable=False
    )

    data_alteracao = Column(
        DateTime,
        default=datetime.utcnow
    )

    descricao = Column(String(200))

    contrato = relationship(
        'Contrato',
        back_populates='historico'
    )
