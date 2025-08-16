from flask import Flask, render_template, request, jsonify, session
import threading
import time
import re
import uuid
import os

import os
import subprocess
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeType

app = Flask(__name__)
app.secret_key = os.urandom(24)

# --- CGPA Calculation Functions ---
# Mechanical Engineering (ME) CGPA Calculations
def calculate_cgpa_sem2_me(marks):
    credits = {
        "Basic Manufacturing Processes": 3,
        "Integral Calculus and Probability Theory": 3,
        "Engineering Chemistry": 3,
        "Human Health Systems": 1,
        "Essential Psychomotor Skills for Engineers": 2,
        "Creative Coding in Python": 2,
        "Indian Knowledge System": 2,
        "Introduction to Emerging Technologies": 2,
        "Programming Fundamentals": 3,
        "Liberal Learning Course": 1
    }
    return calculate_cgpa_generic(marks, credits)

def calculate_cgpa_sem4_me(marks):
    credits = {
        "Fundamentals of Thermodynamics": 3,
        "Mechanics of Solids": 3,
        "Materials Science and Engineering": 3,
        "Materials and Material Testing": 1,
        "Emerging Technology and Law": 2,
        "Open Elective-3": 2,
        "Computer Aided Machine Drawing": 2,
        "Modern Indian Language": 2,
        "Technology Entrepreneurship": 2,
        "Technology Innovation for Sustainable Development": 2,
        "Liberal Learning Course": 1,
        "Indian Knowledge System": 2,
        "Human Health Systems": 1,
        "Creative Coding in Python": 2,
    }
    return calculate_cgpa_generic(marks, credits)

def calculate_cgpa_sem6_me(marks):
    """
    The department-level optional can be any one of:
      - MEDLO6021 Press Tool Design
      - MEDLO6022 Tool Engineering
      - MEDLO6023 Digital Signal Processing
    These are treated as a single subject 'Department Level Optional Course-2' for CGPA.
    """
    credits = {
        "Machine Design": 4,
        "Turbo Machinery": 3, 
        "Heating, Ventilation, Air conditioning and Refrigeration": 3,
        "Automation and Artificial Intelligence": 3, 
        "Department Level Optional Course-2": 3, # This is for the theory part of the optional
        "Machine Design Lab": 1, 
        "Turbo Machinery Lab": 1, 
        "Heating, Ventilation, Air conditioning and Refrigeration Lab": 1, 
        "Measurements and Automation": 2, 
        "Mini Project 2B": 2,
    }
    return calculate_cgpa_generic(marks, credits)

# Computer Engineering (CE) CGPA Calculations
def calculate_cgpa_sem2_ce(marks):
    credits = {
        "Digital Electronics": 3,
        "Integral Calculus and Probability Theory": 3,
        "Engineering Physics": 3,
        "Human Health Systems": 1,
        "Essential Computing Skills for Engineers": 2,
        "Measuring Instruments and Testing Tools": 2,
        "Art of Communication": 2,
        "Introduction to Emerging Technologies": 2,
        "Engineering Graphics": 3,
        "Liberal Learning Course": 1
    }
    return calculate_cgpa_generic(marks, credits)

def calculate_cgpa_sem4_ce(marks):
    credits = {
        "Linear Algebra and Business Statistics": 3,
        "Database Management Systems": 3,
        "Analysis of Algorithm": 3,
        "Advanced JAVA Programming Lab": 1,
        "Emerging Technology and Law": 2,
        "Microprocessor (Open Elective-3)": 2,
        "Full Stack Development Lab": 2,
        "Modern Indian Language": 2,
        "Technology Entrepreneurship": 2,
        "Technology Innovation for Sustainable Development": 2,
        "Liberal Learning Course": 1,
        "Indian Knowledge System": 2,
        "Human Health Systems": 1,
        "Creative Coding in Python": 2,
    }
    return calculate_cgpa_generic(marks, credits)

def calculate_cgpa_sem6_ce(marks):
    """
    The department-level optional can be any one of:
      - CSDLO6011 Internet of Things
      - CSDLO6012 Digital Signal & Image Processing
      - CSDLO6013 Quantitative Analysis
    These are treated as a single subject 'Department Level Optional Course-2' for CGPA.
    """
    credits = {
        "System Programming & Compiler Construction": 3,
        "Cryptography & System Security": 3,
        "Mobile Computing": 3,
        "Artificial Intelligence": 3,
        "Department Level Optional Course-2": 3,
        "System Programming & Compiler Construction Lab": 1,
        "Cryptography & System Security Lab": 1,
        "Mobile Computing Lab": 1,
        "Artificial Intelligence Lab": 1,
        "Skill-based Laboratory": 2,
        "Mini Project 2B": 2,
    }
    return calculate_cgpa_generic(marks, credits)

# Computer Science Engineering (AI & DS) CGPA Calculations
def calculate_cgpa_sem2_aids(marks):
    credits = {
        "Digital Electronics": 3,
        "Integral Calculus and Probability Theory": 3,
        "Engineering Chemistry": 3,
        "Human Health Systems": 1,
        "Essential Psychomotor Skills for Engineers": 2,
        "Creative Coding in Python": 2, # Corrected: removed trailing space
        "Indian Knowledge System": 2,
        "Introduction to Emerging Technologies": 2,
        "Programming Fundamentals": 3,
        "Liberal Learning Course": 1
    }
    return calculate_cgpa_generic(marks, credits)

def calculate_cgpa_sem4_aids(marks):
    credits = {
        "Linear Algebra and Business Statistics": 3,
        "Database Management Systems": 3,
        "Analysis of Algorithm": 3,
        "Data Analytics and Visualization": 1,
        "Emerging Technology and Law": 2,
        "Open Elective-3": 2,
        "Web Programming": 2,
        "Modern Indian Language": 2,
        "Technology Entrepreneurship": 2,
        "Technology Innovation for Sustainable Development": 2,
        "Liberal Learning Course": 1,
        "Indian Knowledge System": 2,
        "Human Health Systems": 1,
        "Creative Coding in Python": 2,
    }
    return calculate_cgpa_generic(marks, credits)

def calculate_cgpa_sem6_aids(marks):
    """
    Calculate CGPA for Semester 6 (AI&DS).
    The department-level optional can be any one of:
      - CSDLO6011 High Performance Computing
      - CSDLO6012 Distributed Computing
      - CSDLO6013 Image & Video processing
    """
    credits = {
        "Data Analytics and Visualization": 3,
        "Cryptography & System Security": 3,
        "Software Engineering and Project Management": 3,
        "Machine Learning": 3,
        "Department Level Optional Course-2": 3,
        "Data Analytics and Visualization Lab": 1,
        "Cryptography & System Security Lab": 1,
        "Software Engineering and Project Management Lab": 1,
        "Machine Learning Lab": 1,
        "Skill base Lab Course: Cloud Computing": 2,
        "Mini Project 2B": 2,
    }
    return calculate_cgpa_generic(marks, credits)


