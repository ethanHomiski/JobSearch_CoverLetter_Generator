import fitz  # PyMuPDF for extracting resume text
import openai
import http.client
import json
import tkinter as tk
from tkinter import filedialog
from keys import OPENAI_KEY, JOOBLE_KEY
# Set your OpenAI and Jooble API Keys
OPENAI_API_KEY = OPENAI_KEY
JOOBLE_API_KEY = JOOBLE_KEY


# Function to extract text from a PDF resume
def extract_text_from_pdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text("text") + "\n"
        return text.strip()
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""


# Function to extract skills, education, and experience using OpenAI
def extract_resume_details(resume_text):
    openai.api_key = OPENAI_API_KEY
    prompt = f"""
    Extract the following information from this resume:
    - Skills
    - Education
    - Work Experience

    Resume:
    {resume_text}

    Format the response as JSON with keys: "skills", "education", "experience".
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "You extract structured information from resumes."},
                      {"role": "user", "content": prompt}]
        )
        parsed_data = json.loads(response["choices"][0]["message"]["content"])
        return parsed_data
    except Exception as e:
        print(f"Error extracting resume details: {e}")
        return {}


# Function to search for jobs using Jooble API
def search_jobs(job_title, location="USA"):
    host = "jooble.org"
    key = JOOBLE_API_KEY
    connection = http.client.HTTPConnection(host)

    headers = {"Content-type": "application/json"}
    body = json.dumps({"keywords": job_title, "location": location})

    try:
        connection.request("POST", f"/api/{key}", body, headers)
        response = connection.getresponse()

        if response.status == 200:
            jobs = json.loads(response.read().decode()).get("jobs", [])
            return jobs[:5]  # Get top 5 job results
        else:
            print(f"Error fetching jobs: {response.status} {response.reason}")
            return []
    except Exception as e:
        print(f"Jooble API request failed: {e}")
        return []
    finally:
        connection.close()


# Function to generate a cover letter
def generate_cover_letter(resume_text, job_title, job_description):
    openai.api_key = OPENAI_API_KEY
    prompt = f"""
    Generate a professional cover letter for the position of {job_title}.
    The job description is as follows:

    {job_description}

    Use the following resume details to craft the cover letter:

    {resume_text}

    The cover letter should be concise, highlight relevant experience, and be tailored for the job.
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "You write professional cover letters."},
                      {"role": "user", "content": prompt}]
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Error generating cover letter: {e}")
        return ""


# Function to browse and select a resume file
def browse_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(title="Select your resume (PDF)", filetypes=[("PDF Files", "*.pdf")])
    return file_path


# Main function
def main():
    print("Select your resume file...")
    pdf_path = browse_file()

    if not pdf_path:
        print("No file selected. Exiting...")
        return

    resume_text = extract_text_from_pdf(pdf_path)
    if not resume_text:
        print("Error: Unable to extract text from the selected PDF.")
        return

    resume_details = extract_resume_details(resume_text)

    job_title = input("Enter the job title you are applying for: ").strip()
    if not job_title:
        print("Error: Job title cannot be empty.")
        return

    print("\nFetching job listings...\n")
    jobs = search_jobs(job_title)

    if not jobs:
        print("No job listings found. Try again later.")
        return

    print("\nSelect a job from the list:")
    for i, job in enumerate(jobs, 1):
        print(f"{i}. {job['title']} - {job['company']} ({job['location']})")
        print(f"   {job['snippet'][:200]}...")  # Show job description preview
        print("-" * 50)

    job_choice = input("Enter the number of the job you want to apply for: ").strip()

    try:
        job_choice = int(job_choice)
        if job_choice < 1 or job_choice > len(jobs):
            print("Invalid selection. Exiting...")
            return
    except ValueError:
        print("Invalid input. Exiting...")
        return

    selected_job = jobs[job_choice - 1]
    job_description = selected_job.get("snippet", "No description available.")

    print("\nGenerating cover letter...\n")
    cover_letter = generate_cover_letter(resume_text, job_title, job_description)

    if cover_letter:
        print("\nGenerated Cover Letter:\n")
        print(cover_letter)
    else:
        print("Error generating cover letter.")


if __name__ == "__main__":
    main()