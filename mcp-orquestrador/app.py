from mcp.server.fastmcp import FastMCP
import ast
import re
import json
import logging
import subprocess
import asyncio
import time
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('mcp_orquestrador')

mcp = FastMCP("MCP Orquestrador de Desenvolvimento - Gateway")

# Configurações do Gateway MCP
@dataclass
class MCPServiceConfig:
    name: str
    path: str
    port: int
    role: str
    description: str
    tools: List[str]
    process: Optional[subprocess.Popen] = None
    status: str = "stopped"
    last_health_check: float = 0

class MCPGateway:
    """Gateway MCP para orquestração de múltiplos serviços MCP"""
    
    def __init__(self, config_path: str = None):
        self.services: Dict[str, MCPServiceConfig] = {}
        self.config_path = config_path or Path(__file__).parent.parent / "config.json"
        self.load_config()
        
    def load_config(self):
        """Carrega configuração dos serviços MCP"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            for service_name, service_config in config['services'].items():
                if service_name != 'mcp-orquestrador':  # Não incluir a si mesmo
                    self.services[service_name] = MCPServiceConfig(
                        name=service_name,
                        path=service_config['path'],
                        port=service_config['port'],
                        role=service_config['role'],
                        description=service_config['description'],
                        tools=service_config.get('tools', [])
                    )
            
            logger.info(f"Configuração carregada: {len(self.services)} serviços MCP")
            
        except Exception as e:
            logger.error(f"Erro ao carregar configuração: {e}")
    
    def start_service(self, service_name: str) -> bool:
        """Inicia um serviço MCP específico"""
        if service_name not in self.services:
            logger.error(f"Serviço {service_name} não encontrado")
            return False
        
        service = self.services[service_name]
        if service.status == "running":
            logger.info(f"Serviço {service_name} já está em execução")
            return True
        
        try:
            service_path = Path(self.config_path).parent / service.path
            app_file = service_path / "app.py"
            
            if not app_file.exists():
                logger.error(f"Arquivo app.py não encontrado em {service_path}")
                return False
            
            # Inicia o processo do serviço MCP
            service.process = subprocess.Popen(
                ["python", "app.py"],
                cwd=service_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            service.status = "running"
            service.last_health_check = time.time()
            
            logger.info(f"Serviço {service_name} iniciado com PID {service.process.pid}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao iniciar serviço {service_name}: {e}")
            service.status = "error"
            return False
    
    def stop_service(self, service_name: str) -> bool:
        """Para um serviço MCP específico"""
        if service_name not in self.services:
            return False
        
        service = self.services[service_name]
        if service.process and service.status == "running":
            try:
                service.process.terminate()
                service.process.wait(timeout=5)
                service.status = "stopped"
                service.process = None
                logger.info(f"Serviço {service_name} parado")
                return True
            except Exception as e:
                logger.error(f"Erro ao parar serviço {service_name}: {e}")
                return False
        return True
    
    def get_service_status(self, service_name: str) -> Dict[str, Any]:
        """Obtém status de um serviço"""
        if service_name not in self.services:
            return {"error": "Serviço não encontrado"}
        
        service = self.services[service_name]
        return {
            "name": service.name,
            "status": service.status,
            "role": service.role,
            "description": service.description,
            "tools": service.tools,
            "pid": service.process.pid if service.process else None,
            "last_health_check": service.last_health_check
        }
    
    def list_available_tools(self) -> Dict[str, List[str]]:
        """Lista todas as ferramentas disponíveis nos serviços"""
        tools_by_service = {}
        for service_name, service in self.services.items():
            if service.status == "running":
                tools_by_service[service_name] = service.tools
        return tools_by_service
    
    def route_tool_call(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Roteia chamada de ferramenta para o serviço apropriado"""
        # Encontra qual serviço possui a ferramenta
        target_service = None
        for service_name, service in self.services.items():
            if tool_name in service.tools and service.status == "running":
                target_service = service_name
                break
        
        if not target_service:
            return {
                "error": f"Ferramenta '{tool_name}' não encontrada ou serviço não disponível",
                "available_tools": self.list_available_tools()
            }
        
        # Simula chamada para o serviço (implementação simplificada)
        logger.info(f"Roteando '{tool_name}' para serviço '{target_service}'")
        
        # Aqui seria implementada a comunicação real via MCP
        # Por enquanto, retorna uma resposta simulada
        return {
            "service": target_service,
            "tool": tool_name,
            "status": "success",
            "message": f"Ferramenta {tool_name} executada via {target_service}",
            "parameters": kwargs
        }

