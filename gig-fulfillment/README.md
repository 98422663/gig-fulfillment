# gig-fulfillment (automated micro-gig system)

Automate tiny, repeatable gigs using GitHub Actions.
- Trigger a workflow with JSON order details
- A Python script generates the deliverable with an LLM
- The workflow publishes a downloadable ZIP and delivery page on GitHub Pages

Privacy: Operate under a pseudonym. Marketplace withdrawals usually require KYC. Follow local laws/taxes.

## Quick Start

1) Create a pseudonymous GitHub account and a new private repo named `gig-fulfillment`.
2) Download this archive and upload its contents to your repo.
3) In repo settings: Secrets and variables -> Actions -> New repository secret:
   - OPENAI_API_KEY = your API key
4) Enable GitHub Pages on the gh-pages branch, root directory.
5) Go to Actions tab and allow workflows if prompted.

### Trigger a fulfillment (curl)
Replace YOUR_GH_TOKEN, USER, REPO:

curl -X POST -H "Accept: application/vnd.github+json"   -H "Authorization: token YOUR_GH_TOKEN"   https://api.github.com/repos/USER/REPO/dispatches   -d '{"event_type":"fulfill-order","client_payload":{"job_id":"job123","gig":"resume_rewrite","client_name":"anonBuyer","text":"Paste the customer resume text here."}}'

### Where are the files published?
After the workflow completes:
https://USER.github.io/REPO/JOB_ID.zip
https://USER.github.io/REPO/JOB_ID.html

(If you prefer a subfolder, adjust the workflow step "Commit outputs to gh-pages".)

## Supported Gig Types
- resume_rewrite
- linkedin_post
- etsy_descriptions
- lead_magnet

## Local Tests
pip install -r requirements.txt
export OPENAI_API_KEY=YOUR_KEY
python scripts/generate.py payload-examples/resume_rewrite.json

Outputs go to /outputs. Commit and push, or let Actions handle it.

## Marketplace Setup
Use files in /marketplace for ready-to-paste gig copy.
