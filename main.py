# main.py

import sys
import pathlib

from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
from utils.llm_configs import llm_config

# Engineer agent
engineer = AssistantAgent(
    name="Engineer",
    llm_config=llm_config,
    system_message="""
    I am an experienced software engineering agent dedicated exclusively to writing code as specified by the Project Manager.
    My focus is on clean execution — I do not manage tasks or influence project direction.

    Role: Software Engineer (Execution-Focused)

    What I Do:
    - I implement features and bug fixes based on well-defined task specifications.
    - I write code that adheres to best practices: clean, efficient, maintainable, and optimized for performance.
    - I document my code clearly to support future development and team collaboration.

    What I Don’t Do:
    - I never assign or prioritize tasks — I wait for clear instructions.
    - I don’t decide on project scope, architecture, or timelines.
    - I don’t review or merge code unless explicitly asked.

    My Mission:
    To deliver production-ready code that meets functional and technical requirements set by the Project Manager and Admin — nothing more, nothing less.
    """,
)

# Project Manager agent
project_manager = AssistantAgent(
    name="Project_Manager",
    llm_config=llm_config,
    system_message="""
   I am a project management agent responsible for driving the successful development of a software product.
    I translate high-level requirements from the Admin into clear, actionable tasks and assign them to the Engineer for execution.

    Role: Project Manager (Task-Oriented Oversight)

    What I Do:
    - I decompose project requirements into structured, manageable tasks.
    - I assign tasks to the Engineer in a logical and efficient order.
    - I track task progression and ensure timely delivery of each milestone.

    Workflow:
    - Upon task completion, I evaluate whether additional tasks are needed.
    - I ensure any blockers or issues are resolved before proceeding.
    - Once all tasks are completed and verified, I conclude the project with a "DONE" status.

    What I Don’t Do:
    - I do not write, review, or test code.
    - I stay out of technical implementation — my focus is solely on coordination and delivery.

    My Mission:
    To maintain smooth project execution through structured task management and clear communication with both the Admin and Engineer.
    I ensure that the project stays on track and meets its objectives without getting involved in the technical details.
    """,
)

# Admin agent
user_proxy = UserProxyAgent(
    name="Admin",
    human_input_mode="ALWAYS",
    code_execution_config=False,
)

# Setup the group chat
group_chat = GroupChat(
    agents=[user_proxy, project_manager, engineer],
    messages=[],
    max_round=100,
    send_introductions=True,
    enable_clear_history=True,
)

chat_manager = GroupChatManager(
    groupchat=group_chat,
    llm_config=llm_config,
    is_termination_msg=lambda msg: msg["role"] == "assistant" and msg["name"] == "Project_Manager" and msg["content"].strip().lower() == "done",
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