# Electronics & Computer Science (ECS) CGPA Calculations
def calculate_cgpa_sem2_ecs(marks):
    credits = {
        "Digital Electronics": 3,
        "Integral Calculus and Probability Theory": 3,
        "Engineering Chemistry": 3,
        "Human Health Systems": 1,
        "Essential Psychomotor Skills for Engineers": 2,
        "Creative Coding in Python": 2,
        "Indian Knowledge System": 2,
        "Introduction to Emerging Technologies": 2,
        "Programming Fundamentals": 3,
        "Liberal Learning Course": 1
    }
    return calculate_cgpa_generic(marks, credits)

def calculate_cgpa_sem4_ecs(marks):
    credits = {
        "Mathematics and Numerical Methods": 3,
        "Analog Electronics": 3,
        "Discrete Structures and AutomataTheory": 3,
        "Embedded Systems": 1,
        "Emerging Technology and Law": 2,
        "Operating Systems": 2,
        "Data Structures": 2,
        "Modern Indian Language": 2,
        "Technology Entrepreneurship": 2,
        "Technology Innovation for Sustainable Development": 2,
        "Liberal Learning Course": 1,
        "Electromagnetic Theory": 3,
        "Creative Coding in Python": 2,
    }
    return calculate_cgpa_generic(marks, credits)

def calculate_cgpa_sem6_ecs(marks):
    """
    Calculate CGPA for Semester 6 (ECS).
    The department-level optional can be any one of:
      - ECCDO6011 Machine Learning
      - ECCDO6012 Industrial Automation
      - ECCDO6013 Digital Signal Processing
      - ECCDO6014 Electronic Product Design
    """
    credits = {
        "Embedded Systems and RTOS": 3,
        "Artificial Intelligence": 3,
        "Computer Networks": 3,
        "Data Warehousing and Mining": 3,
        "Department Level Optional Course-2": 3,
        "Embedded Systems Lab": 1,
        "Artificial Intelligence and Computer Networks Lab": 1,
        "Data Warehousing and Mining Lab": 1,
        "Skill base Laboratory": 2,
        "Mini Project 2B": 2,
    }
    return calculate_cgpa_generic(marks, credits)


def calculate_cgpa_generic(marks, credits):
    """Generic CGPA calculation function based on marks (out of 100) and credits."""
    total_weighted_grade_points = 0
    total_actual_credits = 0 # Sum of credits for subjects that had marks

    for subject_name, mark in marks.items():
        credit = credits.get(subject_name)
        if credit is None:
            # Skip subjects not found in the credit mapping or without credits
            continue 

        grade = 0
        # Special grading for Liberal Learning Course (LLC)
        if subject_name == "Liberal Learning Course":
            if mark >= 90: grade = 10
            elif mark >= 80: grade = 9
            elif mark >= 70: grade = 8
            elif mark >= 60: grade = 7
            elif mark >= 50: grade = 6
            elif mark >= 45: grade = 5
            elif mark >= 40: grade = 4
            else: grade = 0
        else:
            # Standard grading for all other subjects
            if mark >= 85: grade = 10
            elif mark >= 80: grade = 9
            elif mark >= 70: grade = 8
            elif mark >= 60: grade = 7
            elif mark >= 50: grade = 6
            elif mark >= 45: grade = 5
            elif mark >= 40: grade = 4
            else: grade = 0
        
        total_weighted_grade_points += (grade * credit)
        total_actual_credits += credit
    
    if total_actual_credits == 0:
        return 0.0
        
    cgpa = total_weighted_grade_points / total_actual_credits
    return cgpa

def parse_mark_string(mark_str):
    """Parses a mark string like '35/50' and returns the score (35)."""
    try:
        # Extract the first number before '/'
        match = re.match(r'(\d+(\.\d+)?)/', mark_str)
        if match:
            return float(match.group(1))
        # If no '/' or no number before it, try converting directly if it's just a number
        return float(mark_str)
    except (ValueError, TypeError):
        return 0.0 # Return 0 if parsing fails

# --- Max Marks Maps for ME Branch ---
sem6_me_max_marks_map = {
    "Machine Design": 100, # Theory (e.g., sum of ISE1, MSE, ISE2, ESE max marks)
    "Turbo Machinery": 100,
    "Heating, Ventilation, Air conditioning and Refrigeration": 100,
    "Automation and Artificial Intelligence": 100,
    "Department Level Optional Course-2": 100,
    "Machine Design Lab": 50, # Example: if lab is out of 50
    "Turbo Machinery Lab": 25, # Example: if lab is out of 25
    "Heating, Ventilation, Air conditioning and Refrigeration Lab": 50, # Example: if lab is out of 50
    "Measurements and Automation": 50, # Skill-based Lab out of 50
    "Mini Project 2B": 50, # Mini Project out of 50
}

sem4_me_max_marks_map = {
    "Fundamentals of Thermodynamics": 150, # Sum of all components (theory+tutorial)
    "Mechanics of Solids": 150, # Sum of all components (theory+practical)
    "Materials Science and Engineering": 150, # Sum of all components (theory+practical)
    "Materials and Material Testing": 50, # Practical marks
    "Emerging Technology and Law": 100,
    "Open Elective-3": 100,
    "Computer Aided Machine Drawing": 100,
    "Modern Indian Language": 100,
    "Technology Entrepreneurship": 100,
    "Technology Innovation for Sustainable Development": 100,
    "Liberal Learning Course": 50,
    "Indian Knowledge System": 100,
    "Human Health Systems": 50,
    "Creative Coding in Python": 100,
}

sem2_me_max_marks_map = {
    "Basic Manufacturing Processes": 150,
    "Integral Calculus and Probability Theory": 150,
    "Engineering Chemistry": 150,
    "Human Health Systems": 50,
    "Essential Psychomotor Skills for Engineers": 100,
    "Creative Coding in Python": 100,
    "Indian Knowledge System": 100,
    "Introduction to Emerging Technologies": 100,
    "Programming Fundamentals": 150,
    "Liberal Learning Course": 50
}

# --- Max Marks Maps for CE Branch ---
sem6_ce_max_marks_map = {
    "System Programming & Compiler Construction": 100,
    "Cryptography & System Security": 100,
    "Mobile Computing": 100,
    "Artificial Intelligence": 100,
    "Department Level Optional Course-2": 100,
    "System Programming & Compiler Construction Lab": 50,
    "Cryptography & System Security Lab": 25,
    "Mobile Computing Lab": 25,
    "Artificial Intelligence Lab": 50,
    "Skill-based Laboratory": 75,
    "Mini Project 2B": 50,
}

sem4_ce_max_marks_map = {
    "Linear Algebra and Business Statistics": 150,
    "Database Management Systems": 150,
    "Analysis of Algorithm": 150,
    "Advanced JAVA Programming Lab": 50,
    "Emerging Technology and Law": 100,
    "Microprocessor (Open Elective-3)": 100,
    "Full Stack Development Lab": 100,
    "Modern Indian Language": 100,
    "Technology Entrepreneurship": 100,
    "Technology Innovation for Sustainable Development": 100,
    "Liberal Learning Course": 50,
    "Indian Knowledge System": 100,
    "Human Health Systems": 50,
    "Creative Coding in Python": 100,
}

