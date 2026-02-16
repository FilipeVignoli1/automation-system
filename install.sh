#!/bin/bash
# Script de instalação para Linux/Mac

echo "======================================"
echo "Instalando Sistema de Automação Sirius"
echo "======================================"
echo

# Verifica se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "[ERRO] Python 3 não encontrado!"
    echo "Instale o Python 3.8 ou superior"
    exit 1
fi

echo "[OK] Python encontrado"
echo

# Instala dependências
echo "Instalando dependências..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "[ERRO] Falha ao instalar dependências"
    exit 1
fi

echo "[OK] Dependências instaladas"
echo

# Cria arquivo de credenciais se não existir
if [ ! -f config/credentials.env ]; then
    echo "Criando arquivo de credenciais..."
    cp config/credentials.env.example config/credentials.env
    echo
    echo "======================================"
    echo "ATENÇÃO: Configure suas credenciais!"
    echo "======================================"
    echo "Edite o arquivo: config/credentials.env"
    echo
fi

echo
echo "======================================"
echo "Instalação concluída!"
echo "======================================"
echo
echo "Para executar:"
echo "  python3 main.py"
echo
echo "Para ajuda:"
echo "  python3 main.py --help"
echo
