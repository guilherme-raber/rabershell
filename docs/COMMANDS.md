# Catálogo de comandos

Este arquivo documenta somente comandos implementados. O registry em `commands/catalog.py` é a
fonte executável dos mesmos metadados.

## Contexto principal — `raber>`

| Comando | Aliases | Sintaxe | Descrição |
|---|---|---|---|
| `ajuda` | `help`, `?` | `ajuda [comando]` | Exibe ajuda contextual |
| `limpar` | `clear` | `limpar` | Limpa a saída da GUI |
| `versao` | `version` | `versao` | Exibe a versão |
| `varredura` | `sweep` | `varredura <rede-cidr>` | Verifica respostas ICMP em uma rede IPv4 |
| `cancelar` | — | `cancelar` | Solicita cancelamento da varredura ativa |
| `sair` | `exit` | `sair` | Encerra a aplicação |

Não há contextos públicos na versão atual.

## Interação no terminal

- `Enter` executa a linha; em uma linha vazia, apenas cria um novo prompt.
- `↑` e `↓` percorrem o histórico de comandos da sessão.
- `Home` e `End` movem para o início e o fim do comando atual.
- `Backspace` e `Delete` não atravessam o início da entrada nem alteram o histórico visual.
- `Tab` completa comandos e aliases pelo registry.
- No primeiro argumento de `ajuda`, `Tab` completa nomes e aliases do mesmo registry, como
  `ajuda var<Tab>` → `ajuda varredura`.
- Múltiplas correspondências são exibidas sem escolha arbitrária; a linha atual é restaurada.
- `Ctrl+C` copia a seleção. `Ctrl+V` cola uma linha somente na entrada ativa.
- Colagens com múltiplas linhas não vazias são rejeitadas integralmente, não executam nada e não
  alteram o rascunho. Linhas vazias adicionais ao redor de uma única linha são ignoradas.
- No Windows, soltar o botão esquerdo após uma seleção não vazia a copia imediatamente para o
  clipboard; clique sem seleção não o altera. O botão direito cola na linha ativa.
- No X11, selecionar disponibiliza a seleção primária e o botão do meio a cola. Nenhuma colagem
  modifica o histórico ou executa texto.

Durante operações em background, o prompt permanece disponível. Resultados são inseridos antes do
prompt ativo sem destruir o texto digitado, e `cancelar` continua disponível durante uma varredura.

## Varredura

```text
raber> varredura 192.168.1.0/24
```

`sweep` é alias compatível do comando canônico `varredura`; ambos resolvem para a mesma
implementação.

O argumento deve ser uma rede IPv4 CIDR. Bits de host são normalizados para a rede correspondente.
O limite é 4.096 endereços totais (`/20`); endereços de rede e broadcast não são testados quando
não são hosts válidos. Até 32 probes são executados simultaneamente, cada um com um echo ICMP e
timeout curto. Use `cancelar` durante a execução. Cada endereço responsivo aparece em ordem de
descoberta; o resumo final não repete a lista.

## Planejado

Comandos futuros estão descritos apenas em `ROADMAP.md`; não devem ser considerados disponíveis.