sem2_ce_max_marks_map = {
    "Digital Electronics": 150,
    "Integral Calculus and Probability Theory": 150,
    "Engineering Physics": 150,
    "Human Health Systems": 50,
    "Essential Computing Skills for Engineers": 100,
    "Measuring Instruments and Testing Tools": 100,
    "Art of Communication": 100,
    "Introduction to Emerging Technologies": 100,
    "Engineering Graphics": 150,
    "Liberal Learning Course": 50
}

# --- Max Marks Maps for AI&DS Branch ---
sem2_aids_max_marks_map = {
    "Digital Electronics": 150,
    "Integral Calculus and Probability Theory": 150,
    "Engineering Chemistry": 150,
    "Human Health Systems": 50,
    "Essential Psychomotor Skills for Engineers": 100,
    "Creative Coding in Python": 100, # Corrected: removed trailing space
    "Indian Knowledge System": 100,
    "Introduction to Emerging Technologies": 100,
    "Programming Fundamentals": 150,
    "Liberal Learning Course": 50
}

sem4_aids_max_marks_map = {
    "Linear Algebra and Business Statistics": 150,
    "Database Management Systems": 150,
    "Analysis of Algorithm": 150,
    "Data Analytics and Visualization": 50, # Lab/Practical, check actual max
    "Emerging Technology and Law": 100,
    "Open Elective-3": 100,
    "Web Programming": 100, # Lab/Practical, check actual max
    "Modern Indian Language": 100,
    "Technology Entrepreneurship": 100,
    "Technology Innovation for Sustainable Development": 100,
    "Liberal Learning Course": 50,
    "Indian Knowledge System": 100,
    "Human Health Systems": 50,
    "Creative Coding in Python": 100,
}

sem6_aids_max_marks_map = {
    "Data Analytics and Visualization": 100,
    "Cryptography & System Security": 100,
    "Software Engineering and Project Management": 100,
    "Machine Learning": 100,
    "Department Level Optional Course-2": 100,
    "Data Analytics and Visualization Lab": 50,
    "Cryptography & System Security Lab": 25,
    "Software Engineering and Project Management Lab": 25,
    "Machine Learning Lab": 50,
    "Skill base Lab Course: Cloud Computing": 75, # Check actual max
    "Mini Project 2B": 50,
}

# --- Max Marks Maps for ECS Branch ---
sem2_ecs_max_marks_map = {
    "Digital Electronics": 150,
    "Integral Calculus and Probability Theory": 150,
    "Engineering Chemistry": 150,
    "Human Health Systems": 50,
    "Essential Psychomotor Skills for Engineers": 100,
    "Creative Coding in Python": 100,
    "Indian Knowledge System": 100,
    "Introduction to Emerging Technologies": 100,
    "Programming Fundamentals": 150,
    "Liberal Learning Course": 50
}

sem4_ecs_max_marks_map = {
    "Mathematics and Numerical Methods": 150,
    "Analog Electronics": 150,
    "Discrete Structures and AutomataTheory": 150,
    "Embedded Systems": 50, # Lab/Practical, check actual max
    "Emerging Technology and Law": 100,
    "Operating Systems": 100, # Check actual max
    "Data Structures": 100, # Check actual max
    "Modern Indian Language": 100,
    "Technology Entrepreneurship": 100,
    "Technology Innovation for Sustainable Development": 100,
    "Liberal Learning Course": 50,
    "Electromagnetic Theory": 150,
    "Creative Coding in Python": 100,
}

sem6_ecs_max_marks_map = {
    "Embedded Systems and RTOS": 100,
    "Artificial Intelligence": 100,
    "Computer Networks": 100,
    "Data Warehousing and Mining": 100,
    "Department Level Optional Course-2": 100,
    "Embedded Systems Lab": 50,
    "Artificial Intelligence and Computer Networks Lab": 50,
    "Data Warehousing and Mining Lab": 50,
    "Skill base Laboratory": 50, # Check actual max
    "Mini Project 2B": 50,
}

def scale_mark_to_100(subject_key, mark, semester, branch):
    """Scales a given mark to be out of 100 based on the semester, branch, and subject's total max marks."""
    max_marks_map = {}
    if branch == "ME":
        if semester == "sem2":
            max_marks_map = sem2_me_max_marks_map
        elif semester == "sem4":
            max_marks_map = sem4_me_max_marks_map
        elif semester == "sem6":
            max_marks_map = sem6_me_max_marks_map
    elif branch == "CE":
        if semester == "sem2":
            max_marks_map = sem2_ce_max_marks_map
        elif semester == "sem4":
            max_marks_map = sem4_ce_max_marks_map
        elif semester == "sem6":
            max_marks_map = sem6_ce_max_marks_map
    elif branch == "AI&DS":
        if semester == "sem2":
            max_marks_map = sem2_aids_max_marks_map
        elif semester == "sem4":
            max_marks_map = sem4_aids_max_marks_map
        elif semester == "sem6":
            max_marks_map = sem6_aids_max_marks_map
    elif branch == "ECS":
        if semester == "sem2":
            max_marks_map = sem2_ecs_max_marks_map
        elif semester == "sem4":
            max_marks_map = sem4_ecs_max_marks_map
        elif semester == "sem6":
            max_marks_map = sem6_ecs_max_marks_map
    
    max_marks = max_marks_map.get(subject_key, 100) # Default to 100 if not found
    
    if max_marks == 0: # Avoid division by zero
        return 0.0
    
    return (mark / max_marks) * 100

def calculate_subject_mark(subject_key, component_marks, semester, branch):
    """
    Calculates the final mark for a subject by summing its components
    and then scaling it to be out of 100, considering semester and branch.
    """
    if not component_marks:
        return 0.0

    total_component_sum = sum(component_marks)
    
    # The complex logic for combining components is mostly handled by the fact that
    # 'extract_marks_from_page' should ideally get all relevant numeric parts,
    # and 'scale_mark_to_100' uses the total max marks.
    # The specific 'if len(component_marks) >= X' conditions were making it brittle.
    # We now simply sum all extracted components and let scale_mark_to_100 handle the overall scaling.
    
    return scale_mark_to_100(subject_key, total_component_sum, semester, branch)

