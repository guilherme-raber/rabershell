# Arquitetura

Este documento descreve a arquitetura implementada na versão atual.

## Fluxo de execução

```text
TerminalWindow (tkinter)
  -> ShellSession.execute
    -> parser
    -> CommandRegistry / resolução
    -> command handler
    -> PingEngine ou SweepEngine (quando aplicável)
    -> backend ICMP / sistema operacional
  <- CommandResult
```

`CommandResult` traz texto, indicação de erro e uma ação estruturada (`CLEAR`, `EXIT` ou nenhuma).
Isso impede que handlers manipulem widgets e permite reaproveitar a sessão em uma futura CLI.

## Componentes

### GUI

`TerminalWindow` cria saída rolável, prompt, entrada e histórico em memória. Comandos comuns são
enviados a um executor sequencial. Comandos marcados como controle no registry usam um executor
dedicado; hoje apenas `cancelar` tem essa marca. A conclusão volta à thread principal com
`Tk.after`, e somente essa thread altera widgets. A entrada permanece disponível durante operações
longas para que o cancelamento não fique atrás do sweep na fila, sem tornar os demais comandos
concorrentes entre si.

### Parser e sessão

O parser converte a linha em tokens e rejeita aspas incompletas. Não interpreta pipes,
redirecionamentos ou sintaxe de shell. `ShellSession` possui o contexto (`root` ou `icmp`), produz o
prompt, resolve invocações e converte falhas conhecidas em mensagens pt-BR.

### Registry e despacho

`CommandRegistry` é a fonte única para nome canônico, aliases, contexto, exposição na raiz,
descrição, uso, exemplos e handler. A ajuda é renderizada desses metadados. O dispatcher embutido
na sessão resolve:

1. comando visível no contexto atual;
2. comando de contexto explicitamente qualificado, como `icmp ping`;
3. sugestão por similaridade quando não há correspondência.

O mesmo `CommandSpec` e handler de ping é visível em `root` e `icmp`; não há duplicação.

### Commands, core e engines

Handlers validam a forma dos argumentos e chamam operações do runtime. `PingEngine` valida destino,
resolve hostname e usa um `PingBackend` injetado. `SweepEngine` valida uma rede IPv4, mantém apenas
uma janela de até 32 probes ativos e consulta um evento de cancelamento antes de agendar novos
endereços. Sintaxe e DNS são etapas separadas. Testes usam backends falsos e não dependem de rede.

### Plataforma

`SystemPingBackend` concentra argumentos específicos: `-n` no Windows e `-c` em Linux/macOS. O
subprocesso recebe lista de argumentos, `shell=False`, timeout e captura de saída. Plataformas não
suportadas e executável ausente produzem erros próprios.

Para sweep, o mesmo backend executa um único echo por endereço com timeout curto específico da
plataforma. A sessão aceita somente um sweep ativo, guarda seu `threading.Event` e o sinaliza por
`cancelar` ou ao fechar a GUI. Probes já iniciados terminam dentro do timeout; novos não são criados.

## Decisões atuais

- layout `src/` reduz imports acidentais da árvore de trabalho;
- runtime usa apenas biblioteca padrão;
- dispatcher permanece junto da sessão enquanto for pequeno;
- saída nativa do ping é preservada nesta versão, sem parser frágil por idioma do SO;
- todos os comandos passam pelo executor da GUI, simplificando a garantia de responsividade;
- sweep aceita no máximo 4.096 endereços (`/20`) e não enfileira a rede inteira no executor;
- versão existe somente em `rabershell.__version__` e o pacote a lê dinamicamente.
