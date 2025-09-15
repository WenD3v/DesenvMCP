#!/usr/bin/env python3
"""
Script de inicialização para a arquitetura modular MCP.
Permite iniciar os serviços individualmente ou em conjunto.
"""

import subprocess
import sys
import json
import os
import time
from pathlib import Path

def load_config():
    """Carrega a configuração dos MCPs."""
    config_path = Path(__file__).parent / "config.json"
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def start_service(service_name, config):
    """Inicia um serviço MCP específico."""
    service_config = config['services'][service_name]
    service_path = Path(__file__).parent / service_config['path']
    
    print(f"Iniciando {service_name}...")
    print(f"Caminho: {service_path}")
    print(f"Função: {service_config['description']}")
    
    # Muda para o diretório do serviço
    os.chdir(service_path)
    
    # Inicia o serviço
    try:
        process = subprocess.Popen(
            [sys.executable, "app.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print(f"✓ {service_name} iniciado com PID {process.pid}")
        return process
    except Exception as e:
        print(f"✗ Erro ao iniciar {service_name}: {e}")
        return None

def test_service(service_name, config):
    """Testa se um serviço está funcionando corretamente."""
    service_config = config['services'][service_name]
    service_path = Path(__file__).parent / service_config['path']
    
    print(f"\nTestando {service_name}...")
    
    # Verifica se o arquivo app.py existe
    app_file = service_path / "app.py"
    if not app_file.exists():
        print(f"✗ Arquivo app.py não encontrado em {service_path}")
        return False
    
    # Tenta importar e verificar sintaxe
    try:
        # Muda temporariamente para o diretório do serviço
        original_cwd = os.getcwd()
        os.chdir(service_path)
        
        # Verifica sintaxe Python
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", "app.py"],
            capture_output=True,
            text=True
        )
        
        os.chdir(original_cwd)
        
        if result.returncode == 0:
            print(f"✓ {service_name} - Sintaxe OK")
            return True
        else:
            print(f"✗ {service_name} - Erro de sintaxe: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"✗ {service_name} - Erro no teste: {e}")
        return False

def main():
    """Função principal do script."""
    if len(sys.argv) < 2:
        print("Uso: python start_mcps.py [comando] [serviço]")
        print("")
        print("Comandos disponíveis:")
        print("  test [serviço]     - Testa um serviço específico ou todos")
        print("  start [serviço]    - Inicia um serviço específico")
        print("  start-all          - Inicia todos os serviços")
        print("  list               - Lista todos os serviços disponíveis")
        print("")
        print("Serviços disponíveis: mcp-orquestrador, mcp-analise")
        return
    
    command = sys.argv[1]
    config = load_config()
    
    if command == "list":
        print("Serviços MCP disponíveis:")
        print("="*50)
        for name, service_config in config['services'].items():
            print(f"• {name}")
            print(f"  Função: {service_config['description']}")
            print(f"  Caminho: {service_config['path']}")
            print(f"  Tipo: {service_config['role']}")
            print()
    
    elif command == "test":
        if len(sys.argv) > 2:
            service_name = sys.argv[2]
            if service_name in config['services']:
                test_service(service_name, config)
            else:
                print(f"Serviço '{service_name}' não encontrado.")
        else:
            print("Testando todos os serviços...")
            all_ok = True
            for service_name in config['services']:
                if not test_service(service_name, config):
                    all_ok = False
            
            if all_ok:
                print("\n✓ Todos os serviços passaram nos testes!")
            else:
                print("\n✗ Alguns serviços falharam nos testes.")
    
    elif command == "start":
        if len(sys.argv) > 2:
            service_name = sys.argv[2]
            if service_name in config['services']:
                process = start_service(service_name, config)
                if process:
                    print(f"\nServiço {service_name} em execução.")
                    print("Pressione Ctrl+C para parar.")
                    try:
                        process.wait()
                    except KeyboardInterrupt:
                        print(f"\nParando {service_name}...")
                        process.terminate()
            else:
                print(f"Serviço '{service_name}' não encontrado.")
        else:
            print("Especifique o nome do serviço para iniciar.")
    
    elif command == "start-all":
        print("Iniciando todos os serviços MCP...")
        processes = []
        
        # Inicia serviços na ordem de dependência
        service_order = ['mcp-analise', 'mcp-orquestrador']
        
        for service_name in service_order:
            if service_name in config['services']:
                process = start_service(service_name, config)
                if process:
                    processes.append((service_name, process))
                    time.sleep(2)  # Aguarda um pouco entre inicializações
        
        if processes:
            print(f"\n✓ {len(processes)} serviços iniciados com sucesso!")
            print("Pressione Ctrl+C para parar todos os serviços.")
            
            try:
                # Aguarda todos os processos
                for name, process in processes:
                    process.wait()
            except KeyboardInterrupt:
                print("\nParando todos os serviços...")
                for name, process in processes:
                    print(f"Parando {name}...")
                    process.terminate()
        else:
            print("✗ Nenhum serviço foi iniciado com sucesso.")
    
    else:
        print(f"Comando '{command}' não reconhecido.")
        print("Use 'python start_mcps.py' sem argumentos para ver a ajuda.")

if __name__ == "__main__":
    main()