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

CHAMADAS = {"bmo": chamar_ollama, "gemini": chamar_gemini}


def primeira_linha(erro):
    return str(erro).splitlines()[0]
 
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
 
        try:
            destino, tempo_classificacao = classificar(mensagem)
            print(f"[BMO classificou em {tempo_classificacao:.2f}s -> {destino}]")
        except (httpx.HTTPError, KeyError) as erro:
            destino = "gemini"
            print(f"[BMO não conseguiu classificar: {primeira_linha(erro)} -> usando gemini]")

        reserva = "gemini" if destino == "bmo" else "bmo"
        resposta = None

        for ia in (destino, reserva):
            try:
                inicio = time.perf_counter()
                resposta = CHAMADAS[ia](mensagem)
                break
            except (httpx.HTTPError, KeyError) as erro:
                print(f"[{ia} falhou: {primeira_linha(erro)}]")

        if resposta is None:
            print("\nNenhuma IA conseguiu responder. Tente de novo.")
            continue

        tempo_resposta = time.perf_counter() - inicio
        aviso = f", fallback porque {destino} falhou" if ia != destino else ""
        print(f"\nvia {ia} ({tempo_resposta:.2f}s{aviso}): {resposta}")
 
 
if __name__ == "__main__":
    main()