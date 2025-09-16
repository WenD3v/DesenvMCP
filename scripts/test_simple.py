#!/usr/bin/env python3
"""
Teste simples para verificar se o gateway MCP está funcionando
"""

import subprocess
import json
import sys
import time
from pathlib import Path

def test_mcp_simple(service_path: str) -> bool:
    """Teste simples de um MCP"""
    try:
        print(f"Testando {service_path}...")
        
        # Inicia o processo
        process = subprocess.Popen(
            [sys.executable, "app.py"],
            cwd=service_path,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Mensagem de inicialização
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
        
        # Envia inicialização
        process.stdin.write(json.dumps(init_msg) + "\n")
        process.stdin.flush()
        
        # Aguarda resposta com timeout
        import select
        import os
        
        # No Windows, usamos uma abordagem diferente
        if os.name == 'nt':
            time.sleep(1)  # Aguarda um pouco
            
            # Tenta ler a resposta
            try:
                response = process.stdout.readline()
                if response:
                    data = json.loads(response.strip())
                    if "result" in data:
                        print(f"  ✓ {service_path} inicializado")
                        
                        # Tenta listar ferramentas
                        tools_msg = {
                            "jsonrpc": "2.0",
                            "id": 2,
                            "method": "tools/list"
                        }
                        
                        process.stdin.write(json.dumps(tools_msg) + "\n")
                        process.stdin.flush()
                        
                        time.sleep(0.5)
                        tools_response = process.stdout.readline()
                        if tools_response:
                            tools_data = json.loads(tools_response.strip())
                            if "result" in tools_data:
                                tools = tools_data["result"].get("tools", [])
                                print(f"    Ferramentas: {len(tools)}")
                                
                                # Mostra algumas ferramentas
                                for i, tool in enumerate(tools[:5]):
                                    print(f"      {i+1}. {tool.get('name', 'unknown')}")
                                
                                process.terminate()
                                return True
                        
                        print(f"    Sem resposta de ferramentas")
                    else:
                        print(f"  ✗ Erro na inicialização: {data}")
                else:
                    print(f"  ✗ Sem resposta de {service_path}")
            except json.JSONDecodeError as e:
                print(f"  ✗ Erro JSON: {e}")
            except Exception as e:
                print(f"  ✗ Erro: {e}")
        
        process.terminate()
        return False
        
    except Exception as e:
        print(f"  ✗ Erro geral: {e}")
        return False

def main():
    print("=== TESTE SIMPLES DOS MCPs ===")
    
    services = ["mcp-orquestrador", "mcp-analise", "mcp-design"]
    results = {}
    
    for service in services:
        if Path(service).exists():
            results[service] = test_mcp_simple(service)
        else:
            print(f"✗ {service} não encontrado")
            results[service] = False
    
    print("\n=== RESUMO ===")
    for service, status in results.items():
        icon = "✓" if status else "✗"
        print(f"{icon} {service}")
    
    success_count = sum(results.values())
    total_count = len(results)
    
    if success_count == total_count:
        print(f"\n🎉 Todos os {total_count} MCPs estão funcionando!")
    else:
        print(f"\n⚠️  {success_count}/{total_count} MCPs funcionando")
    
    return success_count == total_count

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)