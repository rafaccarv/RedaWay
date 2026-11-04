from django.core.management.base import BaseCommand
import json
from pathlib import Path
from academy.models import EssayExample, Source, Theme


THEMES = {
    2024: "Desafios para a valorização da herança africana no Brasil",
    2023: "Desafios para o enfrentamento da invisibilidade do trabalho de cuidado realizado pela mulher no Brasil",
    2022: "Desafios para a valorização de comunidades e povos tradicionais no Brasil",
    2021: "Invisibilidade e registro civil: garantia de acesso à cidadania no Brasil",
    2020: "O estigma associado às doenças mentais na sociedade brasileira",
    2019: "Democratização do acesso ao cinema no Brasil",
    2018: "Manipulação do comportamento do usuário pelo controle de dados na internet",
    2017: "Desafios para a formação educacional de surdos no Brasil",
}
OFFICIAL_PDFS = {
    2023: ("A Redação no Enem 2024 — Cartilha do Participante", "https://download.inep.gov.br/publicacoes/institucionais/avaliacoes_e_exames_da_educacao_basica/a_redacao_no_enem_2024_cartilha_do_participante.pdf", 35),
    2022: ("A Redação no Enem 2023 — Cartilha do Participante", "https://download.inep.gov.br/publicacoes/institucionais/avaliacoes_e_exames_da_educacao_basica/a_redacao_no_enem_2023_cartilha_do_participante.pdf", 26),
    2021: ("A Redação do Enem 2022 — Cartilha do Participante", "https://download.inep.gov.br/download/enem/cartilha_do_participante_enem_2022.pdf", 27),
    2019: ("A Redação do Enem 2020 — Cartilha do Participante", "https://download.inep.gov.br/publicacoes/institucionais/avaliacoes_e_exames_da_educacao_basica/a_redacao_do_enem_2020_-_cartilha_do_participante.pdf", 32),
    2018: ("A Redação no Enem 2019 — Cartilha do Participante", "https://download.inep.gov.br/publicacoes/institucionais/avaliacoes_e_exames_da_educacao_basica/a_redacao_no_enem_2019_cartilha_do_participante.pdf", 39),
    2017: ("A Redação no Enem 2018 — Cartilha do Participante", "https://download.inep.gov.br/educacao_basica/enem/guia_participante/2018/manual_de_redacao_do_enem_2018.pdf", 28),
}
ANALYSIS_FOCI = [
    "Observe como a introdução delimita o problema e apresenta uma tese que orienta a leitura. Ao estudar a Competência 2, confira se a abordagem responde ao recorte temático; na Competência 3, acompanhe se cada desenvolvimento sustenta uma parte dessa tese com explicação, não apenas com uma referência. Na Competência 4, marque retomadas e conectores que tornam a progressão legível. Por fim, na Competência 5, identifique agente, ação, meio e finalidade e avalie se a proposta responde ao diagnóstico sem ferir direitos humanos.",
    "Leia os dois parágrafos de desenvolvimento como etapas de um projeto. Para cada um, resuma a afirmação central em uma frase e depois localize a evidência ou repertório, a explicação do mecanismo e a consequência social. Essa leitura evidencia Competências 2 e 3. Observe também se pronomes, expressões de retomada e conectores deixam explícitas as relações entre períodos (Competência 4). Na conclusão, verifique se a intervenção é específica e executável, conforme a Competência 5.",
    "Use a redação para estudar decisões de escrita, sem tratar sua estrutura como fórmula obrigatória. Analise a precisão lexical, a construção dos períodos e a pontuação (Competência 1); a pertinência do repertório e a aderência ao tema (Competência 2); e a hierarquia das ideias (Competência 3). Depois, observe como a coesão organiza o texto (Competência 4) e se a conclusão articula uma medida concreta ao problema discutido (Competência 5). A nota máxima descreve o resultado daquela produção, não garante que cada escolha deva ser copiada.",
]


