# RedaWay Academy — Fase 0

Data da auditoria: 3 de novembro de 2026  
Escopo original: inspeção do workspace, prontidão do REA, pesquisa pública de referências e proposta inicial. A implementação começou depois que o usuário confirmou este caminho como raiz do produto.

## 1. Estado do repositório

O caminho de trabalho indicado para o produto é `/home/usuario/Área de trabalho/redaway`. Na auditoria inicial, ele continha apenas documentação; portanto, não havia stack, dependências ou histórico legado para preservar. O usuário confirmou esse caminho como raiz do produto; a fundação de aplicação agora está sendo criada nele.

Há uma cópia-fonte da ferramenta REA em outro caminho do ambiente, mas ela é o repositório da ferramenta de engenharia reversa, não o repositório do produto RedaWay. A instalação do pacote REA também não deve ser tratada como parte da aplicação educacional.

**Conclusão:** a arquitetura foi adotada para iniciar a aplicação neste diretório vazio. A auditoria do REA ainda não tem capturas MCP válidas e permanece uma dependência para a investigação mais profunda das plataformas de referência.

## 2. Tecnologias encontradas

Nenhuma tecnologia de aplicação foi encontrada no diretório do produto. Não foram encontrados `package.json`, `pyproject.toml`, `requirements.txt`, `Cargo.toml`, `go.mod`, arquivos de configuração de banco ou estrutura de frontend/backend.

Não recomendo adicionar dependências agora. A proposta abaixo é uma opção de partida de baixo peso, não uma constatação sobre o projeto existente.

## 3. Estado do REA

- CLI instalado: `rea` 6.8.0.
- O diagnóstico somente de leitura informou que o registro MCP do Codex está alinhado em `~/.codex/config.toml` e que o skill REA versão 49 está instalado.
- A lista de ferramentas desta sessão não expõe ferramentas MCP do REA; por isso, o diagnóstico do arquivo de configuração não comprova uma conexão ativa nesta sessão.
- A tentativa de captura de uma página pública pelo CLI terminou em `execution_failure` com `cleanup_incomplete` e sem Evidence. A mensagem do REA não identificou um recurso concreto para liberar. Não foi feita outra captura após essa falha.
- O registro do Codex contém as variáveis `GHIDRA_INSTALL_DIR` e `JAVA_HOME`; a configuração do provedor Ghidra havia passado no diagnóstico escopado anterior. Ghidra não é necessário para a inspeção de páginas web.

**Limite da investigação:** as páginas abaixo foram consultadas por pesquisa e documentação pública oficial. Isso não equivale a observação de fluxo por REA e não gera Evidence do REA. Antes de uma rodada de capturas com REA, é necessário reconectar/reiniciar o cliente e confirmar que as ferramentas do servidor aparecem na sessão; a limpeza incompleta da captura anterior precisa ser resolvida pela recuperação do REA.

## 4. Referências e padrões aproveitáveis

O estudo abaixo separa informação publicada pelas próprias plataformas de escolhas propostas para a RedaWay. A análise de páginas públicas não comprova todos os detalhes internos nem substitui uma captura de fluxo autenticado.

