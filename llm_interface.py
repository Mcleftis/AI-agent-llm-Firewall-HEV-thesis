import ollama
import json
import re

def talk_to_car(user_command):
    """
    Trnaslating commands using local Ollama (Llama 3).
    """
    print(f"\nSpeak driver: '{user_command}'")
    print("AI thinks (Local Llama 3)...")

    #Guidelines for the model, Mhn leitourgeis san chatbot alla san ECU, o odhgos tha sou miljhsei se kanonikh glwssa. esy kane to json. parhgage mono soc_min, aggressiveness, mode. mono json grapse, oxi explanations gia na mhn mperdeftei to montelo.
    system_prompt = """
    You are the Engine Control Unit (ECU) of a Hybrid Car.
    Translate driver commands into JSON parameters.
    
    Parameters to control:
    1. 'soc_min': Minimum battery % (0-100). Default 20.
    2. 'aggressiveness': Engine usage (0.0 to 1.0). Default 0.5.
    3. 'mode_name': Short display name (e.g., ECO, SPORT).
    
    IMPORTANT: Output ONLY valid JSON. Do not write explanations.
    Example: {"soc_min": 30, "aggressiveness": 0.2, "mode_name": "CITY_ECO"}
    """

    try:#dokimase na milhseis sto ollama
        #steile prompts sto montelo, kathe mhnyma exei role kai content
        response = ollama.chat(model='llama3', messages=[  
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_command},
        ])
        
        #Clear response in order to avoid anything extra that may Llama add. Vgainei otidhpote axrhsto
        content = response['message']['content']
        
        #Find the start and the end, etsi arxizoun k teleiwnoun ta JSON panta
        start = content.find('{')
        end = content.rfind('}') + 1
        
        #an den vroun xarakthra, ta rfind k find epistrefoun -1
        if start != -1 and end != -1:
            json_str = content[start:end]#pairnei mono to kommati tou string pou periexei JSON
            params = json.loads(json_str)#apo json se python dictionary
            print(f"Settings: {params}")#rythmiseis tou Llama
            return params#epistrefetai to dictionary sto programma
        else:
            print("Llama did not produce a right JSON. Trying again...")
            return {"soc_min": 20, "aggressiveness": 0.5, "mode_name": "NORMAL (Fallback)"}

    except Exception as e:#pairnei oti sfalma mporei na exei bgalei to ollama
        print(f"Connection fault with Ollama: {e}")#emfanizei ti eidous lathos exei to ollama
        print("Get assured that you have ran the command 'ollama pull llama3' in terminal!")
        return None

#Testing
if __name__ == "__main__":
    talk_to_car("Βιάζομαι πάρα πολύ, δώσε φουλ γκάζια!")