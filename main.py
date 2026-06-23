import pdfplumber
import os

def extract_resume_text(pdf_path):
    text = ""

    with pdfplumber.open(pdf_path) as pdf: #opens the pdf file and stores it in the variable 'pdf', 'with' statement automatically closes the file when the with block ends
        for page in pdf.pages: #pdf.pages is a list of pages, this loop processes one page at a time
            text += page.extract_text() or "" #.extract_text extracts all readible content from page, or "" is used because some pages are empty or image-only and error arises when '+=' is done on none value

    return text

resumes = []

#--the loop below makes a dictionary of filename as key and it's text as value and adds it to the list 'resumes'
for file in os.listdir("resumes"): #os.listdir lists all the files in a foler, this line takes each filename in the folder 'resumes'
    if file.endswith(".pdf"): #checks if the file is a pdf by checking if the filename ends with the string ".pdf"
        resumes.append({      
            "filename": file,
            "text": extract_resume_text(f"resumes/{file}") #f"resumes/{file}" builds the full file path, if file = 'john.pdf', f"resumes/{file}" becomes "resumes/john.pdf"
        })                                                 #this line of code puts each resume file one-by-one into extract_resume_text function defined earlier
                                                           
skills = [
    "python",
    "sql",
    "java",
    "aws",
    "docker",
    "machine learning",
    "react",
    "javascript",
    "pandas",
    "numpy"
]

def extract_skills(text): #--this function will be used to take each resume dictionary from the list 'resumes' and extract skills from the value 'text' of the dictionaries
    text = text.lower() #in-case the skills are listed in capital letters in resume

    found = []

    for skill in skills:
        if skill in text:
            found.append(skill)

    return found