| Plataforma | Observação pública | O que é útil | Adaptação original proposta |
|---|---|---|---|
| Khan Academy | A central de ajuda descreve um relatório de progresso com minutos de estudo, registro de atividades e mudanças de domínio de habilidades, inclusive por quizzes e testes de unidade. [Central de ajuda](https://support.khanacademy.org/hc/en-us/articles/360032987591) | O progresso pode refletir a aprendizagem por habilidade e atividade, não apenas páginas visitadas. | Exibir domínio por competência/objetivo, aulas concluídas e próxima aula recomendada; guardar tentativas e mudanças de progresso no servidor. |
| Duolingo | A documentação pública descreve um caminho sequencial, lições curtas, prática por tipo/erro, metas e sequência diária; a própria empresa diferencia progresso no caminho de atividades alternativas. [Como estudar no Duolingo](https://blog.duolingo.com/duolingo-101-how-to-learn-a-language-on-duolingo/), [guia de prática](https://blog.duolingo.com/guide-to-duolingo-practice-hub/) | Uma rota de aprendizagem clara e prática de revisão dão orientação e retorno frequente. | Mostrar uma jornada com etapas recomendadas e exercícios de revisão, mas deixar a sequência diária e os pontos opcionais. Não punir pausas nem permitir que pontos substituam aprendizagem. |
| Coursera | O catálogo descreve filtros por assunto, instituição, nível e tipo de curso; páginas públicas de cursos exibem módulos com vídeos, leituras e atividades. Há cursos com acesso de auditoria gratuito com recursos limitados. [Catálogo](https://www.coursera.org/browse/), [exemplo de curso e módulos](https://www.coursera.org/learn/support-and-reporting) | A estrutura modular torna visível o tamanho, os materiais e as atividades de cada curso antes de começar. | Cada trilha deve indicar objetivo, duração estimada, módulos, aulas, materiais e exercícios; manter os conteúdos-base gratuitos sem uma camada de compra. |
| Brilliant | A central de ajuda descreve caminhos com ordem recomendada, conceitos interativos e pontos de verificação; seu FAQ destaca problemas práticos, modelos visuais e feedback imediato. [Learning Paths](https://brilliant.org/help/features/what-are-learning-paths/), [FAQ](https://brilliant.org/faq/) | O estudante aplica o conceito durante a aula e recebe feedback no contexto da atividade. | Incorporar exercícios curtos dentro da explicação: identificar tese, ordenar argumento e revisar conectivos; cada resposta deve explicar o raciocínio. |
| Imaginie | A página pública descreve temas, envio de redação, retorno por competência e recomendação de próximo exercício. [Página oficial](https://www.imaginie.com.br/) | Um ciclo de feedback ligado a uma ação seguinte torna o progresso acionável. | Reaproveitar a ideia de apontar a próxima aula com base em competência, sem implementar envio nem correção de redações nesta versão. Evitar promessas de nota ou evolução garantida. |
| Descomplica | A central de ajuda descreve as áreas “Estudar”, “Treinar” e “Explorar”; páginas públicas de redação agrupam aulas por temas e disponibilizam materiais. [Como começar a estudar](https://no.descomplica.com.br/knowledge/por-onde-come%C3%A7o-a-estudar), [Redação](https://descomplica.com.br/d/descomplica/redacao/), [Eixos temáticos](https://descomplica.com.br/d/descomplica/redacao/dissertacao-ssscs8/eixos-tematicos/) | Separar consumo de conteúdo, treino e exploração ajuda diferentes intenções do estudante. | Usar navegação enxuta para Jornada, Trilhas, Treinar e Explorar, com categorias editoriais consistentes para temas e repertórios. |

### Síntese de UX/UI

1. A unidade de navegação deve ser “o que estudar a seguir”, apoiada por uma trilha visível e conteúdo organizado em módulos.
2. Aulas devem alternar explicação, exemplo e aplicação; feedback útil precisa apontar por que uma resposta funciona e que conceito revisar.
3. Progresso deve representar conteúdo e habilidades demonstradas, não abertura de páginas ou tempo de tela isolado.
4. A biblioteca deve permitir busca e filtros, mas não competir com a rota principal de aprendizagem.
5. Reproduzir padrões pedagógicos em uma identidade própria; não copiar textos, ilustrações, marca ou código das referências.

## 5. Materiais do INEP e fontes locais de redação

O usuário informou a pasta `/home/usuario/Downloads/enem`. A fonte normativa prioritária é **A Redação do Enem 2026 — Cartilha do Participante**, publicação INEP/MEC/DAEB. Ela descreve as cinco competências e seus níveis, o texto dissertativo-argumentativo e o limite de 30 linhas. A matriz oficial do Enem também é edição 2026. Na Cartilha, a Competência I avalia convenções da escrita, gramática, registro, vocabulário e construção sintática. Fontes oficiais: [notícia da Cartilha 2026](https://www.gov.br/inep/pt-br/centrais-de-conteudo/noticias/enem/enem-2026-cartilha-da-redacao-esta-disponivel) e [Matrizes de Referência do Enem](https://www.gov.br/inep/pt-br/centrais-de-conteudo/acervo-linha-editorial/publicacoes-institucionais/avaliacoes-e-exames-da-educacao-basica/matrizes-de-referencia-enem).

### Inventário e uso recomendado

| Arquivos locais | Procedência e classificação | Recomendação para o produto |
|---|---|---|
| `cartilha_enem_2026.pdf` (82 páginas) | Cartilha oficial INEP/MEC/DAEB, edição 2026. | Fonte normativa principal; registrar página e edição em cada unidade didática derivada. Conferir atribuição antes de reproduzir trechos. |
| `enem_matriz_de_referencia_v1.pdf` (58 páginas) | Publicação oficial INEP/MEC, matriz de referência 2026. | Consultar para alinhar objetivos do curso ao exame; não substitui a cartilha nos critérios específicos de redação. |
| `Competencia_1.pdf` a `Competencia_5.pdf` | Cinco módulos pedagógicos com bibliografia principalmente de 2016–2019. | Material secundário e datado; aproveitar apenas após conferir afirmações contra a Cartilha 2026. |
| `Situacoes_nota_zero.pdf` (125 páginas) | Material de apoio sobre nota zero; referências incluem cartilhas e edital anteriores. | Usar como apoio histórico; validar regras atuais em edital e documentos INEP do ano pertinente. |
| `redacoes2024.pdf`, `redacoes2024.html` e `redacoesmais.html` | Matéria do G1 sobre redações nota mil de 2024, publicada em 2025. Fonte jornalística, não publicação oficial do INEP. | Exemplos secundários; verificar atribuição e direitos de reprodução antes de publicar. |
| `redacoes2025.pdf` | Captura de matéria do G1 sobre redações nota mil de 2025, publicada em 2026. Fonte jornalística, não oficial. | Mesmas cautelas de proveniência e autorização. |
| `redacoestb.html` | Página da Toda Matéria com exemplos e comentários; fonte educacional de terceiros. | Referência secundária, sujeita a verificação editorial e de direitos. |
| `redacoes1000.pdf` | Impressão de página da plataforma Lume/Turma do Material, com exemplos de várias edições (2020–2024). Não é documento INEP. | Usar somente como pista para localizar textos; obter fonte e autorização originais antes de reutilizar. |
| `not1.pdf`, `not2.pdf`, `tres_redacoes_enem_nota_1000.pdf` | PDFs sem autoria ou vínculo institucional verificável, gerados em novembro de 2026. Incluem prescrições rígidas de conectivos/modelo e citações sem fonte demonstrada. | Não ensinar como regra oficial nem publicar até apurar autoria, referências e precisão. Apresentar exigências de conectivos ou fórmulas fixas somente quando houver suporte documental. |

Em todo o currículo, separar (1) regra oficial com referência e página, (2) interpretação didática autoral e (3) exemplo de terceiros com proveniência/licença verificadas. A presença de um arquivo na pasta não prova autoria ou permissão de reprodução.

## 6. Arquitetura adotada para a primeira versão

**Monólito Django com páginas renderizadas no servidor**, HTML semântico, CSS próprio e JavaScript modular para as poucas interações que precisarem dele. Não usar React, Next.js ou uma SPA separada. Django oferece autenticação, sessões, formulários, proteção CSRF, ORM, migrações e uma base de permissões/admin sem manter vários serviços em paralelo.

**Banco:** PostgreSQL para desenvolvimento integrado e produção, usando o ORM e migrações desde o começo. Para execução local muito simples, SQLite pode ser usado temporariamente, mas a equipe deve rodar testes de integração também em PostgreSQL antes da publicação para evitar divergências de concorrência e SQL.

**Conteúdo:** armazenar conteúdo estruturado no banco para edição e publicação; usar Markdown apenas no corpo editorial quando a validação, renderização segura e versionamento estiverem definidos. Usar identificadores `slug` estáveis; o progresso deve apontar para IDs persistentes, não para o título mutável da aula.

**Execução:** um serviço da aplicação e um banco. Sem Redis, workers ou microserviços na primeira versão. Ativos estáticos servidos diretamente ou por CDN quando houver publicação. Segredos e configurações em variáveis de ambiente.

## 7. Modelo inicial de dados

- `User` (usuário customizado Django, estado da conta, preferências não sensíveis); permissões via grupos e permissões explícitas.
- `LearningPath` → `Module` → `Lesson` (slugs estáveis, ordem, objetivos, conteúdo, estado de publicação).
- `Exercise` → `ExerciseItem` (formato, enunciado, resposta e feedback didático); `ExerciseAttempt` liga usuário, item, resposta, resultado e data.
- `LessonProgress` (usuário, aula, estado, início, conclusão e última posição), com unicidade usuário+aula.
- `Theme` e `RepertoireEntry`, ambos ligados a `Source`; tema deve distinguir fonte oficial de proposta autoral.
- `OfficialDocument` (título, instituição, edição, URL, página e versão) e `EssayExample` com proveniência/licença registrada antes de publicar.
- `WeeklyGoal`, `Achievement`, `UserAchievement` e `ActivityEvent` para recursos de progresso/gamificação da fase posterior.
- `AdminAuditEvent` (ator, ação, objeto, data, campos alterados e metadados mínimos necessários).

Todas as tabelas privadas de estudante devem ser consultadas com o usuário autenticado como escopo no servidor. Identificadores enviados pelo navegador não são prova de autorização.

## 8. Páginas e navegação

- Público: `/`, `/cadastro`, `/login`, `/recuperar-senha`, páginas explicativas/metodologia e catálogo público de trilhas.
- Estudante: `/app` (jornada), `/app/trilhas`, `/app/aulas/<slug>`, `/app/repertorios`, `/app/temas`, `/app/redacoes-exemplares`, `/app/materiais`, `/app/perfil`, `/app/configuracoes`.
- Gestão: `/admin` com verificação de permissão no servidor em cada rota e operação. Ocultar o link do estudante melhora a navegação, mas não é controle de acesso.

## 9. Autenticação e segurança

Usar autenticação nativa do Django com sessão no servidor, hash de senha gerenciado pela framework, formulários validados no servidor, CSRF, cookies `HttpOnly`/`Secure` em produção e recuperação por token de uso limitado enviado ao e-mail. Não usar JWT no navegador nem persistir credenciais em LocalStorage. Aplicar checagem de propriedade em cada consulta de progresso, tentativa, perfil e meta.

Papéis iniciais: estudante, editor de conteúdo, administrador e superadministrador. O superadministrador inicial deve ser criado por comando de gerenciamento protegido e segredo de ambiente, nunca por credencial fixa no código. Usuários comuns não podem alterar o próprio papel; um administrador não pode conceder poderes acima dos seus. Registrar ações administrativas relevantes e confirmações de exclusão/publicação.

Antes de produção, definir retenção, consentimento e exclusão de dados, política de privacidade, canal de solicitação do titular e limites de coleta. Como estudantes podem ser menores, revisar fluxos e dados pessoais com cuidado antes do lançamento.

## 10. Proposta visual

Identidade editorial própria, usando Manrope em navegação e controles, Source Serif 4 apenas em títulos editoriais e textos longos quando melhorar a leitura. Fundo `#F7F6F3`, superfícies brancas, grafite `#242424`, texto secundário `#77736D`, borda `#E8E5DF`; laranja `#F97316` reservado a ações primárias, progresso ativo e estados selecionados. Tema escuro com tokens equivalentes e contraste verificado. Preferência de tema pode ficar em armazenamento local por não ser dado sensível.

```text
┌──────────────────────┬───────────────────────────────────────────────────────┐
│ RedaWay Academy      │ Bom dia, Ana                                          │
│                      │ Sua jornada de redação                                │
│ Início               │                                                       │
│ Minha jornada        │ ┌──────── Continuar estudando ───────────────────────┐ │
│ Trilhas              │ │ Construindo uma tese          Aula 4 de 8         │ │
│ Repertórios          │ │ Objetivo: defender um ponto de vista              │ │
│ Temas                │ │ [ Continuar aula → ]                              │ │
│ Redações exemplares  │ └────────────────────────────────────────────────────┘ │
│ Materiais oficiais   │                                                       │
│                      │ Trilha atual       Competências       Meta semanal    │
│ Perfil               │ progresso discreto  C1–C5 por objetivo  2 de 3 sessões│
│ Configurações        │                                                       │
└──────────────────────┴───────────────────────────────────────────────────────┘
```

Em aula, esconder elementos decorativos, limitar a coluna de leitura a aproximadamente 65–75 caracteres por linha, usar títulos claros e inserir exemplos e exercícios dentro do fluxo. No celular, sidebar vira navegação recolhida e conteúdo passa a uma coluna. Movimento e animação devem ser discretos e respeitar `prefers-reduced-motion`.

## 11. Painel administrativo

Construir uma interface de gestão própria dentro do mesmo design system, mantendo rotas e políticas no servidor. O modelo de conteúdo precisa permitir rascunho, revisão, publicação e histórico mínimo. A matriz inicial deve separar leitura/edição de conteúdo, gestão de contas, gestão de permissões e administração total. Só superadministrador pode conceder o papel de superadministrador; cada operação crítica deve gerar um evento de auditoria.

## 12. Cronograma preliminar

Estimativa de ordem de grandeza para uma pessoa desenvolvendo com assistência e com conteúdo inicial limitado; não inclui produção/revisão de todo o currículo. Cada etapa deve terminar com validação antes da seguinte.

| Etapa | Estimativa | Entrega |
|---|---:|---|
| Fase 0 — auditoria e decisões | 2–4 dias após receber repositório e pasta oficial | inventário validado, decisões e backlog |
| Fundação, banco e autenticação | 2–3 semanas | cadastro, login, sessões, grupos, migrações |
| Design system e páginas públicas | 1–2 semanas | tokens, responsividade, landing e tema |
| Dashboard e perfil | 1–2 semanas | jornada pessoal e preferências |
| Trilhas, aulas, progresso e exercícios | 3–4 semanas | fluxo principal de aprendizagem |
| Temas, repertórios e fontes | 2–3 semanas | bibliotecas com busca e proveniência |
| Administração e auditoria | 2–3 semanas | papéis, gestão de conteúdo/usuários e logs |
| Gamificação e recomendações | 1–2 semanas | metas e conquistas ligadas a estudo real |
| Qualidade e lançamento | 2–3 semanas | testes, acessibilidade, segurança, desempenho e documentação |

Estimativa global: **14–22 semanas**, dependendo do tamanho da equipe, quantidade de aulas produzidas e requisitos de publicação. O intervalo é planejamento, não compromisso de entrega.

## 13. Riscos e dependências

- **Repositório do produto:** o usuário confirmou `/home/usuario/Área de trabalho/redaway` como raiz. O diretório não tinha histórico Git anterior; foi inicializado como novo projeto.
- **REA:** registro local válido, porém sem ferramentas MCP na sessão; captura CLI falhou com limpeza incompleta. Não tratar páginas acessadas por busca como Evidence REA.
- **Conteúdo oficial:** a pasta local foi localizada em `/home/usuario/Downloads/enem`; há documentos oficiais atuais, materiais pedagógicos antigos e exemplos de terceiros ou sem procedência confirmada.
- **Direitos autorais:** redações exemplares, textos motivadores, imagens e trechos longos precisam de licença/proveniência antes de inclusão.
- **Escopo:** auth, isolamento de dados, administração, conteúdo, gamificação e acessibilidade já compõem um produto amplo; priorizar trilhas/aulas e progresso antes de funcionalidades sociais.
- **Privacidade:** definir coleta mínima e política adequada para estudantes menores antes de abrir cadastro público.
- **Dependências:** a implementação local usa Django 6.1.3 e SQLite. PostgreSQL, implantação e SMTP precisam ser definidos antes da produção.

## 14. Próximos passos

1. Continuar o desenvolvimento da fundação no repositório RedaWay já iniciado nesse caminho.
2. Reconectar o MCP REA e resolver a limpeza incompleta antes de novas capturas de referência.
3. Revisar o aviso de privacidade, papéis administrativos e requisitos de implantação antes de usar dados reais ou publicar o serviço.

**Status:** Fase 0 concluída quanto ao workspace e ao inventário documental; pesquisa pública de referências registrada com a limitação de que não equivale a Evidence REA. A fundação da aplicação foi iniciada após confirmação do caminho. A investigação REA continua pendente de reconexão e resolução da limpeza incompleta.
