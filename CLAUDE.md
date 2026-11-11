# CLAUDE.md — development_team (« AI Development Team »)

Document de reprise à froid. Rédigé le 2026-11-11 à partir de l'exploration du dépôt (code, branches, historique, .gitignore).
Tout ce qui n'a pas pu être vérifié est signalé comme **inconnu**.

## 1. Objectif et contexte

- Prototype d'**équipe de développement logiciel simulée par agents LLM**, basé sur **AutoGen** (`pyautogen` 0.9.0, API « classique » `AssistantAgent` / `UserProxyAgent` / `GroupChat` / `GroupChatManager`).
- L'humain (rôle « Admin ») donne une exigence (texte saisi ou fichier), un agent Project Manager la découpe en tâches, un agent Engineer écrit le code dans `./output/` via des outils fichiers/shell, un agent Debugger (branche `tester-agent`) teste.
- Utilisateur visé : le développeur lui-même (usage personnel / expérimentation). Pas de déploiement, pas d'interface web (une spec d'UI web existe hors git, voir §7).
- Une variante **marketing** (`main-marketing.py`) réutilise la même mécanique pour produire un article de blog santé/pharmacie au format HTML WordPress (agents Marketing Coordinator, Pharmacist Specialist, Content Writer, Corrector). C'est l'ancêtre probable du projet voisin `blog-team`.
- Dépôt GitHub : `https://github.com/Tarekivida/ai_development_team.git` (remote `origin`).

## 2. Stack et versions

