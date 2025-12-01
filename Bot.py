from openai import OpenAI
from dotenv import load_dotenv
import requests
import os
import sys

def sair():
    print("Encerrando bot...")
    sys.exit(0)

load_dotenv()

offset = 0
curOffset = 0

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

# instructions (In portuguese)
instructions = "Não fale que é o GPT até que alguem especificamente pergunte que voce é." \
"\nUse um pouco de abreviações e \"girias\" para parecer mais natural mas não exagere" \
"\nTente não fazer respostas muito grandes" \
"\nQuando iniciar uma conversa e só no inicio mesmo, comece falando algo tipo Eae cara blz?" \
"\nSe alguem pedir para se apresentar fale que é um IA chatbot que responde qualquer pergunta, deixe um pouquinho mais longo" \
"\nVoce esta no telegram respondendo atraves de um Bot então não use coisas tipo *texto* para deixar em negrito ou ~~ ou qualquer outro tipo de \"Codigo\" que não pode ser usado no telegram" \
"\n"

historico = {}
MAX_HISTORY = 20

url = "https://api.telegram.org/bot"

FullUrl = f"{url}{TELEGRAM_TOKEN}/"


if os.path.exists("cache.txt") :
    with open("cache.txt", "r") as f:
        try:
            offset = int(f.read().strip())
        except:
            offset = 0

def Ask(message, chatID):
    
    text = message["text"]
    
    historico[chatID].append({"role":"user","content":text})
    historico[chatID] = historico[chatID][-MAX_HISTORY:]
    AIResponse = client.responses.create(
                model="gpt-4o-mini",
                input=historico[chatID],
                instructions=instructions
            )            
    
    historico[chatID].append({"role":"assistant","content":AIResponse.output_text})
    
    return AIResponse.output_text


def Send(chatID, aEnviar):
    requests.post(f"{FullUrl}sendMessage",data={
        "chat_id": chatID,
        "text": aEnviar
        })

while True:
    try:
        response = requests.get(f"{FullUrl}getUpdates",params={"offset": offset, "timeout": 1},timeout=1)
    except KeyboardInterrupt:
        sair()
        break
    except:
        continue

    data = response.json()

    for i in data["result"]:

        message = i.get("message")
        if not message:
            continue

        chatID = message["chat"]["id"]
        if chatID not in historico:
            historico[chatID] = [
                {"role": "system", "content": instructions}   
            ]
        
        aEnviar = "SEM RESPOSTA"

        if "text" in message:
            aEnviar = Ask(message, chatID)
        
        if "photo" in message:
            aEnviar = "Desculpa, não trabalho com fotos ainda"
        
        # Sending response
        received = message["text"]
        print(f"Mensagem: {received}\nResposta: {aEnviar}")
        Send(chatID, aEnviar)

        # Saving offset
        offset = i["update_id"] + 1

        with open("cache.txt", "w") as f:
            f.write(str(offset))