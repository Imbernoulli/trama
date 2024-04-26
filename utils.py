import openai

def generate_content(prompt, target_word_count, max_retries=100):
    messages = [
        {"role": "system", "content": "You are a helpful assistant that generates content of specified length."},
        {"role": "user", "content": prompt}
    ]
    
    client = openai.OpenAI(
            api_key="sk-xI456rwj0fHZxe4F11C46965BeE8448eAb5aC5A3Db79F01e",
            base_url="https://sailaoda.cn/v1/",
        )

    retries = 0
    while retries < max_retries:
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo-16k",  
                messages=messages,
                temperature=0,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating content: {e}. Retrying...")
            retries += 1
    
    print(f"Failed to generate content after {max_retries} retries.")
    return ""