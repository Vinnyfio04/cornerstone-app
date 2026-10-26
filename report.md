# Milestone Report



Created the general file framework for the project to lead into an easy early implementation phase. No major files were created. Mainly the folder structure and framework, project workflow, and requirements for both the project and the agent.



## Repository URL



[https://github.com/Vinnyfio04/cornerstone-app.git](https://github.com/Vinnyfio04/cornerstone-app.git)



## Submitted Version Commit



e7baca0f0a001550a1a1709cdf6ca684cef3afa3



## Design Documents



* Approach

  * I will implement an application that focuses on urgent situations in which someone with a mental health condition can have some form of quick way to bring them back to reality


Image of Wireframe: https://drive.google.com/file/d/1Rt3Ja9J6wsyq5pNrmSQqCiWSMqft\_LFC/view?usp=sharing

* I could not get Figma working, so I used paint.net



## Verification Evidence



There is no evidence of verification as of yet since nothing has truly been implemented other than the framework. The main verification is the general structure of the front and backend.



## Completed Work



The file structure is so:



cornerstone-app/

├── AGENTS.md

├── README.md

├── report.md

├── backend/

│   ├── requirements.txt

│   └── .venv/                  # Generated Python environment

├── docs/

│   ├── assignment\_instructions.md

│   ├── design-pipeline.md

│   └── design\_notes.md

├── frontend/

│   ├── .vscode/

│   │   ├── extensions.json

│   │   └── settings.json

│   ├── public/

│   │   └── favicon.ico

│   ├── src/

│   │   ├── assets/

│   │   │   ├── base.css

│   │   │   ├── logo.svg

│   │   │   └── main.css

│   │   ├── components/

│   │   │   ├── icons/

│   │   │   │   ├── IconCommunity.vue

│   │   │   │   ├── IconDocumentation.vue

│   │   │   │   ├── IconEcosystem.vue

│   │   │   │   ├── IconSupport.vue

│   │   │   │   └── IconTooling.vue

│   │   │   ├── HelloWorld.vue

│   │   │   ├── TheWelcome.vue

│   │   │   └── WelcomeItem.vue

│   │   ├── App.vue

│   │   └── main.js

│   ├── dist/                   # Generated production build

│   ├── node\_modules/           # Generated dependencies

│   ├── eslint.config.js

│   ├── index.html

│   ├── jsconfig.json

│   ├── package-lock.json

│   ├── package.json

│   ├── README.md

│   └── vite.config.js

├── handoffs/

│   ├── create-handoff.md

│   └── current.md

└── prompts/

&#x20;   ├── 01-bounded-scaffold.md

&#x20;   ├── 02-backend-environment.md

&#x20;   ├── 03-frontend-environment.md

&#x20;   └── 04-complete-scaffold-verification.md



The project workflow is:



User → Vue UI → frontend request module → FastAPI

→ domain/service logic → persistence/model/workflow

→ JSON response → Vue UI



## Evidence Summary



Tested basic file system. The file structure matches the initial state of the project.



## Unresolved Items



Making the first implementation of backend and frontend.



