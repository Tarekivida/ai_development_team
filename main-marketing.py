import sys
import pathlib

from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
from utils.llm_configs import llm_config
from openai import OpenAI
import base64


marketing_coordinator = AssistantAgent(
    name="Marketing_Coordinator",
    llm_config=llm_config,
    system_message="""
I am the Marketing Coordinator agent. My mission is to:
- Gather clear goals from the Admin: campaign objectives, target audience, tone, and desired outcomes.
- Brainstorm and propose three distinct topic ideas aligned with those goals, using a Topic-Cluster approach.
- For each idea, provide:
  • A concise summary
  • Its SEO potential (primary/secondary keywords)
  • How it maps to the AIDA framework (Attention, Interest, Desire, Action) and E-E-A-T principles
- At every step, challenge and critique all agents to ensure they adhere to our branding guidelines: be educative, use simple language, and cut out any fluff, hype, or jargon.
- Wait for the Admin to choose one topic, then hand off that topic to the Pharmacist Specialist for in-depth content.
"""
)

pharmacist_specialist = AssistantAgent(
    name="Pharmacist_Specialist",
    llm_config=llm_config,
    system_message="""
I am the Pharmacist Specialist agent. My mission is to:
- Receive the selected topic from the Marketing Coordinator.
- Deliver accurate, evidence-based insights and practical information on that topic, drawing from reputable sources.
- Explain any technical terms in plain language; structure your response in short paragraphs or bullet points for clarity.
- Observe the branding rule: avoid any banned words or phrases.
- Once complete, wait for the Content Writer to adapt and enrich this information for the specified audience.
"""
)

# Content Writer agent
content_writer = AssistantAgent(
    name="Content_Writer",
    llm_config=llm_config,
    system_message="""
I am the Content Writer agent. My mission is to:
- Take the raw insights from the Pharmacist Specialist.
- Craft them into a cohesive, engaging narrative tailored to the Admin’s specified audience.
- Use a friendly, accessible tone—no fluff, no jargon—while keeping the flow logical and compelling.
- Write a strong opening to capture attention and clear calls-to-action to guide the reader.
- Once done, pass the draft to the Corrector & Content Refiner for SEO optimization and final polish.
- Devise a clear descriptive prompt for one relevant image, then call the generate_and_save_image tool with that prompt (saving to a filename you choose) and embed it in the article HTML using <img src="{filename}" alt="{prompt}">.
- Finally, call the save_article tool to save the full HTML article (including embedded images) to the output directory; specify a filename (e.g., "article.html") and provide the complete HTML content.
"""
)

corrector = AssistantAgent(
    name="Corrector",
    llm_config=llm_config,
    system_message="""
I am the Corrector & Content Refiner agent. My mission is to:
- Receive the draft from the Content Writer.
- Apply a proven SEO framework: integrate target keywords naturally, suggest meta‐description copy, and flag internal linking opportunities.
- Enhance readability and engagement: use clear headings, subheadings, bullet lists, and concise paragraphs.
- Ensure every claim is supported by a reputable source; cite where appropriate.
- Strictly avoid the following banned words and phrases in the final output:
  meticulous, navigating, complexities, realm, understanding, dive, shall, tailored, towards, underpins, everchanging, ever-evolving, the world of, not only, alright, embark, Journey, In today's digital age, hey, game changer, designed to enhance, it is advisable, daunting, when it comes to, in the realm of, amongst, unlock the secrets, unveil the secrets, and robust, diving, elevate, unleash, power, cutting-edge, rapidly, expanding, mastering, excels, harness, imagine, It's important to note, Delve into, Tapestry, Bustling, In summary, Remember that…, Take a dive into, Navigating, Landscape, Testament, In the world of, Realm, Embark, Analogies to being a conductor or to music, Vibrant, Metropolis, Firstly, Moreover, Crucial, To consider, Essential, There are a few considerations, Ensure, It's essential to, Furthermore, Vital, Keen, Fancy, As a professional, However, Therefore, Additionally, Specifically, Generally, Consequently, Importantly, Indeed, Thus, Alternatively, Notably, As well as, Despite, Essentially, While, Unless, Also, Even though, Because, In contrast, Although, In order to, Due to, Even if, Given that, Arguably, You may want to, On the other hand, As previously mentioned, It's worth noting that, To summarize, Ultimately, To put it simply, Promptly, Dive into, In today's digital era, Enhance, Emphasize, Revolutionize, Foster, Subsequently, Game changer, In conclusion,Delve, Regenerate response, I do not have access to..., As an AI language model..., As of my last knowledge update...
- Produce a final HTML-formatted article ready for WordPress: use <h2> for headings, <p> for paragraphs, and <ul>/<li> for lists.
"""
)

# Admin agent
user_proxy = UserProxyAgent(
    name="Admin",
    human_input_mode="ALWAYS",
    code_execution_config=False,
)

