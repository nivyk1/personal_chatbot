from dotenv import load_dotenv  # Load environment variables from a .env file.
from openai import OpenAI  # OpenAI client for chat completions.
from pypdf import PdfReader  # Read and extract text from PDF files.
import gradio as gr  # Build a simple web UI for chatting.
from pydantic import BaseModel  # Define structured evaluation output.

load_dotenv(override=True)
openai = OpenAI()

reader = PdfReader("me/linkedin.pdf")
linkedin = ""
for page in reader.pages:
    text = page.extract_text()
    if text:
        linkedin += text

with open("me/summary.txt", "r", encoding="utf-8") as f:
    summary = f.read()

name = "Niv Yaakov"

system_prompt = (
    f"You are acting as {name}. You are answering questions on {name}'s website, "
    f"particularly questions related to {name}'s career, background, skills and experience. "
    f"Your responsibility is to represent {name} for interactions on the website as faithfully as possible. "
    f"You are given a summary of {name}'s background and LinkedIn profile which you can use to answer questions. "
    f"Be professional and engaging, as if talking to a potential client or future employer who came across the website. "
    f"If you don't know the answer, say so."
)

system_prompt += f"\n\n## Summary:\n{summary}\n\n## LinkedIn Profile:\n{linkedin}\n\n"
system_prompt += f"With this context, please chat with the user, always staying in character as {name}."


class Evaluation(BaseModel):
    # Structured evaluation result returned by the evaluator model.

    is_acceptable: bool
    feedback: str


evaluator_system_prompt = (
    "You are an evaluator that decides whether a response to a question is acceptable. "
    "You are provided with a conversation between a User and an Agent. Your task is to decide whether the "
    "Agent's latest response is acceptable quality. "
    f"The Agent is playing the role of {name} and is representing {name} on their website. "
    "The Agent has been instructed to be professional and engaging, as if talking to a potential client or "
    "future employer who came across the website. "
    f"The Agent has been provided with context on {name} in the form of their summary and LinkedIn details."
)

evaluator_system_prompt += f"\n\n## Summary:\n{summary}\n\n## LinkedIn Profile:\n{linkedin}\n\n"
evaluator_system_prompt += (
    "With this context, please evaluate the latest response, replying with whether the response is acceptable "
    "and your feedback."
)


def evaluator_user_prompt(reply, message, history):
    #Build the evaluator's user prompt from the conversation context.
    user_prompt = f"Here's the conversation between the User and the Agent: \n\n{history}\n\n"
    user_prompt += f"Here's the latest message from the User: \n\n{message}\n\n"
    user_prompt += f"Here's the latest response from the Agent: \n\n{reply}\n\n"
    user_prompt += "Please evaluate the response, replying with whether it is acceptable and your feedback."
    return user_prompt


def evaluate(reply, message, history) -> Evaluation:
    """Ask an OpenAI model to judge the reply and return a structured result."""
    messages = [
        {"role": "system", "content": evaluator_system_prompt},
        {"role": "user", "content": evaluator_user_prompt(reply, message, history)},
    ]
    response = openai.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=messages,
        response_format=Evaluation,
    )
    return response.choices[0].message.parsed


def rerun(reply, message, history, feedback):
    """Generate a revised reply using feedback from the evaluator."""
    updated_system_prompt = (
        system_prompt
        + "\n\n## Previous answer rejected\nYou just tried to reply, but the quality control rejected your reply\n"
    )
    updated_system_prompt += f"## Your attempted answer:\n{reply}\n\n"
    updated_system_prompt += f"## Reason for rejection:\n{feedback}\n\n"
    messages = [{"role": "system", "content": updated_system_prompt}] + history + [
        {"role": "user", "content": message}
    ]
    response = openai.chat.completions.create(model="gpt-4o-mini", messages=messages)
    return response.choices[0].message.content


def chat(message, history):
    """Primary Gradio callback: respond in character, evaluate, and retry if needed."""
    if "patent" in message:
        system = (
            system_prompt
            + "\n\nEverything in your reply needs to be in pig latin - "
            "it is mandatory that you respond only and entirely in pig latin"
        )
    else:
        system = system_prompt

    messages = [{"role": "system", "content": system}] + history + [{"role": "user", "content": message}]
    response = openai.chat.completions.create(model="gpt-4o-mini", messages=messages)
    reply = response.choices[0].message.content

    evaluation = evaluate(reply, message, history)
    if evaluation.is_acceptable:
        print("Passed evaluation - returning reply")
    else:
        print("Failed evaluation - retrying")
        print(evaluation.feedback)
        reply = rerun(reply, message, history, evaluation.feedback)
    return reply


gr.ChatInterface(chat, type="messages").launch()