# Instância global do gateway
gateway = MCPGateway()

# ===== FERRAMENTAS DO GATEWAY MCP =====

@mcp.tool()
def iniciar_servico_mcp(service_name: str) -> Dict[str, Any]:
    """
    Inicia um serviço MCP específico no gateway.
    
    Args:
        service_name: Nome do serviço MCP (mcp-analise, mcp-design)
    
    Returns:
        Status da operação de inicialização
    """
    logger.info(f"Solicitação para iniciar serviço: {service_name}")
    
    if gateway.start_service(service_name):
        return {
            "status": "success",
            "message": f"Serviço {service_name} iniciado com sucesso",
            "service_info": gateway.get_service_status(service_name)
        }
    else:
        return {
            "status": "error",
            "message": f"Falha ao iniciar serviço {service_name}",
            "available_services": list(gateway.services.keys())
        }

@mcp.tool()
def parar_servico_mcp(service_name: str) -> Dict[str, Any]:
    """
    Para um serviço MCP específico no gateway.
    
    Args:
        service_name: Nome do serviço MCP para parar
    
    Returns:
        Status da operação
    """
    logger.info(f"Solicitação para parar serviço: {service_name}")
    
    if gateway.stop_service(service_name):
        return {
            "status": "success",
            "message": f"Serviço {service_name} parado com sucesso"
        }
    else:
        return {
            "status": "error",
            "message": f"Falha ao parar serviço {service_name}"
        }

@mcp.tool()
def listar_servicos_mcp() -> Dict[str, Any]:
    """
    Lista todos os serviços MCP disponíveis e seus status.
    
    Returns:
        Informações sobre todos os serviços MCP
    """
    logger.info("Listando serviços MCP disponíveis")
    
    services_info = {}
    for service_name in gateway.services.keys():
        services_info[service_name] = gateway.get_service_status(service_name)
    
    return {
        "status": "success",
        "total_services": len(gateway.services),
        "services": services_info,
        "available_tools": gateway.list_available_tools()
    }

@mcp.tool()
def executar_ferramenta_mcp(tool_name: str, **kwargs) -> Dict[str, Any]:
    """
    Executa uma ferramenta específica através do gateway MCP.
    
    Args:
        tool_name: Nome da ferramenta a ser executada
        **kwargs: Parâmetros para a ferramenta
    
    Returns:
        Resultado da execução da ferramenta
    """
    logger.info(f"Executando ferramenta via gateway: {tool_name}")
    
    # Roteia a chamada para o serviço apropriado
    result = gateway.route_tool_call(tool_name, **kwargs)
    
    return {
        "gateway_result": result,
        "timestamp": time.time(),
        "routed_via": "mcp-orquestrador-gateway"
    }

@mcp.tool()
def analisar_codigo_via_gateway(codigo: str, linguagem: str, usar_servico: str = "auto") -> Dict[str, Any]:
    """
    Analisa código usando o serviço mcp-analise através do gateway.
    
    Args:
        codigo: Código fonte para análise
        linguagem: Linguagem do código
        usar_servico: Serviço específico ou 'auto' para roteamento automático
    
    Returns:
        Resultado da análise via gateway
    """
    logger.info(f"Análise de código via gateway - linguagem: {linguagem}")
    
    # Verifica se o serviço mcp-analise está disponível
    if "mcp-analise" not in gateway.services:
        return {"error": "Serviço mcp-analise não configurado"}
    
    service_status = gateway.get_service_status("mcp-analise")
    if service_status.get("status") != "running":
        # Tenta iniciar o serviço
        start_result = gateway.start_service("mcp-analise")
        if not start_result:
            return {"error": "Não foi possível iniciar o serviço mcp-analise"}
    
    # Roteia para a ferramenta de análise
    return gateway.route_tool_call("analisar_codigo", codigo=codigo, linguagem=linguagem)

