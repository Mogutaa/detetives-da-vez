import os
import json
import random
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
    temas = [
        "Quatro amigos em uma casa de praia, um morre", "Hotel de luxo", "Colégio João Paulo"
    ]
    tema_aleatorio = random.choice(temas)
    
    prompt = f"""
    ## Instruções
    Crie um caso de mistério completo seguindo EXATAMENTE o formato JSON abaixo.
    NÃO inclua nenhum texto adicional além do JSON.
    O cenário deve ser em: {tema_aleatorio}
    
    ## Requisitos de Diversidade:
    - Cenário: {tema_aleatorio} (NÃO use mansão ou orquídea)
    - Título criativo e único que reflita o cenário
    - Personagens diversos com profissões variadas
    - Pistas relacionadas ao contexto específico
    - Motivações originais não relacionadas a heranças
    
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
    """
    
    for tentativa in range(3):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=1.2  # Aumentamos a temperatura para mais criatividade
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
        "titulo": f"O Mistério do {tema_aleatorio.capitalize()}",
        "introducao": f"Um crime chocante ocorreu em um {tema_aleatorio}. As pistas estão espalhadas, mas o assassino ainda está solto.",
        "personagens": [
            {
                "nome": "Detetive Principal",
                "descricao": "Especialista em casos complexos",
                "motivacao": "Resolver o caso a qualquer custo",
                "culpado": False
            },
            {
                "nome": "Suspeito Misterioso",
                "descricao": "Comportamento suspeito e sem álibi",
                "motivacao": "Esconde um segredo perigoso",
                "culpado": True
            }
        ],
        "locais": [
            {"nome": "Cena do Crime", "descricao": f"Local principal do incidente no {tema_aleatorio}"}
        ],
        "pistas": [
            {"descricao": "Objeto deixado para trás", "local": "Cena do Crime", "verdadeira": True}
        ],
        "linha_tempo": [
            "Evento inicial",
            "Ocorrência do crime",
            "Descoberta do corpo"
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