from mcp.server.fastmcp import FastMCP
import ast
import re
import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('mcp_analise')

mcp = FastMCP("MCP Especialista em Análise de Código")

@mcp.tool()
def analisar_sintaxe_python(codigo: str) -> Dict[str, Any]:
    """
    Analisa a sintaxe de código Python e retorna informações sobre sua estrutura.
    
    Args:
        codigo: Código Python para análise
    
    Returns:
        Dicionário com informações sobre a sintaxe do código
    """
    try:
        tree = ast.parse(codigo)
        
        # Contadores
        funcoes = []
        classes = []
        imports = []
        variaveis = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                funcoes.append({
                    "nome": node.name,
                    "linha": node.lineno,
                    "argumentos": len(node.args.args),
                    "decoradores": len(node.decorator_list)
                })
            elif isinstance(node, ast.ClassDef):
                classes.append({
                    "nome": node.name,
                    "linha": node.lineno,
                    "metodos": len([n for n in node.body if isinstance(n, ast.FunctionDef)]),
                    "heranca": len(node.bases)
                })
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append({
                            "tipo": "import",
                            "modulo": alias.name,
                            "alias": alias.asname,
                            "linha": node.lineno
                        })
                else:  # ImportFrom
                    for alias in node.names:
                        imports.append({
                            "tipo": "from_import",
                            "modulo": node.module,
                            "nome": alias.name,
                            "alias": alias.asname,
                            "linha": node.lineno
                        })
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        variaveis.append({
                            "nome": target.id,
                            "linha": node.lineno,
                            "tipo": "atribuicao"
                        })
        
        linhas = codigo.split('\n')
        
        return {
            "status": "sucesso",
            "linguagem": "python",
            "estatisticas": {
                "total_linhas": len(linhas),
                "linhas_codigo": len([l for l in linhas if l.strip() and not l.strip().startswith('#')]),
                "total_funcoes": len(funcoes),
                "total_classes": len(classes),
                "total_imports": len(imports),
                "total_variaveis": len(variaveis)
            },
            "detalhes": {
                "funcoes": funcoes,
                "classes": classes,
                "imports": imports,
                "variaveis": variaveis[:10]  # Limitar para não sobrecarregar
            }
        }
    except SyntaxError as e:
        return {
            "status": "erro_sintaxe",
            "linguagem": "python",
            "erro": {
                "mensagem": str(e),
                "linha": e.lineno,
                "coluna": e.offset
            }
        }
    except Exception as e:
        return {
            "status": "erro",
            "linguagem": "python",
            "erro": str(e)
        }

@mcp.tool()
def analisar_sintaxe_javascript(codigo: str) -> Dict[str, Any]:
    """
    Analisa a sintaxe básica de código JavaScript usando regex.
    
    Args:
        codigo: Código JavaScript para análise
    
    Returns:
        Dicionário com informações sobre a sintaxe do código
    """
    try:
        # Padrões regex para análise básica
        funcoes = re.findall(r'function\s+(\w+)\s*\(([^)]*)\)', codigo)
        arrow_functions = re.findall(r'(\w+)\s*=\s*\([^)]*\)\s*=>', codigo)
        classes = re.findall(r'class\s+(\w+)', codigo)
        imports_single = re.findall(r"import\s+.*?from\s+'([^']*)'"  , codigo)
        imports_double = re.findall(r'import\s+.*?from\s+"([^"]*)"', codigo)
        imports = imports_single + imports_double
        requires_single = re.findall(r"require\s*\('([^']*)'\)", codigo)
        requires_double = re.findall(r'require\s*\("([^"]*)"\)', codigo)
        requires = requires_single + requires_double
        variaveis = re.findall(r'(?:var|let|const)\s+(\w+)', codigo)
        
        linhas = codigo.split('\n')
        
        return {
            "status": "sucesso",
            "linguagem": "javascript",
            "estatisticas": {
                "total_linhas": len(linhas),
                "total_funcoes": len(funcoes) + len(arrow_functions),
                "total_classes": len(classes),
                "total_imports": len(imports) + len(requires),
                "total_variaveis": len(variaveis)
            },
            "detalhes": {
                "funcoes_normais": [f[0] for f in funcoes],
                "arrow_functions": arrow_functions,
                "classes": classes,
                "imports": imports,
                "requires": requires,
                "variaveis": variaveis[:10]
            }
        }
    except Exception as e:
        return {
            "status": "erro",
            "linguagem": "javascript",
            "erro": str(e)
        }