ESSAY_ANALYSES = {
    (2024, "Danilo Oliveira Batista"): "A tese anuncia dois entraves — políticas públicas ineficazes e falhas educacionais — que reaparecem, em ordem, nos parágrafos de desenvolvimento. O repertório histórico do ciclo do ouro introduz a discussão sobre a herança africana; a referência a Kant é usada para sustentar a crítica à formação escolar. Na conclusão, o Governo Federal e as escolas recebem ações distintas, ligadas aos dois argumentos. Para estudar C3, observe a correspondência entre cada eixo da tese e seu desenvolvimento; em C5, confira como agente, ação, meio e finalidade são explicitados.",
    (2024, "Sabrina Ayumi Alves"): "A abertura usa uma obra ambientada no contexto colonial para apresentar a inferiorização de pessoas negras, e o texto transporta esse mecanismo ao apagamento da cultura afro-brasileira. Os desenvolvimentos articulam a hierarquia social e o enfraquecimento da ancestralidade à construção da autoimagem. A conclusão retoma o silenciamento e propõe ações culturais em parceria entre Estado e escolas. Na leitura, observe como os repertórios de Ailton Krenak e Marilena Chauí são explicados e conectados ao argumento (C2 e C3), e como a intervenção responde ao problema cultural delimitado (C5).",
    (2024, "Marina Vieira Almeida Lima"): "O texto parte de Raízes do Brasil para introduzir a contribuição africana e contrasta esse legado com sua desvalorização. Os argumentos avançam por duas frentes: a permanência de estruturas históricas após a abolição e as limitações da educação para reconhecer a cultura afro-brasileira. A intervenção divide responsabilidades entre o Ministério da Cultura e as secretarias de educação, retomando esses eixos. Para observar C3, resuma a função de cada desenvolvimento; para C4, veja como expressões de causa e adição guiam a passagem entre eles; em C5, avalie a relação entre as ações e o diagnóstico.",
    (2023, "Arthur Sanches Sales"): "A redação organiza a discussão sobre trabalho de cuidado em torno da invisibilidade pública e da marginalização das cuidadoras. As referências a dados demográficos, Djamila Ribeiro e Zygmunt Bauman cumprem funções distintas: contextualizam a necessidade social do cuidado, justificam a importância do debate e criticam instituições que não cumprem plenamente seu papel. Na conclusão, a divulgação de dados e pesquisas é ligada ao enfrentamento do apagamento. Ao estudar C2 e C3, identifique como cada referência é interpretada; em C5, verifique se a medida proposta enfrenta diretamente a invisibilidade diagnosticada.",
    (2021, "Gabriel Borges"): "A introdução mobiliza Norberto Bobbio para relacionar democracia e representatividade à falta de registro civil. O desenvolvimento histórico, apoiado em Karl Marx, trata as desigualdades como condição que precede a vida individual; depois, Vidas Secas ilustra a ausência de apoio estatal. A proposta de um mutirão nacional reúne órgãos e comunidades, coerente com a escala do problema. Observe a progressão entre os dois argumentos (C3), a retomada do eixo de cidadania ao longo do texto (C4) e a especificação de agentes e meios na intervenção (C5).",
    (2020, "Julia Vieira"): "A referência ao filme Coringa apresenta uma situação de sofrimento psíquico e ajuda a introduzir o estigma. Os desenvolvimentos associam a omissão estatal na oferta de atendimento à discriminação social, articulando causas diferentes do mesmo problema. A conclusão atribui ao Ministério da Saúde ações de melhoria nos serviços e de ampliação de profissionais. Para estudar C3, observe como os dois argumentos complementam o diagnóstico; em C2, avalie a função da referência cultural; em C5, confira a relação entre agentes, medidas e necessidades discutidas.",
    (2020, "Aline Soares Alves"): "A redação abre com O Coringa para mostrar como a falta de atendimento pode agravar o sofrimento psíquico. A tese associa negligência estatal e desinformação; os desenvolvimentos explicam primeiro a insuficiência da assistência e depois a circulação de estereótipos. A conclusão reparte as ações entre os ministérios da Saúde e das Comunicações, com financiamento de profissionais e divulgação de informação. Repare na retomada dos dois eixos na intervenção (C3 e C5) e no uso da Constituição como base para a discussão do direito à saúde (C2).",
    (2020, "Ingrid Bascef"): "Quincas Borba apresenta o abandono de uma personagem com sofrimento mental e dá forma literária ao problema de exclusão. O texto desenvolve dois efeitos do estigma: o afastamento social e a demora em procurar ajuda, apoiando o raciocínio em Nise da Silveira e em dados atribuídos à OMS. A proposta de campanhas com profissionais de saúde retoma a necessidade de informação e acolhimento. Observe como cada repertório tem função argumentativa (C2), como os parágrafos avançam de exclusão para barreira de acesso ao tratamento (C3) e como essa lógica chega à intervenção (C5).",
    (2019, "Gabriel Melo Caldas Nogueira"): "A abertura usa David Hume para apresentar o pensamento como possibilidade de imaginar experiências e conecta essa ideia ao acesso ao cinema. O desenvolvimento associa a experiência cultural ao lazer e à vida social; depois, o artigo 215 da Constituição sustenta a discussão sobre cultura como direito. A proposta retoma o problema de acesso e procura adaptar a oferta às realidades locais. Na leitura, acompanhe como as referências são explicadas (C2), como os dois eixos avançam sem se repetir (C3) e como a intervenção conversa com o argumento jurídico (C5).",
    (2019, "Isabella de Oliveira Cardoso"): "O filme Cine Holiúdi funciona como repertório de entrada para contrastar os benefícios culturais do cinema com barreiras concretas. A argumentação separa custo e elitização de infraestrutura e acessibilidade, o que ajuda a organizar causas diferentes. A conclusão propõe ação conjunta do poder público e da mídia com campanhas e recursos audiovisuais. Observe se cada proposta responde ao eixo correspondente (C3 e C5), e como a referência cultural e a garantia de acessibilidade são conectadas à tese (C2).",
}

