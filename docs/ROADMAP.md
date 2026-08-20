# Roadmap

O roadmap registra intenção, não compromisso de prazo.

## Implementado

- pacote Python com entry points gráfico e console instalado;
- shell, sessão, registry, aliases, ajuda e sugestões;
- contexto ICMP e ping direto/contextual com backend de sistema;
- output incremental do ping por eventos de execução reutilizáveis;
- `varredura` ICMP concorrente, incremental, cancelável e limitada a redes IPv4 de até `/20`, com
  alias `sweep`;
- terminal gráfico integrado com histórico protegido, edição de linha e autocomplete contextual;
- testes do núcleo, lint, formatação, tipos e documentação.

## Próximo

- amadurecer portabilidade e testar backends em Linux;
- melhorar apresentação estruturada das estatísticas de ping sem depender do idioma do sistema;
- ampliar testes dos limites da GUI e experiência de distribuição no Windows;
- avaliar uma CLI reutilizando a mesma sessão e os mesmos comandos.

## Futuro

- ICMP: `latency`, `mtu`;
- DNS: `resolve`, `reverse`;
- rotas: `trace`, `mtr`;
- TCP: `check`;
- diagnóstico básico SNMP;
- backends opcionais como hping3, mtr, traceroute, dig e snmpwalk quando justificáveis;
- diagnósticos compostos, como `diagnostico <destino>`.

Funcionalidades ativas ou de varredura deverão manter defaults seguros e exigir autorização no
ambiente alvo. Nenhum item restante desta seção está implementado atualmente.
