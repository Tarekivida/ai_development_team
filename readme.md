# Development Team AI Agent System

This project sets up a collaborative multi-agent AI development team using [AutoGen](https://github.com/microsoft/autogen) to simulate a software development workflow. The team includes:
  
- **Admin (User Proxy Agent):** Initiates the project, provides requirements, and interacts with the system.
- **Project Manager (Assistant Agent):** Breaks down project requirements into tasks and manages the development flow.
- **Engineer (Assistant Agent):** Implements code based on assigned tasks using LLM capabilities and integrated developer tools.

## Features

- Multi-agent orchestration with `GroupChat` and `GroupChatManager`.
- Dynamic role-based task delegation and communication.
- Engineer agent equipped with file system tools:
  - `list_dir`: Lists files in a directory.
  - `see_file`: Views contents of a file.
  - `modify_code`: Replaces code in a file.
  - `create_file_with_code`: Creates a file with specified code.
  - `execute_command`: Runs shell commands inside the output directory.
- Requirements can be passed as a file or interactively via prompt.
- Support for both local (Ollama) and OpenAI (GPT-4) models.

## Project Structure

```
development_team/
├── main.py               # Main script to initialize agents and launch the project
├── readme.md             # Project documentation
└── utils/
    └── llm_configs.py    # LLM configuration for model selection and API setup
```

## Setup

### 1. Clone the repository
```bash
git clone https://github.com/your-username/development_team.git
cd development_team
```

### 2. Create a virtual environment
```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\\Scripts\\activate on Windows
```

### 3. Install dependencies
```bash
pip install pyautogen spotipy typing_extensions
```

### 4. Set up environment variables
```bash
export OPENAI_API_KEY=your_key_here  # required if using OpenAI
```

### 5. Start Ollama (optional for local models)
```bash
ollama run llama3
```

## Usage

### Option 1: Pass requirements file
```bash
python main.py requirements.txt
```

### Option 2: Interactive mode
```bash
python main.py
# Then type your requirement when prompted
```

## Output

All generated files and operations occur inside the `./output/` directory.

## Tooling Logic

Tools are registered to the `Engineer` agent via decorators. These tools give the LLM ability to interact with the file system during the task execution phase.

## Roadmap

- [ ] Add Tester Agent for QA validation.
- [ ] Integrate unit test generation.
- [ ] Add support for Git operations.
- [ ] Extend capabilities with memory and long-term planning.

## License

This project is open-source and MIT licensed.

## Credits

Built using Microsoft's [AutoGen](https://github.com/microsoft/autogen) framework.
