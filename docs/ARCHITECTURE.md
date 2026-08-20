# Arquitetura

Este documento descreve a arquitetura implementada na versão atual.

## Fluxo de execução

```text
TerminalWindow (tkinter)
  -> ShellSession.execute_events
    -> parser
    -> CommandRegistry / resolução
    -> command handler
    -> PingEngine ou SweepEngine (quando aplicável)
    -> backend ICMP / sistema operacional
  <- CommandEvent (OUTPUT... COMPLETED)
```

`CommandResult` continua trazendo texto, indicação de erro e uma ação estruturada (`CLEAR`, `EXIT`
ou nenhuma). `CommandEvent` representa output parcial, conclusão ou erro da fronteira assíncrona.
Isso impede que handlers manipulem widgets e permite reaproveitar sessão e engines em uma futura
CLI.

## Componentes

### GUI

`TerminalWindow` usa um único widget `Text` para banner, histórico visual, saída, prompt e digitação.
Marcas identificam o início do prompt e da linha editável; eventos de teclado alteram apenas um
`TerminalInputModel`, e a GUI renderiza novamente somente a região posterior ao prompt. O conteúdo
anterior continua selecionável e copiável, mas não pode ser editado.

Comandos comuns são enviados a um executor sequencial. Comandos marcados como controle no registry
usam um executor dedicado; hoje apenas `cancelar` tem essa marca. Workers depositam eventos em uma
fila, verificada periodicamente pela thread do tkinter. Ao receber output, a GUI remove
temporariamente o prompt ativo, insere o chunk e restaura o prompt e o texto ainda em edição. Isso
evita acesso ao tkinter por workers e mistura entre resultado e entrada durante operações longas.

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

`ShellSession.complete` consulta os nomes visíveis do registry. Ele completa comandos e aliases do
contexto atual e reconhece o segundo token de formas explícitas como `icmp sw`. A GUI apenas aplica
o resultado ou apresenta múltiplas correspondências; argumentos não são completados.

### Eventos de execução

`ShellSession.execute_events` passa um `EventSink` explicitamente pelo handler. Um comando pode
emitir zero ou mais `OUTPUT`; a sessão emite um único `COMPLETED` com o `CommandResult` ao retornar.
A mesma thread worker produz os eventos de uma execução, preservando sua ordem. Exceções inesperadas
capturadas na fronteira da GUI tornam-se `ERROR`. Comandos sem streaming continuam emitindo apenas
`COMPLETED`.

### Commands, core e engines

Handlers validam a forma dos argumentos e chamam operações do runtime. `PingEngine` valida destino,
resolve hostname e usa um `PingBackend` injetado. `SweepEngine` valida uma rede IPv4, mantém apenas
uma janela de até 32 probes ativos e consulta um evento de cancelamento antes de agendar novos
endereços. Sintaxe e DNS são etapas separadas. Testes usam backends falsos e não dependem de rede.

### Plataforma

`SystemPingBackend` concentra argumentos específicos: `-n` no Windows e `-c` em Linux/macOS. Para
ping interativo, abre `Popen` com lista de argumentos, `shell=False`, stdout em pipe e stderr
redirecionado ao mesmo fluxo. A leitura sequencial linha a linha emite chunks enquanto o processo
ainda executa. O encoding vem da localidade do sistema e usa substituição previsível para bytes
inválidos. Um timer encerra processos que excedem o limite. Plataformas não suportadas e falhas ao
iniciar produzem erros próprios.

Para sweep, o mesmo backend executa um único echo por endereço com timeout curto específico da
plataforma. A sessão aceita somente um sweep ativo, guarda seu `threading.Event` e o sinaliza por
`cancelar` ou ao fechar a GUI. Probes já iniciados terminam dentro do timeout; novos não são criados.

## Decisões atuais

- layout `src/` reduz imports acidentais da árvore de trabalho;
- runtime usa apenas biblioteca padrão;
- dispatcher permanece junto da sessão enquanto for pequeno;
- saída nativa do ping é preservada nesta versão, sem parser frágil por idioma do SO;
- ping emite a saída nativa incrementalmente e não a duplica no resultado final da GUI;
- todos os comandos passam pelo executor da GUI, simplificando a garantia de responsividade;
- histórico e edição da linha atual são modelados sem dependência de widgets, facilitando testes;
- sweep aceita no máximo 4.096 endereços (`/20`) e não enfileira a rede inteira no executor;
- versão existe somente em `rabershell.__version__` e o pacote a lê dinamicamente.
