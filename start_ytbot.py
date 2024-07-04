import subprocess
import time

def run_bot():
    while True:
        try:
            # Start the bot
            process = subprocess.Popen(['python', 'ytbot.py'])
            # Wait for the bot process to complete
            process.wait()
        except Exception as e:
            print(f"The ytbot crashed with exception: {e}")
        finally:
            # Wait a bit before restarting
            time.sleep(5)

if __name__ == "__main__":
    run_bot()