@mcp.tool()
def analisar_sintaxe_typescript(codigo: str) -> Dict[str, Any]:
    """
    Analisa a sintaxe básica de código TypeScript usando regex.
    
    Args:
        codigo: Código TypeScript para análise
    
    Returns:
        Dicionário com informações sobre a sintaxe do código
    """
    try:
        # Padrões específicos do TypeScript
        interfaces = re.findall(r'interface\s+(\w+)', codigo)
        types = re.findall(r'type\s+(\w+)', codigo)
        enums = re.findall(r'enum\s+(\w+)', codigo)
        
        # Reutiliza análise do JavaScript
        js_analysis = analisar_sintaxe_javascript(codigo)
        
        if js_analysis["status"] == "sucesso":
            js_analysis["linguagem"] = "typescript"
            js_analysis["estatisticas"]["total_interfaces"] = len(interfaces)
            js_analysis["estatisticas"]["total_types"] = len(types)
            js_analysis["estatisticas"]["total_enums"] = len(enums)
            js_analysis["detalhes"]["interfaces"] = interfaces
            js_analysis["detalhes"]["types"] = types
            js_analysis["detalhes"]["enums"] = enums
        
        return js_analysis
    except Exception as e:
        return {
             "status": "erro",
             "linguagem": "typescript",
             "erro": str(e)
         }

@mcp.tool()
def detectar_problemas_codigo(codigo: str, linguagem: str) -> Dict[str, Any]:
    """
    Detecta problemas comuns no código baseado na linguagem.
    
    Args:
        codigo: Código para análise
        linguagem: Linguagem do código (python, javascript, typescript)
    
    Returns:
        Lista de problemas encontrados
    """
    problemas = []
    linhas = codigo.split('\n')
    
    if linguagem.lower() == "python":
        # Problemas específicos do Python
        for i, linha in enumerate(linhas, 1):
            linha_limpa = linha.strip()
            
            # Linhas muito longas (PEP 8)
            if len(linha) > 79:
                problemas.append({
                    "tipo": "linha_longa",
                    "linha": i,
                    "severidade": "aviso",
                    "mensagem": f"Linha {i} excede 79 caracteres ({len(linha)} caracteres)",
                    "sugestao": "Considere quebrar a linha para melhor legibilidade"
                })
            
            # Imports não utilizados (básico)
            if linha_limpa.startswith('import ') and 'unused' in linha_limpa:
                problemas.append({
                    "tipo": "import_nao_usado",
                    "linha": i,
                    "severidade": "aviso",
                    "mensagem": f"Import possivelmente não utilizado na linha {i}",
                    "sugestao": "Remova imports desnecessários"
                })
            
            # Variáveis com nomes ruins
            if re.search(r'\b[a-z]\s*=', linha_limpa):
                problemas.append({
                    "tipo": "nome_variavel",
                    "linha": i,
                    "severidade": "sugestao",
                    "mensagem": f"Nome de variável muito curto na linha {i}",
                    "sugestao": "Use nomes mais descritivos para variáveis"
                })
    
    elif linguagem.lower() in ["javascript", "typescript"]:
        # Problemas específicos do JavaScript/TypeScript
        for i, linha in enumerate(linhas, 1):
            linha_limpa = linha.strip()
            
            # Uso de var ao invés de let/const
            if 'var ' in linha_limpa:
                problemas.append({
                    "tipo": "uso_var",
                    "linha": i,
                    "severidade": "aviso",
                    "mensagem": f"Uso de 'var' na linha {i}",
                    "sugestao": "Prefira 'let' ou 'const' ao invés de 'var'"
                })
            
            # Console.log em produção
            if 'console.log' in linha_limpa:
                problemas.append({
                    "tipo": "console_log",
                    "linha": i,
                    "severidade": "aviso",
                    "mensagem": f"console.log encontrado na linha {i}",
                    "sugestao": "Remova console.log antes de enviar para produção"
                })
            
            # Comparação com == ao invés de ===
            if re.search(r'[^=!]==[^=]', linha_limpa):
                problemas.append({
                    "tipo": "comparacao_fraca",
                    "linha": i,
                    "severidade": "aviso",
                    "mensagem": f"Comparação com == na linha {i}",
                    "sugestao": "Use === para comparação estrita"
                })
    
    # Problemas gerais para todas as linguagens
    for i, linha in enumerate(linhas, 1):
        linha_limpa = linha.strip()
        
        # Linhas em branco excessivas
        if i > 1 and not linha_limpa and not linhas[i-2].strip():
            problemas.append({
                "tipo": "linhas_branco_excessivas",
                "linha": i,
                "severidade": "sugestao",
                "mensagem": f"Múltiplas linhas em branco na linha {i}",
                "sugestao": "Mantenha apenas uma linha em branco entre seções"
            })
        
        # Espaços em branco no final da linha
        if linha.endswith(' ') or linha.endswith('\t'):
            problemas.append({
                "tipo": "espacos_finais",
                "linha": i,
                "severidade": "sugestao",
                "mensagem": f"Espaços em branco no final da linha {i}",
                "sugestao": "Remova espaços em branco desnecessários"
            })
    
    return {
        "status": "sucesso",
        "linguagem": linguagem,
        "total_problemas": len(problemas),
        "problemas_encontrados": problemas,
        "resumo_severidade": {
            "critico": len([p for p in problemas if p["severidade"] == "critico"]),
            "aviso": len([p for p in problemas if p["severidade"] == "aviso"]),
            "sugestao": len([p for p in problemas if p["severidade"] == "sugestao"])
        }
    }

