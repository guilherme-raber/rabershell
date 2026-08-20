# Arquitetura

Este documento descreve a arquitetura implementada na versão atual.

## Fluxo de execução

```text
TerminalWindow (tkinter)
  -> ShellSession.execute_events
    -> parser
    -> CommandRegistry / resolução
    -> command handler
    -> SweepEngine (quando aplicável)
    -> backend de probe / sistema operacional
  <- CommandEvent (OUTPUT... COMPLETED)
```

`CommandResult` traz texto, indicação de erro e ação estruturada. `CommandEvent` representa output
parcial, conclusão ou erro da fronteira assíncrona. A GUI não conhece diagnóstico, engines ou
subprocessos.

## Componentes

### GUI

`TerminalWindow` usa um único `Text` para banner, histórico, saída, prompt e digitação. Marcas
protegem todo conteúdo anterior à linha atual; o `TerminalInputModel` é a única fonte de edição.
Workers depositam eventos em fila thread-safe, consumida exclusivamente pela thread do tkinter. Ao
chegar output, a GUI preserva seleção, prompt e rascunho.

`Ctrl+C` copia sem editar. Toda colagem passa pelo modelo ativo: uma linha é aceita sem execução
automática e múltiplas linhas não vazias são rejeitadas atomicamente. No Windows, botão direito usa
o clipboard; no X11, a seleção exportada fica disponível como PRIMARY e o botão do meio a cola.
No Windows, `<ButtonRelease-1>` agenda a cópia por `after_idle`, permitindo que o binding de classe
do `Text` finalize a seleção antes da leitura. Seleção vazia não modifica o clipboard.

### Parser, sessão e contextos

O parser tokeniza apenas a gramática interna e rejeita aspas incompletas; não interpreta pipes,
redirecionamentos ou sintaxe de shell. `ShellSession` mantém prompt, despacho e operação cancelável.
A infraestrutura genérica de contextos permanece no registry e na sessão para uso futuro, mas
nenhum contexto público está registrado atualmente.

### Registry e despacho

`CommandRegistry` é a fonte única para nome canônico, aliases, contexto, exposição, descrição, uso,
exemplos e handler. Ajuda, sugestões e autocomplete derivam desses metadados. `varredura` e seu
alias `sweep` resolvem para o mesmo `CommandSpec` e handler na raiz.
O autocomplete normalmente atua no comando. A única regra de argumento atual é `ajuda <comando>`:
o primeiro argumento consulta os mesmos nomes e aliases visíveis do registry.

### Eventos de execução

`ShellSession.execute_events` passa um `EventSink` ao handler. Um comando emite zero ou mais
`OUTPUT`, seguido de um único `COMPLETED` com `CommandResult`. Exceções inesperadas capturadas na
fronteira da GUI tornam-se `ERROR`.

O coordenador da `SweepEngine` chama callbacks opcionais ao iniciar e quando um future responsivo
termina. A sessão os converte em `OUTPUT` em ordem de descoberta. Probes concorrentes não emitem
eventos diretamente; o resumo final não repete endereços já apresentados.

### Engine e plataforma

`SweepEngine` valida uma rede IPv4, limita a entrada a 4.096 endereços, mantém uma janela de até 32
probes e consulta um `threading.Event` antes de agendar novos trabalhos. A sessão aceita somente uma
varredura ativa e `cancelar` sinaliza seu evento cooperativo.

`SystemSweepProbeBackend` concentra os argumentos específicos de Windows, Linux e macOS. Cada probe
executa um único echo ICMP por `subprocess.run`, com lista estruturada, `shell=False` e timeout. O
uso interno do utilitário nativo é detalhe do backend; não existe comando público que o exponha como
wrapper.

## Direção e decisões atuais

- layout `src/` reduz imports acidentais da árvore de trabalho;
- runtime usa apenas biblioteca padrão;
- o catálogo prioriza ferramentas que agregam valor além de comandos básicos do sistema;
- `ping` não é comando público e não há contexto `icmp`;
- abstrações genéricas de contexto e eventos permanecem reutilizáveis;
- operações bloqueantes permanecem fora da thread da GUI;
- versão existe somente em `rabershell.__version__`.
