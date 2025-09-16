from mcp.server.fastmcp import FastMCP
import json
import logging
import os
from typing import Dict, List, Any, Optional
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('mcp_design')

mcp = FastMCP("MCP Design UI/UX")

# Configurações do MCP de Design
TEMPLATES_DIR = "src/templates/screens"
DESIGN_PRINCIPLES = {
    "accessibility": {
        "contrast_ratio": 4.5,
        "font_size_min": 16,
        "touch_target_min": 44
    },
    "usability": {
        "loading_time_max": 3,
        "click_depth_max": 3,
        "form_fields_max": 7
    },
    "visual_hierarchy": {
        "heading_levels": ["h1", "h2", "h3", "h4", "h5", "h6"],
        "spacing_scale": [4, 8, 16, 24, 32, 48, 64]
    }
}

UX_BEST_PRACTICES = {
    "mobile_first": "Sempre projete primeiro para dispositivos móveis",
    "progressive_disclosure": "Revele informações gradualmente conforme necessário",
    "consistency": "Mantenha padrões consistentes em toda a interface",
    "feedback": "Forneça feedback imediato para ações do usuário",
    "error_prevention": "Previna erros através de design intuitivo",
    "recognition_over_recall": "Torne elementos reconhecíveis ao invés de memoráveis"
}

# Extensões de arquivo suportadas
SUPPORTED_EXTENSIONS = ['.html', '.css', '.js', '.jsx', '.tsx', '.vue', '.svelte']

def carregar_templates_disponiveis() -> List[Dict[str, Any]]:
    """Carrega lista de templates disponíveis na pasta src/templates/screens/"""
    templates = []
    templates_path = Path(TEMPLATES_DIR)
    
    if templates_path.exists():
        for arquivo in templates_path.rglob("*"):
            if arquivo.is_file() and arquivo.suffix in [".html", ".jsx", ".tsx", ".vue", ".svelte"]:
                # Determina o tipo baseado na extensão
                tipo = arquivo.suffix[1:]
                if tipo == 'tsx':
                    framework_type = 'React Native TypeScript'
                elif tipo == 'jsx':
                    framework_type = 'React JavaScript'
                elif tipo == 'html':
                    framework_type = 'HTML'
                elif tipo == 'vue':
                    framework_type = 'Vue.js'
                elif tipo == 'svelte':
                    framework_type = 'Svelte'
                else:
                    framework_type = tipo.upper()
                
                templates.append({
                    "nome": arquivo.stem,
                    "caminho": str(arquivo.relative_to(templates_path)),
                    "tipo": tipo,
                    "framework": framework_type,
                    "tamanho": arquivo.stat().st_size,
                    "categoria": arquivo.parent.name if arquivo.parent.name != "screens" else "geral"
                })
    
    return templates