# --- Enhanced Selenium Automation Function ---
def get_marks_from_portal(username, birth_day, birth_month, birth_year, semester="sem4", branch="ME", progress_callback=None):
    LOGIN_URL = "https://crce-students.contineo.in/parentseven/"
    student_marks = {}
    
    chrome_options = Options()
    # Essential Chrome options for stability
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-software-rasterizer')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--allow-running-insecure-content')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    # Comment out headless for debugging
    # chrome_options.add_argument('--headless=new')

    driver = None
    
    try:
        if progress_callback:
            progress_callback("Initializing browser...")
        
        try:
            # Check Chrome installation
            chrome_version = get_chrome_version()
            if not chrome_version:
                raise Exception("Chrome browser is not installed. Please install Google Chrome first.")
                
            if progress_callback:
                progress_callback(f"Detected Chrome version: {chrome_version}")
            
            # Install ChromeDriver
            from webdriver_manager.core.os_manager import ChromeType
            driver_path = ChromeDriverManager(chrome_type=ChromeType.GOOGLE).install()
            
            if not os.path.exists(driver_path):
                raise Exception("ChromeDriver installation failed. Please check your internet connection and try again.")
            
            # Create service with the driver path
            service = Service(driver_path)
            
            # Create driver with the service and options
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            if progress_callback:
                progress_callback("Browser initialized successfully...")
                
        except Exception as e:
            error_msg = str(e)
            if "Chrome browser is not installed" in error_msg:
                raise Exception("Please install Google Chrome browser first from https://www.google.com/chrome/")
            elif "chromedriver" in error_msg.lower() and "executable" in error_msg.lower():
                raise Exception("ChromeDriver installation failed. Please:\n1. Close all Chrome windows\n2. Check your internet connection\n3. Try again")
            elif "session not created" in error_msg.lower():
                raise Exception(f"Chrome version mismatch. Please update Chrome browser to the latest version. Current version: {get_chrome_version()}")
            else:
                raise Exception(f"Browser initialization failed: {error_msg}\nPlease ensure Chrome is up to date and try again.")
        
        if progress_callback:
            progress_callback("Connecting to portal...")
        
        driver.get(LOGIN_URL)
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        
        # Login process (same as before)
        if progress_callback:
            progress_callback("Processing...")
        
        driver.find_element(By.ID, "username").send_keys(username)
        driver.find_element(By.ID, "dd").send_keys(birth_day)
        
        month_dropdown = Select(driver.find_element(By.ID, "mm"))
        month_dropdown.select_by_value(birth_month)
        
        driver.find_element(By.ID, "yyyy").send_keys(birth_year)
        
        time.sleep(0.5)

        # Login button handling (same as before)
        login_success = False
        login_attempts = [
            (By.XPATH, "//input[@type='submit']"),
            (By.XPATH, "//button[contains(text(), 'Login') or contains(text(), 'Sign In')]"),
            (By.XPATH, "//button | //input[@type='button']")
        ]
        
        for attempt, selector in enumerate(login_attempts):
            if login_success:
                break
            try:
                if progress_callback:
                    progress_callback(f"Verifying...")
                
                login_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable(selector)
                )
                
                try:
                    login_button.click()
                    login_success = True
                except WebDriverException as click_error:
                    if "element click intercepted" in str(click_error):
                        if progress_callback:
                            progress_callback("Login button click intercepted, using JavaScript...")
                        driver.execute_script("arguments[0].click();", login_button)
                        login_success = True
                    else:
                        raise click_error
                        
            except TimeoutException:
                continue
        
        if not login_success:
            raise Exception("Could not find any clickable login button after all attempts.")

        if progress_callback:
            progress_callback("Waiting for dashboard to load...")
        
        WebDriverWait(driver, 20).until(
            EC.url_changes(LOGIN_URL) or EC.presence_of_element_located((By.ID, "dashboardMainContent")) 
        )
        
        dashboard_url = driver.current_url
        print(f"DEBUG: Dashboard URL: {dashboard_url}")
        
        # Check for login errors
        try:
            error_message_element = driver.find_element(By.XPATH, "//*[contains(text(), 'Invalid Username') or contains(text(), 'Incorrect') or contains(text(), 'Authentication failed')]")
            if error_message_element.is_displayed():
                raise Exception(f"Login failed: {error_message_element.text}")
        except NoSuchElementException:
            pass

        if progress_callback:
            progress_callback("Finding subjects...")

        MAIN_SUBJECT_CONTAINER_SELECTOR = "div.uk-card.uk-card-body.cn-pad-20.cn-fee-head" 
        
        subject_list_container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, MAIN_SUBJECT_CONTAINER_SELECTOR))
        )

        subjects_table = WebDriverWait(subject_list_container, 5).until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )

        subject_rows = []
        try:
            tbody = WebDriverWait(subjects_table, 5).until(
                EC.presence_of_element_located((By.TAG_NAME, "tbody"))
            )
            all_trs = tbody.find_elements(By.TAG_NAME, "tr")
            subject_rows = [row for row in all_trs if len(row.find_elements(By.TAG_NAME, "td")) >= 2]
        except TimeoutException:
            all_trs = subjects_table.find_elements(By.TAG_NAME, "tr")
            subject_rows = [row for row in all_trs if len(row.find_elements(By.TAG_NAME, "td")) >= 2]

        if not subject_rows:
            raise Exception("No valid subject rows found in the marks table.")

        total_subjects = len(subject_rows)
        print(f"DEBUG: Found {total_subjects} subjects")
        
        # Print all subjects first for debugging
        for i, subject_row in enumerate(subject_rows):
            try:
                subject_code_element = subject_row.find_element(By.CSS_SELECTOR, "td:nth-child(1)")
                course_code = subject_code_element.text.strip()
                
                subject_name_element = subject_row.find_element(By.CSS_SELECTOR, "td:nth-child(2)")
                raw_subject_name = subject_name_element.text.strip()
                
                print(f"DEBUG: Subject {i+1}: Code='{course_code}', Name='{raw_subject_name}'")
                
                subject_key = map_subject_name(course_code, raw_subject_name, semester, branch)
                print(f"DEBUG: Mapped to: '{subject_key}'")
                
            except Exception as e:
                print(f"DEBUG: Error reading subject {i+1}: {e}")
        
        for i, subject_row in enumerate(subject_rows):
            try:
                if progress_callback:
                    progress_callback(f"Processing subject {i+1} of {total_subjects}...")
                
                print(f"DEBUG: Starting subject {i+1}")
                print(f"DEBUG: Current URL before processing: {driver.current_url}")
                
                subject_code_element = WebDriverWait(subject_row, 2).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "td:nth-child(1)"))
                )
                course_code = subject_code_element.text.strip()

                subject_name_element = WebDriverWait(subject_row, 2).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "td:nth-child(2)"))
                )
                raw_subject_name = subject_name_element.text.strip()

                print(f"DEBUG: Processing {raw_subject_name} ({course_code})")
                
                subject_key = map_subject_name(course_code, raw_subject_name, semester, branch)
                
                if not subject_key:
                    print(f"DEBUG: Skipping unknown subject: {raw_subject_name} ({course_code})")
                    if progress_callback:
                        progress_callback(f"Skipping unknown subject: {raw_subject_name} ({course_code})")
                    continue

                print(f"DEBUG: Looking for CIE button for {subject_key}")

                # Enhanced CIE button detection
                cie_button_selectors = [
                    ".//a[./button[contains(@class, 'cn-cieclr') and text()='CIE']]",
                    ".//button[contains(@class, 'cn-cieclr') and text()='CIE']",
                    ".//a[contains(text(), 'CIE')]",
                    ".//button[contains(text(), 'CIE')]",
                    ".//a[.//*[text()='CIE']]"
                ]
                
                cie_link_element = None
                for selector in cie_button_selectors:
                    try:
                        cie_link_element = WebDriverWait(subject_row, 2).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                        print(f"DEBUG: Found CIE button using selector: {selector}")
                        break
                    except TimeoutException:
                        continue
                
                if not cie_link_element:
                    print(f"DEBUG: No CIE button found for {subject_key}")
                    # Try to find any clickable elements in this row
                    all_links = subject_row.find_elements(By.TAG_NAME, "a")
                    all_buttons = subject_row.find_elements(By.TAG_NAME, "button")
                    print(f"DEBUG: Found {len(all_links)} links and {len(all_buttons)} buttons in row")
                    
                    for j, link in enumerate(all_links):
                        print(f"DEBUG: Link {j+1}: text='{link.text}', class='{link.get_attribute('class')}'")
                    for j, button in enumerate(all_buttons):
                        print(f"DEBUG: Button {j+1}: text='{button.text}', class='{button.get_attribute('class')}'")
                    
                    student_marks[subject_key] = 0.0
                    continue
                
                print(f"DEBUG: Attempting to click CIE for: {subject_key}")
                
                try:
                    driver.execute_script("arguments[0].scrollIntoView(true);", cie_link_element)
                    time.sleep(0.5)
                    print(f"DEBUG: Scrolled to CIE button")
                    
                    cie_link_element.click()
                    print(f"DEBUG: Clicked CIE button")
                    
                except WebDriverException as click_error:
                    print(f"DEBUG: Click intercepted, trying JavaScript click")
                    if "element click intercepted" in str(click_error):
                        driver.execute_script("arguments[0].click();", cie_link_element)
                        print(f"DEBUG: JavaScript click executed")
                    else:
                        raise click_error

                print(f"DEBUG: Waiting for marks page to load...")
                
                # Wait for marks page with multiple strategies
                marks_page_loaded = False
                wait_strategies = [
                    (By.XPATH, f"//caption[contains(text(), '{re.escape(course_code)}') or contains(text(), '{re.escape(raw_subject_name)}')]"),
                    (By.XPATH, "//table[contains(@class, 'marks') or contains(@class, 'result')]"),
                    (By.XPATH, "//table//th[contains(text(), 'Marks') or contains(text(), 'Score')]"),
                    (By.XPATH, "//table")  # Fallback to any table
                ]
                
                for strategy in wait_strategies:
                    try:
                        WebDriverWait(driver, 10).until(EC.presence_of_element_located(strategy))
                        marks_page_loaded = True
                        print(f"DEBUG: Marks page loaded using strategy: {strategy}")
                        break
                    except TimeoutException:
                        continue
                
                if not marks_page_loaded:
                    print(f"DEBUG: Could not confirm marks page loaded for {subject_key}")
                    print(f"DEBUG: Current URL after click: {driver.current_url}")
                    print(f"DEBUG: Page title: {driver.title}")
                    
                    # Print page source snippet for debugging
                    page_source_snippet = driver.page_source[:1000]
                    print(f"DEBUG: Page source snippet: {page_source_snippet}")

                print(f"DEBUG: Current URL after navigation: {driver.current_url}")

                # Extract marks with debugging
                raw_marks_strings = extract_marks_from_page_debug(driver)
                print(f"DEBUG: Raw marks extracted for {subject_key}: {raw_marks_strings}")
                
                if not raw_marks_strings:
                    student_marks[subject_key] = 0.0
                    print(f"DEBUG: No marks found for {raw_subject_name}, assigning 0.")
                    if progress_callback:
                        progress_callback(f"No marks found for {raw_subject_name}, assigning 0.")
                else:
                    component_marks = [parse_mark_string(s) for s in raw_marks_strings]
                    print(f"DEBUG: Component marks: {component_marks}")
                    calculated_mark = calculate_subject_mark(subject_key, component_marks, semester, branch)
                    student_marks[subject_key] = calculated_mark
                    print(f"DEBUG: Final calculated mark for {subject_key}: {calculated_mark}")

                # Return to dashboard
                print(f"DEBUG: Returning to dashboard...")
                driver.back()
                
                # Wait for dashboard with timeout
                try:
                    WebDriverWait(driver, 15).until(
                        EC.url_to_be(dashboard_url) or EC.presence_of_element_located((By.CSS_SELECTOR, MAIN_SUBJECT_CONTAINER_SELECTOR))
                    )
                    print(f"DEBUG: Successfully returned to dashboard")
                except TimeoutException:
                    print(f"DEBUG: Timeout returning to dashboard, current URL: {driver.current_url}")
                    # Try to navigate back to dashboard directly
                    driver.get(dashboard_url)
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, MAIN_SUBJECT_CONTAINER_SELECTOR))
                    )
                    print(f"DEBUG: Manually navigated back to dashboard")

                print(f"DEBUG: Completed subject {i+1}: {subject_key}")

            except Exception as e:
                print(f"DEBUG: Exception for subject {raw_subject_name or course_code}: {str(e)}")
                print(f"DEBUG: Exception type: {type(e).__name__}")
                import traceback
                traceback.print_exc()
                
                if progress_callback:
                    progress_callback(f"Error processing subject {raw_subject_name or course_code}: {str(e)}. Attempting to return to dashboard.")
                
                try: 
                    print(f"DEBUG: Attempting to return to dashboard after error")
                    driver.back()
                    WebDriverWait(driver, 10).until(
                        EC.url_to_be(dashboard_url) or EC.presence_of_element_located((By.CSS_SELECTOR, MAIN_SUBJECT_CONTAINER_SELECTOR))
                    )
                    print(f"DEBUG: Successfully returned to dashboard after error")
                except Exception as return_error:
                    print(f"DEBUG: Failed to return to dashboard: {return_error}")
                    if progress_callback:
                        progress_callback("Failed to return to dashboard after error. Automation might be unstable.")
                    break
                    
        if progress_callback:
            progress_callback("Marks extraction completed successfully!")

    except Exception as e:
        print(f"DEBUG: Main exception: {str(e)}")
        import traceback
        traceback.print_exc()
        
        error_msg = f"Automation failed: {str(e)}"
        if "Authentication failed" in str(e) or "Invalid credentials" in str(e) or "Could not find any clickable login button" in str(e):
            error_msg = "Login failed. Please check your username and birth date."
        elif "No valid subject rows found" in str(e) or "Could not find any marks" in str(e):
            error_msg = "Could not retrieve marks for the selected semester. Data might not be available or page structure changed."
        else:
            error_msg = f"An unexpected error occurred during automation: {str(e)}. The portal might be down or its structure changed."
            
        if progress_callback:
            progress_callback(error_msg)
        raise Exception(error_msg)
    finally:
        if driver:
            try:
                if progress_callback:
                    progress_callback("Calculating...")
                print(f"DEBUG: Cleaning up browser...")
                try:
                    logout_element = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Logout') or contains(text(), 'Log Out')] | //button[contains(text(), 'Logout')]"))
                    )
                    logout_element.click()
                    time.sleep(1)
                    print(f"DEBUG: Logged out successfully")
                except:
                    print(f"DEBUG: Could not find logout button")
                    pass
            except:
                pass
            finally:
                driver.quit()
                print(f"DEBUG: Browser closed")

    return student_marks