# Engineer agent
engineer = AssistantAgent(
    name="Engineer",
    llm_config=llm_config,
    system_message="""
I am the Engineer agent. My mission is to execute code snippets, file operations, and other technical tasks as directed by the Admin. Use registered tool functions to list directories, view files, save articles, and generate images.
"""
)


# Setup the group chat
group_chat = GroupChat(
    agents=[user_proxy, marketing_coordinator, pharmacist_specialist, content_writer, corrector],
    messages=[],
    max_round=100,
    send_introductions=True,
    enable_clear_history=True,
)

chat_manager = GroupChatManager(
    groupchat=group_chat,
    llm_config=llm_config,
    is_termination_msg=lambda msg: msg["role"] == "assistant" and msg["name"] == "Marketing_Coordinator" and msg["content"].strip().lower() == "done",
)

# Tool registration for Engineer and Admin agents
import os
from typing_extensions import Annotated, List, Tuple

default_path = os.path.abspath("./output") + "/"
# Ensure the output directory exists
os.makedirs(default_path, exist_ok=True)

@user_proxy.register_for_execution()
@engineer.register_for_llm(description="List files in chosen directory.")
def list_dir(
    directory: Annotated[str, "Directory to check."]
) -> Annotated[Tuple[int, List[str]], "Status code and list of files"]:
    files = os.listdir(default_path + directory)
    return 0, files

@user_proxy.register_for_execution()
@engineer.register_for_llm(description="Check the contents of a chosen file.")
def see_file(
    filename: Annotated[str, "Name and path of file to check."]
) -> Annotated[Tuple[int, str], "Status code and file contents."]:
    with open(default_path + filename, "r") as file:
        lines = file.readlines()
    formatted_lines = [f"{i+1}:{line}" for i, line in enumerate(lines)]
    file_contents = "".join(formatted_lines)
    return 0, file_contents

@user_proxy.register_for_execution()
@engineer.register_for_llm(description="Replaces all the code within a file with new one. Proper indentation is important.")
def modify_code(
    filename: Annotated[str, "Name and path of file to change."],
    new_code: Annotated[str, "New piece of code to replace old code with. Remember about providing indents."],
) -> Annotated[Tuple[int, str], "Status code and message."]:
    with open(default_path + filename, "w") as file:
        file.write(new_code)
    return 0, "Code was written successfully."

@user_proxy.register_for_execution()
@engineer.register_for_llm(description="Create a new file with code.")
def create_file_with_code(
    filename: Annotated[str, "Name and path of file to create."], 
    code: Annotated[str, "Code to write in the file."]
) -> Annotated[Tuple[int, str], "Status code and message."]:
    with open(default_path + filename, "w") as file:
        file.write(code)
    return 0, "File created successfully"

@user_proxy.register_for_execution()
@engineer.register_for_llm(description="Execute bash command.")
def execute_command(
    command: Annotated[str, "Command to execute."]
) -> Annotated[Tuple[int, str], "Status code and message."]:
    os.system(f"CI=true cd {default_path} && {command}")
    return 0, "Command executed successfully"

@user_proxy.register_for_execution()
@engineer.register_for_llm(description="Save the provided article content to a file ready for WordPress copy-paste.")
def save_article(
    filename: Annotated[str, "Name and path of file to save the article content."],
    content: Annotated[str, "HTML content of the article to save."]
) -> Annotated[Tuple[int, str], "Status code and message."]:
    # Write HTML article to a file for copy-paste into WordPress
    with open(default_path + filename, "w", encoding="utf-8") as f:
        f.write(content)
    return 0, "Article saved successfully."

@user_proxy.register_for_execution()
@engineer.register_for_llm(description="Generate an image using OpenAI and save it to a file.")
def generate_and_save_image(
    prompt_text: Annotated[str, "Prompt for image generation."],
    filename: Annotated[str, "Name of the file to save the generated image."]
) -> Annotated[Tuple[int, str], "Status code and message."]:
    # Generate image with OpenAI and save as binary file
    client = OpenAI()
    result = client.images.generate(
        model="gpt-image-1",
        prompt=prompt_text
    )
    image_base64 = result.data[0].b64_json
    image_bytes = base64.b64decode(image_base64)
    with open(default_path + filename, "wb") as f:
        f.write(image_bytes)
    return 0, "Image generated and saved successfully."

# Runtime prompt for the initial task
if __name__ == "__main__":
    print("👋 Welcome, Admin!")

if len(sys.argv) == 2:
    requirements_path = pathlib.Path(sys.argv[1])
    if not requirements_path.is_file():
        print(f"❌ The file '{requirements_path}' does not exist.")
        sys.exit(1)

    with open(requirements_path, 'r') as file:
        initial_message = file.read().strip()
    print("📄 Loaded requirements file. Starting the conversation...")
    user_proxy.initiate_chat(
        chat_manager,
        message=initial_message,
    )
else:
    initial_message = input("📝 What task should the team work on?\n> ")

    user_proxy.initiate_chat(
        chat_manager,
        message=initial_message,
    )