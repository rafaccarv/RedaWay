# RedaWay Academy

Plataforma gratuita para aprender redação do ENEM. Esta base usa Django 6.1, HTML renderizado no servidor, CSS e JavaScript sem framework de frontend. Não usa React.

## Rodar localmente

Linux/macOS:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py setup_roles
python manage.py seed_curriculum
python manage.py seed_historical_essays
python manage.py createsuperuser
python manage.py runserver
```

Abra `http://127.0.0.1:8000/`. O SQLite local fica em `db.sqlite3` e não é versionado; fotos locais ficam em `media/`, também fora do Git. Em desenvolvimento, e-mails de recuperação de senha aparecem no terminal do servidor. Para produção, configure um serviço SMTP e as variáveis descritas em `.env.example`.

O comando `createsuperuser` solicita e-mail, nome e senha no terminal; nenhuma credencial administrativa padrão existe no código. Entre em `/admin/` com essa conta para cadastrar trilhas, módulos e aulas. Conteúdo só aparece publicamente quando a trilha e a aula estão marcadas como publicadas.

## O que está implementado nesta fundação

- Conta individual por e-mail, cadastro, sessão, login e logout por POST; e-mail único sem distinção entre maiúsculas e minúsculas.
- Foto de perfil opcional no cadastro e editável na conta; imagem servida por rota autenticada, sem perfis públicos ou interação entre estudantes.
- Ambiente Notas separado na navbar, com criação, edição, busca, tema, formatação, grifo e salvamento automático após a criação; cada nota pertence à conta e seu HTML permitido é sanitizado.
- Recuperação e alteração de senha pela autenticação do Django.
- Perfil básico do estudante.
- Seis trilhas publicadas, com aulas sobre fundamentos, construção textual, cinco competências, repertório, argumentação e preparação para a prova.
- Biblioteca de repertórios pesquisável por categoria e termo; cada referência abre uma página própria com contexto, ideia central, aplicações, exemplo autoral, fontes e temas relacionados.
- Biblioteca com 27 redações nota 1000, três por edição de 2017 a 2025. Cada uma tem página individual e análise pedagógica separada; os textos disponíveis nos arquivos fornecidos foram transcritos, e as demais páginas abrem a cartilha ou reportagem de origem.
- Temas oficiais e autorais com filtros; cinco temas publicados são identificados por origem e relacionados a repertórios da biblioteca.
- Oficina de redação com dicas, exemplos comentados de tese/argumento/intervenção e planejador de ideias com impressão/PDF local.
- Quinze exercícios publicados, incluindo dois exercícios por competência do ENEM, com feedback por alternativa e tentativas salvas; dashboard com acertos recentes por competência e recomendação de aula ainda não concluída.
- Dashboard e marcação de conclusão protegidos por autenticação e CSRF.
- Tema claro em off-white ou noturno, menu global, sidebar recolhível, responsividade e navegação por teclado.
- Administração de conteúdo e usuários pelo Django Admin; migrações incrementais e conteúdo inicial repetível pelos comandos `seed_curriculum` e `seed_historical_essays`.
- Fluxo de recuperação e exclusão de conta, com aviso de privacidade de desenvolvimento.

A oficina organiza ideias no navegador e não envia nem salva o rascunho na conta. Não existe ferramenta de envio nem correção de redações. O acompanhamento por competência descreve apenas o desempenho nos exercícios, sem atribuir nota oficial ou declarar domínio. O currículo ainda aguarda revisão docente; consulte [o roteiro](docs/revisao-pedagogica.md).

## Produção

O desenvolvimento local continua usando SQLite e Docker Compose pode ser usado para testar com PostgreSQL. Para a arquitetura de publicação GitHub → Render → Supabase, existe um Blueprint em `render.yaml`: o Render instala as dependências Python, coleta estáticos, aplica migrações e, no primeiro deploy, cria os dados iniciais e o superusuário. As fotos são armazenadas em um bucket privado do Supabase Storage, não no disco efêmero do Render.

Configure no Render a `DATABASE_URL` do Supabase usando o pooler Supavisor em modo session (porta 5432), além das credenciais S3 de servidor do bucket privado. A conexão direta do Supabase pode ser somente IPv6; use o endereço do pooler exibido no painel quando necessário. Configure e teste SMTP antes de depender da recuperação de senha. O cadastro está habilitado no Blueprint do Render; conclua a revisão de privacidade e segurança antes de divulgar o serviço para estudantes. Os três valores `DJANGO_SUPERUSER_*` são usados apenas no primeiro deploy; remova-os do ambiente do Render depois que o superusuário for criado.

O Blueprint está marcado como plano gratuito para prévia, não para receber estudantes reais: o Render desliga serviços gratuitos ociosos, não oferece shell para eles e restringe SMTP nas portas usuais; os limites do banco gratuito do Supabase também precisam ser avaliados. Para uso público contínuo, revise os planos e custos, escolha região e configure domínio, SMTP, backups e monitoramento. Não divulgue o serviço para estudantes até a revisão de privacidade para crianças e adolescentes. Consulte o [roteiro de publicação](docs/prontidao-publicacao.md).

Para o ambiente Docker/PostgreSQL, configure o `.env` a partir do exemplo de produção, troque todos os valores demonstrativos e rode `docker compose up --build -d`. Em uma instalação nova, inicialize os dados e crie a conta administrativa com:

```bash
docker compose exec app python manage.py setup_roles
docker compose exec app python manage.py seed_curriculum
docker compose exec app python manage.py seed_historical_essays
docker compose exec app python manage.py createsuperuser
```

O Compose expõe a aplicação apenas em `127.0.0.1:8000`. Antes de receber tráfego público, configure um proxy reverso com TLS que encaminhe para essa porta e sobrescreva `X-Forwarded-Proto` com o protocolo recebido; a aplicação confia nesse cabeçalho em produção. Só habilite cadastro depois de validar o envio SMTP. SMTP, domínio, TLS público, backups, monitoramento e hospedagem real ainda dependem de provedor e credenciais. Não abra cadastro nem receba dados reais antes de fechar as pendências de privacidade, incluindo a avaliação para crianças e adolescentes. O servidor `runserver` é apenas para desenvolvimento.

## Documentação

- [Auditoria e decisões da Fase 0](docs/fase-0-auditoria.md)
- [Prontidão para publicação e itens de lançamento](docs/prontidao-publicacao.md)
- [Estado e decisões de implementação](docs/decisoes-tecnicas.md)
- [Roteiro de revisão pedagógica docente](docs/revisao-pedagogica.md)
