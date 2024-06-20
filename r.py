import requests
import pickle
import os
import tkinter as tk
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime
import re

content_dir = "out"

urls = [
    "http://localhost:8000/"
]

file_path = 'old.bin'

try:
    with open(file_path, 'rb') as f:
        oldchanges = pickle.load(f)
except:
    oldchanges = {}

def sanitize_filename(url):
    filename = re.sub(r'[<>:"/\\|?*]', '_', url.replace("http://", "").replace("https://", ""))
    return filename[:100] 

def save_changes(url, changes):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_filename = os.path.join(content_dir, f"updates_{sanitize_filename(url)}_{timestamp}.pdf")
    
    # Ensure the directory exists
    if not os.path.exists(content_dir):
        os.makedirs(content_dir)
    
    pdf = canvas.Canvas(pdf_filename, pagesize=letter)
    pdf.setTitle("Website Updates")
    y_position = 750
    pdf.setFont("Helvetica", 12)
    pdf.drawString(40, y_position, "Website Updates Report")
    y_position -= 20  # Move down the y position
    pdf.drawString(40, y_position, "Generated on: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    y_position -= 20  # Move down the y position
    pdf.drawString(40, y_position, f"URL: {url}")
    y_position -= 20  # Move down the y position

    lines = changes.split("\n")
    for line in lines:
        if y_position < 40:  
            pdf.showPage() 
            pdf.setFont("Helvetica", 12)
            y_position = 750 
        pdf.drawString(40, y_position, line)
        print("testing")
        y_position -= 20  

    pdf.save()
    print(f"PDF report '{pdf_filename}' generated with updates.")

def compare(old, new, url):
    if old == new:
        print("same file")
    else:
        splitA = set(old.split("\n"))
        splitB = set(new.split("\n"))

        diff = splitB.difference(splitA)
        diff = ", ".join(diff) 
        diff = diff

        splitA2 = set(new.split("\n"))
        splitB2 = set(old.split("\n"))

        deletes = splitB2.difference(splitA2)
        deletes = ", ".join(deletes) 
        deletes =  deletes 

        temp = diff.strip()
        if temp.isnumeric():
            print("visitors update")
        else:
            save_changes(url, diff)
            

for url in urls:
    print("checking url "+ url)
    html = requests.get(url, verify=False)
    html = str(html.text)
    if url in oldchanges.keys():
        compare(oldchanges[url], html, url)
    else:
        print("added "+ url + " to tracking")
    oldchanges[url] = html
    with open('old.bin', 'wb')as f:
        pickle.dump(oldchanges, f)

    

    

    
    
