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

Abrir a GUI requer ambiente gráfico. Os testes do núcleo não realizam ping real.

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

