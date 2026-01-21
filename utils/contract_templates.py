from __future__ import annotations

from database.models import ModeloContrato


DEFAULT_TEMPLATES: dict[str, str] = {
    "Anual": """CONTRATO DE PRESTAÇÃO DE SERVIÇOS DE JARDINAGEM E MANUTENÇÃO DE ÁREAS VERDES (ANUAL)

QUADRO RESUMO
1) PARTES
CONTRATANTE: {{cliente_nome}}, {{cliente_documento}}, {{cliente_endereco}}, contato: {{cliente_contato}}.
CONTRATADA: {{empresa_nome}} (\"ECOVERDE JARDINAGEM\"), {{empresa_cnpj}}, {{empresa_endereco}} - {{empresa_cidade_uf}}, contato: {{empresa_contato}}.

2) OBJETO
Prestação de serviços de jardinagem e manutenção de áreas verdes, conforme escopo e condições deste instrumento e, quando aplicável, Ordens de Serviço (OS).

3) VIGÊNCIA
Início em {{data_inicio}} e término em {{data_fim}} (12 meses). Renovação: mediante acordo entre as partes.

4) VALOR E PAGAMENTO
Valor total: {{valor_total}}.
Condições: {{condicoes_pagamento}}.

5) ESCOPO (RESUMO)
{{escopo_servicos}}

CONDIÇÕES GERAIS
Pelo presente instrumento particular, as partes identificadas no Quadro Resumo celebram o presente contrato, que se regerá pelo Código Civil e, quando aplicável, pelo Código de Defesa do Consumidor (Lei nº 8.078/1990), pelas cláusulas abaixo.

CLÁUSULA 1ª – DEFINIÇÕES E DOCUMENTOS
1.1 \"Proposta\" e/ou \"OS\" são documentos que detalham serviços, frequências, áreas atendidas, medições, cronograma e materiais, quando necessários. Em caso de divergência: (i) Quadro Resumo; (ii) Condições Gerais; (iii) Proposta/OS.

CLÁUSULA 2ª – DO OBJETO E DA EXECUÇÃO
2.1 A CONTRATADA executará os serviços descritos no Quadro Resumo e na Proposta/OS, com equipe treinada, observando boas práticas de jardinagem, segurança do trabalho e preservação ambiental.
2.2 Eventuais atividades extras (não previstas) somente serão executadas após aprovação do CONTRATANTE (por escrito, mensagem ou assinatura em OS), com orçamento à parte quando aplicável.

CLÁUSULA 3ª – OBRIGAÇÕES DA CONTRATADA (ECOVERDE)
3.1 Executar os serviços com técnica adequada e padrões de qualidade compatíveis com o tipo de serviço contratado.
3.2 Informar ao CONTRATANTE, com antecedência razoável, necessidades de acesso, interrupções ou requisitos para execução (ex.: remoção de objetos, liberação de áreas).
3.3 Comunicar a CONTRATANTE sobre cronograma de agenda, horários em que serão realizados os serviços e os dias que serão. Necessário adicionar adubação e aplicação de venenos específicos para o combate de pragas e matos no paisagismo do CONTRATANTE.
3.4 Empregar materiais e insumos em conformidade com instruções de uso e normas aplicáveis, especialmente defensivos/fitossanitários quando houver, observando segurança e orientação técnica.

CLÁUSULA 4ª – OBRIGAÇÕES DO CONTRATANTE
4.1 Garantir acesso ao local, informar regras internas, restrições e riscos, e disponibilizar condições mínimas para execução.
4.2 Disponibilizar, quando necessário e acordado, pontos de água e energia.
4.3 Autorizar previamente intervenções que possam alterar significativamente o paisagismo (ex.: supressão de planta, alteração de canteiros).
4.4 Efetuar pagamentos conforme pactuado e aprovar/assinar OS quando aplicável.

CLÁUSULA 5ª – INSUMOS, MATERIAIS E DESTINAÇÃO DE RESÍDUOS
5.1 A CONTRATANTE se responsabilizará em fornecer quais materiais como (pedras para jardins, gramas, adubos e outros materiais). Pois a CONTRATADA tem como responsabilidade em fornecer a mão de obra para aplicação após aprovação do orçamento e o fornecimento de venenos específicos contra pragas e matos quando necessário.
5.2 A destinação de resíduos e entulhos após a limpeza e serviço realizado deverá ser destinada para descarte correto pelo CONTRATADO, mas se em orçamento não é prevista a remoção e destinação correta dos entulhos e resíduos, ficará a cargo do CONTRATANTE ou será orçada separadamente.

CLÁUSULA 6ª – VALOR, REAJUSTE E INADIMPLEMENTO
6.1 O valor e forma de pagamento constam do Quadro Resumo/Proposta.
6.2 Reajuste: poderá ocorrer em renovações ou quando houver mudança de escopo, conforme negociação.
6.3 Em caso de atraso, poderá incidir multa e juros conforme previsto em proposta/OS ou acordo entre as partes, e os serviços poderão ser suspensos até a regularização, respeitada a boa-fé e a comunicação prévia.

CLÁUSULA 7ª – GARANTIAS E QUALIDADE DO SERVIÇO
7.1 Garantia de execução: a CONTRATADA compromete-se a corrigir, sem custo de mão de obra, falhas comprovadamente decorrentes de execução inadequada, quando comunicadas em até {{prazo_garantia_dias}} dias.
7.2 Garantia legal (CDC, quando aplicável): caso haja vício de qualidade na prestação do serviço, aplicar-se-ão os direitos previstos no art. 20 do CDC, sem prejuízo da solução amigável.
7.3 A garantia não cobre: eventos climáticos extremos, pragas/doenças preexistentes, danos por terceiros, uso inadequado, falta de irrigação/manutenção quando de responsabilidade do CONTRATANTE, ou alterações no local posteriores ao serviço.

CLÁUSULA 8ª – SAÚDE, SEGURANÇA E RESPONSABILIDADES
8.1 O CONTRATANTE deverá informar previamente riscos e normas do local. A CONTRATADA poderá interromper a execução em caso de risco grave e iminente.
8.2 Cada parte responde por seus atos e por danos diretamente causados por culpa ou dolo, observadas as limitações legais.

CLÁUSULA 9ª – DIREITOS DO CONSUMIDOR (QUANDO APLICÁVEL)
9.1 Quando caracterizada relação de consumo, este contrato observará as normas do CDC (Lei nº 8.078/1990), incluindo informações claras, boa-fé e equilíbrio contratual.
9.2 Direito de arrependimento (art. 49 do CDC): aplica-se apenas quando a contratação ocorrer fora do estabelecimento comercial e/ou por meio eletrônico/telefone, nos termos da lei.

CLÁUSULA 10ª – PROTEÇÃO DE DADOS E CONFIDENCIALIDADE
10.1 As partes tratarão dados pessoais apenas para fins de execução deste contrato, observando a LGPD (Lei nº 13.709/2018), e manterão confidenciais informações técnicas e comerciais.

CLÁUSULA 11ª – RESCISÃO
11.1 Após a aprovação do orçamento e assinatura do contrato no presente momento, o arrependimento ou a quebra de contrato por ambas as partes tanto por falhas técnicas por não atendimento mais por conta da CONTRATADA, ou troca de empresa de jardinagem sem que haja esgotado o tempo determinado em contrato, será cobrado uma porcentagem em multa que também se aplica as seguintes questões:

CONTRATANTE: se arrependeu do valor em contrato, houve separação e irá se mudar, agrediu verbalmente e fisicamente o CONTRATADO, será cobrada uma multa de 40% no valor total de meses restante do contrato que foi firmado entre as partes.

CONTRATADA: não atenderá mais esse CONTRATANTE, não lê mais as mensagens ou ligações, não faz mais manutenção no local, agrediu verbalmente e fisicamente o CONTRATANTE, ou desistiu e fechou as portas da empresa, pagará uma multa de 40% ao CONTRATANTE.
11.2 Rescisão imediata poderá ocorrer em caso de inadimplemento relevante, mediante notificação, quando cabível.

CLÁUSULA 12ª – DISPOSIÇÕES GERAIS E FORO
12.1 Tolerância não implica novação.
12.2 Fica eleito o foro da comarca de {{foro}}, ressalvadas as regras legais aplicáveis (inclusive CDC, quando aplicável).
12.3 Havendo atraso do pagamento dos serviços a qual foram realizados em até 5 dias após a data de pagamento, serão feitas até 3 tentativas de comunicações amigáveis. O CONTRATADO não tendo êxito, entraremos com nossa equipe de jurídico pelos meios legais da lei para que haja por meio do judiciário o pagamento pendente.

E por estarem de acordo, as partes assinam o presente instrumento.

{{cidade_data_assinatura}}

CONTRATANTE: ________________________________
Nome: {{cliente_nome}}

CONTRATADA: ________________________________
{{empresa_nome}}

TESTEMUNHAS:
1) ________________________________  CPF: __________________
2) ________________________________  CPF: __________________
""",
}


