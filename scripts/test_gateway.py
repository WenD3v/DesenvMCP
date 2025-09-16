#!/usr/bin/env python3
"""
Script de teste para verificar a integração do Gateway MCP via stdio
"""

import subprocess
import json
import sys
import time
from pathlib import Path

def test_mcp_service(service_path: str, service_name: str) -> bool:
    """Testa um serviço MCP via stdio"""
    try:
        print(f"\n=== Testando {service_name} ===")
        
        # Inicia o processo MCP
        process = subprocess.Popen(
            [sys.executable, "app.py"],
            cwd=service_path,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Mensagem de inicialização MCP
        init_message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        # Envia mensagem de inicialização
        init_json = json.dumps(init_message) + "\n"
        process.stdin.write(init_json)
        process.stdin.flush()
        
        # Lê resposta
        try:
            response_line = process.stdout.readline()
            if response_line:
                response = json.loads(response_line.strip())
                if "result" in response:
                    print(f"✓ {service_name} inicializado com sucesso")
                    
                    # Lista ferramentas disponíveis
                    tools_message = {
                        "jsonrpc": "2.0",
                        "id": 2,
                        "method": "tools/list"
                    }
                    
                    tools_json = json.dumps(tools_message) + "\n"
                    process.stdin.write(tools_json)
                    process.stdin.flush()
                    
                    tools_response = process.stdout.readline()
                    if tools_response:
                        tools_data = json.loads(tools_response.strip())
                        if "result" in tools_data and "tools" in tools_data["result"]:
                            tools = tools_data["result"]["tools"]
                            print(f"  Ferramentas disponíveis: {len(tools)}")
                            for tool in tools[:3]:  # Mostra apenas as primeiras 3
                                print(f"    - {tool.get('name', 'unknown')}")
                            
                            process.terminate()
                            return True
                
        except json.JSONDecodeError as e:
            print(f"✗ Erro ao decodificar resposta de {service_name}: {e}")
        
        process.terminate()
        return False
        
    except Exception as e:
        print(f"✗ Erro ao testar {service_name}: {e}")
        return False

def test_gateway_integration():
    """Testa a integração específica do gateway"""
    print("\n=== Testando integração do Gateway MCP ===")
    
    gateway_path = Path("mcp-orquestrador")
    if not gateway_path.exists():
        print("✗ Diretório do gateway não encontrado")
        return False
    
    try:
        # Inicia o gateway
        process = subprocess.Popen(
            [sys.executable, "app.py"],
            cwd=gateway_path,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Inicialização
        init_message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            }
        }
        
        process.stdin.write(json.dumps(init_message) + "\n")
        process.stdin.flush()
        
        init_response = process.stdout.readline()
        if not init_response:
            print("✗ Sem resposta de inicialização")
            process.terminate()
            return False
        
        # Lista ferramentas do gateway
        tools_message = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        
        process.stdin.write(json.dumps(tools_message) + "\n")
        process.stdin.flush()
        
        tools_response = process.stdout.readline()
        if tools_response:
            tools_data = json.loads(tools_response.strip())
            if "result" in tools_data and "tools" in tools_data["result"]:
                tools = tools_data["result"]["tools"]
                gateway_tools = [t["name"] for t in tools if "gateway" in t["name"] or "proxy" in t["name"]]
                
                print(f"✓ Gateway tem {len(tools)} ferramentas disponíveis")
                print(f"  Ferramentas de gateway: {len(gateway_tools)}")
                
                # Testa uma ferramenta específica do gateway
                if "listar_servicos_mcp" in [t["name"] for t in tools]:
                    print("\n  Testando ferramenta listar_servicos_mcp...")
                    
                    call_message = {
                        "jsonrpc": "2.0",
                        "id": 3,
                        "method": "tools/call",
                        "params": {
                            "name": "listar_servicos_mcp",
                            "arguments": {}
                        }
                    }
                    
                    process.stdin.write(json.dumps(call_message) + "\n")
                    process.stdin.flush()
                    
                    call_response = process.stdout.readline()
                    if call_response:
                        call_data = json.loads(call_response.strip())
                        if "result" in call_data:
                            print("  ✓ Ferramenta listar_servicos_mcp executada com sucesso")
                            print(f"    Resultado: {call_data['result'][:100]}...")
                        else:
                            print(f"  ✗ Erro na execução: {call_data}")
                
                process.terminate()
                return True
        
        process.terminate()
        return False
        
    except Exception as e:
        print(f"✗ Erro no teste de integração: {e}")
        return False

def main():
    """Função principal de teste"""
    print("=== TESTE DE INTEGRAÇÃO DO GATEWAY MCP (STDIO) ===")
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Testa serviços individuais
    services = {
        "mcp-orquestrador": "mcp-orquestrador",
        "mcp-analise": "mcp-analise", 
        "mcp-design": "mcp-design"
    }
    
    results = {}
    for service_name, service_path in services.items():
        if Path(service_path).exists():
            results[service_name] = test_mcp_service(service_path, service_name)
        else:
            print(f"✗ {service_name} não encontrado em {service_path}")
            results[service_name] = False
    
    # Teste específico do gateway
    gateway_integration = test_gateway_integration()
    
    # Resumo
    print("\n=== RESUMO DOS TESTES ===")
    successful_services = sum(results.values())
    total_services = len(results)
    
    print(f"Serviços MCP funcionais: {successful_services}/{total_services}")
    print(f"Integração do gateway: {'✓' if gateway_integration else '✗'}")
    
    for service, status in results.items():
        status_icon = "✓" if status else "✗"
        print(f"  {status_icon} {service}")
    
    if successful_services == total_services and gateway_integration:
        print("\n🎉 TODOS OS TESTES PASSARAM! Gateway MCP está funcionando corretamente.")
        return True
    else:
        print("\n⚠️  Alguns testes falharam. Verifique os logs acima.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)