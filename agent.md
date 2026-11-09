# Candidate Matching Agent

## Objective

This agent analyzes candidate profiles and job descriptions to identify the most suitable candidates for each role.

The goal is to help recruiters prioritize outreach efforts by generating an automatic ranking and classification of candidates.

## Inputs

The agent expects the following structure:

input/
├── candidates/
└── jobs/

* candidates/: PDF candidate profiles.
* jobs/: PDF job descriptions.

## Workflow

1. Load all candidate profiles.
2. Load the jobs, skills, weights and threshold from `config.json`.
3. Extract text from PDF files.
4. Extract name, headline, location and approximate years of experience.
5. Match each job's skills (whole words, synonyms, case and accent insensitive).
6. Calculate a weighted 0-100 score against each job.
7. Classify candidates (only scores at or above the threshold count):

   * Job A
   * Job B
   * Both
   * Neither
8. Generate recruiter-friendly reports.

## Output

The generated reports are saved in `output/`:

* `report.html` – visual report with score bars, search, filter and per-candidate detail
* `report.md` – summary, ranking, matched and missing skills
* `report.csv` – table for Excel or Google Sheets

Each candidate includes:

* Candidate name, headline and approximate experience
* Score for each job
* Matched and missing skills
* Classification and recommendation
* Ranking

## Execution

Run:

python main.py

## Reusability

This solution is designed to work with future candidate and job datasets.

To evaluate new candidates:

1. Replace PDF files inside input/candidates
2. Replace PDF files inside input/jobs
3. Run python main.py

No code modifications are required.

## Future Improvements

* LLM-powered candidate evaluation (Gemini, Claude, OpenAI)
* Semantic matching
* Automatic publication through Notion MCP
* Recruiter feedback loop
* Advanced scoring models

* ## Notion MCP Setup

To connect Notion MCP:

1. Create a Notion account.
2. Create a Notion workspace.
3. Create a Notion integration through Notion Developers.
4. Generate an integration token.
5. Share the destination page with the integration.
6. Configure the Notion MCP server using the integration token.
7. Run the agent and publish the generated report.

Current implementation generates the report locally in:

output/report.md

Automatic Notion publishing can be enabled after MCP configuration.

