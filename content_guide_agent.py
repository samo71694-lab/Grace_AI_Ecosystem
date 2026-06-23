import os
import sys
import json
import requests
import asyncio
import subprocess
import re

# =====================================================================
# SYSTEM AUTOMATION: GUARANTEE DEPENDENCIES
# =====================================================================
try:
    import edge_tts
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "edge-tts"])
    import edge_tts

try:
    import pypdf
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pypdf"])
    import pypdf

# =====================================================================
# GLOBAL LAYER CONFIGURATION
# =====================================================================
CUSTOM_KEY = "AQ.Ab8RN6KlJlnnY00LlkGukk-Nu6jylXth_aAqZQnJguuobtJPBg"
VOICE_ID = "en-IN-NeerjaNeural"  
AUDIO_OUTPUT = "agent_speech.mp3"
KNOWLEDGE_DIR = "knowledge_base"

if not os.path.exists(KNOWLEDGE_DIR):
    os.makedirs(KNOWLEDGE_DIR)

def clean_text_for_speech(raw_text: str) -> str:
    """Removes markdown symbols and emojis for clean natural narration."""
    cleaned = re.sub(r'\*\*|__', '', raw_text)
    cleaned = re.sub(r'\*', '', cleaned)
    cleaned = cleaned.replace("Smiling face with smiling eyes", "")
    cleaned = cleaned.replace("Smiling face", "")
    cleaned = re.sub(r'[\u2600-\u27BF]|[\uE000-\uF8FF]|\uD83C[\uDC00-\uDFFF]|\uD83D[\uDC00-\uDFFF]|\uD83E[\uDC00-\uDFFF]', '', cleaned)
    return cleaned.strip()

def play_audio_safely(filename: str):
    """Uses native Windows system file associations directly."""
    try:
        full_path = os.path.abspath(filename)
        if os.path.exists(full_path):
            os.startfile(full_path)
    except Exception:
        pass  

async def speak_text(text_to_say: str):
    """Generates and plays clean voice stream instantly."""
    try:
        safe_speech_text = clean_text_for_speech(text_to_say)
        communicate = edge_tts.Communicate(safe_speech_text, VOICE_ID)
        await communicate.save(AUDIO_OUTPUT)
        play_audio_safely(AUDIO_OUTPUT)
    except Exception:
        pass  

# =====================================================================
# OPTIMIZED LIGHTWEIGHT PDF READER
# =====================================================================
def load_local_knowledge() -> str:
    """Extracts first 30 pages to prevent memory freeze while ensuring full chapter context."""
    combined_knowledge = ""
    try:
        if not os.path.exists(KNOWLEDGE_DIR):
            return ""
        files = os.listdir(KNOWLEDGE_DIR)
        for file in files:
            file_path = os.path.join(KNOWLEDGE_DIR, file)
            if file.endswith('.pdf'):
                try:
                    reader = pypdf.PdfReader(file_path)
                    pdf_text = ""
                    # Reading a maximum of 30 pages for fast processing
                    max_pages = min(30, len(reader.pages))
                    for idx in range(max_pages):
                        text = reader.pages[idx].extract_text()
                        if text: pdf_text += text + "\n"
                    if pdf_text.strip():
                        combined_knowledge += f"\n--- Book Reference: {file} ---\n" + pdf_text + "\n"
                except Exception: pass
            elif file.endswith('.txt') or file.endswith('.json'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    combined_knowledge += f"\n--- Document Content: {file} ---\n" + f.read() + "\n"
        if combined_knowledge.strip():
            return "\n[LOCAL BOOK CONTEXT]:\n" + combined_knowledge
        return ""
    except Exception:
        return ""

# =====================================================================
# BACKEND AI PROCESSING CORE
# =====================================================================
def ask_gemini_direct(system_instruction: str, history: list, user_message: str) -> str:
    local_context = load_local_knowledge()
    full_instruction = system_instruction + local_context

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={CUSTOM_KEY}"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "systemInstruction": {"parts": [{"text": full_instruction}]},
        "contents": history + [{"role": "user", "parts": [{"text": user_message}]}]
    }
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        return "Backend authentication setup mismatch."
    except Exception:
        return "Network connection slow hai."

