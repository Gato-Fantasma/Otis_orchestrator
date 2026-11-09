import os
import sys
import time
 
import httpx
from dotenv import load_dotenv
 
load_dotenv()
 
OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODELO = os.getenv("OLLAMA_MODELO", "llama3.2:3b")
GEMINI_CHAVE = os.getenv("GEMINI_API_KEY")
GEMINI_MODELO = os.getenv("GEMINI_MODELO", "gemini-2.5-flash")
 
PROMPT_CLASSIFICACAO = """Você é um classificador. Leia a mensagem do usuário e responda APENAS uma palavra:
SIMPLES - saudação, conversa curta ou pergunta de fato simples.
COMPLEXA - código, explicação longa, análise ou texto elaborado.
 
Mensagem: {mensagem}"""
 
 
def chamar_ollama(texto):
    resposta = httpx.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODELO,
            "messages": [{"role": "user", "content": texto}],
            "stream": False,
        },
        timeout=120,
    )
    resposta.raise_for_status()
    return resposta.json()["message"]["content"]
 
 
def chamar_gemini(texto):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODELO}:generateContent"
    resposta = httpx.post(
        url,
        headers={"x-goog-api-key": GEMINI_CHAVE},
        json={"contents": [{"parts": [{"text": texto}]}]},
        timeout=60,
    )
    resposta.raise_for_status()
    return resposta.json()["candidates"][0]["content"]["parts"][0]["text"]
 
 
def classificar(mensagem):
    inicio = time.perf_counter()
    resposta = chamar_ollama(PROMPT_CLASSIFICACAO.format(mensagem=mensagem))
    duracao = time.perf_counter() - inicio
    destino = "bmo" if resposta.strip().upper().startswith("SIMPLES") else "gemini"
    return destino, duracao
 
 
def main():
    if not GEMINI_CHAVE:
        sys.exit("Erro: GEMINI_API_KEY não encontrada no arquivo .env")
 
    print("Otis - Fase 0 (digite 'sair' para encerrar)")
 
    while True:
        mensagem = input("\nVocê: ").strip()
        if mensagem.lower() == "sair":
            break
        if not mensagem:
            continue
 
        destino, tempo_classificacao = classificar(mensagem)
        print(f"[BMO classificou em {tempo_classificacao:.2f}s -> {destino}]")
 
        inicio = time.perf_counter()
        if destino == "bmo":
            resposta = chamar_ollama(mensagem)
        else:
            resposta = chamar_gemini(mensagem)
        tempo_resposta = time.perf_counter() - inicio
 
        print(f"\nvia {destino} ({tempo_resposta:.2f}s): {resposta}")
 
 
if __name__ == "__main__":
    main()