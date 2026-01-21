from flask import Blueprint, request, jsonify
from database.models import ClienteFornecedor, Contrato, HistoricoAlteracao
from database.db import db

bp = Blueprint('api', __name__)

@bp.route('/clientes', methods=['POST'])
def criar_cliente():
    data = request.json
    cliente = ClienteFornecedor(
        nome=data['nome'],
        contato=data.get('contato'),
        endereco=data.get('endereco'),
        documento=data.get('documento'),
        tipo=data.get('tipo')
    )
    db.session.add(cliente)
    db.session.commit()
    return jsonify({'id': cliente.id}), 201

# Rotas para contratos, histórico, relatórios, etc. podem ser adicionadas aqui
