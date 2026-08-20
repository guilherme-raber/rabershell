# AGENTS.md — fonte da verdade para desenvolvimento

## Projeto e propósito

O rabershell é um toolkit Python de diagnóstico e operação de redes. Sua interface inicial é uma
GUI tkinter leve que se comporta como terminal especializado. Não é shell do sistema, não aceita
comandos arbitrários e não substitui Bash, PowerShell ou CMD. Recursos ativos devem servir a
diagnóstico autorizado, troubleshooting e operação de ambientes administrados pelo usuário.

O princípio central de UX é: **o usuário não deve precisar decorar o rabershell para usá-lo**.
Ofereça descoberta, ajuda contextual, exemplos, defaults seguros e erros acionáveis. A interface
do usuário é pt-BR; identificadores e código-fonte são preferencialmente em inglês. Termos técnicos
consagrados, como ping, ICMP, DNS e TCP, permanecem em inglês.

## Arquitetura e responsabilidades

O fluxo é `GUI -> ShellSession -> parser/registry -> command handler -> engine -> backend de
plataforma`. A GUI apenas coleta entrada e apresenta `CommandResult`; nunca contém diagnóstico.
A sessão possui o contexto atual e o prompt. O parser tokeniza somente a gramática interna. O
registry é a fonte única de nomes, aliases, ajuda e exposição. Handlers validam argumentos e
orquestram engines. Engines representam operações de rede reutilizáveis. Backends isolam detalhes
do sistema operacional.

Estrutura principal:

- `src/rabershell/gui`: widgets, histórico e integração segura com a thread do tkinter;
- `src/rabershell/shell`: parser, sessão, modelos, registry e despacho;
- `src/rabershell/commands`: handlers e catálogo declarativo;
- `src/rabershell/core`: validação e engines independentes da GUI;
- `src/rabershell/platform`: subprocessos e diferenças entre sistemas;
- `tests`: testes sem dependência de rede real;
- `docs`: fontes da verdade técnicas e de uso.

## Registry, contextos, aliases e execução direta

Registre cada comportamento uma única vez em `commands/catalog.py`. `CommandSpec` define nome
canônico, aliases, contexto, exposição na raiz, ajuda, uso, exemplos e handler. Aliases resolvem
para o mesmo objeto; nunca crie handlers duplicados. Um comando de contexto pode definir
`root_exposed=True`. Assim, o único `ping` atende `ping HOST`, `icmp ping HOST` e, após `icmp`,
`ping HOST`. Contextos pertencem à `ShellSession`, não à GUI.

Operações longas devem oferecer cancelamento cooperativo quando aplicável. O `sweep` mantém no
máximo uma execução ativa por sessão, usa uma janela limitada de probes concorrentes e responde ao
comando global `cancelar`; a GUI deve continuar aceitando esse comando durante a operação.
Comandos que precisam ultrapassar a fila sequencial devem ser explicitamente marcados como controle
no `CommandSpec`; não aumente indiscriminadamente a concorrência do executor principal.

Para adicionar comando: implemente handler pequeno, reutilize/crie engine quando houver operação,
registre um único `CommandSpec`, teste resolução/argumentos/erros e atualize `COMMANDS.md`. Para
adicionar contexto: registre descrição, comandos contextuais, navegação necessária e testes do
prompt/despacho. Para adicionar engine/backend: defina contrato no core, injete a implementação,
isole plataforma em `platform/` e teste com fake.

## Segurança e dependências

Nunca use `shell=True`, concatenação de entrada em comando, `eval`, escape para shell ou execução
fora do catálogo explícito. Valide destinos, redes, portas, quantidades e opções conforme o caso.
Passe argumentos estruturados ao subprocesso. Validação sintática de hostname e resolução DNS são
etapas distintas: falha de DNS não transforma hostname sintaticamente válido em entrada inválida.
Centralize diferenças de plataforma.

Runtime deve permanecer na biblioteca padrão enquanto ela resolver bem o problema. Antes de nova
dependência, documente a necessidade e o custo. Ferramentas de desenvolvimento ficam no extra
`dev`. Não invente funcionalidades não solicitadas nem implemente itens do roadmap por antecipação.

## Testes e validação

Priorize parser, registry, dispatcher/sessão, aliases, contextos, validação e engines. Não dependa
de internet ou hosts reais: injete fakes na fronteira de backend. Mudanças de GUI devem manter toda
operação bloqueante fora da thread principal; widgets só podem ser atualizados por ela.

Antes de concluir:

```powershell
python -m pytest
ruff check .
ruff format --check .
mypy
```

Também faça smoke test dos entry points quando houver display disponível, revise `git diff` e
`git status` e compare implementação com `ARCHITECTURE.md`, `COMMANDS.md` e `ROADMAP.md`.

## Convenções e documentação

Use Python 3.11+, type hints, funções curtas e alterações pequenas. Preserve compatibilidade de
comandos, aliases e entry points; mudanças incompatíveis exigem decisão explícita e changelog.
Textos visíveis são pt-BR e devem ficar em handlers/metadados ou camada de apresentação, não em
backends. Atualize README, changelog e docs quando o comportamento mudar. `COMMANDS.md` deve
catalogar somente o que existe; itens futuros ficam claramente em `ROADMAP.md`. Não mantenha listas
paralelas de ajuda no código. Comentários explicam decisões, não repetem o código.