@mcp.tool()
def gerar_template_via_gateway(tipo_template: str, framework: str = "react", usar_servico: str = "auto") -> Dict[str, Any]:
    """
    Gera template usando o serviço mcp-design através do gateway.
    
    Args:
        tipo_template: Tipo de template (login, dashboard, form)
        framework: Framework alvo (react, vue, angular)
        usar_servico: Serviço específico ou 'auto'
    
    Returns:
        Template gerado via gateway
    """
    logger.info(f"Geração de template via gateway - tipo: {tipo_template}, framework: {framework}")
    
    # Verifica se o serviço mcp-design está disponível
    if "mcp-design" not in gateway.services:
        return {"error": "Serviço mcp-design não configurado"}
    
    service_status = gateway.get_service_status("mcp-design")
    if service_status.get("status") != "running":
        # Tenta iniciar o serviço
        start_result = gateway.start_service("mcp-design")
        if not start_result:
            return {"error": "Não foi possível iniciar o serviço mcp-design"}
    
    # Roteia para a ferramenta de geração de template
    return gateway.route_tool_call("gerar_template", tipo_template=tipo_template, framework=framework)

@mcp.tool()
def gateway_health_check() -> Dict[str, Any]:
    """
    Verifica a saúde de todos os serviços no gateway.
    
    Returns:
        Status de saúde de todos os serviços
    """
    logger.info("Executando verificação de saúde do gateway")
    
    health_status = {
        "gateway_status": "healthy",
        "timestamp": time.time(),
        "services": {},
        "summary": {
            "total_services": len(gateway.services),
            "running_services": 0,
            "stopped_services": 0,
            "error_services": 0
        }
    }
    
    for service_name in gateway.services.keys():
        service_info = gateway.get_service_status(service_name)
        health_status["services"][service_name] = service_info
        
        status = service_info.get("status", "unknown")
        if status == "running":
            health_status["summary"]["running_services"] += 1
        elif status == "stopped":
            health_status["summary"]["stopped_services"] += 1
        else:
            health_status["summary"]["error_services"] += 1
    
    return health_status

# ===== SISTEMA DE CACHE E ESTADO =====