- Python **3.13** (version du `.venv` local ; aucune contrainte de version déclarée dans le repo).
- `pyautogen==0.9.0`, `openai==1.76.2`, `python-dotenv==1.1.0` (installé mais **non utilisé** dans le code), `docker==7.1.0` (dépendance transitive d'AutoGen), `tiktoken`, `pydantic 2.11`.
- LLM : modèles **Ollama** locaux (`llama3.1:8b`, `llama3.2:3b`, `qwen:7b-q4_K_M` sur `http://localhost:11434`) + **OpenAI `gpt-4`** dans la même `config_list` (AutoGen essaie les configs dans l'ordre, fallback).
- Génération d'image (variante marketing uniquement) : OpenAI `gpt-image-1`.

## 3. Branches et historique

| Branche | Où | Contenu |
|---|---|---|
| `main` | local + `origin/main` (branche par défaut GitHub) | Version de mai 2025 : 3 agents (Admin, Project_Manager, Engineer), `main.py` + `utils/llm_configs.py`. Dernier commit `749fce9` (2025-05-01). |
| `tester-agent` | local (**branche checkée**) + `origin/tester-agent` | `main` + commit `202d2b9` (2025-05-02, lancement auto du chat après lecture du fichier) + sauvegarde des travaux locaux du 2026-11-11 (`bb3e137`) : ajout de l'agent **Debugger**, `main-local.py`, `main-marketing.py`, `utils/llm_configs_split.py`, `project_folder_structure.md`, `test.py` (vide). Merge `63b3a18` « version locale conservée ». |

`tester-agent` n'a pas été fusionnée dans `main`. **C'est la branche la plus complète ; travailler dessus** (ou la fusionner dans `main` après relecture).

Historique : 9 commits, du 2025-05-01 au 2026-11-11 (le dernier est une sauvegarde technique avant archivage GitHub).

## 4. Arborescence commentée (branche `tester-agent`)

```
development_team/
├── main.py                    # Point d'entrée principal : Admin + Project_Manager + Engineer + Debugger, outils fichiers
├── main-local.py              # Même équipe, mais chaque agent sur un modèle Ollama précis (qwen 7b / llama 3b) via llm_configs_split
├── main-marketing.py          # Variante « rédaction d'article » (agents marketing/pharmacien/rédacteur/correcteur) + outils save_article et generate_and_save_image
├── utils/
│   ├── llm_configs.py         # llm_config unique : config_list Ollama x3 + gpt-4 (fallback)
│   └── llm_configs_split.py   # Mêmes modèles exposés en dicts séparés (llama3_8b_config, llama3_3b_config, qwen_7b_config, gpt4_config)
├── requirements.txt           # Dépendances pip figées (PAS un fichier d'exigences pour les agents, voir pièges)
├── readme.md                  # README d'origine (anglais)
├── project_folder_structure.md# Sortie de `tree` (instantané, informatif)
├── test.py                    # Vide
├── LICENSE                    # MIT
└── .gitignore
```

Hors git (présents seulement en local) : `.venv/`, `output/`, `gitignorefolder/`, `.cache/`, `__pycache__/`, `.env`, `.DS_Store`.

## 5. Architecture et flux

1. `main.py` est exécuté **au niveau module** (pas de fonction `main()`).
2. Agents :
   - `Admin` : `UserProxyAgent`, `human_input_mode="ALWAYS"` (l'humain doit répondre à chaque tour où il est sélectionné), `code_execution_config=False`. C'est lui qui **exécute** les outils.
   - `Project_Manager` : découpe et assigne ; doit répondre exactement `DONE` pour terminer.
   - `Engineer` : seul agent qui **propose** des appels d'outils (`register_for_llm`).
   - `Debugger` : écrit/exécute des tests à la demande du PM (mais n'a pas d'outils enregistrés : il ne peut que rédiger).
3. `GroupChat(max_round=100, send_introductions=True, enable_clear_history=True)` ; le `GroupChatManager` (LLM) choisit le prochain orateur.
4. Terminaison : message `assistant` de `Project_Manager` dont le contenu vaut `done` (insensible à la casse).
5. Outils (tous relatifs à `./output/`, créé automatiquement) : `list_dir`, `see_file` (contenu numéroté), `modify_code` (réécrit le fichier entier), `create_file_with_code`, `execute_command` (`os.system("CI=true cd <output> && <cmd>")`, retourne toujours 0, sortie non capturée).
6. Entrée : `python main.py <fichier>` lit le fichier comme premier message ; sans argument, `input()` interactif.

Variante marketing (`main-marketing.py`) : Admin → Marketing_Coordinator (3 idées de sujets, SEO, AIDA, E-E-A-T) → Pharmacist_Specialist → Content_Writer → Corrector (liste de mots bannis, HTML WordPress). Terminaison sur `DONE` du Marketing_Coordinator.

## 6. Installation et lancement

```bash
git clone https://github.com/Tarekivida/ai_development_team.git development_team
cd development_team
git checkout tester-agent
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY=...        # obligatoire même en local, voir pièges
# Optionnel (modèles locaux) :
ollama pull llama3.1:8b && ollama pull llama3.2:3b && ollama pull qwen:7b-q4_K_M
ollama serve                     # écoute sur localhost:11434

python main.py                   # mode interactif
python main.py chemin/vers/exigences.md   # exigences depuis un fichier
python main-local.py             # tout en Ollama, un modèle par agent
python main-marketing.py         # variante article de blog
```

- Pas de build, pas de tests automatisés (`test.py` vide), pas de CI, pas de déploiement.
- Les fichiers générés atterrissent dans `./output/` (ignoré par git).

## 7. Variables d'environnement et services externes

| Variable | Rôle | Où l'obtenir |
|---|---|---|
| `OPENAI_API_KEY` | Clé pour `gpt-4` (fallback de la config_list) et `gpt-image-1` (variante marketing). Lue via `os.environ[...]` dans `utils/llm_configs*.py` → **KeyError à l'import si absente**. | https://platform.openai.com/api-keys |

Aucun `.env` n'est chargé par le code (python-dotenv non appelé) : exporter la variable dans le shell. Aucun `.env` n'existait localement.

Services : OpenAI API ; Ollama local (aucune clé ; `api_key: "NotRequired"`).

## 8. Données et fichiers exclus de git

- `output/` : produits générés par les agents (localement : un « Egg Timer » `index.html`, `script.js`, `timer.js` — résultats de test). Régénérables en relançant les agents ; aucune valeur à préserver.
- `gitignorefolder/` : documents de spécification utilisés comme entrées d'exigences, **non sauvegardés sur GitHub** (retirés volontairement, commit `b1f6641`) :
  - `functional_requirements.md` : spec d'une UI web (champ de saisie, conversation en streaming, gestion des secrets par env) destinée à remplacer l'interaction terminal de `main.py`.
  - `spotimood.md` : spec fonctionnelle « SpotyMood » (app web Spotify OAuth analysant valence/énergie des titres) — projet test donné aux agents.
  Si ces fichiers sont nécessaires, il faut les récupérer depuis la machine d'origine ; sinon, rédiger de nouvelles exigences.
- `.venv/`, `.cache/` (cache AutoGen/disk), `__pycache__/` : régénérables.

## 9. État d'avancement, TODO, bugs connus

État : prototype fonctionnel en mode terminal, non maintenu depuis mai 2025 (hors sauvegarde de nov. 2026).

Roadmap du README : agent Tester (fait partiellement : Debugger sans outils), génération de tests unitaires, opérations Git, mémoire/planification long terme. Spec web UI dans `gitignorefolder/` non commencée.

Bugs / faiblesses constatés en lisant le code :
- `main.py` / `main-marketing.py` : le bloc `if len(sys.argv) == 2:` est **hors** du `if __name__ == "__main__":` (seul le `print` est dedans) → importer le module lance le chat. `main-local.py` a la bonne indentation.
- `utils/llm_configs_split.py` : `llama3_3b_config` pointe sur `llama3.1:3b`, modèle qui **n'existe pas** dans Ollama (le bon est `llama3.2:3b`, utilisé dans `llm_configs.py`). `main-local.py` utilise ce config → échec probable pour PM et Debugger.
- `OPENAI_API_KEY` requise à l'import même pour un usage 100 % Ollama.
- `execute_command` : `os.system` sans capture de sortie ni code retour (toujours « success ») ; aucune isolation (exécution shell arbitraire sur la machine hôte). `CI=true cd ...` : la variable ne s'applique qu'au `cd`, pas à la commande.
- Chemins construits par concaténation (`default_path + filename`) sans contrôle : pas de protection contre `../`.
- `main-marketing.py` : les outils sont enregistrés sur l'agent `Engineer`, mais `Engineer` **n'est pas dans le GroupChat** ; le Content_Writer est censé appeler `generate_and_save_image`/`save_article` → ces appels d'outils ne fonctionneront pas en l'état.
- Debugger n'a aucun outil pour exécuter des tests.
- `test.py` vide.

## 10. Conventions, décisions, pièges

- Prompts système des agents en anglais, rédigés à la 1re personne (« I am… What I Do / What I Don't Do »).
- **Piège** : le README dit `python main.py requirements.txt`, mais `requirements.txt` est le fichier de dépendances pip ; le passer en argument enverrait la liste de paquets comme « exigence » aux agents. Utiliser un autre fichier (ex. un `.md` de spec).
- `human_input_mode="ALWAYS"` : le terminal sollicite l'humain à chaque passage par Admin (appuyer sur Entrée pour laisser continuer, taper `exit` pour arrêter).
- `cache_seed: None` → pas de cache de réponses LLM déterministe.
- Ordre de la `config_list` = ordre de préférence : Ollama d'abord, gpt-4 en dernier recours.
- Le code dépend de l'API AutoGen 0.2/`pyautogen` ; les versions récentes d'AutoGen (`autogen-agentchat` 0.4+) ont une API différente → ne pas mettre à jour sans réécriture.

## 11. Reprendre le projet

1. `git clone` puis `git checkout tester-agent` (branche la plus récente).
2. Créer le venv, `pip install -r requirements.txt`, exporter `OPENAI_API_KEY`.
3. Vérifier qu'Ollama tourne et que les modèles sont tirés, ou retirer les entrées Ollama de `utils/llm_configs.py` pour n'utiliser que gpt-4.
4. Lancer `python main.py` avec une petite exigence (ex. « crée une page HTML de minuteur ») et vérifier `./output/`.
5. Corrections rapides prioritaires : indentation du bloc `__main__`, nom du modèle `llama3.2:3b` dans `llm_configs_split.py`, `os.environ.get` pour la clé OpenAI, ajout de l'Engineer (ou réenregistrement des outils) dans `main-marketing.py`.
6. Décider : fusionner `tester-agent` dans `main` ; donner des outils d'exécution au Debugger ; éventuellement migrer vers une version maintenue d'AutoGen/AG2.
