# MCP Especialista em Desenvolvimento - Arquitetura Modular

Este é um sistema MCP (Model Context Protocol) modular especializado em análise e desenvolvimento de código. A arquitetura foi projetada seguindo as melhores práticas do MCP, com separação de responsabilidades entre orquestrador e serviços especializados.

## 🏗️ Arquitetura

### Estrutura Modular
O sistema é composto por MCPs especializados:

- **MCP Orquestrador**: Coordena análises e gera relatórios consolidados
- **MCP Design UI/UX**: Especializado em design de interfaces e experiência do usuário
- **MCP Análise**: Realiza análises específicas de código (legado)

### Benefícios da Arquitetura
- ✅ **Separação de Responsabilidades**: Cada MCP tem uma função específica
- ✅ **Escalabilidade**: Fácil adição de novos serviços especializados
- ✅ **Manutenibilidade**: Código organizado e modular
- ✅ **Testabilidade**: Cada componente pode ser testado independentemente
- ✅ **Reutilização**: Serviços podem ser usados por outros orquestradores

## 🚀 Funcionalidades

### MCP Orquestrador
- Análise completa de código (coordena múltiplas análises)
- Análise de projetos inteiros
- Geração de relatórios consolidados
- Resumo executivo de análises

### MCP Análise
- **Análise de Sintaxe**: Python (AST), JavaScript, TypeScript
- **Detecção de Problemas**: Identificação de anti-padrões
- **Métricas de Código**: Complexidade, densidade de comentários
- **Sugestões de Melhoria**: Recomendações específicas por linguagem
- **Verificação de Padrões**: Conformidade com padrões (PEP 8, ES6+)

### MCP Design UI/UX
- **Análise de Interfaces**: HTML/CSS/JS e frameworks modernos
- **Verificação de Acessibilidade**: Conformidade com WCAG 2.1
- **Sugestões de UX**: Personalizadas por público-alvo
- **Geração de Guias de Estilo**: Padrões visuais consistentes
- **Templates de Referência**: Acesso a bibliotecas de componentes
- **Melhores Práticas**: Design patterns e usabilidade
- **Suporte Multi-Framework**: React, Vue, Svelte, Angular

## 📦 Como Usar

### Pré-requisitos
```bash
pip install mcp fastmcp
```

### Gerenciamento de Serviços

O sistema inclui um script de gerenciamento completo:

```bash
# Listar todos os serviços
python start_mcps.py list

# Testar todos os serviços
python start_mcps.py test

# Testar um serviço específico
python start_mcps.py test mcp-analise

# Iniciar um serviço específico
python start_mcps.py start mcp-analise
python start_mcps.py start mcp-orquestrador

# Iniciar todos os serviços
python start_mcps.py start-all
```

### Ferramentas Disponíveis

#### MCP Orquestrador
1. **analisar_codigo_completo(codigo: str, linguagem: str)**
   - Análise completa coordenando múltiplos serviços

2. **analisar_projeto(caminho_projeto: str)**
   - Análise de projeto inteiro

3. **gerar_relatorio_consolidado(resultados: list)**
   - Geração de relatórios consolidados

#### MCP Análise
1. **analisar_sintaxe_python/javascript/typescript(codigo: str)**
2. **detectar_problemas_codigo(codigo: str, linguagem: str)**
3. **calcular_metricas_codigo(codigo: str, linguagem: str)**
4. **sugerir_melhorias(codigo: str, linguagem: str)**
5. **verificar_padroes_codigo(codigo: str, linguagem: str)**

## 📁 Estrutura do Projeto

```
DesenvMCP/
├── mcp-orquestrador/          # MCP Orquestrador
│   ├── app.py                 # Servidor orquestrador
│   └── mcp.json              # Configuração
├── mcp-analise/               # MCP Análise
│   ├── app.py                 # Servidor de análise
│   └── mcp.json              # Configuração
├── start_mcps.py              # Script de gerenciamento
├── config.json                # Configuração global
├── README.md                  # Documentação
├── app.py                     # Servidor MCP original (legado)
├── mcp.json                   # Configuração original (legado)
├── venv/                      # Ambiente virtual Python
└── __pycache__/               # Cache Python
```

## 🔧 Configuração

### config.json
Arquivo de configuração global que define:
- Arquitetura dos serviços
- Protocolos de comunicação
- Configurações de logging
- Dependências entre serviços

### Arquivos mcp.json
Cada serviço possui sua própria configuração MCP individual.

## 🔧 Dependências

- `mcp`: Protocolo Model Context
- `fastmcp`: Framework rápido para MCP
- `ast`: Análise de sintaxe Python (built-in)
- `re`: Expressões regulares (built-in)
- `json`: Manipulação JSON (built-in)
- `logging`: Sistema de logs (built-in)
- `subprocess`: Execução de processos (built-in)
- `pathlib`: Manipulação de caminhos (built-in)

## 💡 Exemplos de Uso

### Teste da Arquitetura
```bash
# Verificar se todos os serviços estão funcionando
python start_mcps.py test

# Resultado esperado:
# ✓ mcp-orquestrador - Sintaxe OK
# ✓ mcp-analise - Sintaxe OK
# ✓ Todos os serviços passaram nos testes!
```

### Execução Individual
```bash
# Iniciar apenas o serviço de análise
python start_mcps.py start mcp-analise

# Iniciar o orquestrador (requer mcp-analise rodando)
python start_mcps.py start mcp-orquestrador
```

## 🎯 Próximas Funcionalidades

- [ ] Comunicação HTTP entre MCPs
- [ ] Cache distribuído de análises
- [ ] Métricas de performance dos serviços
- [ ] Dashboard de monitoramento
- [ ] Suporte para mais linguagens (Go, Rust, Java)
- [ ] Integração com linters externos
- [ ] API REST complementar
- [ ] Análise de dependências entre projetos

## 📊 Monitoramento

O sistema inclui logging estruturado e pode ser facilmente integrado com:
- Prometheus/Grafana para métricas
- ELK Stack para logs centralizados
- Health checks automáticos

## 📄 Licença

Este projeto está sob licença MIT. Veja o arquivo LICENSE para mais detalhes.

---

**Desenvolvido com ❤️ seguindo as melhores práticas de arquitetura MCP**