import os
from openai import OpenAI
from datetime import datetime
from dotenv import dotenv_values
config = dotenv_values() # create a dict of keys

class OpenAIClient:
    def __init__(self, model="gpt-3.5-turbo"):
        self.client = OpenAI(api_key=config.get('OPENAI_API_KEY'))
        self.model = model
        self.log_directory = 'logs'
        if not os.path.exists(self.log_directory):
            os.makedirs(self.log_directory)

    def generate_answer(self, messages):
        response = self.client.chat.completions.create(model=self.model, messages=messages)
        self._log_request(messages, response)
        return response.choices[0].message

    def _log_request(self, messages, response):
        current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        file_name = f"{self.log_directory}/openai_request_{current_time}.log"
        with open(file_name, 'w') as file:
            log_content = {
                'time': current_time,
                'model': self.model,
                'messages': messages,
                'response': {
                    'choices': response.choices
                }
            }
            file.write(str(log_content))

# Usage
client = OpenAIClient()
answer = client.generate_answer(
    messages=[
        {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
        {"role": "user", "content": "Compose a poem that explains the concept of recursion in programming."}
    ]
)
print(answer)
