import os
import openai
import time
from datetime import datetime
from dotenv import dotenv_values
config = dotenv_values() # create a dict of keys


class OpenAIAssistantManager:
    def __init__(self, model="gpt-3.5-turbo"):
        self.client = openai.OpenAI(api_key=config.get('OPENAI_API_KEY'))
        self.model = model
        self.assistants = {}
        self.threads = {}
        self.log_directory = 'logs'
        self._setup_log_directory()

    def _setup_log_directory(self):
        if not os.path.exists(self.log_directory):
            os.makedirs(self.log_directory)

    def create_assistant(self, name, instructions):
        assistant = self.client.beta.assistants.create(
            name=name, instructions=instructions, model=self.model
        )
        self.assistants[name] = assistant.id
        return assistant

    def create_thread(self):
        thread = self.client.beta.threads.create()
        self.threads[thread.id] = thread
        return thread

    def send_message(self, assistant_name, thread_id, content):
        if assistant_name not in self.assistants:
            raise ValueError("Assistant not found")

        message = self.client.beta.threads.messages.create(
            thread_id=thread_id, role="user", content=content
        )
        return message

    def send_message_and_run_thread(self, assistant_name, thread_id, content):
        if assistant_name not in self.assistants:
            raise ValueError("Assistant not found")

        # Send a message to the thread
        self.send_message(assistant_name, thread_id, content)

        # Execute the run and wait for completion
        run = self.run_thread(assistant_name, thread_id)

        # Retrieve and log messages
        messages = self.list_messages(thread_id=thread_id)
        return messages

    def run_thread(self, assistant_name, thread_id):
        if assistant_name not in self.assistants:
            raise ValueError("Assistant not found")

        assistant_id = self.assistants[assistant_name]
        run = self.client.beta.threads.runs.create(
            thread_id=thread_id, assistant_id=assistant_id
        )
        run_completed = self.wait_on_run(run, thread_id)
        return run_completed
    
    def _log_message(self, thread_id, message):
        # Create a directory for today's date if it doesn't exist
        daily_directory = os.path.join(self.log_directory, datetime.now().strftime('%d_%m_%Y'))
        if not os.path.exists(daily_directory):
            os.makedirs(daily_directory)

        # Define the log file name using the thread ID
        file_name = os.path.join(daily_directory, f'thread_{thread_id}.log')

        # Write the log message to the file
        with open(file_name, 'a') as file:
            log_content = f"Thread ID: {thread_id}, Message: {message}\n"
            file.write(log_content)

        # log file to each request
        file_name = os.path.join(daily_directory, f'{datetime.now().strftime("%H-%M-%S")}.log')
        with open(file_name, 'a') as file:
            log_content = f"Thread ID: {thread_id}, Message: {message}\n"
            file.write(log_content)

    def list_messages(self, thread_id, order='asc', after_message_id=None):
        messages = self.client.beta.threads.messages.list(
            thread_id=thread_id, order=order, after=after_message_id
        )
        self._log_message(thread_id, messages)
        return messages

    def wait_on_run(self, run, thread):
        while run.status == "queued" or run.status == "in_progress":
            run = self.client.beta.threads.runs.retrieve(
                thread_id=thread, run_id=run.id
            )
            time.sleep(0.5)
        return run

# MAIN

manager = OpenAIAssistantManager()

# Create an assistant
assistant = manager.create_assistant(
    name="Math Tutor",
    instructions="You are a personal math tutor. Answer questions briefly, in a sentence or less."
)

# Create a thread
thread = manager.create_thread()

# Send a message to the thread and wait for the assistant's response
messages = manager.send_message_and_run_thread(
    assistant_name="Math Tutor",
    thread_id=thread.id,
    content="I need to solve the equation `3x + 11 = 14`. Can you help me?"
)

# Send a message to the thread and wait for the assistant's response
messages = manager.send_message_and_run_thread(
    assistant_name="Math Tutor",
    thread_id=thread.id,
    content="Could you explain this to me?"
)

# question me
messages = manager.send_message_and_run_thread(
    assistant_name="Math Tutor",
    thread_id=thread.id,
    content="Nice. Now your turn, ask me to solve a equation."
)

