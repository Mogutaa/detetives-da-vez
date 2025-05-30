import os
import json
from openai import OpenAI
from dotenv import load_dotenv
import re

load_dotenv()

# Configuração da OpenRouter
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
    default_headers={
        "HTTP-Referer": "https://github.com/Mogutaa/detetives-da-vez",
        "X-Title": "Detetives da Vez"
    }
)
MODEL = "google/gemma-3-27b-it:free"

def extrair_json(texto):
    """Tenta extrair um bloco JSON de uma string"""
    try:
        # Tenta encontrar o primeiro bloco de texto entre {}
        inicio = texto.index('{')
        fim = texto.rindex('}')
        json_str = texto[inicio:fim+1]
        return json.loads(json_str)
    except (ValueError, json.JSONDecodeError):
        return None

def gerar_caso(modo="normal", nomes_jogadores=[]):
    prompt = f"""
    ## Instruções
    Crie um caso de mistério completo seguindo EXATAMENTE o formato JSON abaixo.
    NÃO inclua nenhum texto adicional além do JSON.

    ## Formato JSON Exigido:
    {{
      "titulo": "Título do Caso",
      "introducao": "Introdução com cenário do crime",
      "personagens": [
        {{
          "nome": "Nome do Personagem",
          "descricao": "Descrição do personagem",
          "motivacao": "Motivação oculta",
          "culpado": true/false
        }}
      ],
      "locais": [
        {{
          "nome": "Nome do Local",
          "descricao": "Descrição do local"
        }}
      ],
      "pistas": [
        {{
          "descricao": "Descrição da pista",
          "local": "Nome do local associado",
          "verdadeira": true/false
        }}
      ],
      "linha_tempo": [
        "Evento 1",
        "Evento 2"
      ]
    }}

    ## Requisitos:
    - Título criativo
    - Introdução envolvente com cenário do crime
    - 4 a 6 personagens (atribua 'culpado': true para apenas um)
    - 3 a 5 locais com descrições
    - 5 a 7 pistas (algumas com 'verdadeira': false)
    - Linha do tempo com 3 a 5 eventos
    
    Modo: {modo}
    {f"Nomes dos jogadores como personagens: {', '.join(nomes_jogadores)}" if nomes_jogadores else ""}
    """
    
    for tentativa in range(3):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.7
            )
            
            conteudo = response.choices[0].message.content
            
            # Tenta extrair JSON mesmo se houver texto extra
            caso = extrair_json(conteudo)
            if caso:
                # Validação básica da estrutura
                if all(key in caso for key in ["titulo", "introducao", "personagens", "locais", "pistas"]):
                    return caso
                
            # Se não encontrou JSON válido, tenta novamente
            print(f"Tentativa {tentativa+1}: JSON inválido recebido")
            print(conteudo)
            
        except Exception as e:
            print(f"Erro na tentativa {tentativa+1}: {str(e)}")
    
    # Fallback se todas as tentativas falharem
    return {
        "titulo": "O Caso do JSON Desaparecido",
        "introducao": "Algo deu errado ao gerar o caso. O JSON fugiu!",
        "personagens": [
            {
                "nome": "Detetive Falhou",
                "descricao": "Especialista em casos perdidos",
                "motivacao": "Encontrar o JSON perdido",
                "culpado": True
            }
        ],
        "locais": [
            {"nome": "Servidor 404", "descricao": "Lugar onde JSONs se perdem"}
        ],
        "pistas": [
            {"descricao": "Fragmentos de código", "local": "Servidor 404", "verdadeira": True}
        ],
        "linha_tempo": [
            "JSON solicitado",
            "JSON desapareceu",
            "Caso criado manualmente"
        ]
    }

def interrogar_personagem(personagem, pergunta, caso):
    char_info = next((c for c in caso['personagens'] if c['nome'] == personagem), None)
    if not char_info:
        return "Personagem não encontrado"
    
    prompt = f"""
    Você é {personagem} ({char_info['descricao']}). 
    Motivação oculta: {char_info.get('motivacao', '')}
    {'Você é o culpado!' if char_info.get('culpado', False) else 'Você é inocente.'}
    
    Responda à pergunta do detetive de forma breve e natural, mantendo seu personagem:
    "{pergunta}"
    """
    
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content

def avaliar_teoria(teoria, caso):
    prompt = f"""
    Avalie esta teoria sobre o caso '{caso['titulo']}':
    "{teoria}"
    
    Informações reais (em JSON):
    {json.dumps(caso, indent=2)}
    
    Responda com:
    - "CORRETO" se a teoria estiver totalmente correta
    - "INCORRETO" caso contrário
    - Uma narrativa de desfecho
    - Explicação breve dos acertos/erros (sem revelar detalhes não descobertos)
    """
    
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content

def gerar_resumo(caso, pistas, interrogatorios):
    prompt = f"""
    Resuma o caso '{caso['titulo']}' para os detetives:
    - Pistas encontradas: {', '.join(p['descricao'][:50] for p in pistas)}
    - Interrogatórios realizados: {len(interrogatorios)} personagens
    
    Destaque:
    - Contradições importantes
    - Pontos-chave ainda não resolvidos
    - Possíveis teorias (sem revelar o culpado)
    - Sugestões de próximos passos
    """
    
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content