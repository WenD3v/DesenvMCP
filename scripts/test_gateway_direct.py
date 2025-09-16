#!/usr/bin/env python3
"""
Teste direto das funcionalidades do gateway MCP
"""

import subprocess
import json
import sys
import time

def test_gateway_direct():
    """Testa diretamente as funcionalidades do gateway"""
    print("=== TESTE DIRETO DO GATEWAY MCP ===")
    
    try:
        # Inicia o orquestrador
        process = subprocess.Popen(
            [sys.executable, "app.py"],
            cwd="mcp-orquestrador",
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Inicialização
        init_msg = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "clientInfo": {"name": "test", "version": "1.0"}
            }
        }
        
        print("Enviando inicialização...")
        process.stdin.write(json.dumps(init_msg) + "\n")
        process.stdin.flush()
        
        time.sleep(1)
        
        # Lê resposta de inicialização
        init_response = process.stdout.readline()
        if init_response:
            init_data = json.loads(init_response.strip())
            print(f"Inicialização: {init_data.get('result', {}).get('protocolVersion', 'OK')}")
        
        # Envia mensagem initialized
        initialized_msg = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        
        process.stdin.write(json.dumps(initialized_msg) + "\n")
        process.stdin.flush()
        
        time.sleep(1)
        
        # Testa ferramenta específica do gateway
        print("\nTestando ferramenta listar_servicos_mcp...")
        
        call_msg = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "listar_servicos_mcp",
                "arguments": {}
            }
        }
        
        process.stdin.write(json.dumps(call_msg) + "\n")
        process.stdin.flush()
        
        time.sleep(2)
        
        # Lê resposta da ferramenta
        call_response = process.stdout.readline()
        if call_response:
            call_data = json.loads(call_response.strip())
            if "result" in call_data:
                print(f"✓ Ferramenta executada com sucesso")
                print(f"  Resultado: {call_data['result']}")
                
                # Testa health check
                print("\nTestando gateway_health_check...")
                
                health_msg = {
                    "jsonrpc": "2.0",
                    "id": 4,
                    "method": "tools/call",
                    "params": {
                        "name": "gateway_health_check",
                        "arguments": {}
                    }
                }
                
                process.stdin.write(json.dumps(health_msg) + "\n")
                process.stdin.flush()
                
                time.sleep(1)
                
                health_response = process.stdout.readline()
                if health_response:
                    health_data = json.loads(health_response.strip())
                    if "result" in health_data:
                        print(f"✓ Health check executado")
                        print(f"  Status: {health_data['result']}")
                        
                        # Testa análise de código integrada
                        print("\nTestando análise de código integrada...")
                        
                        analise_msg = {
                            "jsonrpc": "2.0",
                            "id": 5,
                            "method": "tools/call",
                            "params": {
                                "name": "analisar_codigo_completo",
                                "arguments": {
                                    "codigo": "def hello():\n    print('Hello World')\n    return True",
                                    "linguagem": "python"
                                }
                            }
                        }
                        
                        process.stdin.write(json.dumps(analise_msg) + "\n")
                        process.stdin.flush()
                        
                        time.sleep(2)
                        
                        analise_response = process.stdout.readline()
                        if analise_response:
                            analise_data = json.loads(analise_response.strip())
                            if "result" in analise_data:
                                print(f"✓ Análise de código executada")
                                result = analise_data['result']
                                if isinstance(result, dict) and 'sintaxe' in result:
                                    print(f"  Funções encontradas: {len(result['sintaxe'].get('funcoes', []))}")
                                    print(f"  Status: {result.get('status', 'unknown')}")
                                
                                process.terminate()
                                return True
                            else:
                                print(f"✗ Erro na análise: {analise_data}")
                        else:
                            print("✗ Sem resposta da análise")
                    else:
                        print(f"✗ Erro no health check: {health_data}")
                else:
                    print("✗ Sem resposta do health check")
            else:
                print(f"✗ Erro na ferramenta: {call_data}")
        else:
            print("✗ Sem resposta da ferramenta")
        
        process.terminate()
        return False
        
    except Exception as e:
        print(f"✗ Erro no teste: {e}")
        return False

def main():
    success = test_gateway_direct()
    
    print("\n=== RESULTADO ===")
    if success:
        print("🎉 Gateway MCP está funcionando corretamente!")
        print("✓ Inicialização OK")
        print("✓ Ferramentas de gateway OK")
        print("✓ Análise integrada OK")
    else:
        print("⚠️  Gateway MCP apresentou problemas")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)