def get_agent_instructions(profile: dict) -> str:
    base = (
        "You are 'Grace Content Guide Agent' from Grace Study Centre. Teach kids lovingly. "
        "Simplify concepts using NCERT/PSEB rules. Keep text response clean, short and precise. "
        "Do NOT write markdown style stars or emojis in sentences if possible.\n\n"
    )
    return base + f"Student Grade: {profile['class_level']}, Subject: {profile['subject']}."

# =====================================================================
# INTERACTIVE APPLICATION INTERACTION LOOP
# =====================================================================
async def main_tutor_loop():
    print("\n" + "="*60)
    print("      🔴 GRACE STUDY CENTRE: MULTI-MODAL LIVE PORTAL v2.2 🔴       ")
    print("="*60 + "\n")
    
    name = input("Aapka Naam kya hai? (Student Name): ").strip()
    class_level = input("Aap kaunsi class mein hain? (e.g., 8th): ").strip()
    subject = input("Aaj kaunsa subject padhna hai? (e.g., Science): ").strip()
    
    print("\n--- PASANDIDA OUTPUT MODE CHUNEN ---")
    print("1. Text Only (Sirf screen par likh kar dikhao)")
    print("2. Voice Only (Sirf bol kar sunao, screen clean rakho)")
    print("3. Hybrid Mode (Likh kar aur Bol kar dono)")
    mode_choice = input("Apna option select karein (1, 2, ya 3): ").strip()
    
    interaction_mode = "hybrid"
    if mode_choice == "1": interaction_mode = "text"
    elif mode_choice == "2": interaction_mode = "voice"
    
    profile = {
        "name": name if name else "Student",
        "class_level": class_level if class_level else "8th",
        "subject": subject if subject else "Science",
        "mode": interaction_mode
    }
    
    sys_instruction = get_agent_instructions(profile)
    chat_history = []
    
    welcome_prompt = f"Hi! My name is {profile['name']}. Greet me short according to my level."
    
    print("\n[System] Connecting to Grace Audio Engine Core...")
    reply = ask_gemini_direct(sys_instruction, chat_history, welcome_prompt)
    
    if profile["mode"] in ["text", "hybrid"]:
        print(f"\n[Agent]: {reply}")
    if profile["mode"] in ["voice", "hybrid"]:
        if profile["mode"] == "voice":
            print(f"\n[Agent]: Speaking response...")
        await speak_text(reply)
        
    chat_history.append({"role": "user", "parts": [{"text": welcome_prompt}]})
    chat_history.append({"role": "model", "parts": [{"text": reply}]})
    
    print("\n--- Portal Active! (Type 'EXIT' to quit, Type 'BOLKARI' to hear last statement) ---")
    
    while True:
        try:
            user_input = input(f"\n[{profile['name']}]: ").strip()
            if user_input.upper() in ["EXIT", "BYE", "QUIT"]:
                exit_msg = f"Goodbye {profile['name']}! Grace Study Centre ke sath padhte raho!"
                if profile["mode"] != "voice": print(f"\n[Agent]: {exit_msg}")
                await speak_text(exit_msg)
                break
            if not user_input:
                continue
                
            if "bol kar sunao" in user_input.lower() or "sunao" in user_input.lower():
                print("\n[System]: Reading last answer out loud...")
                await speak_text(chat_history[-1]["parts"][0]["text"])
                continue
                
            reply = ask_gemini_direct(sys_instruction, chat_history, user_input)
            
            if profile["mode"] in ["text", "hybrid"]:
                print(f"\n[Agent]: {reply}")
            if profile["mode"] in ["voice", "hybrid"]:
                if profile["mode"] == "voice":
                    print(f"\n[Agent]: Speaking response...")
                await speak_text(reply)
                
            chat_history.append({"role": "user", "parts": [{"text": user_input}]})
            chat_history.append({"role": "model", "parts": [{"text": reply}]})
        except (KeyboardInterrupt, SystemExit):
            break

if __name__ == "__main__":
    asyncio.run(main_tutor_loop())