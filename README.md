# rabershell

Toolkit experimental de diagnóstico e operação de redes, escrito em Python e apresentado por
uma interface gráfica leve com comportamento de terminal especializado.

> **Status:** experimental (0.1.0). A interface e a arquitetura ainda podem evoluir.

O rabershell não é um terminal arbitrário nem substitui Bash, PowerShell ou CMD. Ele oferece um
conjunto explícito de operações validadas, com ajuda contextual, exemplos e mensagens em
Português do Brasil. O princípio de UX é simples: o usuário não deve precisar decorar a
ferramenta para conseguir usá-la.

O catálogo prioriza diagnósticos e utilitários que agregam valor além dos comandos básicos já
disponíveis no sistema operacional. O projeto não pretende ser apenas um wrapper desses comandos.

## Funcionalidades atuais

- shell próprio, aliases, sugestões e suporte arquitetural a contextos futuros;
- `varredura` ICMP concorrente, incremental e cancelável para redes IPv4 de até `/20`
  (`sweep` é alias);
- terminal tkinter integrado e responsivo, com histórico protegido, ↑/↓ e autocomplete por Tab;
- backend de sistema isolado e execução sem `shell=True`.

```text
raber> ajuda
raber> varredura 192.168.1.0/24
raber> cancelar
```

O prompt, a digitação e a saída compartilham a mesma superfície visual. Use `Tab` para completar
comandos e aliases. `Home`, `End`, setas, Backspace e Delete atuam somente na linha atual; texto
anterior permanece selecionável e pode ser copiado com `Ctrl+C`.
`Ctrl+V` cola uma linha na entrada ativa, sem executar automaticamente. Colagens com múltiplas
linhas não vazias são rejeitadas integralmente e preservam o rascunho atual.
No Windows, concluir uma seleção com o mouse já a copia para o clipboard, e o botão direito cola na
linha ativa. No X11, o botão do meio cola a seleção primária. Esses atalhos nunca alteram o
histórico protegido. `ajuda <prefixo>` também aceita Tab, por exemplo `ajuda var<Tab>`.

## Requisitos e instalação

- Python 3.11 ou mais recente;
- Windows nesta primeira versão (a fronteira de plataforma também contempla Linux/macOS);
- tkinter disponível na instalação do Python.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e .
```

Execute com:

```powershell
rabershell
# ou
python -m rabershell
```

## Desenvolvimento e testes

```powershell
python -m pip install -e ".[dev]"
python -m pytest
ruff check .
ruff format --check .
mypy
```

Veja [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) para o fluxo completo, e
[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) para as decisões técnicas.

## Roadmap resumido

O próximo ciclo deve amadurecer portabilidade, análise de redes/prefixos e testes da interface.
DNS avançado, rotas, ASN/BGP e diagnósticos compostos são possibilidades futuras, não
funcionalidades atuais. Consulte [docs/ROADMAP.md](docs/ROADMAP.md).

## Uso responsável

Use o rabershell somente em redes e sistemas sob sua administração ou onde exista autorização
explícita para testes. O projeto é destinado a diagnóstico, troubleshooting e operação legítima.

## Licença

Distribuído sob a licença [MIT](LICENSE).