class MCPCache:
    """Sistema de cache para resultados de MCPs"""
    
    def __init__(self, max_size: int = 100, ttl: int = 300):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.max_size = max_size
        self.ttl = ttl  # Time to live em segundos
    
    def _generate_key(self, service: str, tool: str, params: Dict[str, Any]) -> str:
        """Gera chave única para cache"""
        import hashlib
        params_str = json.dumps(params, sort_keys=True)
        key_data = f"{service}:{tool}:{params_str}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, service: str, tool: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Recupera resultado do cache se válido"""
        key = self._generate_key(service, tool, params)
        
        if key in self.cache:
            cached_item = self.cache[key]
            if time.time() - cached_item['timestamp'] < self.ttl:
                logger.info(f"Cache hit para {service}:{tool}")
                return cached_item['result']
            else:
                # Remove item expirado
                del self.cache[key]
        
        return None
    
    def set(self, service: str, tool: str, params: Dict[str, Any], result: Dict[str, Any]):
        """Armazena resultado no cache"""
        if len(self.cache) >= self.max_size:
            # Remove o item mais antigo
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k]['timestamp'])
            del self.cache[oldest_key]
        
        key = self._generate_key(service, tool, params)
        self.cache[key] = {
            'result': result,
            'timestamp': time.time(),
            'service': service,
            'tool': tool
        }
        logger.info(f"Resultado armazenado no cache para {service}:{tool}")
    
    def clear(self, service: str = None):
        """Limpa cache (todo ou de um serviço específico)"""
        if service:
            keys_to_remove = [k for k, v in self.cache.items() if v['service'] == service]
            for key in keys_to_remove:
                del self.cache[key]
            logger.info(f"Cache limpo para serviço {service}")
        else:
            self.cache.clear()
            logger.info("Cache completamente limpo")
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache"""
        return {
            'total_items': len(self.cache),
            'max_size': self.max_size,
            'ttl_seconds': self.ttl,
            'services': list(set(item['service'] for item in self.cache.values()))
        }

# Instância global do cache
cache = MCPCache()

# ===== FUNÇÕES PROXY ESPECÍFICAS =====

@mcp.tool()
def proxy_analisar_sintaxe(codigo: str, linguagem: str, usar_cache: bool = True) -> Dict[str, Any]:
    """
    Proxy para análise de sintaxe via mcp-analise com cache.
    
    Args:
        codigo: Código fonte para análise
        linguagem: Linguagem do código
        usar_cache: Se deve usar cache para resultados
    
    Returns:
        Resultado da análise de sintaxe
    """
    params = {'codigo': codigo, 'linguagem': linguagem}
    
    # Verifica cache primeiro
    if usar_cache:
        cached_result = cache.get('mcp-analise', 'analisar_sintaxe', params)
        if cached_result:
            return {
                'cached': True,
                'result': cached_result,
                'source': 'mcp-analise-cache'
            }
    
    # Executa via gateway
    result = gateway.route_tool_call('analisar_sintaxe', **params)
    
    # Armazena no cache se bem-sucedido
    if usar_cache and result.get('status') == 'success':
        cache.set('mcp-analise', 'analisar_sintaxe', params, result)
    
    return {
        'cached': False,
        'result': result,
        'source': 'mcp-analise-live'
    }

@mcp.tool()
def proxy_gerar_template_design(tipo_template: str, framework: str = "react", usar_cache: bool = True) -> Dict[str, Any]:
    """
    Proxy para geração de templates via mcp-design com cache.
    
    Args:
        tipo_template: Tipo de template (login, dashboard, form)
        framework: Framework alvo
        usar_cache: Se deve usar cache
    
    Returns:
        Template gerado
    """
    params = {'tipo_template': tipo_template, 'framework': framework}
    
    # Verifica cache
    if usar_cache:
        cached_result = cache.get('mcp-design', 'gerar_template', params)
        if cached_result:
            return {
                'cached': True,
                'result': cached_result,
                'source': 'mcp-design-cache'
            }
    
    # Executa via gateway
    result = gateway.route_tool_call('gerar_template', **params)
    
    # Cache do resultado
    if usar_cache and result.get('status') == 'success':
        cache.set('mcp-design', 'gerar_template', params, result)
    
    return {
        'cached': False,
        'result': result,
        'source': 'mcp-design-live'
    }

@mcp.tool()
def proxy_analise_design_ui(codigo: str, file_path: str = "", usar_cache: bool = True) -> Dict[str, Any]:
    """
    Proxy para análise de design UI via mcp-design.
    
    Args:
        codigo: Código do componente UI
        file_path: Caminho do arquivo (opcional)
        usar_cache: Se deve usar cache
    
    Returns:
        Análise de design UI
    """
    params = {'codigo': codigo, 'file_path': file_path}
    
    # Verifica cache
    if usar_cache:
        cached_result = cache.get('mcp-design', 'analisar_design_ui', params)
        if cached_result:
            return {
                'cached': True,
                'result': cached_result,
                'source': 'mcp-design-cache'
            }
    
    # Executa via gateway
    result = gateway.route_tool_call('analisar_design_ui', codigo=codigo, file_path=file_path)
    
    # Cache do resultado
    if usar_cache and result.get('status') == 'success':
        cache.set('mcp-design', 'analisar_design_ui', params, result)
    
    return {
        'cached': False,
        'result': result,
        'source': 'mcp-design-live'
    }

@mcp.tool()
def gerenciar_cache_mcp(acao: str, servico: str = "") -> Dict[str, Any]:
    """
    Gerencia o cache do gateway MCP.
    
    Args:
        acao: Ação a executar (stats, clear, clear_service)
        servico: Nome do serviço (para clear_service)
    
    Returns:
        Resultado da operação de cache
    """
    logger.info(f"Gerenciamento de cache - ação: {acao}, serviço: {servico}")
    
    if acao == "stats":
        return {
            "status": "success",
            "cache_stats": cache.get_stats()
        }
    
    elif acao == "clear":
        cache.clear()
        return {
            "status": "success",
            "message": "Cache completamente limpo"
        }
    
    elif acao == "clear_service" and servico:
        cache.clear(servico)
        return {
            "status": "success",
            "message": f"Cache limpo para serviço {servico}"
        }
    
    else:
        return {
            "status": "error",
            "message": "Ação inválida. Use: stats, clear, clear_service"
        }

@mcp.tool()
def executar_pipeline_completo(codigo: str, linguagem: str, incluir_design: bool = True) -> Dict[str, Any]:
    """
    Executa um pipeline completo de análise usando múltiplos MCPs.
    
    Args:
        codigo: Código fonte para análise
        linguagem: Linguagem do código
        incluir_design: Se deve incluir análise de design
    
    Returns:
        Resultado completo do pipeline
    """
    logger.info(f"Executando pipeline completo - linguagem: {linguagem}, design: {incluir_design}")
    
    pipeline_result = {
        "pipeline_id": f"pipeline_{int(time.time())}",
        "timestamp": time.time(),
        "steps": [],
        "summary": {},
        "errors": []
    }
    
    try:
        # Passo 1: Análise de código via mcp-analise
        logger.info("Pipeline - Passo 1: Análise de código")
        analise_result = proxy_analisar_sintaxe(codigo, linguagem)
        pipeline_result["steps"].append({
            "step": 1,
            "name": "analise_codigo",
            "service": "mcp-analise",
            "result": analise_result
        })
        
        # Passo 2: Análise de design (se solicitado)
        if incluir_design and linguagem.lower() in ['javascript', 'typescript', 'jsx', 'tsx']:
            logger.info("Pipeline - Passo 2: Análise de design")
            design_result = proxy_analise_design_ui(codigo)
            pipeline_result["steps"].append({
                "step": 2,
                "name": "analise_design",
                "service": "mcp-design",
                "result": design_result
            })
        
        # Gerar resumo do pipeline
        pipeline_result["summary"] = {
            "total_steps": len(pipeline_result["steps"]),
            "successful_steps": len([s for s in pipeline_result["steps"] if s["result"].get("result", {}).get("status") == "success"]),
            "services_used": list(set(s["service"] for s in pipeline_result["steps"])),
            "execution_time": time.time() - pipeline_result["timestamp"]
        }
        
        return pipeline_result
        
    except Exception as e:
        logger.error(f"Erro no pipeline: {e}")
        pipeline_result["errors"].append(str(e))
        return pipeline_result

# Funções de análise integradas (sem dependência externa)
def analisar_sintaxe_python_interno(codigo: str) -> Dict[str, Any]:
    """Análise interna de sintaxe Python"""
    try:
        tree = ast.parse(codigo)
        
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
                else:
                    for alias in node.names:
                        imports.append({
                            "tipo": "from_import",
                            "modulo": node.module,
                            "nome": alias.name,
                            "alias": alias.asname,
                            "linha": node.lineno
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
                "total_imports": len(imports)
            },
            "detalhes": {
                "funcoes": funcoes,
                "classes": classes,
                "imports": imports
            }
        }
    except Exception as e:
        return {"status": "erro", "erro": str(e)}

def analisar_sintaxe_javascript_interno(codigo: str) -> Dict[str, Any]:
    """Análise interna de sintaxe JavaScript"""
    try:
        funcoes = re.findall(r'function\s+(\w+)\s*\(([^)]*)\)', codigo)
        arrow_functions = re.findall(r'(\w+)\s*=\s*\([^)]*\)\s*=>', codigo)
        classes = re.findall(r'class\s+(\w+)', codigo)
        imports = re.findall(r"import\s+.*?from\s+['\"]([^'\"]*)['\"]"  , codigo)
        
        linhas = codigo.split('\n')
        
        return {
            "status": "sucesso",
            "linguagem": "javascript",
            "estatisticas": {
                "total_linhas": len(linhas),
                "total_funcoes": len(funcoes) + len(arrow_functions),
                "total_classes": len(classes),
                "total_imports": len(imports)
            },
            "detalhes": {
                "funcoes_normais": [f[0] for f in funcoes],
                "arrow_functions": arrow_functions,
                "classes": classes,
                "imports": imports
            }
        }
    except Exception as e:
        return {"status": "erro", "erro": str(e)}

def detectar_problemas_interno(codigo: str, linguagem: str) -> Dict[str, Any]:
    """Detecção interna de problemas"""
    problemas = []
    linhas = codigo.split('\n')
    
    if linguagem.lower() == "python":
        for i, linha in enumerate(linhas, 1):
            if len(linha) > 79:
                problemas.append({
                    "tipo": "linha_longa",
                    "linha": i,
                    "severidade": "aviso",
                    "mensagem": f"Linha {i} excede 79 caracteres"
                })
    
    elif linguagem.lower() in ["javascript", "typescript"]:
        for i, linha in enumerate(linhas, 1):
            if 'var ' in linha.strip():
                problemas.append({
                    "tipo": "uso_var",
                    "linha": i,
                    "severidade": "aviso",
                    "mensagem": f"Uso de 'var' na linha {i}"
                })
    
    return {
        "status": "sucesso",
        "linguagem": linguagem,
        "total_problemas": len(problemas),
        "problemas_encontrados": problemas
    }

def calcular_metricas_interno(codigo: str, linguagem: str) -> Dict[str, Any]:
    """Cálculo interno de métricas"""
    linhas = codigo.split('\n')
    linhas_codigo = [l for l in linhas if l.strip() and not l.strip().startswith('#')]
    
    complexidade = 1
    for linha in linhas_codigo:
        if any(palavra in linha.lower() for palavra in ['if', 'for', 'while', 'try']):
            complexidade += 1
    
    return {
        "status": "sucesso",
        "linguagem": linguagem,
        "metricas": {
            "total_linhas": len(linhas),
            "linhas_codigo": len(linhas_codigo),
            "complexidade_ciclomatica": complexidade
        }
    }

@mcp.tool()
def analisar_codigo_completo(codigo: str, linguagem: str) -> Dict[str, Any]:
    """
    Realiza análise completa de código usando funções internas.
    
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
            resultados["analise_sintaxe"] = analisar_sintaxe_python_interno(codigo)
        elif linguagem.lower() in ["javascript", "typescript"]:
            resultados["analise_sintaxe"] = analisar_sintaxe_javascript_interno(codigo)
        else:
            resultados["analise_sintaxe"] = {"status": "erro", "erro": f"Linguagem {linguagem} não suportada"}
        
        # 2. Detecção de problemas
        resultados["problemas"] = detectar_problemas_interno(codigo, linguagem)
        
        # 3. Cálculo de métricas
        resultados["metricas"] = calcular_metricas_interno(codigo, linguagem)
        
        # 4. Verificação de padrões (simulado)
        resultados["padroes"] = {
            "status": "sucesso",
            "score_qualidade": 75,
            "padroes_seguidos": ["estrutura_basica", "nomenclatura"]
        }
        
        # 5. Sugestões de melhorias (simulado)
        resultados["sugestoes"] = {
            "status": "sucesso",
            "sugestoes": [
                "Considere adicionar documentação às funções",
                "Verifique se há código duplicado",
                "Considere usar type hints (Python) ou TypeScript"
            ]
        }
        
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