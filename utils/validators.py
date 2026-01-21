# Funções utilitárias para validação, conversão de arquivos, envio de e-mails, etc.

def validar_documento(documento):
    # Validação simples de CPF/CNPJ
    return len(documento) in [11, 14]

# Outras funções utilitárias podem ser adicionadas aqui