def map_subject_name(course_code, raw_subject_name, semester, branch):
    """Maps course codes and raw subject names from the portal to standardized subject keys based on semester and branch."""
    normalized_raw_name = raw_subject_name.strip()
    
    if branch == "ME":
        if semester == "sem2":
            if course_code == "PCC11ME05": return "Basic Manufacturing Processes"
            elif course_code == "BSC11ME03": return "Integral Calculus and Probability Theory"
            elif course_code == "BSC11ME04": return "Engineering Chemistry"
            elif course_code == "ESC11BME04": return "Human Health Systems"
            elif course_code == "PCC11ME04": return "Essential Psychomotor Skills for Engineers"
            elif course_code == "VSE11ME02": return "Creative Coding in Python"
            elif course_code == "IKS11ME01": return "Indian Knowledge System"
            elif course_code == "HMM11ME01": return "Introduction to Emerging Technologies"
            elif course_code == "ESC11ME03": return "Programming Fundamentals"
            elif course_code.startswith("LLC"): return "Liberal Learning Course"
            
        elif semester == "sem4":
            if course_code == "BSC12ME06": return "Fundamentals of Thermodynamics"
            elif course_code == "PCC12ME08": return "Mechanics of Solids"
            elif course_code == "PCC12ME09": return "Materials Science and Engineering"
            elif course_code == "PCC12ME10": return "Materials and Material Testing"
            elif course_code == "MDM02": return "Emerging Technology and Law"
            elif course_code.startswith("OEME2"): return "Open Elective-3"
            elif course_code == "VSE12ME03": return "Computer Aided Machine Drawing"
            elif course_code.startswith("AEC12ME02"): return "Modern Indian Language"
            elif course_code == "EEM12ME02": return "Technology Entrepreneurship"
            elif course_code == "VEC12ME02": return "Technology Innovation for Sustainable Development"
            elif course_code.startswith("LLC"): return "Liberal Learning Course"
            elif course_code == "IKS11ME01": return "Indian Knowledge System"
            elif course_code == "ESC11BME04":return "Human Health Systems"
            elif course_code == "VSE12ME02": return "Creative Coding in Python"
            
        elif semester == "sem6":
            if course_code == "MEC 601": return "Machine Design"
            elif course_code == "MEC602": return "Turbo Machinery"
            elif course_code == "MEC603": return "Heating, Ventilation, Air conditioning and Refrigeration"
            elif course_code == "MEC604": return "Automation and Artificial Intelligence"
            elif course_code in ["MEDLO6021", "MEDLO6022", "MEDLO6023"]: return "Department Level Optional Course-2"
            elif course_code == "MEL601": return "Machine Design Lab"
            elif course_code == "MEL602": return "Turbo Machinery Lab"
            elif course_code == "MEL603": return "Heating, Ventilation, Air conditioning and Refrigeration Lab"
            elif course_code == "MESBL601": return "Measurements and Automation"
            elif course_code == "MEPBL601": return "Mini Project 2B"
    
    elif branch == "CE":
        if semester == "sem2":
            if course_code == "PCC11CE03": return "Digital Electronics"
            elif course_code == "BSC11CE03": return "Integral Calculus and Probability Theory"
            elif course_code == "BSC11CE02": return "Engineering Physics"
            elif course_code == "ESC11CE04": return "Human Health Systems"
            elif course_code == "PCC11CE02": return "Essential Computing Skills for Engineers"
            elif course_code == "VSE11CE01": return "Measuring Instruments and Testing Tools"
            elif course_code == "AEC11CE01": return "Art of Communication"
            elif course_code == "HMM11CE01": return "Introduction to Emerging Technologies"
            elif course_code == "ESC11CE01": return "Engineering Graphics"
            elif course_code.startswith("LLC"): return "Liberal Learning Course"
        
        elif semester == "sem4":
            if course_code == "BSC12CE06": return "Linear Algebra and Business Statistics"
            elif course_code == "PCC12CE08": return "Database Management Systems"
            elif course_code == "PCC12CE09": return "Analysis of Algorithm"
            elif course_code == "PCC12CE10": return "Advanced JAVA Programming Lab"
            elif course_code == "MDM02": return "Emerging Technology and Law"
            elif course_code.startswith("OECE3"): return "Microprocessor (Open Elective-3)"
            elif course_code == "VSE12CE03": return "Full Stack Development Lab"
            elif course_code.startswith("AEC12CE02"): return "Modern Indian Language"
            elif course_code == "EEM12CE02": return "Technology Entrepreneurship"
            elif course_code == "VEC12CE02": return "Technology Innovation for Sustainable Development"
            elif course_code.startswith("LLC"): return "Liberal Learning Course"
            elif course_code == "IKS11CE01": return "Indian Knowledge System"
            elif course_code == "ESC11BCE04": return "Human Health Systems"
            elif course_code == "VSE11CE02": return "Creative Coding in Python"
            
        elif semester == "sem6":
            if course_code == "CSC601": return "System Programming & Compiler Construction"
            elif course_code == "CSC602": return "Cryptography & System Security"
            elif course_code == "CSC603": return "Mobile Computing"
            elif course_code == "CSC604": return "Artificial Intelligence"
            elif course_code in ["CSDLO6011", "CSDLO6012", "CSDLO6013"]: return "Department Level Optional Course-2"
            elif course_code == "CSL601": return "System Programming & Compiler Construction Lab"
            elif course_code == "CSL602": return "Cryptography & System Security Lab"
            elif course_code == "CSL603": return "Mobile Computing Lab"
            elif course_code == "CSL604": return "Artificial Intelligence Lab"
            elif course_code == "CSL605": return "Skill-based Laboratory"
            elif course_code == "CSM601": return "Mini Project 2B"

    elif branch == "AI&DS":
        if semester == "sem2":
            if course_code == "PCC11CS03": return "Digital Electronics"
            elif course_code == "BSC11CS03": return "Integral Calculus and Probability Theory"
            elif course_code == "BSC11CS04": return "Engineering Chemistry"
            elif course_code == "ESC11CS04": return "Human Health Systems"
            elif course_code == "PCC11CS04": return "Essential Psychomotor Skills for Engineers"
            elif course_code == "VSE11CS02": return "Creative Coding in Python" # Corrected
            elif course_code == "IKS11CS01": return "Indian Knowledge System"
            elif course_code == "HMM11CS01": return "Introduction to Emerging Technologies"
            elif course_code == "ESC11CS03": return "Programming Fundamentals"
            elif course_code.startswith("LLC"): return "Liberal Learning Course"
        
        elif semester == "sem4":
            if course_code == "BSC12CS06": return "Linear Algebra and Business Statistics"
            elif course_code == "PCC12CS09": return "Database Management Systems"
            elif course_code == "PCC12CS08": return "Analysis of Algorithm"
            elif course_code == "PCC12CS10": return "Data Analytics and Visualization"
            elif course_code == "AMDM02": return "Emerging Technology and Law"
            elif course_code.startswith("OECS2"): return "Open Elective-3" # Assuming this is the pattern for AI&DS open electives
            elif course_code == "AVSE12CS03": return "Web Programming"
            elif course_code.startswith("AEC12CS02"): return "Modern Indian Language"
            elif course_code == "AEEM12CS02": return "Technology Entrepreneurship"
            elif course_code == "AVEC12CS02": return "Technology Innovation for Sustainable Development"
            elif course_code.startswith("LLC"): return "Liberal Learning Course"
            elif course_code == "AIKS11CS01": return "Indian Knowledge System"
            elif course_code == "AESC11BCS04": return "Human Health Systems"
            elif course_code == "AVSE11CS02": return "Creative Coding in Python" # Assuming this maps to CE's Creative Coding
            
        elif semester == "sem6":
            if course_code == "ACSC601": return "Data Analytics and Visualization"
            elif course_code == "ACSC602": return "Cryptography & System Security"
            elif course_code == "ACSC603": return "Software Engineering and Project Management"
            elif course_code == "ACSC604": return "Machine Learning"
            elif course_code in ["CSDLO6011", "CSDLO6012", "CSDLO6013"]: return "Department Level Optional Course-2"
            elif course_code == "ACSL601": return "Data Analytics and Visualization Lab"
            elif course_code == "ACSL602": return "Cryptography & System Security Lab"
            elif course_code == "ACSL603": return "Software Engineering and Project Management Lab"
            elif course_code == "ACSL604": return "Machine Learning Lab"
            elif course_code == "ACSL605": return "Skill base Lab Course: Cloud Computing"
            elif course_code == "ACSM601": return "Mini Project 2B"

    elif branch == "ECS":
        if semester == "sem2":
            if course_code == "PCC11EC03": return "Digital Electronics"
            elif course_code == "BSC11EC03": return "Integral Calculus and Probability Theory"
            elif course_code == "BSC11EC04": return "Engineering Chemistry"
            elif course_code == "ESC11EC04": return "Human Health Systems"
            elif course_code == "PCC11EC04": return "Essential Psychomotor Skills for Engineers"
            elif course_code == "VSE11EC02": return "Creative Coding in Python"
            elif course_code == "IKS11EC01": return "Indian Knowledge System"
            elif course_code == "HMM11EC01": return "Introduction to Emerging Technologies"
            elif course_code == "ESC11EC03": return "Programming Fundamentals"
            elif course_code.startswith("LLC"): return "Liberal Learning Course"
        
        elif semester == "sem4":
            if course_code == "BSC12EC06": return "Mathematics and Numerical Methods"
            elif course_code == "PCC12EC08": return "Analog Electronics"
            elif course_code == "PCC12EC09": return "Discrete Structures and AutomataTheory"
            elif course_code == "PCC12EC10": return "Embedded Systems"
            elif course_code == "MDM02": return "Emerging Technology and Law"
            elif course_code.startswith("OEEC31"): return "Operating Systems" # Assuming this is the pattern for ECS open electives
            elif course_code == "VSE12EC03": return "Data Structures"
            elif course_code.startswith("AEC12EC02"): return "Modern Indian Language"
            elif course_code == "EEM12EC02": return "Technology Entrepreneurship"
            elif course_code == "VEC12EC02": return "Technology Innovation for Sustainable Development"
            elif course_code.startswith("LLC"): return "Liberal Learning Course"
            elif course_code == "BC12EC01": return "Electromagnetic Theory"
            elif course_code == "ESC11EC04": return "Human Health Systems" # Re-appears in Sem 4
            elif course_code == "VSE11EC02": return "Creative Coding in Python" # Assuming this maps to CE's Creative Coding
            
        elif semester == "sem6":
            if course_code == "ECC601": return "Embedded Systems and RTOS"
            elif course_code == "ECC602": return "Artificial Intelligence"
            elif course_code == "ECC603": return "Computer Networks"
            elif course_code == "ECC604": return "Data Warehousing and Mining"
            elif course_code in ["ECCDO601", "ECCDO6012", "ECCDO6013", "ECCDO6014"]: return "Department Level Optional Course-2"
            elif course_code == "ECL601": return "Embedded Systems Lab"
            elif course_code == "ECL602": return "Artificial Intelligence and Computer Networks Lab"
            elif course_code == "ECL603": return "Data Warehousing and Mining Lab"
            elif course_code == "ECL604": return "Skill base Laboratory"
            elif course_code == "ECM601": return "Mini Project 2B"

    return None # Return None if no mapping is found

