# Ire Tracker — Publicar online

1. Crie um repositório PRIVADO no GitHub e envie os arquivos desta pasta (não envie chaves).
2. Em https://dashboard.render.com escolha **New > Blueprint**, conecte o repositório e selecione o arquivo `render.yaml`.
3. Configure `RIOT_API_KEY` no painel de variáveis de ambiente do Render, nunca no HTML, repositório ou chat.
4. Aguarde o deploy e abra a URL HTTPS fornecida pelo Render.
5. O site sincroniza ao carregar e a cada 5 minutos enquanto a aba estiver visível. O servidor guarda o resultado em cache por 5 minutos para reduzir requisições.
6. Em novos commits no GitHub, o Render poderá republicar o site automaticamente.

**Limitações:** o plano gratuito pode suspender o servidor após inatividade; a primeira visita pode demorar. A chave de desenvolvimento da Riot expira e precisa ser substituída; para operação pública duradoura, verifique aprovação e políticas da Riot. Não é acompanhamento ao vivo de cada evento da partida. Os valores MMR do RankedKings continuam manuais. O armazenamento local do navegador não sincroniza entre dispositivos.

**Segurança:** nunca publique sua chave Riot, e não armazene segredos no GitHub.
