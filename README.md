# rabershell

Toolkit experimental de diagnóstico e operação de redes, escrito em Python e apresentado por
uma interface gráfica leve com comportamento de terminal especializado.

> **Status:** experimental (0.1.0). A interface e a arquitetura ainda podem evoluir.

O rabershell não é um terminal arbitrário nem substitui Bash, PowerShell ou CMD. Ele oferece um
conjunto explícito de operações validadas, com ajuda contextual, exemplos e mensagens em
Português do Brasil. O princípio de UX é simples: o usuário não deve precisar decorar a
ferramenta para conseguir usá-la.

## Funcionalidades atuais

- shell próprio, contextos, aliases e sugestões de comandos;
- contexto ICMP e `ping` real para IPv4 ou hostname;
- sweep ICMP concorrente e cancelável para redes IPv4 de até `/20`;
- `ping` direto, explícito (`icmp ping`) ou dentro do contexto ICMP;
- terminal tkinter integrado e responsivo, com histórico protegido, ↑/↓ e autocomplete por Tab;
- backend de sistema isolado e execução sem `shell=True`.

```text
raber> ajuda
raber> ping 8.8.8.8
raber> icmp ping google.com --quantidade 5
raber> sweep 192.168.1.0/24
raber> cancelar
raber> icmp
raber/icmp> ping 127.0.0.1
raber/icmp> voltar
```

O prompt, a digitação e a saída compartilham a mesma superfície visual. Use `Tab` para completar
comandos e aliases, inclusive `icmp <subcomando>`. `Home`, `End`, setas, Backspace e Delete atuam
somente na linha atual; texto anterior permanece selecionável e pode ser copiado com `Ctrl+C`.
`Ctrl+V` cola na linha ativa e transforma quebras de linha em espaços, sem executar automaticamente.

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

O próximo ciclo deve amadurecer portabilidade, apresentação do resultado de ping e testes da
interface. DNS, rotas, TCP, SNMP e diagnósticos compostos são possibilidades futuras, não
funcionalidades atuais. Consulte [docs/ROADMAP.md](docs/ROADMAP.md).

## Uso responsável

Use o rabershell somente em redes e sistemas sob sua administração ou onde exista autorização
explícita para testes. O projeto é destinado a diagnóstico, troubleshooting e operação legítima.

## Licença

Distribuído sob a licença [MIT](LICENSE).