def extract_marks_from_page_debug(driver):
    """Enhanced marks extraction with debugging."""
    raw_marks_strings = []
    
    print(f"DEBUG: Starting marks extraction")
    print(f"DEBUG: Current URL: {driver.current_url}")
    print(f"DEBUG: Page title: {driver.title}")
    
    # Print all tables found
    tables = driver.find_elements(By.TAG_NAME, "table")
    print(f"DEBUG: Found {len(tables)} tables on page")
    
    for i, table in enumerate(tables):
        print(f"DEBUG: Table {i+1} class: {table.get_attribute('class')}")
        print(f"DEBUG: Table {i+1} id: {table.get_attribute('id')}")
        
        # Print table headers
        headers = table.find_elements(By.TAG_NAME, "th")
        if headers:
            header_texts = [h.text.strip() for h in headers]
            print(f"DEBUG: Table {i+1} headers: {header_texts}")
        
        # Print first few rows of data
        rows = table.find_elements(By.TAG_NAME, "tr")
        for j, row in enumerate(rows[:5]):  # First 5 rows only
            cells = row.find_elements(By.TAG_NAME, "td")
            if cells:
                cell_texts = [c.text.strip() for c in cells]
                print(f"DEBUG: Table {i+1}, Row {j+1}: {cell_texts}")
    
    # Strategy 1: Look for cells containing '/' (e.g., "35/50")
    try:
        mark_cells = driver.find_elements(By.XPATH, "//table//td[contains(text(), '/')]")
        print(f"DEBUG: Found {len(mark_cells)} cells with '/' character")
        for cell in mark_cells:
            text = cell.text.strip()
            print(f"DEBUG: Cell with '/': '{text}'")
            if re.match(r'^\s*\d+(\.\d+)?/\d+(\.\d+)?\s*$', text):
                raw_marks_strings.append(text)
                print(f"DEBUG: Added mark: '{text}'")
    except Exception as e:
        print(f"DEBUG: Strategy 1 failed: {e}")
                        
    # Strategy 2: Look for numeric cells
    if not raw_marks_strings:
        try:
            mark_cells = driver.find_elements(By.XPATH, "//table//td[normalize-space() != '']")
            print(f"DEBUG: Found {len(mark_cells)} non-empty cells")
            for cell in mark_cells:
                text = cell.text.strip()
                if re.match(r'^\d+(\.\d+)?$', text):
                    print(f"DEBUG: Found numeric cell: '{text}'")
                    raw_marks_strings.append(text)
        except Exception as e:
            print(f"DEBUG: Strategy 2 failed: {e}")
                            
    # Strategy 3: Look for any number-like text
    if not raw_marks_strings:
        try:
            all_cells = driver.find_elements(By.XPATH, "//table//td")
            print(f"DEBUG: Checking all {len(all_cells)} table cells")
            for cell in all_cells:
                text = cell.text.strip()
                if re.match(r'^\d+(\.\d+)?(/\d+(\.\d+)?)?$', text):
                    print(f"DEBUG: Found potential mark: '{text}'")
                    raw_marks_strings.append(text)
        except Exception as e:
            print(f"DEBUG: Strategy 3 failed: {e}")
    
    print(f"DEBUG: Final extracted marks: {raw_marks_strings}")
    return raw_marks_strings