class Command(BaseCommand):
    help = "Publica 24 páginas de estudo de redações nota mil das edições de 2017 a 2024."

    def handle(self, *args, **options):
        user_supplied = json.loads((Path(__file__).resolve().parents[2] / "fixtures" / "historical_essay_texts.json").read_text(encoding="utf-8"))
        user_texts = {(item["year"], item["attribution"]): item["full_text"] for item in user_supplied}
        tm_source, _ = Source.objects.update_or_create(title="Exemplos de redação nota 1000 no Enem", defaults={"institution":"Toda Matéria", "edition":"acesso em 2026", "url":"https://www.todamateria.com.br/redacao-nota-1000-enem-exemplos/", "is_official":False})
        for year, theme_title in THEMES.items():
            theme = Theme.objects.filter(year=year).first()
            if theme is None:
                theme = Theme.objects.filter(title__iexact=theme_title).first()
            if year == 2024:
                text_source, _ = Source.objects.update_or_create(title="Redações nota mil do Enem 2024 — G1", defaults={"institution":"G1 Educação", "edition":"2024", "url":"https://g1.globo.com/educacao/enem/2024/noticia/2025/03/14/enem-2024-leia-redacoes-nota-mil.ghtml", "is_official":False})
                analysis_source = text_source
                authors = ["Danilo Oliveira Batista", "Sabrina Ayumi Alves", "Marina Vieira Almeida Lima"]
                pages = [None, None, None]
            elif year == 2020:
                text_source, _ = Source.objects.update_or_create(title="Redações nota mil do Enem 2020 — Brasil Escola", defaults={"institution":"Brasil Escola", "edition":"2020", "url":"https://vestibular.brasilescola.uol.com.br/enem/leia-redacoes-nota-mil-no-enem-2020/350135.html", "is_official":False})
                analysis_source = text_source
                authors = ["Julia Vieira", "Aline Soares Alves", "Ingrid Bascef"]
                pages = [None, None, None]
            else:
                title, url, first_page = OFFICIAL_PDFS[year]
                text_source, _ = Source.objects.update_or_create(title=title, defaults={"institution":"INEP / Ministério da Educação", "edition":str(year + 1), "url":url, "page":f"Amostras da edição {year}", "is_official":True})
                analysis_source = text_source
                if year == 2023:
                    authors = ["Arthur Sanches Sales", "Amostra comentada 2 · INEP", "Amostra comentada 3 · INEP"]
                elif year == 2022:
                    authors = ["Juliana Moreau de Almeida Soares", "Nicole Carvalho Almeida", "Amostra comentada 3 · INEP"]
                elif year == 2021:
                    authors = ["Gabriel Borges", "Pedro Henrique Rezende Machado", "Emanuelle Severino Gontijo Boucinhas"]
                elif year == 2019:
                    authors = ["Gabriel Melo Caldas Nogueira", "Isabella de Oliveira Cardoso", "Amostra comentada 3 · INEP"]
                elif year == 2018:
                    authors = ["André Bahia Pereira", "Amostra comentada 2 · INEP", "Amostra comentada 3 · INEP"]
                elif year == 2017:
                    authors = ["Mariana Camelier Mascarenhas", "Lorena Magalhães de Macedo", "Amostra comentada 3 · INEP"]
                else:
                    authors = [f"Amostra comentada {i} · INEP" for i in range(1, 4)]
                pages = [first_page + i for i in range(3)]
            for idx, (author, page) in enumerate(zip(authors, pages), 1):
                slug = f"enem-{year}-nota-mil-{idx}"
                title = f"{author} · redação nota mil (Enem {year})"
                page_line = f"Documento aberto na página aproximada {page}." if page else "A fonte reúne diferentes redações nota mil; consulte a publicação original."
                analysis = (f"Tema da edição: {theme_title}.\n\n"
                           f"{ANALYSIS_FOCI[(idx - 1) % len(ANALYSIS_FOCI)]}\n\n"
                           "Roteiro de estudo: (1) escreva a tese com suas palavras; (2) resuma a função de cada desenvolvimento; "
                           "(3) destaque uma escolha de coesão por parágrafo; (4) decomponha a intervenção em agente, ação, meio e finalidade. "
                           "Compare suas observações com os comentários e critérios publicados pela fonte. "
                           "Este comentário é uma leitura pedagógica autoral, não uma nota oficial por competência.")
                analysis = ESSAY_ANALYSES.get((year, author), analysis)
                captured_text = user_texts.get((year, author), "")
                entry_source = (text_source if year == 2024 else tm_source) if captured_text else text_source
                entry_source_page = None if captured_text else page
                attribution = author + (" · texto integral conforme fonte indicada" if captured_text else "")
                EssayExample.objects.update_or_create(slug=slug, defaults={"title":title, "edition_year":year, "text_source_page":entry_source_page, "theme":theme, "source":analysis_source, "text_source":entry_source, "attribution":attribution, "permission_note":(("Texto integral transcrito da reportagem do G1, conforme cópia fornecida para o projeto." if year == 2024 else "Texto integral transcrito do artigo da Toda Matéria, conforme cópia fornecida para o projeto.") if captured_text else f"Fonte original identificada. {page_line} O conteúdo é exibido pela publicação de origem."), "full_text":captured_text, "analysis":analysis, "is_published":True})
        self.stdout.write(self.style.SUCCESS("24 páginas históricas criadas ou atualizadas."))