@mcp.tool()
def calcular_metricas_codigo(codigo: str, linguagem: str) -> Dict[str, Any]:
    """
    Calcula métricas de qualidade do código.
    
    Args:
        codigo: Código para análise
        linguagem: Linguagem do código
    
    Returns:
        Métricas calculadas do código
    """
    linhas = codigo.split('\n')
    linhas_codigo = [l for l in linhas if l.strip() and not l.strip().startswith('#') and not l.strip().startswith('//')]
    linhas_comentario = [l for l in linhas if l.strip().startswith('#') or l.strip().startswith('//')]
    linhas_branco = [l for l in linhas if not l.strip()]
    
    # Complexidade ciclomática básica
    complexidade = 1  # Começa com 1
    palavras_complexidade = ['if', 'elif', 'else', 'for', 'while', 'try', 'except', 'case', 'switch']
    
    for linha in linhas_codigo:
        for palavra in palavras_complexidade:
            if palavra in linha.lower():
                complexidade += 1
    
    # Aninhamento máximo
    max_aninhamento = 0
    aninhamento_atual = 0
    
    for linha in linhas:
        espacos_iniciais = len(linha) - len(linha.lstrip())
        if linguagem.lower() == "python":
            nivel = espacos_iniciais // 4  # Assumindo 4 espaços por nível
        else:
            nivel = linha.count('{') - linha.count('}')
        
        aninhamento_atual += nivel
        max_aninhamento = max(max_aninhamento, aninhamento_atual)
    
    # Tamanho médio de função (estimativa)
    if linguagem.lower() == "python":
        funcoes = re.findall(r'def\s+\w+', codigo)
    else:
        funcoes = re.findall(r'function\s+\w+|\w+\s*=\s*\([^)]*\)\s*=>', codigo)
    
    tamanho_medio_funcao = len(linhas_codigo) / max(len(funcoes), 1)
    
    return {
        "status": "sucesso",
        "linguagem": linguagem,
        "metricas": {
            "total_linhas": len(linhas),
            "linhas_codigo": len(linhas_codigo),
            "linhas_comentario": len(linhas_comentario),
            "linhas_branco": len(linhas_branco),
            "complexidade_ciclomatica": complexidade,
            "max_aninhamento": max_aninhamento,
            "total_funcoes": len(funcoes),
            "tamanho_medio_funcao": round(tamanho_medio_funcao, 2),
            "densidade_comentarios": round(len(linhas_comentario) / max(len(linhas_codigo), 1) * 100, 2)
        },
        "qualidade": {
            "legibilidade": "boa" if max_aninhamento <= 3 else "ruim",
            "manutenibilidade": "boa" if complexidade <= 10 else "ruim",
            "documentacao": "boa" if len(linhas_comentario) / max(len(linhas_codigo), 1) > 0.1 else "ruim"
        }
    }

