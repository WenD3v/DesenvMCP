from mcp.server.fastmcp import FastMCP
import json
import logging
import requests
from typing import Dict, List, Any, Optional
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('mcp_orquestrador')

mcp = FastMCP("MCP Orquestrador de Desenvolvimento")

# Configuração do MCP de Análise
ANALISE_MCP_URL = "http://localhost:8001"  # URL do MCP de análise

class MCPAnaliseClient:
    """Cliente para comunicação com o MCP de Análise"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
    
    def call_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Chama uma ferramenta no MCP de Análise"""
        try:
            response = requests.post(
                f"{self.base_url}/tools/{tool_name}",
                json=kwargs,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Erro ao chamar {tool_name}: {e}")
            return {"erro": f"Falha na comunicação com MCP de Análise: {str(e)}"}

analise_client = MCPAnaliseClient(ANALISE_MCP_URL)

@mcp.tool()
def analisar_codigo_completo(codigo: str, linguagem: str) -> Dict[str, Any]:
    """
    Realiza análise completa de código usando o MCP de Análise.
    
    Args:
        codigo: Código fonte para análise
        linguagem: Linguagem do código (python, javascript, typescript)
    
    Returns:
        Análise completa incluindo sintaxe, problemas, métricas e sugestões
    """
    logger.info(f"Iniciando análise completa para linguagem: {linguagem}")
    
    resultados = {
        "linguagem": linguagem,
        "analise_sintaxe": {},
        "problemas": {},
        "metricas": {},
        "padroes": {},
        "sugestoes": {},
        "resumo": {}
    }
    
    try:
        # 1. Análise de sintaxe
        if linguagem.lower() == "python":
            resultados["analise_sintaxe"] = analise_client.call_tool(
                "analisar_sintaxe_python", codigo=codigo
            )
        elif linguagem.lower() == "javascript":
            resultados["analise_sintaxe"] = analise_client.call_tool(
                "analisar_sintaxe_javascript", codigo=codigo
            )
        elif linguagem.lower() == "typescript":
            resultados["analise_sintaxe"] = analise_client.call_tool(
                "analisar_sintaxe_typescript", codigo=codigo
            )
        
        # 2. Detecção de problemas
        resultados["problemas"] = analise_client.call_tool(
            "detectar_problemas_codigo", codigo=codigo, linguagem=linguagem
        )
        
        # 3. Cálculo de métricas
        resultados["metricas"] = analise_client.call_tool(
            "calcular_metricas_codigo", codigo=codigo, linguagem=linguagem
        )
        
        # 4. Verificação de padrões
        resultados["padroes"] = analise_client.call_tool(
            "verificar_padroes_codigo", codigo=codigo, linguagem=linguagem
        )
        
        # 5. Sugestões de melhorias
        resultados["sugestoes"] = analise_client.call_tool(
            "sugerir_melhorias", codigo=codigo, linguagem=linguagem
        )
        
        # 6. Gerar resumo executivo
        resultados["resumo"] = _gerar_resumo_executivo(resultados)
        
        logger.info("Análise completa finalizada com sucesso")
        return resultados
        
    except Exception as e:
        logger.error(f"Erro durante análise completa: {e}")
        return {
            "erro": f"Falha na análise completa: {str(e)}",
            "linguagem": linguagem
        }

@mcp.tool()
def analisar_projeto(caminho_projeto: str, extensoes: List[str] = None) -> Dict[str, Any]:
    """
    Analisa um projeto inteiro, processando múltiplos arquivos.
    
    Args:
        caminho_projeto: Caminho para o diretório do projeto
        extensoes: Lista de extensões de arquivo para analisar (ex: ['.py', '.js'])
    
    Returns:
        Análise agregada de todo o projeto
    """
    if extensoes is None:
        extensoes = ['.py', '.js', '.ts', '.jsx', '.tsx']
    
    projeto_path = Path(caminho_projeto)
    if not projeto_path.exists():
        return {"erro": f"Caminho não encontrado: {caminho_projeto}"}
    
    resultados = {
        "projeto": str(projeto_path),
        "arquivos_analisados": [],
        "resumo_geral": {},
        "problemas_criticos": [],
        "metricas_agregadas": {},
        "recomendacoes": []
    }
    
    arquivos_encontrados = []
    for ext in extensoes:
        arquivos_encontrados.extend(projeto_path.rglob(f"*{ext}"))
    
    logger.info(f"Encontrados {len(arquivos_encontrados)} arquivos para análise")
    
    for arquivo in arquivos_encontrados[:20]:  # Limitar a 20 arquivos por performance
        try:
            with open(arquivo, 'r', encoding='utf-8') as f:
                codigo = f.read()
            
            # Determinar linguagem pela extensão
            ext = arquivo.suffix.lower()
            linguagem_map = {
                '.py': 'python',
                '.js': 'javascript', 
                '.jsx': 'javascript',
                '.ts': 'typescript',
                '.tsx': 'typescript'
            }
            
            linguagem = linguagem_map.get(ext, 'javascript')
            
            # Analisar arquivo
            analise_arquivo = analisar_codigo_completo(codigo, linguagem)
            
            resultados["arquivos_analisados"].append({
                "arquivo": str(arquivo.relative_to(projeto_path)),
                "linguagem": linguagem,
                "analise": analise_arquivo
            })
            
        except Exception as e:
            logger.error(f"Erro ao analisar {arquivo}: {e}")
            continue
    
    # Gerar resumo agregado
    resultados["resumo_geral"] = _gerar_resumo_projeto(resultados["arquivos_analisados"])
    
    return resultados

@mcp.tool()
def gerar_relatorio_qualidade(analise_resultado: Dict[str, Any]) -> Dict[str, Any]:
    """
    Gera um relatório de qualidade baseado nos resultados de análise.
    
    Args:
        analise_resultado: Resultado de análise de código ou projeto
    
    Returns:
        Relatório formatado com métricas de qualidade
    """
    relatorio = {
        "score_qualidade": 0,
        "nivel_qualidade": "Baixo",
        "pontos_fortes": [],
        "areas_melhoria": [],
        "acoes_recomendadas": [],
        "metricas_principais": {}
    }
    
    try:
        # Calcular score baseado nos resultados
        score = 100
        
        if "problemas" in analise_resultado:
            problemas = analise_resultado["problemas"]
            if "problemas_encontrados" in problemas:
                score -= len(problemas["problemas_encontrados"]) * 5
        
        if "padroes" in analise_resultado:
            padroes = analise_resultado["padroes"]
            if "score_qualidade" in padroes:
                score = (score + padroes["score_qualidade"]) / 2
        
        relatorio["score_qualidade"] = max(0, min(100, score))
        
        # Determinar nível
        if score >= 80:
            relatorio["nivel_qualidade"] = "Excelente"
        elif score >= 60:
            relatorio["nivel_qualidade"] = "Bom"
        elif score >= 40:
            relatorio["nivel_qualidade"] = "Regular"
        else:
            relatorio["nivel_qualidade"] = "Baixo"
        
        return relatorio
        
    except Exception as e:
        logger.error(f"Erro ao gerar relatório: {e}")
        return {"erro": f"Falha na geração do relatório: {str(e)}"}

def _gerar_resumo_executivo(resultados: Dict[str, Any]) -> Dict[str, Any]:
    """Gera resumo executivo da análise"""
    resumo = {
        "total_problemas": 0,
        "score_qualidade": 0,
        "principais_issues": [],
        "recomendacoes_prioritarias": []
    }
    
    # Contar problemas
    if "problemas" in resultados and "problemas_encontrados" in resultados["problemas"]:
        resumo["total_problemas"] = len(resultados["problemas"]["problemas_encontrados"])
    
    # Score de qualidade
    if "padroes" in resultados and "score_qualidade" in resultados["padroes"]:
        resumo["score_qualidade"] = resultados["padroes"]["score_qualidade"]
    
    return resumo

def _gerar_resumo_projeto(arquivos_analisados: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Gera resumo agregado do projeto"""
    resumo = {
        "total_arquivos": len(arquivos_analisados),
        "linguagens": {},
        "problemas_totais": 0,
        "score_medio": 0
    }
    
    scores = []
    for arquivo in arquivos_analisados:
        lang = arquivo["linguagem"]
        resumo["linguagens"][lang] = resumo["linguagens"].get(lang, 0) + 1
        
        if "analise" in arquivo and "padroes" in arquivo["analise"]:
            if "score_qualidade" in arquivo["analise"]["padroes"]:
                scores.append(arquivo["analise"]["padroes"]["score_qualidade"])
    
    if scores:
        resumo["score_medio"] = sum(scores) / len(scores)
    
    return resumo

if __name__ == "__main__":
    mcp.run()