def analisar_template(caminho_template: str) -> Dict[str, Any]:
    """Analisa um template específico e extrai informações de design"""
    try:
        with open(caminho_template, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        # Análise básica do template
        analise = {
            "componentes_identificados": [],
            "padroes_ui": [],
            "elementos_interativos": [],
            "estrutura_layout": {}
        }
        
        # Identificar componentes comuns
        componentes_comuns = [
            "header", "nav", "sidebar", "main", "footer", "button", "form", 
            "input", "card", "modal", "dropdown", "table", "list"
        ]
        
        for componente in componentes_comuns:
            if componente.lower() in conteudo.lower():
                analise["componentes_identificados"].append(componente)
        
        # Identificar padrões de UI
        if "grid" in conteudo.lower() or "flex" in conteudo.lower():
            analise["padroes_ui"].append("layout_responsivo")
        if "@media" in conteudo or "responsive" in conteudo.lower():
            analise["padroes_ui"].append("design_responsivo")
        
        return {
            "status": "sucesso",
            "template": caminho_template,
            "analise": analise
        }
    
    except Exception as e:
        return {"status": "erro", "erro": str(e)}

@mcp.resource("templates://screens")
def listar_templates() -> str:
    """Lista todos os templates disponíveis na pasta src/templates/screens/"""
    templates = carregar_templates_disponiveis()
    
    if not templates:
        return json.dumps({
            "mensagem": "Nenhum template encontrado",
            "sugestao": "Crie templates na pasta src/templates/screens/",
            "templates": []
        }, indent=2, ensure_ascii=False)
    
    return json.dumps({
        "total_templates": len(templates),
        "templates_por_tipo": {},
        "templates": templates
    }, indent=2, ensure_ascii=False)

@mcp.tool()
def analisar_design_ui(codigo_html: str, tipo_componente: str = "geral", file_path: str = "") -> Dict[str, Any]:
    """
    Analisa código HTML/CSS/JS/TSX e fornece sugestões de melhoria baseadas em princípios de UI/UX.
    
    Args:
        codigo_html: Código HTML/CSS/JS/TSX para análise
        tipo_componente: Tipo do componente (header, form, card, etc.)
        file_path: Caminho do arquivo para detectar o tipo (opcional)
    
    Returns:
        Análise detalhada com sugestões de melhoria
    """
    try:
        analise = {
            "status": "sucesso",
            "tipo_componente": tipo_componente,
            "problemas_encontrados": [],
            "sugestoes_melhoria": [],
            "score_ux": 0,
            "templates_recomendados": [],
            "framework_detectado": "HTML"
        }
        
        # Detecta o tipo de framework baseado na extensão
        if file_path.endswith('.vue'):
            framework = 'Vue.js'
        elif file_path.endswith('.svelte'):
            framework = 'Svelte'
        elif file_path.endswith(('.js', '.jsx')):
            framework = 'React/JavaScript'
        elif file_path.endswith('.tsx'):
            framework = 'React Native/TypeScript'
        else:
            framework = 'HTML/CSS'
        
        analise["framework_detectado"] = framework
        
        # Verificações de acessibilidade
        if "alt=" not in codigo_html and "<img" in codigo_html:
            analise["problemas_encontrados"].append({
                "tipo": "acessibilidade",
                "problema": "Imagens sem texto alternativo",
                "severidade": "alta"
            })
        
        if "aria-" not in codigo_html and any(tag in codigo_html for tag in ["<button", "<input", "<form"]):
            analise["problemas_encontrados"].append({
                "tipo": "acessibilidade",
                "problema": "Falta de atributos ARIA",
                "severidade": "média"
            })
        
        # Verificações de usabilidade
        if "<form" in codigo_html and "required" not in codigo_html:
            analise["sugestoes_melhoria"].append({
                "categoria": "usabilidade",
                "sugestao": "Adicionar validação de campos obrigatórios",
                "implementacao": "Use o atributo 'required' em campos essenciais"
            })
        
        # Verificações de design responsivo
        if "@media" not in codigo_html and "viewport" not in codigo_html:
            analise["sugestoes_melhoria"].append({
                "categoria": "responsividade",
                "sugestao": "Implementar design responsivo",
                "implementacao": "Adicione meta viewport e media queries"
            })
        
        # Análises específicas por tipo de arquivo
        score_base = 70
        
        if file_path.endswith(('.js', '.jsx', '.tsx', '.vue', '.svelte')):
            # Análise de componentes JavaScript/Framework
            if 'useState' in codigo_html or 'useEffect' in codigo_html:
                analise["sugestoes_melhoria"].append({
                    "categoria": "performance",
                    "sugestao": "Considere usar React.memo para componentes que não precisam re-renderizar frequentemente",
                    "implementacao": "Envolva o componente com React.memo()"
                })
            
            if 'style=' in codigo_html and codigo_html.count('style=') > 3:
                analise["problemas_encontrados"].append({
                    "tipo": "manutenibilidade",
                    "problema": "Muitos estilos inline detectados",
                    "severidade": "média"
                })
                score_base -= 10
            
            # Análises específicas para React Native (.tsx)
            if file_path.endswith('.tsx'):
                if 'StyleSheet.create' not in codigo_html and 'styles.' in codigo_html:
                    analise["problemas_encontrados"].append({
                        "tipo": "performance",
                        "problema": "Use StyleSheet.create para melhor performance em React Native",
                        "severidade": "média"
                    })
                    score_base -= 10
                
                if 'accessibilityLabel' not in codigo_html and ('TouchableOpacity' in codigo_html or 'Button' in codigo_html):
                    analise["problemas_encontrados"].append({
                        "tipo": "acessibilidade",
                        "problema": "Adicione accessibilityLabel aos componentes interativos para melhor acessibilidade",
                        "severidade": "alta"
                    })
                    score_base -= 15
                
                if 'KeyboardAvoidingView' not in codigo_html and 'TextInput' in codigo_html:
                    analise["sugestoes_melhoria"].append({
                        "categoria": "usabilidade",
                        "sugestao": "Considere usar KeyboardAvoidingView com TextInput para melhor UX",
                        "implementacao": "Envolva TextInput com KeyboardAvoidingView"
                    })
                    score_base -= 5
                
        elif file_path.endswith('.html'):
            # Análise específica para HTML
            if '<img' in codigo_html and 'alt=' not in codigo_html:
                analise["problemas_encontrados"].append({
                    "tipo": "acessibilidade",
                    "problema": "Imagens sem atributo alt detectadas - problema de acessibilidade",
                    "severidade": "alta"
                })
                score_base -= 15
                
            if '<button' in codigo_html and 'aria-label' not in codigo_html:
                analise["problemas_encontrados"].append({
                    "tipo": "acessibilidade",
                    "problema": "Botões sem aria-label podem ter problemas de acessibilidade",
                    "severidade": "média"
                })
                score_base -= 10
        
        # Buscar templates relacionados
        templates = carregar_templates_disponiveis()
        for template in templates:
            if tipo_componente.lower() in template["nome"].lower() or template["categoria"] == tipo_componente:
                analise["templates_recomendados"].append(template)
        
        # Calcular score UX (0-100)
        score_base += len(analise["templates_recomendados"]) * 5
        analise["score_ux"] = max(0, min(100, score_base))
        
        return analise
    
    except Exception as e:
        logger.error(f"Erro na análise de design: {e}")
        return {"status": "erro", "erro": str(e)}

@mcp.tool()
def sugerir_melhorias_ux(descricao_interface: str, publico_alvo: str = "geral") -> Dict[str, Any]:
    """
    Sugere melhorias de UX baseadas na descrição da interface e público-alvo.
    
    Args:
        descricao_interface: Descrição da interface ou funcionalidade
        publico_alvo: Público-alvo (jovens, idosos, profissionais, etc.)
    
    Returns:
        Sugestões personalizadas de UX
    """
    try:
        sugestoes = {
            "status": "sucesso",
            "publico_alvo": publico_alvo,
            "principios_aplicados": [],
            "sugestoes_especificas": [],
            "templates_recomendados": [],
            "proximos_passos": []
        }
        
        # Aplicar princípios baseados no público-alvo
        if "idoso" in publico_alvo.lower():
            sugestoes["principios_aplicados"].extend([
                "Fontes maiores (mínimo 18px)",
                "Alto contraste de cores",
                "Botões grandes e espaçados",
                "Navegação simples e linear"
            ])
        elif "jovem" in publico_alvo.lower():
            sugestoes["principios_aplicados"].extend([
                "Design moderno e dinâmico",
                "Interações gestuais",
                "Feedback visual imediato",
                "Gamificação quando apropriado"
            ])
        else:
            sugestoes["principios_aplicados"].extend([
                "Design limpo e profissional",
                "Navegação intuitiva",
                "Informações organizadas",
                "Responsividade completa"
            ])
        
        # Sugestões específicas baseadas na descrição
        if "formulário" in descricao_interface.lower():
            sugestoes["sugestoes_especificas"].extend([
                "Agrupe campos relacionados",
                "Use validação em tempo real",
                "Forneça feedback de progresso",
                "Implemente salvamento automático"
            ])
        
        if "dashboard" in descricao_interface.lower():
            sugestoes["sugestoes_especificas"].extend([
                "Priorize informações mais importantes",
                "Use visualizações de dados claras",
                "Permita personalização do layout",
                "Implemente filtros e busca"
            ])
        
        # Buscar templates relevantes
        templates = carregar_templates_disponiveis()
        palavras_chave = descricao_interface.lower().split()
        for template in templates:
            if any(palavra in template["nome"].lower() for palavra in palavras_chave):
                sugestoes["templates_recomendados"].append(template)
        
        # Próximos passos
        sugestoes["proximos_passos"] = [
            "Criar wireframes baseados nas sugestões",
            "Desenvolver protótipo interativo",
            "Realizar testes de usabilidade",
            "Iterar baseado no feedback dos usuários"
        ]
        
        return sugestoes
    
    except Exception as e:
        logger.error(f"Erro ao sugerir melhorias UX: {e}")
        return {"status": "erro", "erro": str(e)}

@mcp.tool()
def gerar_guia_estilo(nome_projeto: str, paleta_cores: List[str] = None) -> Dict[str, Any]:
    """
    Gera um guia de estilo básico para o projeto.
    
    Args:
        nome_projeto: Nome do projeto
        paleta_cores: Lista de cores em hexadecimal (opcional)
    
    Returns:
        Guia de estilo completo
    """
    try:
        if paleta_cores is None:
            paleta_cores = ["#2563eb", "#1f2937", "#f3f4f6", "#10b981", "#ef4444"]
        
        guia = {
            "status": "sucesso",
            "projeto": nome_projeto,
            "tipografia": {
                "fonte_primaria": "Inter, system-ui, sans-serif",
                "fonte_secundaria": "Georgia, serif",
                "tamanhos": {
                    "h1": "2.5rem",
                    "h2": "2rem",
                    "h3": "1.5rem",
                    "body": "1rem",
                    "small": "0.875rem"
                }
            },
            "cores": {
                "primaria": paleta_cores[0] if len(paleta_cores) > 0 else "#2563eb",
                "secundaria": paleta_cores[1] if len(paleta_cores) > 1 else "#1f2937",
                "fundo": paleta_cores[2] if len(paleta_cores) > 2 else "#f3f4f6",
                "sucesso": paleta_cores[3] if len(paleta_cores) > 3 else "#10b981",
                "erro": paleta_cores[4] if len(paleta_cores) > 4 else "#ef4444"
            },
            "espacamento": DESIGN_PRINCIPLES["visual_hierarchy"]["spacing_scale"],
            "componentes": {
                "botao_primario": {
                    "background": paleta_cores[0] if len(paleta_cores) > 0 else "#2563eb",
                    "color": "#ffffff",
                    "padding": "12px 24px",
                    "border_radius": "8px",
                    "font_weight": "600"
                },
                "card": {
                    "background": "#ffffff",
                    "border": "1px solid #e5e7eb",
                    "border_radius": "12px",
                    "padding": "24px",
                    "box_shadow": "0 1px 3px rgba(0, 0, 0, 0.1)"
                }
            },
            "principios_design": DESIGN_PRINCIPLES,
            "melhores_praticas": UX_BEST_PRACTICES
        }
        
        return guia
    
    except Exception as e:
        logger.error(f"Erro ao gerar guia de estilo: {e}")
        return {"status": "erro", "erro": str(e)}

if __name__ == "__main__":
    mcp.run()