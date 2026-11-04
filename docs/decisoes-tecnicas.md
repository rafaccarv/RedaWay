# RedaWay Academy — estado da implementação

Atualizado em 3 de novembro de 2026.

## Base técnica

- Projeto iniciado em `/home/usuario/Área de trabalho/redaway`; o diretório não continha uma aplicação nem histórico Git prévio.
- Django 6.1.3 com Python 3.13.5, HTML de servidor, CSS e JavaScript simples; sem React ou serviços em segundo plano.
- SQLite para desenvolvimento local. O caminho de produção previsto é PostgreSQL.
- Usuário customizado, autenticado por e-mail; senha e sessão são geridas pelo Django.
- Progresso de aula pertence ao usuário no banco e tem unicidade por estudante+aula.
- Preferência de tema é a única persistência no navegador e não contém dado de conta.
- Django Admin protege operações de conteúdo e conta por sessão, staff e permissões do servidor.

## Etapas

1. **Fase 0 — auditoria:** inventário, recomendações e limites da investigação registrados em [fase-0-auditoria.md](fase-0-auditoria.md). A conexão REA continua pendente; o relatório não apresenta pesquisa pública como Evidence REA.
2. **Fase 1 — fundação:** estrutura Django, configuração local, modelo customizado de conta, conteúdo e progresso, autenticação, senha, perfil, exclusão de conta e admin com grupos de função criados.
3. **Fase 2 — design system:** identidade laranja/grafite, modo claro/escuro, sidebar recolhível, navegação responsiva, componentes de formulário e páginas iniciais implementados.
4. **Fase 3 — experiência pública/estudante:** landing, cadastro, login, dashboard, perfil, configuração de senha e aviso de privacidade de desenvolvimento disponíveis.
5. **Fase 4 — aprendizagem:** seis trilhas publicadas, com aulas de fundamentos, construção textual, cinco competências, repertório, argumentação avançada e preparação para a prova. A conclusão, pontos, sequência e progresso por estudante são persistidos.
6. **Fase 5 — bibliotecas e oficina:** acervo de repertórios ampliado para 22 referências contextualizadas em sete categorias; cinco temas oficiais e autorais têm filtros e repertórios relacionados; três redações nota 1000 têm páginas individuais, texto integral atribuído ao g1 e análise pedagógica separada com fonte da análise. Oficina inclui dicas, exemplos de escrita e planejador de ideias processado no navegador. Não há envio nem correção de redações, conforme decisão do produto.
7. **Fase 6 — administração:** cadastro de fontes, aulas, temas, repertórios, exercícios, usuários e metas via Django Admin; grupos para Estudante, Editor de conteúdo e Administrador. O superadministrador é criado pelo comando interativo do Django.
8. **Fase 7 — acompanhamento:** quinze exercícios no seed, dez ligados explicitamente a C1–C5 (dois por competência); o dashboard resume as tentativas mais recentes por exercício e recomenda a competência de menor aproveitamento. A taxa só aparece com respostas em pelo menos dois exercícios distintos e não é apresentada como nota oficial ou domínio definitivo.
9. **Fase 8 — preparo de produção:** Dockerfile, Compose com PostgreSQL, Gunicorn e WhiteNoise; cadastro fechado por padrão em produção; exigência de chave secreta longa; proteção de cookies, HTTPS e cabeçalhos de segurança. `manage.py check --deploy` passou com variáveis representativas de produção.

## Limites antes de produção

- Não foi possível iniciar PostgreSQL aqui: não há Docker nem cliente/servidor PostgreSQL instalados. O Compose está preparado, mas não executado.
- Configurar provedor de hospedagem, DNS/domínio, TLS e SMTP usando contas e credenciais reais; nenhum serviço externo está provisionado.
- Fechar a política de privacidade com identidade/canal do controlador, base legal, retenção de contas e logs administrativos, backups, fornecedores e atendimento aos direitos.
- Avaliar LGPD e ECA Digital para crianças/adolescentes com profissionais qualificados; o cadastro de produção permanece desativado até isso ser concluído.
- Rever e ampliar permissões por função e auditoria dedicada antes de produção; o Django Admin registra alterações e oferece controles básicos.
- Revisar contraste com ferramentas de acessibilidade e testar em leitores de tela e dispositivos reais.
- Fazer revisão docente documentada das aulas, exercícios, repertórios e análises. O status atual de todo o acervo é “aguardando revisão docente”; ver [roteiro pedagógico](revisao-pedagogica.md).
- Não publicar arquivos de origem desconhecida.
- Capturas das plataformas por REA ainda dependem de reconectar o MCP e resolver o erro de limpeza anotado na auditoria.
