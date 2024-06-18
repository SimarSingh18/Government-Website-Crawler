import os
import tkinter as tk
from tkinter import filedialog
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import time
from datetime import datetime
import re
from selenium.webdriver.common.by import By
from difflib import ndiff

# Define the URLs to scrape
urls = [
    "http://localhost:8000/login/?next=/",
]

# Function to open a directory selection dialog
def select_directory():
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    directory = filedialog.askdirectory()
    if not directory:
        print("No directory selected, exiting.")
        exit()
    return directory

# Prompt the user to select the directory to save previous content and PDF
content_dir = select_directory()

# Ensure the directory exists
os.makedirs(content_dir, exist_ok=True)

# Set up Selenium WebDriver
options = Options()
options.headless = True
service = Service("C:\\Program Files (x86)\\chromedriver.exe")  # Update this to your chromedriver path
driver = webdriver.Chrome(service=service, options=options)

# Function to fetch visible text content of the webpage
def fetch_visible_text(url):
    driver.get(url)
    time.sleep(3)  # Allow time for the page to load; adjust as needed

    # Get all elements that contain visible text
    elements = driver.find_elements(By.XPATH, "//*[not(self::script or self::style)]")

    visible_text = []
    for element in elements:
        text = element.text.strip()
        if text and text not in visible_text:
            visible_text.append(text)

    return "\n".join(visible_text)

# Function to sanitize filenames
def sanitize_filename(url):
    # Remove the 'http://' or 'https://' part and replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', url.replace("http://", "").replace("https://", ""))
    return filename[:100]  # Limit filename length for safety

# Function to check for updates
def check_for_updates(url):
    current_content = fetch_visible_text(url)
    filename = os.path.join(content_dir, sanitize_filename(url) + ".txt")

    if os.path.exists(filename):
        with open(filename, "r") as file:
            previous_content = file.read()
            changes = find_changes(previous_content, current_content)
            if changes:
                save_changes(url, changes)
                return True, changes
    else:
        # Save current content as this is the first time running for this URL
        with open(filename, "w") as file:
            file.write(current_content)
        return True, current_content

    return False, ""

# Function to find changes between previous and current content
def find_changes(previous_content, current_content):
    changes = ""
    for line in ndiff(previous_content.splitlines(), current_content.splitlines()):
        if line.startswith('+'):
            changes += line[1:] + "\n"
    return changes.strip()

# Function to save changes to a PDF report
def save_changes(url, changes):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_filename = os.path.join(content_dir, f"updates_{sanitize_filename(url)}_{timestamp}.pdf")

    pdf = canvas.Canvas(pdf_filename, pagesize=letter)
    pdf.setTitle("Website Updates")

    # Set up initial text position
    y_position = 750

    # Define font and size
    pdf.setFont("Helvetica", 12)

    # Add header and timestamp
    pdf.drawString(40, y_position, "Website Updates Report")
    y_position -= 20  # Move down the y position

    pdf.drawString(40, y_position, "Generated on: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    y_position -= 20  # Move down the y position

    # Display changes in PDF
    pdf.drawString(40, y_position, f"URL: {url}")
    y_position -= 20  # Move down the y position

    lines = changes.split("\n")
    for line in lines:
        if y_position < 40:  # Check if space is running out
            pdf.showPage()  # Start a new page
            pdf.setFont("Helvetica", 12)
            y_position = 750  # Reset y position
        pdf.drawString(40, y_position, line)
        print("testing")
        y_position -= 20  # Move down the y position

    # Save PDF
    pdf.save()
    print(f"PDF report '{pdf_filename}' generated with updates.")

# Main logic
if __name__ == "__main__":
    updates = {}

    for url in urls:
        updated, changes = check_for_updates(url)
        if updated:
            updates[url] = changes

    if updates:
        print("Updates found. Generating PDF report(s)...")
    else:
        print("No updates found.")

    driver.quit()