@mcp.tool()
def sugerir_melhorias(codigo: str, linguagem: str) -> Dict[str, Any]:
    """
    Sugere melhorias específicas para o código baseado na linguagem.
    
    Args:
        codigo: Código para análise
        linguagem: Linguagem do código
    
    Returns:
        Lista de sugestões de melhoria
    """
    sugestoes = []
    linhas = codigo.split('\n')
    
    if linguagem.lower() == "python":
        # Sugestões específicas para Python
        
        # Verificar imports
        imports_linha = [i for i, linha in enumerate(linhas) if linha.strip().startswith('import') or linha.strip().startswith('from')]
        if len(imports_linha) > 1:
            # Verificar se imports estão agrupados
            gaps = [imports_linha[i+1] - imports_linha[i] for i in range(len(imports_linha)-1)]
            if any(gap > 1 for gap in gaps):
                sugestoes.append({
                    "tipo": "organizacao",
                    "prioridade": "media",
                    "titulo": "Agrupar imports",
                    "descricao": "Agrupe todos os imports no início do arquivo",
                    "exemplo": "# Coloque todos os imports juntos no topo\nimport os\nimport sys\nfrom typing import Dict"
                })
        
        # Verificar docstrings
        funcoes_sem_doc = []
        for i, linha in enumerate(linhas):
            if linha.strip().startswith('def '):
                # Verificar se próximas linhas têm docstring
                has_docstring = False
                for j in range(i+1, min(i+5, len(linhas))):
                    if '"""' in linhas[j] or "'''" in linhas[j]:
                        has_docstring = True
                        break
                if not has_docstring:
                    funcoes_sem_doc.append(linha.strip())
        
        if funcoes_sem_doc:
            sugestoes.append({
                "tipo": "documentacao",
                "prioridade": "alta",
                "titulo": "Adicionar docstrings",
                "descricao": f"Adicione docstrings para {len(funcoes_sem_doc)} função(ões)",
                "exemplo": 'def minha_funcao(param):\n    """\n    Descrição da função.\n    \n    Args:\n        param: Descrição do parâmetro\n    \n    Returns:\n        Descrição do retorno\n    """'
            })
        
        # Verificar list comprehensions
        for i, linha in enumerate(linhas):
            if 'for ' in linha and 'append(' in linha:
                sugestoes.append({
                    "tipo": "performance",
                    "prioridade": "media",
                    "titulo": "Usar list comprehension",
                    "descricao": f"Linha {i+1} pode ser otimizada com list comprehension",
                    "exemplo": "# Ao invés de:\nresult = []\nfor item in lista:\n    result.append(item.upper())\n\n# Use:\nresult = [item.upper() for item in lista]"
                })
                break
    
    elif linguagem.lower() in ["javascript", "typescript"]:
        # Sugestões específicas para JavaScript/TypeScript
        
        # Verificar uso de const/let
        for i, linha in enumerate(linhas):
            if 'var ' in linha:
                sugestoes.append({
                    "tipo": "modernizacao",
                    "prioridade": "alta",
                    "titulo": "Substituir var por const/let",
                    "descricao": f"Linha {i+1} usa 'var', prefira 'const' ou 'let'",
                    "exemplo": "// Ao invés de:\nvar nome = 'João';\n\n// Use:\nconst nome = 'João'; // se não vai mudar\n// ou\nlet nome = 'João'; // se vai mudar"
                })
        
        # Verificar arrow functions
        funcoes_normais = re.findall(r'function\s+(\w+)', codigo)
        if funcoes_normais:
            sugestoes.append({
                "tipo": "modernizacao",
                "prioridade": "media",
                "titulo": "Considerar arrow functions",
                "descricao": "Algumas funções podem ser convertidas para arrow functions",
                "exemplo": "// Ao invés de:\nfunction somar(a, b) {\n    return a + b;\n}\n\n// Use:\nconst somar = (a, b) => a + b;"
            })
        
        # Verificar template literals
        for i, linha in enumerate(linhas):
            if '+' in linha and ('"' in linha or "'" in linha):
                sugestoes.append({
                    "tipo": "modernizacao",
                    "prioridade": "media",
                    "titulo": "Usar template literals",
                    "descricao": f"Linha {i+1} pode usar template literals",
                    "exemplo": "// Ao invés de:\nconst msg = 'Olá ' + nome + '!';\n\n// Use:\nconst msg = `Olá ${nome}!`;"
                })
                break
    
    # Sugestões gerais
    
    # Verificar complexidade de funções
    metricas = calcular_metricas_codigo(codigo, linguagem)
    if metricas["status"] == "sucesso":
        if metricas["metricas"]["complexidade_ciclomatica"] > 10:
            sugestoes.append({
                "tipo": "refatoracao",
                "prioridade": "alta",
                "titulo": "Reduzir complexidade",
                "descricao": f"Complexidade ciclomática alta ({metricas['metricas']['complexidade_ciclomatica']})",
                "exemplo": "Considere quebrar funções grandes em funções menores e mais específicas"
            })
        
        if metricas["metricas"]["tamanho_medio_funcao"] > 20:
            sugestoes.append({
                "tipo": "refatoracao",
                "prioridade": "media",
                "titulo": "Reduzir tamanho das funções",
                "descricao": f"Funções muito grandes (média: {metricas['metricas']['tamanho_medio_funcao']} linhas)",
                "exemplo": "Funções devem ter idealmente menos de 20 linhas"
            })
    
    return {
        "status": "sucesso",
        "linguagem": linguagem,
        "total_sugestoes": len(sugestoes),
        "sugestoes": sugestoes,
        "resumo_prioridade": {
            "alta": len([s for s in sugestoes if s["prioridade"] == "alta"]),
            "media": len([s for s in sugestoes if s["prioridade"] == "media"]),
            "baixa": len([s for s in sugestoes if s["prioridade"] == "baixa"])
        }
    }

