# Catálogo de comandos

Este arquivo documenta somente comandos implementados. O registry em `commands/catalog.py` é a
fonte executável dos mesmos metadados.

## Contexto principal — `raber>`

| Comando | Aliases | Sintaxe | Descrição |
|---|---|---|---|
| `ajuda` | `help`, `?` | `ajuda [comando]` | Exibe ajuda contextual |
| `limpar` | `clear` | `limpar` | Limpa a saída da GUI |
| `versao` | `version` | `versao` | Exibe a versão |
| `icmp` | — | `icmp [comando]` | Entra no contexto ou qualifica um comando ICMP |
| `ping` | — | `ping <destino> [--quantidade N]` | Executa ping sem entrar no contexto |
| `sair` | `exit` | `sair` | Encerra a aplicação |

`--count` é alias de `--quantidade`. A quantidade padrão é 4 e o intervalo aceito é 1–20.

## Contexto ICMP — `raber/icmp>`

| Comando | Aliases | Sintaxe | Descrição |
|---|---|---|---|
| `ajuda` | `help`, `?` | `ajuda [comando]` | Exibe ajuda contextual |
| `ping` | — | `ping <destino> [--quantidade N]` | Testa IPv4 ou hostname |
| `voltar` | `back` | `voltar` | Retorna ao contexto principal |

Os comandos globais `limpar`, `versao` e `sair`, com seus aliases, também permanecem disponíveis.

## Formas equivalentes de ping

```text
raber> ping 8.8.8.8
raber> icmp ping 8.8.8.8
raber> icmp
raber/icmp> ping 8.8.8.8
```

Exemplos adicionais:

```text
ping google.com --quantidade 5
ping 127.0.0.1 --count 2
ajuda ping
```

## Planejado

Comandos futuros estão descritos apenas em `ROADMAP.md`; não devem ser considerados disponíveis.