# Function to get Chrome version
def get_chrome_version():
    try:
        # Check standard Chrome paths
        paths = [
            r'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
            r'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
            os.path.expanduser('~') + r'\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe'
        ]
        
        for path in paths:
            if os.path.exists(path):
                try:
                    result = subprocess.check_output(
                        f'wmic datafile where name="{path.replace("\\", "\\\\")}" get Version /value',
                        shell=True
                    )
                    version = result.decode().strip().split('=')[-1].strip()
                    if version:
                        return version
                except:
                    continue
                
        # Alternative method using registry
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\\Google\\Chrome\\BLBeacon')
            version, _ = winreg.QueryValueEx(key, 'version')
            return version
        except:
            pass
            
    except Exception as e:
        print(f"Error getting Chrome version: {str(e)}")
    return None

# Global variable to store progress
progress_data = {}

def update_progress(session_id, message):
    progress_data[session_id] = {'status': 'processing', 'message': message}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_cgpa', methods=['POST'])
def get_cgpa():
    try:
        data = request.get_json()
        username = data.get('username')
        birth_day = data.get('birth_day')
        birth_month = data.get('birth_month')
        birth_year = data.get('birth_year')
        semester = data.get('semester', 'sem4') # Default to sem4
        branch = data.get('branch', 'ME') # Default to ME

        if not all([username, birth_day, birth_month, birth_year]):
            return jsonify({'status': 'error', 'error': 'All fields are required.'}), 400

        session_id = str(uuid.uuid4())
        session['session_id'] = session_id

        # Initial progress message
        update_progress(session_id, "Starting automation thread...")
        
        def run_automation():
            try:
                def progress_callback(message):
                    update_progress(session_id, message)
                
                marks = get_marks_from_portal(username, birth_day, birth_month, birth_year, semester, branch, progress_callback)
                
                # Calculate CGPA based on semester and branch
                cgpa = 0.0
                if branch == "ME":
                    if semester == "sem6":
                        cgpa = calculate_cgpa_sem6_me(marks)
                    elif semester == "sem2":
                        cgpa = calculate_cgpa_sem2_me(marks)
                    else: # sem4 ME
                        cgpa = calculate_cgpa_sem4_me(marks)
                elif branch == "CE":
                    if semester == "sem6":
                        cgpa = calculate_cgpa_sem6_ce(marks)
                    elif semester == "sem2":
                        cgpa = calculate_cgpa_sem2_ce(marks)
                    else: # sem4 CE
                        cgpa = calculate_cgpa_sem4_ce(marks)
                elif branch == "AI&DS":
                    if semester == "sem6":
                        cgpa = calculate_cgpa_sem6_aids(marks)
                    elif semester == "sem2":
                        cgpa = calculate_cgpa_sem2_aids(marks)
                    else: # sem4 AI&DS
                        cgpa = calculate_cgpa_sem4_aids(marks)
                elif branch == "ECS":
                    if semester == "sem6":
                        cgpa = calculate_cgpa_sem6_ecs(marks)
                    elif semester == "sem2":
                        cgpa = calculate_cgpa_sem2_ecs(marks)
                    else: # sem4 ECS
                        cgpa = calculate_cgpa_sem4_ecs(marks)
                
                progress_data[session_id] = {
                    'status': 'completed',
                    'marks': marks,
                    'cgpa': cgpa,
                    'semester': semester,
                    'branch': branch
                }
            except Exception as e:
                progress_data[session_id] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        thread = threading.Thread(target=run_automation)
        thread.start()
        
        return jsonify({'status': 'started', 'session_id': session_id})
        
    except Exception as e:
        return jsonify({'status': 'error', 'error': f"Server error: {str(e)}"}), 500 # Use 500 for server-side errors

