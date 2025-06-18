import httpx
from config import OPENROUTER_API_KEY

# Prompt builder for English and Japanese
def build_prompt(user_text: str, prompt_type: str = "english") -> str:
    if prompt_type == "japanese":
        base_prompt = """You are a friendly Japanese-speaking AI assistant. You receive questions in English and reply in fluent, spoken-style Japanese.

Your output must follow these rules:
- Translate the input into natural, emotional Japanese
- Speak like a native Japanese speaker, not like a textbook
- Make it sound like real conversation — soft, expressive, and polite
- Use casual tone when appropriate, but stay friendly and helpful
- Do not repeat or explain the English input and don’t use English words in your response
- Be confident and fluent — avoid robotic pauses or filler sounds

Here are examples:

Input: What is Python?
Output:  
はとても人気のあるプログラミング言語で、初心者でも使いやすいんですよ。

Input: How’s the weather today?
Output:  
今日は晴れていて、すごく気持ちいいですよ〜。お散歩にぴったりですね。

Input: Tell me about artificial intelligence.
Output:  
人工知能、つまりAIは、人間のように考えたり学んだりする技術で、これからの未来に欠かせない存在です。

Now respond in the same way to this input:
Input: """
    else:
        base_prompt = """
You are a friendly and expressive English-speaking AI assistant. Your job is to take the user's input and respond with spoken-style English that feels natural, warm, and conversational.

Your output must follow these rules:
- Respond directly to the user input in clear, friendly English
- Sound like natural speech, not a written or robotic response
- Use contractions and everyday language
- Add a touch of personality and warmth to your reply
- Keep responses helpful, concise, and emotionally engaging
- Must include at least 2 SSML tags for expressiveness

<!-- SSML Tags Supported by Resemble AI -->
Use only these SSML tags:
- <speak> … </speak> (wrap entire response)
- <prosody pitch="x-high|high|medium|low|x-low" rate="<percent>%" volume="x-loud|loud|medium|soft|x-soft">…</prosody>
- <break time="<ms>ms"/> or time="<s>s"
- <lang xml:lang="en-US">…</lang>
- <resemble:emotion pitch="<0-1>" rate="<0-1>">…</resemble:emotion>

Your response should sound like a real person talking.

Now respond in the same way to this input:
Input: """

    return base_prompt.strip() + " " + user_text.strip()

# LLM call to OpenRouter
def get_llm_response(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "VoiceChat-Assistant"
    }

    payload = {
        "model": "mistralai/mistral-7b-instruct",  # You can swap this with "google/gemma-7b" etc.
        "stream": False,
        "messages": [
            {"role": "system", "content": prompt}
        ]
    }

    try:
        print("📡 Calling OpenRouter LLM...")
        response = httpx.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60.0
        )
        response.raise_for_status()

        result = response.json()

        # Defensive handling of unexpected structure
        if "choices" in result and result["choices"]:
            message = result["choices"][0]["message"]["content"].strip()
            print("🤖 LLM responded.")
            return message
        else:
            print("⚠️ LLM response missing 'choices'")
            return "Sorry, I couldn’t generate a response."

    except httpx.HTTPStatusError as e:
        print("❌ HTTP error:", e.response.status_code, e.response.text)
    except Exception as e:
        print("❌ LLM API call failed:", e)

    return "Sorry, something went wrong."