def ensure_default_templates(session, *, upgrade_existing: bool = True) -> None:
    for tipo, conteudo in DEFAULT_TEMPLATES.items():
        exists = session.query(ModeloContrato).filter(ModeloContrato.tipo == tipo).first()
        if not exists:
            session.add(ModeloContrato(tipo=tipo, conteudo=conteudo))
            continue
        if not upgrade_existing:
            continue

        conteudo_atual = exists.conteudo or ""
        conteudo_atualizado = (
            conteudo_atual.replace("Eco-Verde", "Ecoverde")
            .replace("Eco Verde", "Ecoverde")
            .replace("ECO VERDE", "ECOVERDE")
        )
        clausulas_atualizadas = {
            "3.3 Manter comunicação sobre cronograma, ocorrências e recomendações técnicas (ex.: poda, adubação, irrigação, controle de pragas).": (
                "3.3 Comunicar a CONTRATANTE sobre cronograma de agenda, horários em que serão realizados os serviços "
                "e os dias que serão. Necessário adicionar adubação e aplicação de venenos específicos para o combate "
                "de pragas e matos no paisagismo do CONTRATANTE."
            ),
            "5.1 Responsabilidade por insumos (adubos, mudas, defensivos, etc.): {{responsavel_insumos}}.": (
                "5.1 A CONTRATANTE se responsabilizará em fornecer quais materiais como (pedras para jardins, gramas, "
                "adubos e outros materiais). Pois a CONTRATADA tem como responsabilidade em fornecer a mão de obra para "
                "aplicação após aprovação do orçamento e o fornecimento de venenos específicos contra pragas e matos "
                "quando necessário."
            ),
            "5.2 A destinação de resíduos será realizada conforme escopo. Quando não prevista, ficará a cargo do CONTRATANTE ou será orçada separadamente.": (
                "5.2 A destinação de resíduos e entulhos após a limpeza e serviço realizado deverá ser destinada para "
                "descarte correto pelo CONTRATADO, mas se em orçamento não é prevista a remoção e destinação correta dos "
                "entulhos e resíduos, ficará a cargo do CONTRATANTE ou será orçada separadamente."
            ),
            "11.1 O contrato poderá ser rescindido por qualquer parte mediante aviso prévio escrito de {{aviso_previo_dias}} dias.": (
                "11.1 Após a aprovação do orçamento e assinatura do contrato no presente momento, o arrependimento ou a "
                "quebra de contrato por ambas as partes tanto por falhas técnicas por não atendimento mais por conta da "
                "CONTRATADA, ou troca de empresa de jardinagem sem que haja esgotado o tempo determinado em contrato, "
                "será cobrado uma porcentagem em multa que também se aplica as seguintes questões:\n\n"
                "CONTRATANTE: se arrependeu do valor em contrato, houve separação e irá se mudar, agrediu verbalmente e "
                "fisicamente o CONTRATADO, será cobrada uma multa de 40% no valor total de meses restante do contrato que "
                "foi firmado entre as partes.\n\n"
                "CONTRATADA: não atenderá mais esse CONTRATANTE, não lê mais as mensagens ou ligações, não faz mais "
                "manutenção no local, agrediu verbalmente e fisicamente o CONTRATANTE, ou desistiu e fechou as portas da "
                "empresa, pagará uma multa de 40% ao CONTRATANTE."
            ),
        }
        for clausula_antiga, clausula_nova in clausulas_atualizadas.items():
            if clausula_antiga in conteudo_atualizado and clausula_nova not in conteudo_atualizado:
                conteudo_atualizado = conteudo_atualizado.replace(clausula_antiga, clausula_nova)

        clausula_12_2 = "12.2 Fica eleito o foro da comarca de {{foro}}, ressalvadas as regras legais aplicáveis (inclusive CDC, quando aplicável)."
        clausula_12_3 = (
            "12.3 Havendo atraso do pagamento dos serviços a qual foram realizados em até 5 dias após a data de "
            "pagamento, serão feitas até 3 tentativas de comunicações amigáveis. O CONTRATADO não tendo êxito, "
            "entraremos com nossa equipe de jurídico pelos meios legais da lei para que haja por meio do judiciário o "
            "pagamento pendente."
        )
        if clausula_12_3 not in conteudo_atualizado and clausula_12_2 in conteudo_atualizado:
            conteudo_atualizado = conteudo_atualizado.replace(clausula_12_2, f"{clausula_12_2}\n{clausula_12_3}")
        if conteudo_atualizado != conteudo_atual:
            exists.conteudo = conteudo_atualizado

        if "Lei nº 8.078/1990" not in (exists.conteudo or ""):
            exists.conteudo = conteudo
    session.commit()
