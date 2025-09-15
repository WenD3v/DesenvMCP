from mcp.server.fastmcp import FastMCP
import ast
import re
import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('dev_mcp')

mcp = FastMCP("MCP Especialista em Desenvolvimento")

@mcp.resources("config://app")
def get_app_config():
    with open("mcp.json", "r") as f:
        return json.load(f)

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
                        imports.append({"tipo": "import", "modulo": alias.name, "linha": node.lineno})
                else:
                    imports.append({"tipo": "from", "modulo": node.module, "linha": node.lineno})
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        variaveis.append({"nome": target.id, "linha": node.lineno})
        
        return {
            "status": "sucesso",
            "linguagem": "python",
            "estatisticas": {
                "total_linhas": len(codigo.split('\n')),
                "total_funcoes": len(funcoes),
                "total_classes": len(classes),
                "total_imports": len(imports),
                "total_variaveis": len(variaveis)
            },
            "detalhes": {
                "funcoes": funcoes,
                "classes": classes,
                "imports": imports,
                "variaveis": variaveis[:10]  # Limita a 10 para não sobrecarregar
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
            # Linhas muito longas
            if len(linha) > 120:
                problemas.append({
                    "tipo": "linha_longa",
                    "linha": i,
                    "mensagem": f"Linha muito longa ({len(linha)} caracteres)",
                    "severidade": "aviso"
                })
            
            # Imports não utilizados (básico)
            if linha.strip().startswith('import ') and linha.count(' as ') == 0:
                modulo = linha.replace('import ', '').strip()
                if modulo not in codigo.replace(linha, ''):
                    problemas.append({
                        "tipo": "import_nao_usado",
                        "linha": i,
                        "mensagem": f"Import '{modulo}' pode não estar sendo usado",
                        "severidade": "aviso"
                    })
            
            # Variáveis não utilizadas (básico)
            if '=' in linha and not linha.strip().startswith('#'):
                var_match = re.match(r'\s*(\w+)\s*=', linha)
                if var_match:
                    var_name = var_match.group(1)
                    if var_name not in codigo.replace(linha, '') and not var_name.startswith('_'):
                        problemas.append({
                            "tipo": "variavel_nao_usada",
                            "linha": i,
                            "mensagem": f"Variável '{var_name}' pode não estar sendo usada",
                            "severidade": "aviso"
                        })
    
    elif linguagem.lower() in ["javascript", "typescript"]:
        # Problemas específicos do JS/TS
        for i, linha in enumerate(linhas, 1):
            # Uso de var em vez de let/const
            if re.search(r'\bvar\s+\w+', linha):
                problemas.append({
                    "tipo": "uso_var",
                    "linha": i,
                    "mensagem": "Considere usar 'let' ou 'const' em vez de 'var'",
                    "severidade": "sugestao"
                })
            
            # Console.log esquecido
            if 'console.log' in linha:
                problemas.append({
                    "tipo": "console_log",
                    "linha": i,
                    "mensagem": "Console.log encontrado - remover antes da produção",
                    "severidade": "aviso"
                })
            
            # Comparação com == em vez de ===
            if re.search(r'\w+\s*==\s*\w+', linha) and '===' not in linha:
                problemas.append({
                    "tipo": "comparacao_fraca",
                    "linha": i,
                    "mensagem": "Considere usar '===' em vez de '=='",
                    "severidade": "sugestao"
                })
    
    return {
        "status": "sucesso",
        "linguagem": linguagem,
        "total_problemas": len(problemas),
        "problemas": problemas
    }

@mcp.tool()
def calcular_metricas_codigo(codigo: str, linguagem: str) -> Dict[str, Any]:
    """
    Calcula métricas básicas do código.
    
    Args:
        codigo: Código para análise
        linguagem: Linguagem do código
    
    Returns:
        Métricas calculadas do código
    """
    linhas = codigo.split('\n')
    linhas_codigo = [l for l in linhas if l.strip() and not l.strip().startswith('#') and not l.strip().startswith('//')]
    linhas_comentario = [l for l in linhas if l.strip().startswith('#') or l.strip().startswith('//')]
    linhas_vazias = [l for l in linhas if not l.strip()]
    
    # Complexidade ciclomática básica
    complexidade = 1  # Base
    palavras_complexidade = ['if', 'elif', 'else', 'for', 'while', 'try', 'except', 'case', 'switch']
    
    for linha in linhas_codigo:
        for palavra in palavras_complexidade:
            if palavra in linha:
                complexidade += 1
    
    # Aninhamento máximo
    max_aninhamento = 0
    aninhamento_atual = 0
    
    for linha in linhas:
        espacos = len(linha) - len(linha.lstrip())
        if linguagem.lower() == "python":
            aninhamento_atual = espacos // 4  # Assumindo 4 espaços por nível
        else:
            aninhamento_atual = linha.count('{')
        
        max_aninhamento = max(max_aninhamento, aninhamento_atual)
    
    return {
        "status": "sucesso",
        "linguagem": linguagem,
        "metricas": {
            "total_linhas": len(linhas),
            "linhas_codigo": len(linhas_codigo),
            "linhas_comentario": len(linhas_comentario),
            "linhas_vazias": len(linhas_vazias),
            "complexidade_ciclomatica": complexidade,
            "aninhamento_maximo": max_aninhamento,
            "densidade_comentarios": round(len(linhas_comentario) / max(len(linhas_codigo), 1) * 100, 2),
            "caracteres_total": len(codigo),
            "caracteres_por_linha": round(len(codigo) / max(len(linhas), 1), 2)
        }
    }

@mcp.tool()
def sugerir_melhorias(codigo: str, linguagem: str) -> Dict[str, Any]:
    """
    Sugere melhorias para o código baseado em boas práticas.
    
    Args:
        codigo: Código para análise
        linguagem: Linguagem do código
    
    Returns:
        Lista de sugestões de melhoria
    """
    sugestoes = []
    linhas = codigo.split('\n')
    
    if linguagem.lower() == "python":
        # Sugestões específicas do Python
        if 'import *' in codigo:
            sugestoes.append({
                "tipo": "import_especifico",
                "mensagem": "Evite usar 'import *', prefira imports específicos",
                "exemplo": "from module import specific_function"
            })
        
        if not any('"""' in linha or "'''" in linha for linha in linhas):
            sugestoes.append({
                "tipo": "documentacao",
                "mensagem": "Considere adicionar docstrings às suas funções",
                "exemplo": 'def funcao():\n    """Descrição da função."""'
            })
        
        # Verifica se há funções muito longas
        funcao_atual = None
        linhas_funcao = 0
        for linha in linhas:
            if linha.strip().startswith('def '):
                if funcao_atual and linhas_funcao > 20:
                    sugestoes.append({
                        "tipo": "funcao_longa",
                        "mensagem": f"Função '{funcao_atual}' muito longa ({linhas_funcao} linhas). Considere dividir em funções menores",
                        "exemplo": "Divida em funções menores com responsabilidades específicas"
                    })
                funcao_atual = linha.split('(')[0].replace('def ', '').strip()
                linhas_funcao = 1
            elif funcao_atual:
                linhas_funcao += 1
    
    elif linguagem.lower() in ["javascript", "typescript"]:
        # Sugestões específicas do JS/TS
        if 'function(' in codigo:
            sugestoes.append({
                "tipo": "arrow_function",
                "mensagem": "Considere usar arrow functions para funções simples",
                "exemplo": "const func = () => { ... }"
            })
        
        if linguagem.lower() == "javascript" and ('any' not in codigo):
            sugestoes.append({
                "tipo": "typescript",
                "mensagem": "Considere migrar para TypeScript para melhor tipagem",
                "exemplo": "Adicione tipos às variáveis e parâmetros"
            })
    
    return {
        "status": "sucesso",
        "linguagem": linguagem,
        "total_sugestoes": len(sugestoes),
        "sugestoes": sugestoes
    }

@mcp.tool()
def verificar_padroes_codigo(codigo: str, linguagem: str) -> dict:
    """
    Verifica padrões de código e convenções de nomenclatura.
    
    Args:
        codigo: O código fonte a ser analisado
        linguagem: A linguagem do código (python, javascript, typescript)
    
    Returns:
        Dicionário com verificações de padrões e convenções
    """
    try:
        padroes = {
            "nomenclatura": [],
            "estrutura": [],
            "boas_praticas": [],
            "score_qualidade": 0
        }
        
        linhas = codigo.split('\n')
        score = 100
        
        if linguagem.lower() == "python":
            # Verificar PEP 8
            for i, linha in enumerate(linhas, 1):
                # Snake_case para funções e variáveis
                funcoes_camel = re.findall(r'def\s+([a-z][a-zA-Z0-9]*[A-Z][a-zA-Z0-9]*)', linha)
                if funcoes_camel:
                    padroes["nomenclatura"].append(f"Linha {i}: Função '{funcoes_camel[0]}' deveria usar snake_case")
                    score -= 5
                
                # Classes em PascalCase
                classes_snake = re.findall(r'class\s+([a-z_][a-z0-9_]*)', linha)
                if classes_snake:
                    padroes["nomenclatura"].append(f"Linha {i}: Classe '{classes_snake[0]}' deveria usar PascalCase")
                    score -= 5
                
                # Imports no topo
                if re.match(r'^\s*import\s+|^\s*from\s+', linha) and i > 10:
                    if not any('def ' in l or 'class ' in l for l in linhas[:i-1]):
                        padroes["estrutura"].append(f"Linha {i}: Import deveria estar no topo do arquivo")
                        score -= 3
        
        elif linguagem.lower() in ["javascript", "typescript"]:
            # Verificar convenções JS/TS
            for i, linha in enumerate(linhas, 1):
                # CamelCase para funções e variáveis
                vars_snake = re.findall(r'(?:var|let|const)\s+([a-z]+_[a-z0-9_]*)', linha)
                if vars_snake:
                    padroes["nomenclatura"].append(f"Linha {i}: Variável '{vars_snake[0]}' deveria usar camelCase")
                    score -= 5
                
                # PascalCase para classes
                classes_camel = re.findall(r'class\s+([a-z][a-zA-Z0-9]*)', linha)
                if classes_camel:
                    padroes["nomenclatura"].append(f"Linha {i}: Classe '{classes_camel[0]}' deveria usar PascalCase")
                    score -= 5
                
                # Ponto e vírgula no final
                if re.match(r'^\s*(?:var|let|const|return)\s+.*[^;{]\s*$', linha.strip()):
                    padroes["boas_praticas"].append(f"Linha {i}: Faltando ponto e vírgula")
                    score -= 2
        
        # Verificações gerais
        for i, linha in enumerate(linhas, 1):
            # Linhas muito longas
            if len(linha) > 120:
                padroes["estrutura"].append(f"Linha {i}: Linha muito longa ({len(linha)} caracteres)")
                score -= 2
            
            # Espaços em branco no final
            if linha.endswith(' ') or linha.endswith('\t'):
                padroes["boas_praticas"].append(f"Linha {i}: Espaços em branco no final da linha")
                score -= 1
            
            # Tabs misturados com espaços
            if '\t' in linha and '    ' in linha:
                padroes["estrutura"].append(f"Linha {i}: Mistura de tabs e espaços para indentação")
                score -= 3
        
        # Verificar estrutura geral
        if not any('def ' in linha or 'function ' in linha for linha in linhas):
            padroes["estrutura"].append("Nenhuma função encontrada no código")
        
        if linguagem.lower() == "python" and not any('"""' in linha or "'''" in linha for linha in linhas):
            if any('def ' in linha for linha in linhas):
                padroes["boas_praticas"].append("Considere adicionar docstrings às funções")
                score -= 5
        
        padroes["score_qualidade"] = max(0, score)
        
        return {
            "padroes_encontrados": padroes,
            "total_problemas": len(padroes["nomenclatura"]) + len(padroes["estrutura"]) + len(padroes["boas_praticas"]),
            "linguagem": linguagem,
            "resumo": f"Score de qualidade: {padroes['score_qualidade']}/100"
        }
        
    except Exception as e:
        logger.error(f"Erro ao verificar padrões: {e}")
        return {"erro": f"Erro na verificação: {str(e)}"}


if __name__ == "__main__":
    mcp.run()