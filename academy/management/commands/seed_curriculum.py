from django.core.management.base import BaseCommand
from django.utils.text import slugify
from pathlib import Path
import json

from academy.models import Achievement, EssayExample, Exercise, ExerciseChoice, LearningPath, Lesson, Module, RepertoireEntry, Source, Theme


class Command(BaseCommand):
    help = "Cria a estrutura inicial da jornada RedaWay e conteúdos de demonstração revisáveis."

    def handle(self, *args, **options):
        cartilha, _ = Source.objects.update_or_create(
            title="A Redação do Enem 2026 — Cartilha do Participante",
            defaults={
                "institution": "INEP / Ministério da Educação / DAEB",
                "edition": "2026",
                "url": "https://www.gov.br/inep/pt-br/centrais-de-conteudo/acervo-linha-editorial/publicacoes-institucionais/avaliacoes-e-exames-da-educacao-basica/a-redacao-do-enem-2026-cartilha-do-a-participante",
                "is_official": True,
            },
        )
        Source.objects.update_or_create(
            title="Matrizes de Referência do Enem",
            defaults={
                "institution": "INEP / Ministério da Educação",
                "edition": "2026",
                "url": "https://www.gov.br/inep/pt-br/centrais-de-conteudo/acervo-linha-editorial/publicacoes-institucionais/avaliacoes-e-exames-da-educacao-basica/matrizes-de-referencia-enem",
                "is_official": True,
            },
        )
        constitution_education, _ = Source.objects.update_or_create(
            title="Constituição Federal — art. 205 (educação)",
            defaults={
                "institution": "Presidência da República — Casa Civil",
                "edition": "1988 (texto compilado)",
                "url": "https://www.planalto.gov.br/ccivil_03/constituicao/constituicaocompilado.htm",
                "page": "art. 205",
                "is_official": True,
            },
        )
        constitution_culture, _ = Source.objects.update_or_create(
            title="Constituição Federal — arts. 215–216 (cultura)",
            defaults={
                "institution": "Presidência da República — Casa Civil",
                "edition": "1988 (texto compilado)",
                "url": "https://www.planalto.gov.br/ccivil_03/constituicao/constituicaocompilado.htm",
                "page": "arts. 215–216",
                "is_official": True,
            },
        )
        source_specs = [
            ("Estatuto da Criança e do Adolescente — Lei nº 8.069/1990", "Presidência da República — Casa Civil", "1990 (texto compilado)", "https://www.planalto.gov.br/ccivil_03/leis/l8069.htm", "arts. 4º, 19, 53, 58–59"),
            ("Estatuto da Pessoa Idosa — Lei nº 10.741/2003", "Presidência da República — Casa Civil", "2003 (texto compilado)", "https://www.planalto.gov.br/ccivil_03/leis/2003/l10.741.htm", "arts. 2º–3º, 20–25"),
            ("Lei Brasileira de Inclusão — Lei nº 13.146/2015", "Presidência da República — Casa Civil", "2015 (texto compilado)", "https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13146.htm", "arts. 8º, 27–30"),
            ("Marco Civil da Internet — Lei nº 12.965/2014", "Presidência da República — Casa Civil", "2014 (texto compilado)", "https://www.planalto.gov.br/ccivil_03/_ato2011-2014/2014/lei/l12965.htm", "arts. 2º–3º"),
            ("Estatuto da Igualdade Racial — Lei nº 12.288/2010", "Presidência da República — Casa Civil", "2010 (texto compilado)", "https://www.planalto.gov.br/ccivil_03/_ato2007-2010/2010/lei/l12288.htm", "arts. 1º, 3º, 4º"),
            ("Declaração Universal dos Direitos Humanos", "Organização das Nações Unidas", "1948", "https://www.un.org/en/about-us/universal-declaration-of-human-rights", "arts. 25–27"),
            ("Constituição Federal — arts. 5º, 6º, 196 e 227", "Presidência da República — Casa Civil", "1988 (texto compilado)", "https://www.planalto.gov.br/ccivil_03/constituicao/constituicaocompilado.htm", "arts. 5º, 6º, 196 e 227"),
        ]
        extra_sources = {}
        for title, institution, edition, url, page in source_specs:
            source, _ = Source.objects.update_or_create(title=title, defaults={
                "institution": institution, "edition": edition, "url": url, "page": page, "is_official": True,
            })
            extra_sources[title] = source
        creative_sources = {}
        for title, institution, edition, url in [
            ("Quarto de Despejo: diário de uma favelada", "Carolina Maria de Jesus", "1960", ""),
            ("Vidas Secas", "Graciliano Ramos", "1938", ""),
            ("A Sociedade do Cansaço", "Byung-Chul Han", "2010 (edição original)", ""),
            ("Ilha das Flores", "Casa de Cinema de Porto Alegre · direção de Jorge Furtado", "1989", "https://www.casacinepoa.com.br/filmes/ilha-das-flores/"),
            ("Que Horas Ela Volta?", "Direção de Anna Muylaert", "2015", ""),
            ("Olhos d'Água", "Conceição Evaristo", "2014", ""),
            ("O Karaíba: uma história do pré-Brasil", "Daniel Munduruku", "Obra literária", "https://stoapi.nees.ufal.br/pnld-guias-digitais-prod/guias/publicacoes/PNLD_LITERARIO_ANOS_FINAIS.pdf"),
            ("Vitória", "Globoplay · direção de Andrucha Waddington", "Filme brasileiro, 2025", "https://globoplay.globo.com/vitoria/t/Gg8vLXWZnG/"),
            ("Lei nº 3.270/1885 — Lei dos Sexagenários", "Câmara dos Deputados · Legislação Informatizada", "28 set. 1885", "https://www2.camara.leg.br/legin/fed/leimp/1824-1899/lei-3270-28-setembro-1885-543466-norma-pl.html"),
            ("A integração do negro na sociedade de classes", "Florestan Fernandes · sociologia brasileira", "Tese defendida em 1964; 6ª edição, 2021", "https://www.editoracontracorrente.com.br/product/a-integracao-do-negro-na-sociedade-de-classes"),
            ("Agenda 2030 para o Desenvolvimento Sustentável", "Organização das Nações Unidas", "A/RES/70/1, 2015", "https://sdgs.un.org/2030agenda"),
            ("Constituição da Organização Mundial da Saúde", "Organização Mundial da Saúde", "Adotada em 1946; em vigor desde 1948", "https://www.who.int/about/governance/constitution/"),
            ("Relatório de Síntese do Sexto Ciclo de Avaliação do IPCC", "Painel Intergovernamental sobre Mudanças Climáticas", "AR6 Synthesis Report, 2023", "https://www.ipcc.ch/report/sixth-assessment-report-cycle/2023/"),
        ]:
            source, _ = Source.objects.update_or_create(title=title, defaults={
                "institution": institution, "edition": edition, "url": url, "is_official": False,
            })
            creative_sources[title] = source

        structures = [
            ("Fundamentos da redação", "Entenda a proposta do ENEM, reconheça o problema central e organize as primeiras ideias.", True, [
                ("Comece pela proposta", "O que a prova pede", "Reconhecer o gênero textual e os elementos centrais solicitados na redação.", "A Cartilha do Participante do Enem 2026 descreve a redação como um texto dissertativo-argumentativo, em modalidade escrita formal, sobre tema de ordem social, científica, cultural ou política. O estudante deve defender um ponto de vista apoiado em argumentos coerentes e coesos e apresentar uma proposta de intervenção que respeite os direitos humanos.\n\nEsses elementos são uma orientação oficial sobre o que a produção deve contemplar. As cinco competências são avaliadas separadamente; cada avaliador atribui até 200 pontos por competência. A Cartilha explica esse processo nas páginas 5 e 6.\n\nNesta plataforma, explicações e exercícios ajudam a praticar, mas não substituem a avaliação do INEP e não prometem uma nota específica."),
                ("Uma ideia que se sustenta", "Tese e ponto de vista", "Distinguir o tema amplo de uma tese que assume uma posição discutível.", "O tema indica o assunto. A tese apresenta o ponto de vista que você vai defender sobre esse assunto. Para chegar a uma tese, pergunte: qual aspecto do problema vou discutir e o que penso sobre ele?\n\nExemplo autoral: diante de um tema de estudo sobre acesso à leitura, uma tese pode discutir como a desigualdade de acesso a bibliotecas e a baixa oferta de mediação de leitura dificultam a formação de leitores. Essa formulação é apenas um exemplo didático da RedaWay, não um tema oficial do ENEM.\n\nUma tese útil é específica o bastante para orientar os parágrafos seguintes e aberta o bastante para ser defendida com razões. Evite apenas repetir o tema ou listar palavras relacionadas a ele."),
                ("Do ponto de vista ao plano", "Planejamento antes de escrever", "Rascunhar uma sequência de ideias coerente com o ponto de vista escolhido.", "Antes de redigir, transforme sua tese em um plano curto: registre o problema que pretende discutir, escolha as razões que sustentam seu ponto de vista e pense em como a conclusão pode responder ao problema.\n\nUma forma didática de organizar o texto é apresentar a tese, desenvolver razões em parágrafos e concluir com uma proposta relacionada ao problema. Essa sequência é uma ferramenta de planejamento da RedaWay; a Cartilha define as características avaliadas, mas não exige um número fixo de parágrafos.\n\nAo revisar o plano, confira se cada razão explica algo sobre o problema e se as ideias avançam sem se contradizer."),
            ]),
            ("Construção textual", "Organize introduções, argumentos, parágrafos e conclusões com progressão de ideias.", True, [
                ("A estrutura do texto", "Introdução, desenvolvimento e conclusão", "Compreender como as partes do texto cumprem funções conectadas.", "A redação do Enem é dissertativo-argumentativa. Uma organização possível começa situando o recorte e apresentando uma tese, desenvolve razões que sustentam essa posição e conclui com uma intervenção relacionada ao problema. A Cartilha avalia o texto e as competências; ela não determina uma fórmula fixa de parágrafos.\n\nPergunta de revisão: se alguém lesse apenas a primeira frase de cada parágrafo, conseguiria acompanhar o raciocínio? Se não, talvez falte uma ligação clara entre as partes."),
                ("Aberturas que apresentam o recorte", "Introdução e delimitação", "Abrir o texto sem perder o foco na proposta.", "Uma introdução pode aproximar o leitor do assunto, delimitar qual problema será discutido e anunciar uma tese defensável. Evite começar com uma frase ampla que serviria para qualquer tema; aproxime a contextualização do recorte real da proposta.\n\nExemplo autoral: para um treino sobre acesso à leitura, em vez de ‘A leitura é importante desde sempre’, delimite o desafio: ‘Embora a leitura amplie a participação social, a distribuição desigual de bibliotecas e a falta de mediação dificultam seu acesso em muitas comunidades’. A frase aponta o recorte e prepara argumentos possíveis."),
                ("Da tese aos argumentos", "Planejamento da introdução", "Transformar a tese em razões que podem ser desenvolvidas.", "A tese expressa o ponto de vista; os argumentos explicam por que ele faz sentido. Para planejar, escolha duas razões diferentes que sustentem a tese e que você consiga explicar.\n\nExemplo de treino: tese — ‘barreiras de acesso à leitura reduzem oportunidades de formação’; razões — distribuição desigual de espaços de leitura e ausência de ações regulares de mediação. Essas razões são tópicos de um plano, não parágrafos prontos. Confirme que cada uma responde ao mesmo recorte."),
                ("Construindo parágrafos", "Unidade e progressão", "Relacionar ideia central, explicação e evidência em um parágrafo.", "Um parágrafo argumentativo não é apenas um tópico nem uma citação. Apresente uma ideia, explique o mecanismo que a sustenta, acrescente uma referência ou exemplo pertinente e conecte essa informação à tese.\n\nExemplo esquemático: ‘A falta de bibliotecas próximas restringe o contato cotidiano com livros. Quando o deslocamento é longo e não há transporte acessível, o estudante tem menos oportunidades de frequentar esses espaços. Por isso, ampliar pontos de leitura em equipamentos comunitários pode enfrentar uma barreira concreta’. A sequência mostra ideia, explicação e consequência; adapte o raciocínio à proposta recebida."),
                ("Conectar sem repetir fórmulas", "Coesão e progressão", "Escolher conectivos conforme a relação entre as ideias.", "Conectivos sinalizam relações: ‘além disso’ acrescenta, ‘porém’ contrapõe, ‘por isso’ apresenta consequência e ‘por exemplo’ introduz uma ilustração. Primeiro defina a relação lógica; depois escolha a palavra adequada.\n\nFaça uma revisão local: substitua o conectivo por uma descrição da relação (‘causa’, ‘contraste’, ‘consequência’). Se a palavra escolhida não expressar essa relação, reescreva o período. Não é necessário iniciar todos os parágrafos com um conector diferente."),
                ("Conclusões que respondem ao problema", "Fechamento e intervenção", "Concluir retomando o diagnóstico e propondo uma resposta coerente.", "A conclusão deve dialogar com o problema realmente desenvolvido. Uma proposta precisa indicar uma ação executável, um agente que possa realizá-la, um meio ou modo e um objetivo; detalhes ajudam a explicar como a ação funcionaria.\n\nExemplo autoral para o treino sobre leitura: ‘As secretarias municipais de educação podem ampliar horários de bibliotecas escolares e organizar rodas de leitura com mediadores, para facilitar o acesso de estudantes que vivem longe dos equipamentos culturais’. A proposta liga agente, ação, meio e finalidade ao problema delimitado. Ajuste cada componente ao tema e respeite os direitos humanos."),
            ]),
            ("As cinco competências", "Estude os critérios da matriz do ENEM com explicações e referências rastreáveis.", True, [
                ("Competência 1", "Escrita formal e clareza sintática", "Revisar convenções da escrita, gramática, registro, vocabulário e construção das frases.", "A Competência I observa o domínio da modalidade escrita formal. A Cartilha do Enem 2026 considera a construção sintática e desvios de convenções da escrita, gramática, registro e escolha vocabular.\n\nExemplo autoral para revisar: ‘Os projetos de leitura amplia o acesso, e aproxima estudantes dos livros.’ Há discordância entre ‘projetos’ e ‘amplia/aproxima’; a vírgula também interrompe a ligação entre verbos coordenados. Uma revisão possível é: ‘Os projetos de leitura ampliam o acesso e aproximam estudantes dos livros.’ A correção melhora a concordância e mantém a relação entre as ações.\n\nNa autoanálise, procure: (1) sujeito e verbo de cada oração; (2) concordância e regência; (3) pontuação que represente a estrutura da frase; (4) palavras cujo sentido você domina; (5) períodos completos, sem ambiguidades ou truncamentos. A Cartilha descreve níveis de desempenho e recorrência de desvios; não estabelece uma cota fixa de erros. Este exemplo explica um ponto de revisão, não prevê nota.", "Cartilha do Participante do Enem 2026, pp. 12–13."),
                ("Competência 2", "Tema, gênero e repertório", "Compreender o recorte temático e desenvolver um texto dissertativo-argumentativo em prosa.", "A Competência II avalia a compreensão da proposta e o desenvolvimento do tema no tipo textual solicitado. A redação deve defender um ponto de vista sobre o recorte, em vez de apenas expor informações.\n\nExemplo autoral de análise: para um tema de treino sobre barreiras de acesso à leitura, a tese ‘A distância entre equipamentos culturais e bairros periféricos, somada à pouca mediação, restringe oportunidades de formação leitora’ responde ao recorte e anuncia duas linhas de discussão. A referência ao direito à educação pode ser produtiva se o texto explicar como as barreiras dificultam o exercício desse direito; citar a Constituição sem estabelecer essa relação seria apenas mencionar uma fonte.\n\nAntes de escrever, separe assunto amplo, recorte específico e comando. Depois confira se a tese responde ao recorte, se o texto mantém o gênero dissertativo-argumentativo e se cada repertório é pertinente, explicado e integrado. A Cartilha orienta não copiar os textos motivadores e ir além deles com conhecimentos relacionados. O exemplo é didático, não oficial nem uma previsão de nota.", "Cartilha do Participante do Enem 2026, pp. 14–16."),
                ("Competência 3", "Projeto de texto e argumentos", "Selecionar, relacionar, organizar e interpretar informações em defesa de uma tese.", "A Competência III observa como informações, fatos, opiniões e argumentos são selecionados e organizados para defender um ponto de vista. O projeto de texto é o planejamento que orienta a ordem e a função dos argumentos.\n\nExemplo autoral de análise: tese: ‘A distância até bibliotecas e a ausência de mediação reduzem o acesso contínuo à leitura.’ Argumento 1 pode explicar como tempo e custo de deslocamento reduzem visitas; argumento 2 pode mostrar como atividades de mediação aproximam leitores iniciantes do acervo. A sequência desenvolve duas causas diferentes que sustentam a tese. Se o segundo parágrafo apenas disser ‘a leitura é importante’, sem explicar a relação, a ideia fica afirmada, mas pouco desenvolvida.\n\nNo rascunho, anote para cada argumento: afirmação, explicação do mecanismo, evidência ou exemplo pertinente e vínculo com a tese. Na revisão, procure repetições, saltos de raciocínio e informações sem função. A coerência do projeto é diferente dos conectivos, foco principal da Competência IV. Esta análise é didática e não atribui pontuação.", "Cartilha do Participante do Enem 2026, pp. 28–30."),
                ("Competência 4", "Coesão e encadeamento", "Usar mecanismos linguísticos para ligar ideias e construir a progressão argumentativa.", "A Competência IV observa recursos linguísticos que conectam frases, períodos e parágrafos e explicitam relações entre ideias. A Cartilha destaca operadores argumentativos e recursos de referenciação, como pronomes e expressões nominais.\n\nExemplo autoral de análise: ‘A prefeitura ampliou o horário da biblioteca. No entanto, parte dos estudantes ainda não conhece o serviço.’ ‘No entanto’ sinaliza contraste entre oferta e conhecimento. Em seguida, ‘essa falta de informação’ pode retomar a segunda ideia com referente mais claro do que um pronome vago como ‘isso’. Se o objetivo fosse indicar consequência, seria necessário reorganizar a relação e escolher um conector compatível, como ‘por isso’.\n\nNa revisão, pergunte: que relação lógica existe entre as ideias? O conector expressa essa relação? O pronome tem antecedente identificável? Há repetição desnecessária? Não existe uma quantidade fixa de conectivos: a prioridade é a ligação clara e adequada ao argumento. O exemplo é autoral e não prevê nota.", "Cartilha do Participante do Enem 2026, pp. 31–34."),
                ("Competência 5", "Proposta de intervenção", "Apresentar uma ação relacionada ao problema, articulada ao texto e respeitosa aos direitos humanos.", "A Competência V avalia uma proposta para o problema abordado. Ela deve se relacionar ao tema, ser coerente com o ponto de vista e integrar o projeto do texto. Apenas constatar o problema não constitui uma ação de intervenção.\n\nExemplo autoral de análise: ‘As secretarias municipais de educação devem ampliar os horários das bibliotecas escolares, por meio de equipes de mediação e divulgação nos bairros, para facilitar o acesso dos estudantes à leitura.’ É possível identificar agentes (secretarias), ação (ampliar horários), meios (equipes e divulgação) e finalidade (facilitar o acesso). O trecho pode ficar mais preciso se o texto explicar quais horários e como o serviço alcançaria os estudantes do recorte.\n\nNa autoanálise, confira se a medida enfrenta uma causa discutida, se o agente tem relação plausível com a ação, se o modo de execução está claro e se a finalidade é concreta. Verifique também se a proposta respeita os direitos humanos. Os elementos servem como perguntas de planejamento, não como fórmula obrigatória nem garantia de pontuação. Esta leitura é didática.", "Cartilha do Participante do Enem 2026, pp. 35–37."),
            ]),
            ("Repertório sociocultural", "Relacione conhecimentos a problemas sociais com pertinência e contexto.", True, [
                ("Repertório produtivo", "Referência com função argumentativa", "Explicar como uma referência fortalece a tese.", "Repertório sociocultural é conhecimento que ajuda a interpretar o tema. A Cartilha do Enem 2026 alerta para referências genéricas ou decoradas sem ligação demonstrada. Em vez de perguntar ‘qual frase posso citar?’, pergunte ‘que ideia me ajuda a explicar este problema?’.\n\nExemplo autoral: ao discutir desigualdade de acesso à cultura, o artigo 215 da Constituição pode situar a cultura como direito. Para a referência ser produtiva, o texto precisa explicar que barreira concreta impede esse direito de se realizar e como isso sustenta a tese."),
                ("Fatos, conceitos e obras", "Escolha e verificação de fontes", "Diferenciar uma obra, um conceito e uma afirmação factual.", "Uma referência pode ser uma lei, obra literária, filme, conceito, acontecimento histórico ou dado. Confirme autoria, contexto e sentido antes de usá-la. Um conceito não deve ser atribuído a um autor apenas porque aparece em resumos de internet; um dado precisa de fonte, período e população observada.\n\nA biblioteca da RedaWay apresenta a origem e uma aplicação possível de cada item. Consulte a fonte vinculada e confira se ela sustenta exatamente o que você quer afirmar. Paráfrases devem ser escritas com suas palavras; não invente citações."),
                ("Conectar repertório ao tema", "Pertinência e explicação", "Construir uma ponte explícita entre a referência e o recorte.", "Use uma sequência curta: apresente a referência com precisão, explique a ideia relevante e aplique essa ideia ao aspecto específico do tema.\n\nExemplo autoral: ‘Em Quarto de Despejo, Carolina Maria de Jesus registra sua experiência da pobreza urbana. Essa perspectiva ajuda a discutir como a insegurança alimentar limita a participação social; no tema proposto, porém, é preciso relacioná-la aos dados atuais sobre o grupo e o território em análise’. A referência abre uma leitura, mas não substitui evidências contemporâneas."),
                ("Evitar referências decorativas", "Seleção em vez de acúmulo", "Revisar se cada repertório cumpre uma função no argumento.", "Uma obra famosa não fortalece o texto automaticamente. Se a referência pudesse ser retirada sem alterar a explicação do argumento, talvez esteja decorativa. Também evite empilhar nomes de autores em uma mesma frase sem explicar as ideias.\n\nTeste: complete ‘Esta referência ajuda a defender minha tese porque…’. Se a continuação apenas repetir o tema, busque uma ligação mais específica ou escolha outro repertório. Uma referência bem explicada vale mais, didaticamente, do que várias menções sem função."),
            ]),
            ("Argumentação avançada", "Aprofunde causas, consequências, comparações e fundamentação.", True, [
                ("Explicar causas e mecanismos", "Além de nomear o problema", "Desenvolver a cadeia que liga causa, mecanismo e consequência.", "Dizer que existe desigualdade apenas nomeia um problema. A argumentação avança quando explica como ele se produz: que barreira, decisão, prática ou falta de serviço o mantém? Quem é afetado e de que forma?\n\nRoteiro de raciocínio: causa → mecanismo → consequência → relação com a tese. Use essa sequência como pergunta de planejamento, não como modelo obrigatório de frases. Separe aquilo que a fonte comprova da interpretação que você está propondo."),
                ("Causa, consequência e comparação", "Relacionar evidências", "Usar exemplos e contrastes para esclarecer uma ideia.", "A comparação pode revelar diferenças entre grupos, períodos ou lugares, desde que os casos sejam comparáveis. A exemplificação ilustra uma afirmação, mas um caso isolado não prova que o fenômeno ocorre sempre.\n\nAo usar um dado, explique o que ele mede e como se conecta ao argumento. Evite estatísticas sem ano, fonte ou população. Se não houver evidência suficiente, delimite a afirmação em vez de apresentá-la como verdade universal."),
                ("Desenvolver sem generalizar", "Precisão e nuance", "Reconhecer limites e evitar afirmações absolutas sem sustentação.", "Termos como ‘todos’, ‘nunca’ e ‘sempre’ exigem evidência forte. Prefira delimitar quem, onde e em que condições o problema ocorre. A precisão torna a análise mais convincente porque mostra que você considera a complexidade do tema.\n\nExemplo de revisão: ‘A tecnologia exclui os idosos’ é amplo demais. Uma formulação mais precisa pode identificar que a ausência de recursos acessíveis e de apoio para uso de serviços digitais pode criar barreiras para parte da população idosa."),
                ("Sustentar o ponto de vista", "Coerência do projeto de texto", "Verificar se cada parágrafo acrescenta uma razão relevante.", "Depois de redigir, resuma cada desenvolvimento em uma frase. Confira se os dois resumos sustentam a tese por caminhos distintos e se não se contradizem. Procure explicações incompletas: por que o fato apresentado leva à consequência mencionada? Como essa consequência importa para o tema?\n\nSe um argumento depende de uma informação externa, registre a fonte e confirme a precisão. Se for uma interpretação sua, sinalize o raciocínio que leva a ela."),
            ]),
            ("Preparação para a prova", "Planeje, revise e pratique uma estratégia de escrita para o dia da prova.", True, [
                ("Ler a proposta com atenção", "Tema, comando e textos motivadores", "Identificar o recorte completo antes de começar a escrever.", "Leia a frase temática e marque mentalmente o assunto, o recorte e o espaço social indicado. Repare se a proposta pede causas, desafios, perspectivas ou outra relação. Depois leia os textos motivadores para compreender dados e pontos de partida, sem copiá-los como se fossem repertório externo.\n\nAntes de planejar, explique o tema com suas palavras em uma frase. Confira se sua frase preserva todos os elementos do recorte."),
                ("Montar um plano enxuto", "Tese, argumentos e intervenção", "Distribuir as ideias antes de redigir para manter unidade temática.", "Escreva a tese em uma linha. Liste duas razões diferentes que a sustentam; anote, para cada razão, uma explicação e uma evidência ou referência que você conhece bem. Pense numa intervenção relacionada ao diagnóstico.\n\nEsse rascunho é um mapa, não um molde pronto. Se a tese mudar durante a escrita, revise os argumentos e a conclusão para que continuem conectados."),
                ("Administrar o tempo", "Ritmo de leitura, escrita e revisão", "Reservar tempo suficiente para planejar e reler o texto.", "A distribuição do tempo varia conforme o ritmo de cada estudante e as demais provas do exame. Em simulados, experimente reservar momentos para leitura do tema, planejamento, redação e revisão, e ajuste a divisão com base no que realmente funciona para você.\n\nNão gaste todo o tempo lapidando a primeira frase. Primeiro assegure um projeto coerente; depois refine vocabulário e pontuação. Treine em condições semelhantes às da prova para estimar seu ritmo."),
                ("Revisar com método", "Checklist final", "Encontrar lacunas de conteúdo e problemas de linguagem na revisão.", "Faça duas passagens. Na primeira, confira conteúdo: respondi ao recorte? A tese está clara? Cada argumento foi explicado? A conclusão enfrenta o problema? Na segunda, revise a escrita: concordância, regência, pontuação, acentuação, repetições e palavras com referente confuso.\n\nLeia cada período até o ponto final. Se faltar sujeito, verbo ou ligação lógica, reescreva. Priorize clareza e correção; não troque uma palavra precisa por um sinônimo cujo sentido você não domina."),
                ("Aprender com textos exemplares", "Leitura analítica", "Estudar escolhas de escrita sem decorar uma redação pronta.", "Ao ler uma redação nota 1000, identifique o recorte, a tese, o papel de cada repertório, as relações entre argumentos e a função da intervenção. Depois feche o exemplo e reconstrua o projeto com suas próprias palavras.\n\nUm texto de outra pessoa não deve ser memorizado para encaixar em qualquer tema. A proposta muda; o que pode ser aprendido são decisões de leitura, organização e explicação. A biblioteca RedaWay reúne comentários autorais e links às fontes dos exemplos."),
            ]),
        ]

        for order, (title, summary, is_published, lessons) in enumerate(structures, 1):
            path, _ = LearningPath.objects.update_or_create(
                slug=slugify(title), defaults={"title": title, "summary": summary, "description": summary, "order": order, "is_published": is_published}
            )
            competency_track = title == "As cinco competências"
            if competency_track:
                previous_module = Module.objects.filter(path=path, slug="unidade-inicial").first()
                if previous_module:
                    previous_module.title = "Conteúdo substituído por unidades oficiais"
                    previous_module.save(update_fields=["title"])
                    previous_module.lessons.update(is_published=False)

            initial_module, _ = Module.objects.update_or_create(
                path=path, slug="unidade-inicial", defaults={"title": "Unidade inicial", "summary": "Objetivos e conceitos essenciais", "order": 1}
            )
            module_orders = {}
            for lesson_order, lesson_data in enumerate(lessons, 1):
                module_title, lesson_title, objective, body = lesson_data[:4]
                reference_note = lesson_data[4] if len(lesson_data) > 4 else ""
                if competency_track:
                    module_slug = slugify(module_title)
                    module_orders.setdefault(module_slug, len(module_orders) + 1)
                    module, _ = Module.objects.update_or_create(
                        path=path, slug=module_slug,
                        defaults={"title": module_title, "summary": "Critério oficial e aplicação didática", "order": module_orders[module_slug]},
                    )
                    lesson_slug = slugify(lesson_title)
                    order_in_module = 1
                else:
                    module = initial_module
                    lesson_slug = slugify(module_title)
                    order_in_module = lesson_order
                lesson, _ = Lesson.objects.update_or_create(
                    module=module, slug=lesson_slug, defaults={
                        "title": lesson_title, "summary": module_title, "objective": objective, "body": body,
                        "reference_note": reference_note, "order": order_in_module, "estimated_minutes": 8,
                        "is_published": is_published,
                    }
                )
                if is_published:
                    lesson.sources.add(cartilha)
        Achievement.objects.filter(title="Uma jornada inteira").update(title="Dez passos de estudo")
        for title, description, required in [
            ("Primeiro passo", "Conclua sua primeira aula.", 1),
            ("Ritmo de estudo", "Conclua cinco aulas da sua jornada.", 5),
            ("Dez passos de estudo", "Conclua dez aulas da sua jornada.", 10),
        ]:
            Achievement.objects.update_or_create(title=title, defaults={"description": description, "required_lessons": required})

        repertoire_items = [
            ("Educação como direito social", "law", "Constituição Federal de 1988 · art. 205", "O artigo 205 enquadra a educação como direito de todos e dever do Estado e da família, vinculada ao desenvolvimento da pessoa, ao preparo para a cidadania e à qualificação para o trabalho.", "Direito à educação e responsabilidades públicas", "Pode ajudar a contextualizar discussões sobre acesso, permanência, qualidade e participação na educação. Relacione o dispositivo ao recorte concreto do tema e explique a conexão; a referência não substitui evidências sobre um caso específico.", constitution_education),
            ("Direitos culturais", "law", "Constituição Federal de 1988 · arts. 215–216", "Os artigos 215 e 216 tratam da garantia de direitos culturais e da proteção das manifestações e referências culturais brasileiras.", "Acesso à cultura e proteção da diversidade cultural", "Pode ser relacionado a debates sobre acesso a espaços culturais, valorização de manifestações e proteção de referências culturais. Evite usar o artigo como uma citação decorativa: explique qual aspecto do tema ele ilumina.", constitution_culture),
        ]
        for title, category, origin, explanation, concept, applications, source in repertoire_items:
            slug = slugify(title)
            item, _ = RepertoireEntry.objects.update_or_create(slug=slug, defaults={
                "title": title, "category": category, "origin_author": origin, "context": "Síntese didática da fonte oficial indicada. A formulação é uma paráfrase da RedaWay, não uma citação literal.",
                "explanation": explanation, "central_concept": concept, "applications": applications, "is_published": True,
            })
            item.sources.set([source])

        extra_repertoire = [
            ("Proteção integral de crianças e adolescentes", "law", "Estatuto da Criança e do Adolescente · Lei nº 8.069/1990", "O ECA estabelece prioridade absoluta e reúne direitos ligados à educação, cultura, dignidade e convivência familiar e comunitária.", "Prioridade absoluta e proteção integral", "Use em discussões sobre infância, evasão escolar, violência, acesso à cultura e dever compartilhado entre Estado, família e sociedade. Explique qual direito está em jogo e como a situação concreta revela uma barreira à sua efetivação.", extra_sources["Estatuto da Criança e do Adolescente — Lei nº 8.069/1990"]),
            ("Envelhecimento com dignidade", "law", "Estatuto da Pessoa Idosa · Lei nº 10.741/2003", "O Estatuto assegura direitos às pessoas com 60 anos ou mais e prevê proteção à vida, à saúde, à dignidade, ao respeito e à convivência.", "Dignidade e participação social na velhice", "Pode fundamentar análises sobre etarismo, acesso à saúde, mobilidade, trabalho e participação cultural. Evite reduzir o envelhecimento a uma questão individual: relacione direitos, barreiras sociais e responsabilidades públicas.", extra_sources["Estatuto da Pessoa Idosa — Lei nº 10.741/2003"]),
            ("Acessibilidade como direito", "law", "Lei Brasileira de Inclusão · Lei nº 13.146/2015", "A LBI define a inclusão como garantia de condições de igualdade e trata de acessibilidade, educação, saúde, cultura e participação social.", "Remoção de barreiras e igualdade de oportunidades", "Aplique a temas de educação inclusiva, transporte, trabalho, comunicação e acesso a espaços culturais. Identifique a barreira e proponha uma mudança de ambiente ou serviço, sem atribuir o problema à pessoa com deficiência.", extra_sources["Lei Brasileira de Inclusão — Lei nº 13.146/2015"]),
            ("Direitos e princípios no ambiente digital", "law", "Marco Civil da Internet · Lei nº 12.965/2014", "O Marco Civil estabelece princípios, garantias, direitos e deveres para o uso da internet no Brasil, incluindo liberdade de expressão, privacidade e proteção de dados.", "Direitos fundamentais e responsabilidades online", "Pode apoiar temas sobre cidadania digital, privacidade, discurso de ódio e acesso à informação. Diferencie os princípios legais de uma solução concreta e conecte cada referência à situação discutida.", extra_sources["Marco Civil da Internet — Lei nº 12.965/2014"]),
            ("Igualdade racial e combate à discriminação", "law", "Estatuto da Igualdade Racial · Lei nº 12.288/2010", "O Estatuto busca garantir à população negra a efetivação da igualdade de oportunidades e combater discriminação e intolerância étnica.", "Igualdade de oportunidades e enfrentamento ao racismo", "Relacione a temas de desigualdade racial, acesso a direitos, cultura e participação. Nomeie mecanismos e contextos específicos em vez de tratar o racismo como episódio isolado ou apenas como opinião individual.", extra_sources["Estatuto da Igualdade Racial — Lei nº 12.288/2010"]),
            ("Direitos humanos como referência comum", "law", "Declaração Universal dos Direitos Humanos · ONU", "A Declaração apresenta um horizonte comum de direitos, incluindo educação, participação na vida cultural e condições de vida dignas.", "Universalidade e interdependência dos direitos", "Use para enquadrar temas de dignidade, educação, cultura e proteção social. Para fortalecer a argumentação, aproxime o princípio universal do contexto brasileiro e mostre a distância entre o direito e sua realização.", extra_sources["Declaração Universal dos Direitos Humanos"]),
            ("Saúde como direito de todos", "law", "Constituição Federal · arts. 6º e 196", "A Constituição inclui a saúde entre os direitos sociais e estabelece que ela é direito de todos e dever do Estado, garantida por políticas sociais e econômicas.", "Direito à saúde e ação pública", "Pode ser relacionado a prevenção, acesso a serviços, saúde mental e desigualdades territoriais. Evite afirmar que a lei, sozinha, resolve o problema: use-a para discutir responsabilidades e as condições necessárias à efetivação do direito.", extra_sources["Constituição Federal — arts. 5º, 6º, 196 e 227"]),
        ]
        for title, category, origin, explanation, concept, applications, source in extra_repertoire:
            entry, _ = RepertoireEntry.objects.update_or_create(slug=slugify(title), defaults={
                "title": title, "category": category, "origin_author": origin,
                "context": "Síntese didática autoral baseada na fonte indicada; não é citação literal.",
                "explanation": explanation, "central_concept": concept, "applications": applications, "is_published": True,
            })
            entry.sources.set([source])

        cultural_repertoire = [
            ("Quarto de Despejo e a invisibilidade social", "literature", "Carolina Maria de Jesus · Quarto de Despejo (1960)", "O diário narra a vida de uma mulher negra que sustenta a família na favela do Canindé, em São Paulo, e expõe a pobreza urbana a partir da experiência de quem a vive.", "Desigualdade, fome e direito à cidade", "A obra ajuda a discutir insegurança alimentar, moradia, desigualdade racial e invisibilidade. Apresente-a como testemunho literário situado em seu contexto histórico e conecte uma experiência narrada a evidências mais amplas, sem generalizar a partir de uma única voz.", creative_sources["Quarto de Despejo: diário de uma favelada"]),
            ("Vidas Secas e a desigualdade no campo", "literature", "Graciliano Ramos · Vidas Secas (1938)", "O romance acompanha uma família de retirantes submetida à seca, à pobreza e à precariedade, construindo uma narrativa sobre desamparo e desigualdade social.", "Migração, pobreza e vulnerabilidade socioambiental", "Pode contribuir para temas sobre acesso à água, migração, pobreza rural e efeitos sociais de crises ambientais. Relacione a obra a condições históricas e políticas específicas; ela não substitui dados atuais sobre o problema discutido.", creative_sources["Vidas Secas"]),
            ("Sociedade do desempenho e esgotamento", "philosophy", "Byung-Chul Han · A Sociedade do Cansaço (2010)", "Han analisa como a pressão por desempenho e produtividade pode levar indivíduos a internalizar exigências de rendimento e a formas de esgotamento.", "Produtividade, autocobrança e saúde mental", "Use como lente para discutir saúde mental, cultura do trabalho e cobrança por desempenho. Explique o mecanismo social que a referência ajuda a interpretar e evite tratar a teoria como diagnóstico de toda experiência individual.", creative_sources["A Sociedade do Cansaço"]),
            ("Ilha das Flores e a desigualdade de acesso", "cinema", "Jorge Furtado · curta-metragem Ilha das Flores (1989)", "O curta acompanha o percurso de um tomate para construir uma crítica satírica às relações entre consumo, descarte e desigualdade, expondo a negação de direitos básicos.", "Consumo, fome e dignidade humana", "Pode ser relacionado a insegurança alimentar, desperdício, resíduos e desigualdade. Analise como a montagem e a ironia constroem a crítica; em seguida, conecte a obra a dados e políticas atuais sobre o recorte escolhido.", creative_sources["Ilha das Flores"]),
            ("Que Horas Ela Volta? e as desigualdades do cuidado", "cinema", "Anna Muylaert · filme Que Horas Ela Volta? (2015)", "O filme acompanha uma trabalhadora doméstica e sua relação com a família empregadora, expondo hierarquias de classe, trabalho e pertencimento no espaço doméstico.", "Trabalho doméstico, classe e acesso a oportunidades", "Ajuda a discutir divisão do trabalho de cuidado, desigualdade de classe, direitos trabalhistas e mobilidade social. Aponte as estruturas mostradas pela narrativa sem reduzir o debate a conflitos individuais entre personagens.", creative_sources["Que Horas Ela Volta?"]),
            ("Olhos d'Água e as vozes de mulheres negras", "literature", "Conceição Evaristo · Olhos d'Água (2014)", "A coletânea de contos dá centralidade às experiências de mulheres negras e aborda relações entre memória, pobreza, violência e afeto.", "Representação, gênero e desigualdade racial", "Pode apoiar discussões sobre representatividade, violência de gênero e desigualdades raciais. Contextualize a obra e mostre como a perspectiva narrativa ilumina o tema, sem transformar experiências diversas em uma única realidade.", creative_sources["Olhos d'Água"]),
        ]
        for title, category, origin, explanation, concept, applications, source in cultural_repertoire:
            entry, _ = RepertoireEntry.objects.update_or_create(slug=slugify(title), defaults={
                "title": title, "category": category, "origin_author": origin,
                "context": "Referência cultural contextualizada em síntese autoral da RedaWay.",
                "explanation": explanation, "central_concept": concept, "applications": applications, "is_published": True,
            })
            entry.sources.set([source])

        historical_cultural_entries = [
            ("O Karaíba e os saberes dos povos originários", "literature", "Daniel Munduruku · O Karaíba: uma história do pré-Brasil", "O romance de Daniel Munduruku apresenta uma perspectiva indígena sobre comunidades e modos de vida anteriores à colonização portuguesa.", "Diversidade de saberes e respeito intergeracional", "A referência pode ajudar a discutir diversidade cultural, representação indígena e modos de compreender a relação entre gerações. Contextualize a autoria indígena e não apresente uma obra como representação de todos os povos originários.", creative_sources["O Karaíba: uma história do pré-Brasil"]),
            ("Vitória e o protagonismo na velhice", "cinema", "Filme Vitória (2025) · direção de Andrucha Waddington", "O filme brasileiro acompanha uma mulher idosa que registra a violência em sua vizinhança e decide agir diante da situação.", "Agência, participação e representações da velhice", "Pode contribuir para discutir etarismo e protagonismo de pessoas idosas. A obra permite analisar como uma personagem rompe estereótipos, mas não deve ser usada como prova estatística sobre a população idosa.", creative_sources["Vitória"]),
            ("Lei dos Sexagenários e a história da escravidão", "history", "Lei nº 3.270, de 28 de setembro de 1885", "A chamada Lei dos Sexagenários regulou a extinção gradual da escravidão e previu alforria para pessoas escravizadas a partir de 60 anos, sob condições descritas no texto legal.", "Abolição gradual e limites da liberdade formal", "Em redações, a lei pode contextualizar a forma como idade, escravidão e desigualdade se cruzaram na história brasileira. Consulte o texto da norma e fontes históricas; não a descreva como emancipação plena nem a use sem explicar suas condições e limites.", creative_sources["Lei nº 3.270/1885 — Lei dos Sexagenários"]),
            ("Florestan Fernandes e a integração racial", "sociology", "Florestan Fernandes · A integração do negro na sociedade de classes", "A pesquisa de Florestan Fernandes examina a integração da população negra na sociedade brasileira após a Abolição e questiona a ideia de que a igualdade formal eliminou a desigualdade racial.", "Racismo estrutural e cidadania", "Use para discutir as continuidades da desigualdade racial e os limites de uma igualdade apenas formal. Situe a obra na pesquisa social do século XX e combine a referência histórica com dados atuais, sem atribuir ao livro estatísticas que ele não apresenta.", creative_sources["A integração do negro na sociedade de classes"]),
            ("Agenda 2030 e desenvolvimento sustentável", "sociology", "ONU · Agenda 2030 para o Desenvolvimento Sustentável", "A Agenda 2030 reúne objetivos e metas internacionais sobre temas como educação, redução das desigualdades, cidades sustentáveis, consumo e ação climática.", "Metas públicas e desenvolvimento integrado", "Escolha um objetivo específico e use-o para organizar a pergunta sobre o problema. A Agenda é um compromisso internacional, não prova de que uma meta foi cumprida no Brasil; verifique indicadores e políticas nacionais antes de fazer essa afirmação.", creative_sources["Agenda 2030 para o Desenvolvimento Sustentável"]),
            ("Saúde como bem-estar social", "science", "Constituição da Organização Mundial da Saúde", "A Constituição da OMS apresenta uma compreensão ampla de saúde que inclui dimensões físicas, mentais e sociais, além da ausência de doença.", "Determinantes sociais da saúde", "A referência ajuda a discutir saúde mental, prevenção e condições sociais que afetam o bem-estar. Relacione a dimensão escolhida ao problema e recorra a fontes de saúde pública para afirmações específicas; a definição, sozinha, não comprova a frequência de um fenômeno.", creative_sources["Constituição da Organização Mundial da Saúde"]),
            ("IPCC e a base científica das mudanças climáticas", "science", "IPCC · Relatório de Síntese AR6 (2023)", "A síntese do IPCC reúne avaliações científicas internacionais sobre causas, impactos, riscos e respostas às mudanças climáticas. O relatório atribui o aquecimento observado principalmente às atividades humanas e às emissões de gases de efeito estufa.", "Evidência científica, risco e adaptação", "Use o relatório para contextualizar debates sobre mudanças climáticas, adaptação e justiça ambiental. Identifique a edição e o escopo da conclusão, depois conecte a evidência ao território ou grupo afetado; evite transformar projeções condicionais em previsões inevitáveis.", creative_sources["Relatório de Síntese do Sexto Ciclo de Avaliação do IPCC"]),
        ]
        for title, category, origin, explanation, concept, applications, source in historical_cultural_entries:
            entry, _ = RepertoireEntry.objects.update_or_create(slug=slugify(title), defaults={
                "title": title, "category": category, "origin_author": origin,
                "context": "Referência real apresentada em síntese autoral da RedaWay. Consulte a obra e a fonte vinculada para verificar o contexto.",
                "explanation": explanation, "central_concept": concept, "applications": applications, "is_published": True,
            })
            entry.sources.set([source])

        repertoire_examples = {
            "Educação como direito social": "Exemplo autoral: ‘Embora a educação seja reconhecida como direito de todos, a permanência escolar depende de condições concretas, como transporte, alimentação e apoio pedagógico’. O artigo 205 situa o direito; a argumentação precisa mostrar qual barreira está em foco.",
            "Direitos culturais": "Exemplo autoral: ‘A garantia constitucional dos direitos culturais torna relevante discutir se os moradores de bairros periféricos conseguem acessar espaços de arte e leitura’. A referência abre a análise; dados locais podem demonstrar o obstáculo.",
            "Proteção integral de crianças e adolescentes": "Exemplo autoral: ‘O princípio de prioridade absoluta previsto no ECA reforça que a proteção de crianças e adolescentes deve orientar ações de educação, saúde e cultura’. Em seguida, delimite o direito e a falha que o tema apresenta.",
            "Envelhecimento com dignidade": "Exemplo autoral: ‘O Estatuto da Pessoa Idosa reconhece direitos de dignidade e respeito; por isso, barreiras de mobilidade e práticas etaristas podem ser analisadas como obstáculos à participação social’. Verifique o artigo adequado ao argumento.",
            "Acessibilidade como direito": "Exemplo autoral: ‘A Lei Brasileira de Inclusão orienta a remoção de barreiras, de modo que a ausência de comunicação acessível limita a participação de pessoas com deficiência em serviços públicos’. Especifique a barreira discutida.",
            "Direitos e princípios no ambiente digital": "Exemplo autoral: ‘Os princípios do Marco Civil da Internet permitem discutir como privacidade e liberdade de expressão devem ser consideradas em políticas de convivência digital’. A lei contextualiza direitos; não determina, sozinha, toda solução técnica.",
            "Igualdade racial e combate à discriminação": "Exemplo autoral: ‘O Estatuto da Igualdade Racial oferece uma referência legal para examinar se oportunidades de acesso à educação e ao trabalho estão distribuídas de modo igualitário’. Acrescente evidências atuais e delimite o contexto.",
            "Direitos humanos como referência comum": "Exemplo autoral: ‘A Declaração Universal reconhece a educação como direito; a análise do tema pode então investigar quais barreiras impedem sua concretização em determinado território’. Relacione o princípio amplo ao caso brasileiro.",
            "Saúde como direito de todos": "Exemplo autoral: ‘A Constituição atribui ao Estado o dever de garantir a saúde por políticas sociais e econômicas, o que permite discutir a oferta desigual de prevenção em diferentes territórios’. Use dados confiáveis para sustentar a comparação.",
            "Quarto de Despejo e a invisibilidade social": "Exemplo autoral: ‘O diário de Carolina Maria de Jesus revela a pobreza urbana a partir de uma experiência situada; sua leitura pode abrir uma discussão sobre insegurança alimentar, que deve ser complementada por evidências atuais’. Não generalize uma narrativa individual.",
            "Vidas Secas e a desigualdade no campo": "Exemplo autoral: ‘A trajetória da família de Vidas Secas permite discutir a vulnerabilidade diante da seca e da pobreza rural; no tema contemporâneo, a obra deve ser relacionada a dados sobre água, renda ou migração’. A narrativa não substitui informação atual.",
            "Sociedade do desempenho e esgotamento": "Exemplo autoral: ‘A crítica de Byung-Chul Han à pressão por desempenho pode ajudar a interpretar a autocobrança no trabalho; para sustentar a análise, delimite o grupo e os efeitos discutidos’. Apresente a obra como lente teórica, não como diagnóstico universal.",
            "Ilha das Flores e a desigualdade de acesso": "Exemplo autoral: ‘Ilha das Flores usa ironia para expor relações entre descarte e desigualdade; a obra pode introduzir uma discussão sobre desperdício de alimentos, acompanhada de dados sobre produção e insegurança alimentar’. ",
            "Que Horas Ela Volta? e as desigualdades do cuidado": "Exemplo autoral: ‘A relação entre trabalho doméstico e hierarquia social mostrada em Que Horas Ela Volta? ajuda a discutir a valorização do cuidado; explique como as condições de trabalho e os direitos laborais se conectam ao recorte escolhido’. ",
            "Olhos d'Água e as vozes de mulheres negras": "Exemplo autoral: ‘Os contos de Conceição Evaristo dão centralidade a experiências de mulheres negras e podem apoiar uma discussão sobre representação; evite tratar personagens e vivências diversas como um grupo homogêneo’. ",
            "O Karaíba e os saberes dos povos originários": "Exemplo autoral: ‘A perspectiva indígena construída por Daniel Munduruku em O Karaíba amplia a discussão sobre diversidade de saberes; use a obra para contextualizar a representação e consulte fontes de povos e autores indígenas sobre o recorte específico’. ",
            "Vitória e o protagonismo na velhice": "Exemplo autoral: ‘A personagem idosa do filme Vitória toma iniciativa diante da violência em seu entorno, o que permite discutir agência e estereótipos sobre a velhice’. A obra ilustra uma representação, não prova uma tendência social.",
            "Lei dos Sexagenários e a história da escravidão": "Exemplo autoral: ‘A Lei nº 3.270/1885 mostra que a alforria prevista para pessoas escravizadas a partir de 60 anos estava inserida em um processo gradual e condicionado’. Consulte o texto histórico e explique os limites da medida.",
            "Florestan Fernandes e a integração racial": "Exemplo autoral: ‘A pesquisa de Florestan Fernandes ajuda a questionar a ideia de que a Abolição, por si só, garantiu integração igualitária’. Relacione o contexto histórico da obra a evidências atuais sobre o recorte escolhido.",
            "Agenda 2030 e desenvolvimento sustentável": "Exemplo autoral: ‘O ODS 4 da Agenda 2030 coloca a educação de qualidade entre as metas internacionais; a discussão pode então avaliar que barreiras locais dificultam sua realização’. Não trate o objetivo como resultado já alcançado.",
            "Saúde como bem-estar social": "Exemplo autoral: ‘A compreensão ampla de saúde adotada pela OMS permite analisar como fatores sociais e emocionais também interferem no bem-estar’. Sustente qualquer afirmação específica com dados ou pesquisa de saúde pública.",
            "IPCC e a base científica das mudanças climáticas": "Exemplo autoral: ‘A síntese do IPCC permite contextualizar que as mudanças climáticas têm causas humanas documentadas; o argumento pode avançar para medidas de adaptação que considerem grupos mais expostos’. Indique a fonte e o ano do relatório.",
        }
        for title, example in repertoire_examples.items():
            RepertoireEntry.objects.filter(title=title).update(use_example=example)

        sample_theme, _ = Theme.objects.update_or_create(
            slug="perspectivas-acerca-do-envelhecimento-na-sociedade-brasileira",
            defaults={"title": "Perspectivas acerca do envelhecimento na sociedade brasileira", "category": "Direitos e cidadania", "year": 2025, "origin": Theme.Origin.OFFICIAL, "context": "Tema oficial do Enem 2025, utilizado nas redações comentadas da Cartilha do Participante 2026.", "is_published": True},
        )
        nota_mil_source, _ = Source.objects.update_or_create(
            title="Como é uma redação nota mil do Enem? Conheça 3 exemplos da edição de 2025",
            defaults={
                "institution": "Folha de S.Paulo",
                "edition": "18 mar. 2026",
                "url": "https://www1.folha.uol.com.br/educacao/2026/03/como-e-uma-redacao-nota-mil-do-enem-conheca-3-exemplos-da-edicao-de-2025.shtml",
                "is_official": False,
            },
        )
        g1_essay_source, _ = Source.objects.update_or_create(
            title="Leia redações nota mil do Enem 2025",
            defaults={
                "institution": "g1 / Grupo Globo",
                "edition": "17 mar. 2026",
                "url": "https://g1.globo.com/educacao/enem/2025/noticia/2026/03/17/leia-redacao-nota-mil-do-enem-2025.ghtml",
                "is_official": False,
            },
        )
        full_essays = json.loads((Path(__file__).resolve().parents[2] / "fixtures" / "essay_full_texts.json").read_text(encoding="utf-8"))
        full_essay_by_author = {item["attribution"]: item for item in full_essays}
        essay_author_names = {"Carlos Eduardo": "Carlos Eduardo Gomes dos Santos", "Caio Braga": "Caio Silva Braga", "Wellington Ribeiro": "Wellington Ribeiro"}
        cartilha_examples = [
            ("Carlos Eduardo · redação nota 1000 (Enem 2025)", "Texto integral atribuído à reportagem do g1; análise didática da Folha e da Cartilha do Inep.", "Contexto e tese: a ideia de ‘sociologia das ausências’ apresenta a invisibilidade da população idosa; a tese delimita duas causas — negligência estatal e omissão midiática.\n\nArgumentação: o primeiro eixo conecta falta de ações de saúde e convivência a danos concretos; o segundo relaciona baixa representatividade a estigmas e isolamento. O texto explica os mecanismos das causas antes de encaminhar consequências, o que ajuda a observar a Competência III.\n\nCoesão: expressões como ‘Diante desse cenário’, ‘Consequentemente’ e ‘Outrossim’ organizam a sequência e assinalam relações diferentes. Ao estudar o texto, verifique se cada conectivo corresponde à lógica entre as ideias — não apenas se inicia um parágrafo.\n\nIntervenção: o estudante propõe ações para os serviços de saúde e para os veículos de comunicação, retomando os dois eixos do diagnóstico. Observe os agentes e o vínculo entre cada medida e o problema.\n\nCompetências: o relato permite observar atendimento ao tema (C2), projeto de argumentos (C3), encadeamento (C4) e propostas relacionadas ao problema (C5). A Folha informa que a redação recebeu 1000 pontos; esta síntese não atribui notas por competência nem substitui a correção oficial."),
            ("Caio Braga · redação nota 1000 (Enem 2025)", "Texto integral atribuído à reportagem do g1; análise didática da Folha e da Cartilha do Inep.", "Introdução e tese: O Karaíba, de Daniel Munduruku, contextualiza uma perspectiva indígena de respeito aos mais velhos. A abertura prepara um contraste com a maneira como o envelhecimento é tratado no Brasil e anuncia uma leitura histórica e contemporânea.\n\nArgumentos e repertórios: a Lei dos Sexagenários sustenta a reflexão sobre exclusão no passado; o filme Vitória desloca a discussão para o protagonismo atual. A passagem entre os dois eixos cria progressão temporal. Cada referência recebe explicação e função no argumento, em vez de aparecer como lista de títulos.\n\nCoesão: ‘Nesse contexto’, ‘Historicamente’, ‘Por outro lado’ e ‘Dessa forma’ ajudam a sinalizar contexto, recorte temporal, contraste e fechamento. A Cartilha destaca a continuidade temática e o uso pertinente dos repertórios (2026, pp. 47–49).\n\nConclusão e intervenção: a proposta mobiliza o Ministério da Educação e ações de capacitação e autonomia digital. Ela conversa com a discussão sobre independência e participação.\n\nCompetências: a Cartilha comenta compreensão do tema (C2), repertório produtivo e projeto argumentativo (C3), articulação (C4) e uma proposta compatível com o desenvolvimento (C5). A Folha identifica a nota 1000. Estes comentários são uma leitura didática, sem pontuação própria por competência."),
            ("Wellington Ribeiro · redação nota 1000 (Enem 2025)", "Texto integral atribuído à reportagem do g1; análise didática da Folha e da Cartilha do Inep.", "Introdução e tese: o conto Feliz Aniversário, de Clarice Lispector, apresenta a discussão sobre invisibilidade familiar; o texto amplia o recorte para raízes históricas e descaso governamental. A tese anuncia dois caminhos para os desenvolvimentos.\n\nArgumentação: a referência à Lei dos Sexagenários introduz uma leitura da marginalização histórica; em seguida, a discussão aborda falta de políticas e campanhas públicas para a qualidade de vida. A redação conecta passado e presente, mas não trata a norma histórica como prova suficiente de um fenômeno atual.\n\nCoesão: conectores de continuidade e conclusão orientam o percurso do texto. Ao reler, observe como as expressões retomam as ideias anteriores e como o vocabulário do tema reaparece sem depender de um único termo.\n\nIntervenção: a proposta de debates públicos conduzidos por pessoas idosas atribui agência ao próprio grupo discutido e explicita uma finalidade de enfrentamento à marginalização. Confira se agente, ação, meio e finalidade respondem aos argumentos desenvolvidos.\n\nCompetências: a reportagem identifica a redação como nota 1000 e publica o texto. Esta análise autoral destaca escolhas de recorte, organização, coesão e intervenção; não representa uma correção oficial do Inep."),
        ]
        for title, attribution, analysis in cartilha_examples:
            author = title.split(" ·", 1)[0]
            full_essay = full_essay_by_author[essay_author_names[author]]
            EssayExample.objects.update_or_create(title=title, defaults={
                "slug": full_essay["slug"], "edition_year": 2025, "theme": sample_theme, "source": nota_mil_source,
                "text_source": g1_essay_source, "full_text": full_essay["full_text"],
                "attribution": f"{author}; reportagem do g1 informa nota 1000 no Enem 2025.",
                "permission_note": "Transcrição integral conforme g1; confirme as condições de reprodução antes de publicar fora deste ambiente.",
                "analysis": analysis, "is_published": True,
            })

        theme_items = [
            ("Barreiras de acesso à leitura e a espaços culturais", "Educação e cultura", "Tema de treino autoral para praticar recorte, tese e organização de argumentos. Não é proposta oficial nem previsão do ENEM.", "Quais barreiras podem limitar o acesso a livros, bibliotecas e atividades culturais? Que aspectos do problema dependem de condições locais, políticas públicas ou participação comunitária?", "Investigue barreiras de acesso; relacione a oferta de espaços à mediação de leitura e à participação cultural. Sustente cada argumento com fontes consultadas pelo estudante.", [constitution_education, constitution_culture]),
            ("Convivência respeitosa em ambientes digitais", "Tecnologia e cidadania", "Tema de treino autoral para discutir práticas de convivência e responsabilidades em espaços digitais. Não é proposta oficial nem previsão do ENEM.", "Como conciliar liberdade de expressão, respeito a outras pessoas e participação em comunidades digitais? Que agentes podem contribuir para relações mais seguras?", "Delimite uma prática ou grupo afetado; avalie causas e consequências com fontes confiáveis; considere educação para cidadania e responsabilidades de plataformas e usuários sem generalizações.", []),
            ("Participação de jovens em decisões comunitárias", "Cidadania e juventude", "Tema de treino autoral para praticar a construção de argumentos sobre participação social. Não é proposta oficial nem previsão do ENEM.", "Que condições facilitam ou dificultam a participação de jovens em decisões que afetam sua comunidade? Como criar espaços de escuta e diálogo?", "Analise acesso à informação, canais de participação e retorno às propostas. Diferencie uma opinião pessoal de uma afirmação que precisa de evidências.", [constitution_education]),
        ]
        for title, category, context, questions, argument_paths, sources in theme_items:
            theme, _ = Theme.objects.update_or_create(slug=slugify(title), defaults={
                "title": title, "category": category, "difficulty": Theme.Difficulty.INTRODUCTORY, "origin": Theme.Origin.REDAWAY,
                "context": context, "central_problem": "Transforme o assunto em uma questão delimitada e defensável.",
                "reflection_questions": questions, "argument_paths": argument_paths, "is_published": True,
            })
            theme.sources.set(sources)

        theme_repertoire_map = {
            "Perspectivas acerca do envelhecimento na sociedade brasileira": ["Envelhecimento com dignidade", "Sociedade do desempenho e esgotamento", "Vitória e o protagonismo na velhice", "Lei dos Sexagenários e a história da escravidão", "O Karaíba e os saberes dos povos originários"],
            "Barreiras de acesso à leitura e a espaços culturais": ["Educação como direito social", "Direitos culturais", "Quarto de Despejo e a invisibilidade social", "Olhos d'Água e as vozes de mulheres negras"],
            "Convivência respeitosa em ambientes digitais": ["Direitos e princípios no ambiente digital", "Acessibilidade como direito", "Direitos humanos como referência comum"],
            "Participação de jovens em decisões comunitárias": ["Proteção integral de crianças e adolescentes", "Educação como direito social", "Direitos culturais", "O Karaíba e os saberes dos povos originários"],
        }
        racial_access_theme, _ = Theme.objects.update_or_create(
            slug="obstaculos-a-igualdade-racial-na-educacao-e-no-trabalho",
            defaults={
                "title": "Obstáculos à igualdade racial na educação e no trabalho",
                "category": "Direitos e cidadania",
                "difficulty": Theme.Difficulty.INTERMEDIATE,
                "origin": Theme.Origin.REDAWAY,
                "context": "Tema de treino autoral para analisar como desigualdades raciais podem aparecer em trajetórias escolares e oportunidades de trabalho. Não é proposta oficial nem previsão do Enem.",
                "central_problem": "Que barreiras institucionais e sociais dificultam a igualdade de oportunidades e como podem ser enfrentadas?",
                "reflection_questions": "Como distinguir igualdade formal de acesso efetivo? Que evidências ajudam a descrever diferenças entre grupos? Que responsabilidades cabem a instituições públicas e empregadores?",
                "argument_paths": "Delimite um contexto específico; consulte dados oficiais com recorte de raça e ano; examine mecanismos de discriminação e acesso; proponha medidas avaliáveis sem atribuir o problema a características individuais.",
                "is_published": True,
            },
        )
        racial_access_theme.sources.set([
            extra_sources["Estatuto da Igualdade Racial — Lei nº 12.288/2010"],
            extra_sources["Constituição Federal — arts. 5º, 6º, 196 e 227"],
        ])
        theme_repertoire_map[racial_access_theme.title] = [
            "Florestan Fernandes e a integração racial",
            "Igualdade racial e combate à discriminação",
            "Quarto de Despejo e a invisibilidade social",
            "Olhos d'Água e as vozes de mulheres negras",
        ]
        for theme_title, repertoire_titles in theme_repertoire_map.items():
            theme = Theme.objects.get(title=theme_title)
            theme.repertoires.set(RepertoireEntry.objects.filter(title__in=repertoire_titles))
        sample_theme.sources.add(cartilha)

        exercise, _ = Exercise.objects.update_or_create(
            slug="identificar-uma-tese",
            defaults={
                "title": "Uma tese ou apenas um assunto?",
                "prompt": "Qual alternativa apresenta um ponto de vista que poderia orientar uma argumentação sobre o acesso à leitura?",
                "explanation": "Uma tese apresenta uma posição sobre o assunto e pode ser sustentada por razões. Nomear o assunto sem assumir uma posição ainda não orienta a argumentação.",
                "lesson": Lesson.objects.get(module__path__slug="fundamentos-da-redacao", slug="uma-ideia-que-se-sustenta"),
                "is_published": True,
            },
        )
        choices = [
            ("A leitura, as bibliotecas e os livros no Brasil.", False, "Essa opção reúne tópicos, mas não apresenta uma posição sobre o assunto."),
            ("A ampliação de bibliotecas comunitárias pode reduzir barreiras de acesso à leitura quando vem acompanhada de ações de mediação.", True, "Correto. A frase assume uma posição e indica duas razões que podem ser explicadas e sustentadas."),
            ("Desde muito tempo, a leitura faz parte da vida das pessoas.", False, "A frase faz uma afirmação ampla, mas não apresenta uma posição específica sobre o problema proposto."),
            ("A leitura é importante para a sociedade.", False, "A afirmação expressa uma avaliação genérica, mas ainda não define um problema ou uma linha de argumentação."),
        ]
        for order, (text, is_correct, feedback) in enumerate(choices, 1):
            ExerciseChoice.objects.update_or_create(exercise=exercise, order=order, defaults={"text": text, "is_correct": is_correct, "feedback": feedback})

        focused_exercises = [
            ("construir-uma-tese-delimitada", "Construa uma tese delimitada", "Qual alternativa apresenta uma tese clara para um tema de treino sobre barreiras de acesso à leitura?", "Uma tese precisa responder ao recorte com uma posição que possa ser sustentada por razões.", "construcao-textual", "aberturas-que-apresentam-o-recorte", [
                ("A leitura é importante desde a Antiguidade.", False, "A frase é ampla e não apresenta uma posição sobre as barreiras do recorte."),
                ("A distribuição desigual de bibliotecas e a falta de mediação dificultam o acesso contínuo de estudantes à leitura.", True, "Correto. A tese mantém o recorte e indica dois aspectos que podem ser explicados."),
                ("Livros, escolas, bibliotecas e tecnologia no Brasil.", False, "A lista de assuntos não expressa um ponto de vista."),
            ]),
            ("repertorio-com-funcao", "Um repertório com função", "Como relacionar o artigo 215 da Constituição a uma discussão sobre acesso à cultura?", "O repertório se torna produtivo quando a redação explica como a referência ajuda a interpretar o recorte.", "repertorio-sociocultural", "repertorio-produtivo", [
                ("Citar o número do artigo e seguir para outro assunto.", False, "A citação isolada não explica a relação entre o direito cultural e o tema."),
                ("Apresentar o direito cultural e explicar qual barreira concreta dificulta seu exercício no contexto discutido.", True, "Correto. A alternativa conecta a referência a um problema específico e prepara a argumentação."),
                ("Usar o artigo como prova de que todas as pessoas têm acesso igual à cultura.", False, "A existência de um direito não prova que ele se concretize igualmente em todos os lugares."),
            ]),
            ("aprofundar-cadeia-argumentativa", "Desenvolva o mecanismo do argumento", "Qual sequência aprofunda melhor uma análise sobre falta de bibliotecas em determinado território?", "Um argumento bem desenvolvido explica como uma condição produz efeitos relevantes para a tese.", "argumentacao-avancada", "explicar-causas-e-mecanismos", [
                ("Afirmar que bibliotecas são importantes e repetir o tema na frase seguinte.", False, "A afirmação não explica o mecanismo nem como a falta do serviço afeta o grupo."),
                ("Identificar a distância até os espaços, explicar como ela dificulta a frequência e relacionar essa barreira à tese.", True, "Correto. A resposta encadeia condição, mecanismo e consequência para o argumento."),
                ("Listar um filme, um autor e uma lei sem explicar a relação entre eles.", False, "Acumular referências não substitui a explicação do raciocínio."),
            ]),
            ("ler-o-recorte-da-proposta", "Leia o recorte antes de planejar", "O que deve ser feito antes de escolher repertórios para uma proposta de redação?", "A leitura do tema e do comando delimita o problema que a redação precisa desenvolver.", "preparacao-para-a-prova", "ler-a-proposta-com-atencao", [
                ("Escolher uma citação decorada que possa servir para vários temas.", False, "A referência pode não ter relação com o recorte; primeiro compreenda o que a proposta pede."),
                ("Explicar o tema com as próprias palavras e conferir quais elementos do recorte precisam aparecer.", True, "Correto. Isso ajuda a evitar tangenciamento e orienta a tese."),
                ("Começar pela conclusão para não precisar reler os textos motivadores.", False, "A conclusão depende do problema e dos argumentos que serão desenvolvidos."),
            ]),
        ]
        for slug, title, prompt, explanation, path_slug, lesson_slug, choices in focused_exercises:
            linked_lesson = Lesson.objects.get(module__path__slug=path_slug, slug=lesson_slug)
            exercise, _ = Exercise.objects.update_or_create(slug=slug, defaults={
                "title": title, "prompt": prompt, "explanation": explanation, "lesson": linked_lesson, "is_published": True,
            })
            for order, (text, is_correct, feedback) in enumerate(choices, 1):
                ExerciseChoice.objects.update_or_create(exercise=exercise, order=order, defaults={
                    "text": text, "is_correct": is_correct, "feedback": feedback,
                })

        competency_exercises = [
            ("revisar-modalidade-formal", "Revisão da escrita formal", "Qual frase está mais adequada à modalidade escrita formal?", "A modalidade escrita formal envolve escolha de registro, convenções da escrita e construção sintática.", "escrita-formal-e-clareza-sintatica", [
                ("A gente tem que vê esse problema com mais atenção.", False, "A expressão coloquial e a forma verbal precisam ser revistas para a modalidade formal."),
                ("A ampliação do acesso exige ações contínuas e articuladas.", True, "Correto. A frase apresenta construção completa, vocabulário adequado e concordância regular."),
                ("Esse problema tem muitas causa e precisa ser resolvido.", False, "Há um desvio de concordância nominal em ‘muitas causa’."),
            ]),
            ("reconhecer-recorte-tematico", "Do tema à tese", "Uma proposta de treino discute barreiras de acesso à leitura. Qual tese mantém relação direta com esse recorte?", "A Competência II exige compreensão do recorte proposto e desenvolvimento do tipo textual solicitado.", "tema-genero-e-repertorio", [
                ("A literatura surgiu em diferentes períodos da história.", False, "A frase muda para um assunto amplo e não discute as barreiras de acesso indicadas."),
                ("Ampliar espaços de leitura e ações de mediação pode reduzir barreiras de acesso à formação leitora.", True, "Correto. A posição responde ao recorte e já aponta aspectos que podem ser argumentados."),
                ("A tecnologia está presente em muitas atividades cotidianas.", False, "A frase pode ser verdadeira, mas não desenvolve o tema delimitado."),
            ]),
            ("organizar-projeto-texto", "Organize seu projeto de texto", "Qual plano conecta melhor argumentos a uma tese sobre barreiras de acesso à leitura?", "O projeto de texto organiza razões pertinentes e mostra como elas sustentam o ponto de vista.", "projeto-de-texto-e-argumentos", [
                ("Introdução: citar livros; desenvolvimento: falar de tecnologia; conclusão: repetir o tema.", False, "Os tópicos não apresentam uma linha de raciocínio que desenvolva a tese."),
                ("Tese sobre barreiras de acesso; argumento sobre distribuição de espaços; argumento sobre mediação; conclusão ligada ao problema.", True, "Correto. O plano ordena razões relacionadas e permite explicar como cada uma sustenta a tese."),
                ("Listar todas as ideias lembradas sem escolher as mais pertinentes.", False, "A seleção e a organização são necessárias; uma lista sem hierarquia não mostra um projeto claro."),
            ]),
            ("escolher-relacao-coesiva", "Escolha uma relação coesiva", "Complete: ‘A proposta amplia os horários da biblioteca; ___, parte dos estudantes ainda não conhece o serviço.’ Qual conector sinaliza melhor o contraste?", "A coesão depende de escolher recursos linguísticos de acordo com a relação de sentido entre as ideias.", "coesao-e-encadeamento", [
                ("por isso", False, "Esse conector sinaliza consequência, mas a frase apresenta uma ressalva."),
                ("além disso", False, "Esse conector acrescenta uma informação, mas não explicita o contraste pretendido."),
                ("no entanto", True, "Correto. ‘No entanto’ apresenta uma ressalva em relação à informação anterior."),
            ]),
            ("proposta-intervencao-integrada", "Uma proposta de intervenção concreta", "Qual proposta apresenta uma ação articulada ao problema e respeito aos direitos humanos?", "Uma proposta precisa indicar uma ação para enfrentar o problema, estar ligada ao projeto do texto e respeitar os direitos humanos.", "proposta-de-intervencao", [
                ("É importante que a sociedade se conscientize sobre a leitura.", False, "A frase expressa uma intenção genérica, mas não explicita uma ação nem como realizá-la."),
                ("A prefeitura deve ampliar o horário das bibliotecas de bairro, com equipes de mediação de leitura, para facilitar o acesso dos estudantes.", True, "Correto. A proposta explicita agente, ação, meio e finalidade, e se relaciona ao problema discutido."),
                ("As pessoas que não leem devem ser punidas para mudar de comportamento.", False, "A proposta é punitiva e não respeita direitos; também não oferece uma medida educacional adequada."),
            ]),
        ]
        additional_competency_exercises = [
            ("c1-editar-periodo", "C1 · Revise concordância e pontuação", "Qual versão apresenta concordância e pontuação adequadas?", "Na Competência 1, revise convenções da escrita e a construção dos períodos.", "escrita-formal-e-clareza-sintatica", [("Os projetos de leitura amplia o acesso, e aproxima estudantes dos livros.", False, "Há problema de concordância e vírgula separando termos coordenados."), ("Projetos de leitura ampliam o acesso e aproximam estudantes dos livros.", True, "Correto. Os verbos concordam com o sujeito e a coordenação está clara."), ("Projetos de leitura, amplia o acesso e aproxima os estudantes.", False, "A vírgula separa sujeito e verbo, e a concordância não está adequada.")]),
            ("c2-repertorio-pertinente", "C2 · Avalie a pertinência do repertório", "Para um tema sobre barreiras de acesso à leitura, qual referência está mais bem relacionada?", "Na Competência 2, a referência precisa ser pertinente e articulada ao recorte temático.", "tema-genero-e-repertorio", [("Mencionar uma obra famosa sem explicar sua relação com o tema.", False, "Fama não garante pertinência nem produtividade."), ("Relacionar o direito à educação e à cultura às barreiras concretas de acesso a bibliotecas.", True, "Correto. A referência ajuda a interpretar o recorte e pode ser explicada."), ("Descrever a história de um autor sem conectá-la ao problema.", False, "A informação fica desconectada do tema proposto.")]),
            ("c3-evidencia-e-analise", "C3 · Desenvolva a análise", "Qual trecho mais desenvolve um argumento sobre distância até bibliotecas?", "Na Competência 3, a organização precisa mostrar como as ideias sustentam a tese.", "projeto-de-texto-e-argumentos", [("Bibliotecas são muito importantes para todos.", False, "A afirmação é genérica e não desenvolve mecanismo ou consequência."), ("Quando o equipamento cultural fica distante, o custo e o tempo de deslocamento reduzem a frequência; isso limita oportunidades de leitura no cotidiano escolar.", True, "Correto. O trecho explica condição, mecanismo e efeito ligado à tese."), ("Há bibliotecas, livros, escolas e leitores.", False, "A enumeração não constitui uma linha argumentativa desenvolvida.")]),
            ("c4-retomada-sem-repeticao", "C4 · Retome uma ideia com clareza", "Qual alternativa retoma ‘a falta de transporte até a biblioteca’ sem deixar dúvida sobre o referente?", "Na Competência 4, os mecanismos coesivos devem manter relações claras entre as partes.", "coesao-e-encadeamento", [("Ela é um problema e isso prejudica tudo.", False, "Os pronomes não indicam com precisão a que se referem."), ("Essa dificuldade de deslocamento reduz a possibilidade de frequentar o espaço.", True, "Correto. A expressão retoma a ideia anterior com referente claro."), ("Além disso, contudo, portanto, a situação permanece.", False, "Os conectores acumulados não expressam uma relação lógica definida.")]),
            ("c5-detalhar-agente-e-meio", "C5 · Detalhe a intervenção", "Qual proposta explicita agente, ação, meio e finalidade?", "Na Competência 5, detalhe elementos da proposta e conecte-a ao problema, respeitando os direitos humanos.", "proposta-de-intervencao", [("O governo precisa fazer alguma coisa para melhorar a leitura.", False, "Agente e intenção aparecem de modo vago; faltam ação concreta, meio e finalidade."), ("As secretarias municipais de educação devem ampliar horários de bibliotecas escolares, com equipes e divulgação nos bairros, para facilitar o acesso de estudantes à leitura.", True, "Correto. A proposta explicita responsável, ação, meio e finalidade relacionados ao diagnóstico."), ("Os estudantes devem ser obrigados a ler mais.", False, "A medida não explica meios nem enfrenta barreiras de acesso.")]),
        ]
        competency_exercises.extend(additional_competency_exercises)
        competency_by_slug = {"revisar-modalidade-formal":"C1", "reconhecer-recorte-tematico":"C2", "organizar-projeto-texto":"C3", "escolher-relacao-coesiva":"C4", "proposta-intervencao-integrada":"C5", "c1-editar-periodo":"C1", "c2-repertorio-pertinente":"C2", "c3-evidencia-e-analise":"C3", "c4-retomada-sem-repeticao":"C4", "c5-detalhar-agente-e-meio":"C5"}
        for slug, title, prompt, explanation, lesson_slug, exercise_choices in competency_exercises:
            linked_lesson = Lesson.objects.get(module__path__slug="as-cinco-competencias", slug=lesson_slug)
            item, _ = Exercise.objects.update_or_create(slug=slug, defaults={
                "title": title, "prompt": prompt, "explanation": explanation, "lesson": linked_lesson, "competency": competency_by_slug[slug], "is_published": True,
            })
            for order, (text, is_correct, feedback) in enumerate(exercise_choices, 1):
                ExerciseChoice.objects.update_or_create(exercise=item, order=order, defaults={"text": text, "is_correct": is_correct, "feedback": feedback})

        self.stdout.write(self.style.SUCCESS("Jornada inicial, fontes e quinze exercícios criados ou atualizados."))
