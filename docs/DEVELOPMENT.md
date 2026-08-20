# Desenvolvimento

## Requisitos

- Python 3.11 ou superior;
- Git;
- tkinter (incluído normalmente no instalador oficial do Python para Windows).

## Ambiente e instalação

No PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Runtime não possui dependências externas. O extra `dev` instala pytest, Ruff e mypy.

## Execução e validação

```powershell
python -m rabershell
rabershell
python -m pytest
ruff check .
ruff format .
ruff format --check .
mypy
```

Abrir a GUI requer ambiente gráfico. Os testes do núcleo não realizam ping ou varredura reais; use
backends falsos para testar concorrência, limites e cancelamento de forma determinística.

A edição da linha fica em `gui/input_model.py` para permitir testes sem display. Autocomplete é
responsabilidade da sessão e do registry, não do widget. Mudanças no terminal devem testar limites
de edição, histórico, paste e conclusão sem depender de rede; faça também smoke test visual quando
houver ambiente gráfico.
Teste clipboard pela fronteira do widget sem depender de pixels: seleção deve permanecer somente
leitura, paste de uma linha deve atingir o modelo ativo e múltiplas linhas não vazias devem ser
rejeitadas sem alterar o rascunho. PRIMARY é específico de X11 e o botão direito para paste é
específico do Windows.

Streaming usa `CommandEvent` e um callback explícito até o backend. Testes devem usar processo e
stream falsos, incluindo um stream bloqueante que prove que o primeiro `OUTPUT` chega antes da
conclusão. Verifique ordem, evento final, códigos não zero, falha de inicialização e ausência de
duplicação; nunca dependa de um host público.
Para varredura, teste callbacks com probes bloqueantes: um `OUTPUT` deve ser observável antes do
relatório final, a ordem deve acompanhar a conclusão dos futures e o limite de workers deve ser
preservado.

## Estrutura

- `src/rabershell/shell`: linguagem interna, catálogo resolvido e estado da sessão;
- `src/rabershell/commands`: handlers e registro declarativo;
- `src/rabershell/core`: validação e operações reutilizáveis;
- `src/rabershell/platform`: detalhes do SO e subprocessos;
- `src/rabershell/gui`: apresentação tkinter;
- `tests`: testes unitários com fakes;
- `docs`: arquitetura, comandos, roadmap e desenvolvimento.

## Novos recursos

Leia `AGENTS.md`. Para um comando, modele metadados no registry, use um handler pequeno e crie uma
engine injetável se houver I/O. Para contexto, registre-o e teste entrada, prompt, resolução
explícita e retorno. Para backend, mantenha argumentos estruturados, `shell=False` e diferenças de
plataforma isoladas. Nunca faça testes dependerem de rede pública.

Antes do commit, formate, execute todas as validações, faça smoke test apropriado e confira se
README, changelog, `COMMANDS.md`, `ARCHITECTURE.md` e `ROADMAP.md` refletem o comportamento real.
