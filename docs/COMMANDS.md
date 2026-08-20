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
| `sweep` | — | `sweep <rede-cidr>` | Verifica respostas ICMP em uma rede IPv4 |
| `cancelar` | — | `cancelar` | Solicita cancelamento do sweep ativo |
| `sair` | `exit` | `sair` | Encerra a aplicação |

`--count` é alias de `--quantidade`. A quantidade padrão é 4 e o intervalo aceito é 1–20.

## Contexto ICMP — `raber/icmp>`

| Comando | Aliases | Sintaxe | Descrição |
|---|---|---|---|
| `ajuda` | `help`, `?` | `ajuda [comando]` | Exibe ajuda contextual |
| `ping` | — | `ping <destino> [--quantidade N]` | Testa IPv4 ou hostname |
| `sweep` | — | `sweep <rede-cidr>` | Verifica respostas ICMP em uma rede IPv4 |
| `voltar` | `back` | `voltar` | Retorna ao contexto principal |

Os comandos globais `limpar`, `versao`, `cancelar` e `sair`, com seus aliases, também permanecem
disponíveis.

## Interação no terminal

- `Enter` executa a linha; em uma linha vazia, apenas cria um novo prompt.
- `↑` e `↓` percorrem o histórico de comandos da sessão.
- `Home` e `End` movem para o início e o fim do comando atual.
- `Backspace` e `Delete` não atravessam o início da entrada nem alteram o histórico visual.
- `Tab` completa comandos, aliases, contextos e subcomandos explícitos pelo registry.
- Múltiplas correspondências são exibidas sem escolha arbitrária; a linha atual é restaurada.
- `Ctrl+C` copia a seleção. `Ctrl+V` cola somente na linha ativa e converte quebras em espaços.

Durante operações em background, o prompt permanece disponível. Resultados são inseridos antes do
prompt ativo sem destruir o texto digitado, e `cancelar` continua disponível durante um sweep.

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

## Sweep ICMP

As formas abaixo usam o mesmo comando interno:

```text
raber> sweep 192.168.1.0/24
raber> icmp sweep 192.168.1.0/24
raber/icmp> sweep 192.168.1.0/24
```

O argumento deve ser uma rede IPv4 CIDR. Bits de host são normalizados para a rede correspondente.
O limite é 4.096 endereços totais (`/20`); endereços de rede e broadcast não são testados quando
não são hosts válidos. Até 32 probes são executados simultaneamente, cada um com um echo e timeout
curto. Use `cancelar` durante a execução. O resumo lista somente endereços responsivos.

## Planejado

Comandos futuros estão descritos apenas em `ROADMAP.md`; não devem ser considerados disponíveis.
