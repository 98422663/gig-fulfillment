#!/usr/bin/env python3
# scripts/generate.py
import os, sys, json, uuid, zipfile, pathlib
from datetime import datetime
from typing import Dict, Any

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from openai import OpenAI

OUTPUT_DIR = "outputs"

def llm_complete(prompt: str, max_tokens: int = 900, temperature: float = 0.7) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")
    client = OpenAI(api_key=api_key)
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role":"system","content":"You are a concise, helpful writing assistant that outputs clean, ready-to-use text."},
            {"role":"user","content":prompt}
        ],
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return resp.choices[0].message.content.strip()

def create_pdf(text: str, filename: str):
    pathlib.Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    textobject = c.beginText(40, height - 50)
    textobject.setFont("Helvetica", 11)
    for line in text.splitlines():
        textobject.textLine(line[:110])
    c.drawText(textobject)
    c.showPage()
    c.save()

def write_text(text: str, filename: str):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)

def package_outputs(jobid: str, files):
    zipname = f"{OUTPUT_DIR}/{jobid}.zip"
    with zipfile.ZipFile(zipname, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in files:
            zf.write(f, arcname=os.path.basename(f))
    return zipname

def build_prompt(payload: Dict[str, Any]) -> str:
    gig = payload.get("gig", "resume_rewrite")
    if gig == "resume_rewrite":
        return (
            "Rewrite this resume for clarity, achievements, and ATS optimization. "
            "Keep it to one page; use strong action verbs and quantifiable results. "
            f"Source resume text:\n{payload.get('text','')}"
        )
    if gig == "linkedin_post":
        return (
            "Write a 120-220 word LinkedIn post announcing that the person is now open to work. "
            "Tone: optimistic, human, professional. Include a 1-line call to action and up to 5 relevant hashtags. "
            f"Context: {payload.get('context','')}"
        )
    if gig == "etsy_descriptions":
        count = int(payload.get('count', 2))
        return (
            f"Create {count} Etsy product listings. For each, provide:\n"
            "- Title (<= 80 chars)\n- 200-300 word description focused on benefits and materials\n"
            "- 5 SEO tags\n- 3 bullet highlights\n"
            f"Product context: {payload.get('context','')}"
        )
    if gig == "lead_magnet":
        return (
            "Create a one-page printable checklist/cheat-sheet. 8-12 actionable bullets, "
            "short introduction, and a closing call to action or next step. "
            f"Topic: {payload.get('context','')}"
        )
    return payload.get("prompt", "Write something helpful and structured.")

def main():
    if len(sys.argv) > 1:
        payload = json.loads(open(sys.argv[1], "r", encoding="utf-8").read())
    else:
        payload = json.load(sys.stdin)

    pathlib.Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

    jobid = payload.get("job_id", str(uuid.uuid4())[:8])
    gig = payload.get("gig", "resume_rewrite")
    client_name = payload.get("client_name", "Client")

    prompt = build_prompt(payload)
    text = llm_complete(prompt)

    pdf_file = f"{OUTPUT_DIR}/{jobid}_{gig}.pdf"
    txt_file = f"{OUTPUT_DIR}/{jobid}_{gig}.txt"
    write_text(text, txt_file)
    create_pdf(text, pdf_file)

    html_file = f"{OUTPUT_DIR}/{jobid}.html"
    zip_file = package_outputs(jobid, [pdf_file, txt_file])
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(\"\"\"<!doctype html>
<html><head><meta charset="utf-8"><title>Delivery</title></head>
<body>
  <h2>Delivery {} - {}</h2>
  <p>For: {}</p>
  <p><a href="{}">Download deliverable (ZIP)</a></p>
  <p>Generated: {}Z</p>
</body></html>\"\"\".format(jobid, gig, client_name, os.path.basename(zip_file), datetime.utcnow().isoformat()))

    print(json.dumps({"job_id": jobid, "gig": gig, "zip": os.path.basename(zip_file), "html": os.path.basename(html_file)}))

if __name__ == "__main__":
    main()
