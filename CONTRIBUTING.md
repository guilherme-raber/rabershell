# Como contribuir

Obrigado pelo interesse no rabershell. Antes de começar, leia `AGENTS.md`, o README e a
documentação em `docs/`.

## Princípios

- Mantenha alterações pequenas e focadas.
- Preserve a interface em pt-BR e use inglês no código.
- Não exponha execução arbitrária do sistema.
- Reutilize registry, comandos e engines; não duplique caminhos de execução.
- Atualize testes, `docs/COMMANDS.md` e demais fontes da verdade ao mudar comportamento.

## Fluxo sugerido

1. Crie e ative um ambiente virtual.
2. Instale `python -m pip install -e ".[dev]"`.
3. Implemente e teste a menor mudança coerente.
4. Execute `python -m pytest`, `ruff check .`, `ruff format --check .` e `mypy`.
5. Descreva motivação, comportamento e validação na contribuição.

Relate vulnerabilidades de forma privada aos mantenedores em vez de publicar detalhes
exploráveis em uma issue.

