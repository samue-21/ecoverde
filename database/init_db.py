from database.db import engine, Base
from database.models import ClienteFornecedor, Contrato, ModeloContrato, HistoricoAlteracao

def init_db():
    Base.metadata.create_all(engine)
    print('Banco de dados inicializado com sucesso!')

if __name__ == '__main__':
    init_db()