@app.route('/progress')
def get_progress():
    session_id = request.args.get('session_id')
    if session_id in progress_data:
        return jsonify(progress_data[session_id])
    else:
        return jsonify({'status': 'waiting', 'message': 'Initializing...'})

@app.route('/calculate_manual', methods=['POST'])
def calculate_manual():
    """Allow manual CGPA calculation without automation."""
    try:
        data = request.get_json()
        marks = data.get('marks', {})
        semester = data.get('semester', 'sem4') # Default to sem4
        branch = data.get('branch', 'ME') # Default to ME
        
        # Ensure marks are floats
        processed_marks = {k: float(v) for k, v in marks.items()}

        cgpa = 0.0
        if branch == "ME":
            if semester == "sem6":
                cgpa = calculate_cgpa_sem6_me(processed_marks)
            elif semester == "sem2":
                cgpa = calculate_cgpa_sem2_me(processed_marks)
            else: # sem4 ME
                cgpa = calculate_cgpa_sem4_me(processed_marks)
        elif branch == "CE":
            if semester == "sem6":
                cgpa = calculate_cgpa_sem6_ce(processed_marks)
            elif semester == "sem2":
                cgpa = calculate_cgpa_sem2_ce(processed_marks)
            else: # sem4 CE
                cgpa = calculate_cgpa_sem4_ce(processed_marks)
        elif branch == "AI&DS":
            if semester == "sem6":
                cgpa = calculate_cgpa_sem6_aids(processed_marks)
            elif semester == "sem2":
                cgpa = calculate_cgpa_sem2_aids(processed_marks)
            else: # sem4 AI&DS
                cgpa = calculate_cgpa_sem4_aids(processed_marks)
        elif branch == "ECS":
            if semester == "sem6":
                cgpa = calculate_cgpa_sem6_ecs(processed_marks)
            elif semester == "sem2":
                cgpa = calculate_cgpa_sem2_ecs(processed_marks)
            else: # sem4 ECS
                cgpa = calculate_cgpa_sem4_ecs(processed_marks)
            
        return jsonify({
            'status': 'success',
            'cgpa': cgpa,
            'marks': processed_marks, # Return processed marks for consistency
            'semester': semester,
            'branch': branch
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
    # For deployment, consider setting host and port explicitly:
    app.run(host='0.0.0.0', port=6000)