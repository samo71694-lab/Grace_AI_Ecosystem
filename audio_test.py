import os
import sys
import subprocess
import asyncio

# Ensure environment is perfectly mapped
try:
    import edge_tts
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "edge-tts"])
    import edge_tts

# We switch to an extremely stable Indian-English voice that bypasses server check errors
VOICE_ID = "en-IN-NeerjaNeural"
OUTPUT_FILE = "grace_welcome.mp3"

async def generate_speech_test():
    # Streamlined text parameter to guarantee response
    test_text = "Welcome to Grace Study Centre AI Portal. Your audio environment is now fully configured."
    
    print("[INFO] Initiating handshake with stable speech engine...")
    try:
        communicate = edge_tts.Communicate(test_text, VOICE_ID)
        await communicate.save(OUTPUT_FILE)
        
        print(f"[SUCCESS] Audio file successfully created: {OUTPUT_FILE}")
        print("[INFO] Launching system audio player...")
        os.system(f"start {OUTPUT_FILE}")
    except Exception as e:
        print(f"[ERROR] Audio track creation failed: {e}")

if __name__ == "__main__":
    print("=== GRACE STUDY CENTRE: FIXED AUDIO INITIALIZER ===")
    asyncio.run(generate_speech_test())