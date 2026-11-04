# Prontidão para publicação

Revisão em 3 de novembro de 2026. A aplicação passa nas verificações funcionais locais e recebeu configuração-base para GitHub → Render → Supabase. Ainda não está ligada a contas reais nem pronta para receber estudantes.

## Verificações executadas

- `python manage.py test academy`: 8 testes passaram. Cobrem rotas públicas, redirecionamentos de páginas privadas, cadastro fechado, unicidade de e-mail e isolamento, sanitização, salvamento e exclusão de notas.
- `python manage.py check`: sem problemas.
- `python manage.py makemigrations --check --dry-run`: nenhuma migração pendente.
- `python manage.py collectstatic --noinput`: arquivos estáticos coletados.
- `pip check`: sem dependências incompatíveis.
- `python manage.py check --deploy`: sem falhas; os avisos HSTS W005 e W021 são intencionais enquanto o domínio final não for escolhido. Subdomínios e preload não devem ser ativados sem revisar todos os hosts cobertos pelo domínio.
- Render tem um Blueprint em `render.yaml`, com Python nativo, segredos configuráveis, migrações na inicialização, dados iniciais e superusuário de primeiro deploy.
- A configuração aceita `DATABASE_URL` com TLS e nomes de host Render; o armazenamento do avatar pode usar bucket privado Supabase Storage por S3.

Docker não está instalado neste ambiente; a imagem Compose não foi construída. O Blueprint Render, a rede até o Supabase e o bucket não puderam ser validados sem conectar contas e preencher segredos. O diretório Git ainda não tem arquivos versionados nem remoto GitHub configurado.

## Antes de abrir o site ao público

1. Criar o repositório privado no GitHub e enviar os arquivos. Não incluir `.env`, senhas, chaves S3 nem o banco SQLite.
2. Criar o projeto Supabase e um bucket privado para fotos. Copiar do painel a URL de conexão do pooler Supavisor em modo session e os valores S3 (endpoint, região, chave e segredo) para os segredos do Render.
3. Conectar o repositório no Render via Blueprint e preencher a chave e senha temporárias do superusuário. Remover as variáveis `DJANGO_SUPERUSER_*` após o primeiro deploy.
4. Escolher planos de produção que atendam disponibilidade, limites, SMTP e backup. O Blueprint gratuito é para prévia: o Render informa que serviços gratuitos não são destinados à produção, desligam quando ociosos e não têm shell; os arquivos locais também são efêmeros.
5. Validar SMTP em produção, incluindo entrega e recuperação de senha. O Blueprint atual define `REDAWAY_REGISTRATION_ENABLED=1`; revise a privacidade e segurança antes de divulgar o cadastro a estudantes.
6. Configurar domínio, TLS, backups e teste de restauração do Supabase, alertas e monitoramento.
7. Revisar política de privacidade, retenção/exclusão de dados, controles de acesso e operação com crianças e adolescentes antes de cadastrar estudantes reais.
8. Fazer revisão docente do conteúdo e dos exemplos antes de apresentá-los como material pedagógico aprovado; conferir login, recuperação de senha, páginas, imagens e persistência em staging.

O repositório local ainda não tem arquivos versionados nem remoto Git configurado. Para publicar via pipeline, primeiro é necessário enviar o projeto a um remoto sob controle da equipe. Nenhum segredo ou usuário real foi configurado nesta revisão.
