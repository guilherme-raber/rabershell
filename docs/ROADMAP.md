# Roadmap

O roadmap registra intenção, não compromisso de prazo.

## Implementado

- pacote Python com entry points gráfico e console instalado;
- shell, sessão, registry, aliases, ajuda e sugestões;
- infraestrutura reutilizável de eventos de execução e output incremental;
- `varredura` ICMP concorrente, incremental, cancelável e limitada a redes IPv4 de até `/20`, com
  alias `sweep`;
- terminal gráfico integrado com histórico protegido, edição de linha e autocomplete contextual;
- testes do núcleo, lint, formatação, tipos e documentação.

## Próximo

- amadurecer portabilidade e testar backends em Linux;
- amadurecer análise de redes e prefixos sem replicar comandos básicos do sistema;
- ampliar testes dos limites da GUI e experiência de distribuição no Windows;
- avaliar uma CLI reutilizando a mesma sessão e os mesmos comandos.

## Futuro

- análise e manipulação de redes, prefixos e CIDR;
- consultas e análises avançadas de DNS;
- ferramentas de análise de ASN/BGP e rotas;
- utilitários operacionais de troubleshooting;
- diagnósticos compostos, como `diagnostico <destino>`.

Funcionalidades ativas ou de varredura deverão manter defaults seguros e exigir autorização no
ambiente alvo. Nenhum item restante desta seção está implementado atualmente.
