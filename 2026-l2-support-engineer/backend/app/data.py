TOPICS = [
    ("contratacoes", "Contratações", ["Licitação eletrônica", "Contrato administrativo", "Contratação direta", "Gestão de fornecedores"]),
    ("orcamento", "Orçamento", ["Execução orçamentária", "Prestação de contas", "Previsão de despesas", "Conciliação de receitas"]),
    ("pessoas", "Pessoas", ["Previdência complementar", "Cessão de servidores", "Capacitação profissional", "Avaliação de desempenho"]),
    ("governanca", "Governança", ["Auditoria interna", "Proteção da informação", "Gestão de riscos", "Transparência pública"]),
    ("servicos", "Serviços", ["Acessibilidade digital", "Emissão de certidões", "Atendimento ao cidadão", "Integração de sistemas"]),
]
SECTIONS = ["Visão geral", "Procedimentos", "Documentação necessária", "Prazos", "Responsabilidades", "Perguntas frequentes", "Conferência", "Orientações", "Exemplos", "Referências"]
CATEGORIES = [{"id": key, "name": name} for key, name, _ in TOPICS]
DOCUMENTS = {}
for category, category_name, subjects in TOPICS:
    for subject in subjects:
        for section in SECTIONS:
            ident = len(DOCUMENTS) + 1
            DOCUMENTS[ident] = {
                "id": ident,
                "title": f"{subject}: {section.lower()}",
                "summary": f"Orientações sobre {subject.lower()}, com critérios de análise, verificação e acompanhamento pela equipe responsável.",
                "body": f"{section} de {subject.lower()}. Confira a documentação, registre a solicitação e acompanhe a conclusão. Este conteúdo é fictício e serve apenas à demonstração do portal.",
                "category": category,
                "category_name": category_name,
                "updated_at": "2026-09-18",
            }
