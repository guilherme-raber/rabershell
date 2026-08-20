# Changelog

Todas as mudanças relevantes deste projeto serão documentadas neste arquivo. O formato é
baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/) e o projeto segue
[Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [Unreleased]

### Removido

- Comando público `ping` e contexto `icmp`, alinhando o catálogo à prioridade por ferramentas que
  agregam valor além dos utilitários básicos do sistema.

### Alterado

- `varredura` permanece diretamente na raiz, com `sweep` como alias compatível.
- Autocomplete de `ajuda <comando>` consulta nomes e aliases do registry.
- Seleções concluídas com o mouse no Windows são copiadas automaticamente para o clipboard.

### Adicionado

- Fundação do pacote Python, shell especializado e GUI tkinter.
- Registry declarativo, contextos, aliases, ajuda e sugestões.
- Contexto ICMP com ping seguro e assíncrono na interface.
- Testes e documentação inicial do projeto.
- Sweep ICMP concorrente e cancelável para redes IPv4 CIDR de até 4.096 endereços.
- Superfície única de terminal com histórico protegido, autocomplete contextual e edição da linha
  ativa.
- Infraestrutura reutilizável de eventos de execução e output incremental em tempo real para ping.
- `varredura` como nome canônico pt-BR do comando ICMP, preservando `sweep` como alias.
- Cópia explícita da seleção e colagem protegida por clipboard, botão direito no Windows e seleção
  primária pelo botão do meio no X11.
- Output incremental de hosts responsivos durante `varredura`, sem duplicação no resumo final.
- Rejeição segura de colagens com múltiplas linhas, preservando a entrada atual.