@mcp.tool()
def verificar_padroes_codigo(codigo: str, linguagem: str) -> dict:
    """
    Verifica se o código segue padrões e convenções da linguagem.
    
    Args:
        codigo: Código fonte para verificação
        linguagem: Linguagem do código (python, javascript, typescript)
    
    Returns:
        Dicionário com verificações de padrões e score de qualidade
    """
    verificacoes = []
    score = 100
    
    linhas = codigo.split('\n')
    
    if linguagem.lower() == "python":
        # Verificações específicas do Python (PEP 8)
        
        # 1. Comprimento de linha
        linhas_longas = [i+1 for i, linha in enumerate(linhas) if len(linha) > 79]
        if linhas_longas:
            verificacoes.append({
                "padrao": "PEP 8 - Comprimento de linha",
                "status": "falha",
                "detalhes": f"{len(linhas_longas)} linhas excedem 79 caracteres",
                "linhas": linhas_longas[:5]  # Mostrar apenas as primeiras 5
            })
            score -= len(linhas_longas) * 2
        else:
            verificacoes.append({
                "padrao": "PEP 8 - Comprimento de linha",
                "status": "ok",
                "detalhes": "Todas as linhas respeitam o limite de 79 caracteres"
            })
        
        # 2. Nomenclatura de funções (snake_case)
        funcoes_nome_ruim = []
        for linha in linhas:
            match = re.search(r'def\s+(\w+)', linha)
            if match:
                nome_funcao = match.group(1)
                if not re.match(r'^[a-z_][a-z0-9_]*$', nome_funcao):
                    funcoes_nome_ruim.append(nome_funcao)
        
        if funcoes_nome_ruim:
            verificacoes.append({
                "padrao": "PEP 8 - Nomenclatura de funções",
                "status": "falha",
                "detalhes": f"Funções não seguem snake_case: {', '.join(funcoes_nome_ruim)}"
            })
            score -= len(funcoes_nome_ruim) * 5
        else:
            verificacoes.append({
                "padrao": "PEP 8 - Nomenclatura de funções",
                "status": "ok",
                "detalhes": "Funções seguem convenção snake_case"
            })
        
        # 3. Imports organizados
        imports_desorganizados = False
        import_lines = [(i, linha) for i, linha in enumerate(linhas) if linha.strip().startswith(('import ', 'from '))]
        
        if len(import_lines) > 1:
            # Verificar se há código entre imports
            for i in range(len(import_lines) - 1):
                linha_atual = import_lines[i][0]
                proxima_linha = import_lines[i + 1][0]
                
                # Se há mais de uma linha de diferença, verificar se há código
                if proxima_linha - linha_atual > 1:
                    for j in range(linha_atual + 1, proxima_linha):
                        if linhas[j].strip() and not linhas[j].strip().startswith('#'):
                            imports_desorganizados = True
                            break
        
        if imports_desorganizados:
            verificacoes.append({
                "padrao": "PEP 8 - Organização de imports",
                "status": "falha",
                "detalhes": "Imports não estão agrupados no início do arquivo"
            })
            score -= 10
        else:
            verificacoes.append({
                "padrao": "PEP 8 - Organização de imports",
                "status": "ok",
                "detalhes": "Imports estão bem organizados"
            })
    
    elif linguagem.lower() in ["javascript", "typescript"]:
        # Verificações para JavaScript/TypeScript
        
        # 1. Uso de const/let ao invés de var
        uso_var = len([linha for linha in linhas if 'var ' in linha])
        if uso_var > 0:
            verificacoes.append({
                "padrao": "ES6+ - Declaração de variáveis",
                "status": "falha",
                "detalhes": f"{uso_var} ocorrências de 'var' encontradas"
            })
            score -= uso_var * 3
        else:
            verificacoes.append({
                "padrao": "ES6+ - Declaração de variáveis",
                "status": "ok",
                "detalhes": "Usa const/let apropriadamente"
            })
        
        # 2. Nomenclatura camelCase
        variaveis_nome_ruim = []
        for linha in linhas:
            # Buscar declarações de variáveis
            matches = re.findall(r'(?:const|let|var)\s+(\w+)', linha)
            for var_name in matches:
                if not re.match(r'^[a-z][a-zA-Z0-9]*$', var_name) and var_name.upper() != var_name:
                    variaveis_nome_ruim.append(var_name)
        
        if variaveis_nome_ruim:
            verificacoes.append({
                "padrao": "Nomenclatura - camelCase",
                "status": "falha",
                "detalhes": f"Variáveis não seguem camelCase: {', '.join(set(variaveis_nome_ruim))}"
            })
            score -= len(set(variaveis_nome_ruim)) * 3
        else:
            verificacoes.append({
                "padrao": "Nomenclatura - camelCase",
                "status": "ok",
                "detalhes": "Variáveis seguem convenção camelCase"
            })
        
        # 3. Uso de === ao invés de ==
        comparacoes_fracas = len(re.findall(r'[^=!]==[^=]', codigo))
        if comparacoes_fracas > 0:
            verificacoes.append({
                "padrao": "Comparação estrita",
                "status": "falha",
                "detalhes": f"{comparacoes_fracas} comparações com == encontradas"
            })
            score -= comparacoes_fracas * 2
        else:
            verificacoes.append({
                "padrao": "Comparação estrita",
                "status": "ok",
                "detalhes": "Usa === para comparações"
            })
    
    # Verificações gerais para todas as linguagens
    
    # 1. Densidade de comentários
    linhas_codigo = [l for l in linhas if l.strip() and not l.strip().startswith('#') and not l.strip().startswith('//')]
    linhas_comentario = [l for l in linhas if l.strip().startswith('#') or l.strip().startswith('//')]
    
    densidade_comentarios = len(linhas_comentario) / max(len(linhas_codigo), 1) * 100
    
    if densidade_comentarios < 10:
        verificacoes.append({
            "padrao": "Documentação - Comentários",
            "status": "falha",
            "detalhes": f"Baixa densidade de comentários ({densidade_comentarios:.1f}%)"
        })
        score -= 15
    else:
        verificacoes.append({
            "padrao": "Documentação - Comentários",
            "status": "ok",
            "detalhes": f"Boa densidade de comentários ({densidade_comentarios:.1f}%)"
        })
    
    # 2. Espaços em branco no final das linhas
    linhas_espacos_finais = [i+1 for i, linha in enumerate(linhas) if linha.endswith(' ') or linha.endswith('\t')]
    if linhas_espacos_finais:
        verificacoes.append({
            "padrao": "Formatação - Espaços finais",
            "status": "falha",
            "detalhes": f"{len(linhas_espacos_finais)} linhas com espaços no final"
        })
        score -= len(linhas_espacos_finais)
    else:
        verificacoes.append({
            "padrao": "Formatação - Espaços finais",
            "status": "ok",
            "detalhes": "Sem espaços desnecessários no final das linhas"
        })
    
    # Garantir que o score não seja negativo
    score = max(0, score)
    
    # Determinar nível de qualidade
    if score >= 90:
        nivel = "Excelente"
    elif score >= 75:
        nivel = "Bom"
    elif score >= 60:
        nivel = "Regular"
    elif score >= 40:
        nivel = "Ruim"
    else:
        nivel = "Muito Ruim"
    
    return {
        "status": "sucesso",
        "linguagem": linguagem,
        "score_qualidade": score,
        "nivel_qualidade": nivel,
        "total_verificacoes": len(verificacoes),
        "verificacoes_ok": len([v for v in verificacoes if v["status"] == "ok"]),
        "verificacoes_falha": len([v for v in verificacoes if v["status"] == "falha"]),
        "verificacoes": verificacoes,
        "recomendacoes": [
            "Mantenha o score acima de 80 para código de qualidade",
            "Revise regularmente as convenções da linguagem",
            "Use ferramentas de linting automático"
        ]
    }

if __name__ == "__main__":
    mcp.run()