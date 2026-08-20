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
| `varredura` | `sweep` | `varredura <rede-cidr>` | Verifica respostas ICMP em uma rede IPv4 |
| `cancelar` | — | `cancelar` | Solicita cancelamento da varredura ativa |
| `sair` | `exit` | `sair` | Encerra a aplicação |

`--count` é alias de `--quantidade`. A quantidade padrão é 4 e o intervalo aceito é 1–20.

## Contexto ICMP — `raber/icmp>`

| Comando | Aliases | Sintaxe | Descrição |
|---|---|---|---|
| `ajuda` | `help`, `?` | `ajuda [comando]` | Exibe ajuda contextual |
| `ping` | — | `ping <destino> [--quantidade N]` | Testa IPv4 ou hostname |
| `varredura` | `sweep` | `varredura <rede-cidr>` | Verifica respostas ICMP em uma rede IPv4 |
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
- `Ctrl+C` copia a seleção. `Ctrl+V` cola uma linha somente na entrada ativa.
- Colagens com múltiplas linhas não vazias são rejeitadas integralmente, não executam nada e não
  alteram o rascunho. Linhas vazias adicionais ao redor de uma única linha são ignoradas.
- No Windows, o botão direito cola o clipboard na linha ativa. No X11, o botão do meio cola a
  seleção primária. Nenhuma forma de colagem executa automaticamente ou modifica o histórico.

Durante operações em background, o prompt permanece disponível. Resultados são inseridos antes do
prompt ativo sem destruir o texto digitado, e `cancelar` continua disponível durante uma varredura.

O `ping` apresenta cada linha conforme `ping.exe` ou a ferramenta equivalente a produz. Ao final,
o stdout não é repetido. Erros de validação ou de inicialização continuam aparecendo como mensagens
estruturadas. A `varredura` apresenta cada host responsivo quando descoberto e termina com um
resumo que não repete os endereços.

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

## Varredura ICMP

As formas abaixo usam o mesmo comando interno:

```text
raber> varredura 192.168.1.0/24
raber> icmp varredura 192.168.1.0/24
raber/icmp> varredura 192.168.1.0/24
```

`sweep` é alias compatível do comando canônico `varredura` nas três formas.

O argumento deve ser uma rede IPv4 CIDR. Bits de host são normalizados para a rede correspondente.
O limite é 4.096 endereços totais (`/20`); endereços de rede e broadcast não são testados quando
não são hosts válidos. Até 32 probes são executados simultaneamente, cada um com um echo e timeout
curto. Use `cancelar` durante a execução. Cada endereço responsivo aparece em ordem de descoberta;
o resumo final informa rede, quantidade verificada, total responsivo e duração, sem repetir a lista.

## Planejado

Comandos futuros estão descritos apenas em `ROADMAP.md`; não devem ser considerados disponíveis.
