from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS

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
# from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeType

app = Flask(__name__)
CORS(app)  # allow frontend on Vercel to talk to backend
app.secret_key = os.urandom(24)

# Add this right after: app.secret_key = os.urandom(24)

def check_browser_setup():
    """Check if Chrome and ChromeDriver are properly installed for containerized environments."""
    chrome_bin = os.environ.get("CHROME_BIN", "/usr/bin/chromium")
    chromedriver_path = os.environ.get("CHROMEDRIVER_PATH", "/usr/bin/chromedriver")
    
    print("=" * 50)
    print("BROWSER SETUP CHECK")
    print("=" * 50)
    
    if not os.path.exists(chrome_bin):
        print(f"⚠️  WARNING: Chrome binary not found at {chrome_bin}")
        # Check alternative locations
        alternative_locations = ["/usr/bin/google-chrome", "/usr/bin/chrome", "/usr/bin/chromium-browser"]
        for alt in alternative_locations:
            if os.path.exists(alt):
                print(f"✅ Found Chrome at alternative location: {alt}")
                os.environ["CHROME_BIN"] = alt
                chrome_bin = alt
                break
    else:
        print(f"✅ Chrome binary found: {chrome_bin}")
    
    if not os.path.exists(chromedriver_path):
        print(f"⚠️  WARNING: ChromeDriver not found at {chromedriver_path}")
        # Check alternative locations
        alternative_locations = ["/usr/local/bin/chromedriver", "/opt/chromedriver/chromedriver"]
        for alt in alternative_locations:
            if os.path.exists(alt):
                print(f"✅ Found ChromeDriver at alternative location: {alt}")
                os.environ["CHROMEDRIVER_PATH"] = alt
                chromedriver_path = alt
                break
    else:
        print(f"✅ ChromeDriver found: {chromedriver_path}")
    
    # Test if ChromeDriver is executable
    try:
        import stat
        if os.path.exists(chromedriver_path):
            file_stat = os.stat(chromedriver_path)
            if file_stat.st_mode & stat.S_IEXEC:
                print(f"✅ ChromeDriver is executable")
            else:
                print(f"⚠️  ChromeDriver exists but is not executable")
    except Exception as e:
        print(f"⚠️  Could not check ChromeDriver permissions: {e}")
    
    print(f"📍 Final Chrome binary: {chrome_bin}")
    print(f"📍 Final ChromeDriver: {chromedriver_path}")
    print("=" * 50)
    
    return chrome_bin, chromedriver_path

# Call the check function
try:
    check_browser_setup()
    print("🚀 Browser setup check completed")
except Exception as e:
    print(f"❌ Browser setup check failed: {e}")

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
# --- Enhanced Selenium Automation Function ---
def get_marks_from_portal(username, birth_day, birth_month, birth_year, semester="sem4", branch="ME", progress_callback=None):
    LOGIN_URL = "https://crce-students.contineo.in/parentseven/"
    student_marks = {}
    
    chrome_options = Options()
    
    # Essential options for containerized deployment
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-web-security')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-plugins')
    chrome_options.add_argument('--disable-images')
    chrome_options.add_argument('--disable-logging')
    chrome_options.add_argument('--disable-dev-tools')
    chrome_options.add_argument('--disable-crash-reporter')
    chrome_options.add_argument('--disable-background-timer-throttling')
    chrome_options.add_argument('--disable-backgrounding-occluded-windows')
    chrome_options.add_argument('--disable-renderer-backgrounding')
    chrome_options.add_argument('--disable-features=TranslateUI')
    chrome_options.add_argument('--disable-ipc-flooding-protection')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_argument('--remote-debugging-port=9222')
    
    # Memory and performance optimizations for Railway/Render
    chrome_options.add_argument('--memory-pressure-off')
    chrome_options.add_argument('--max-old-space-size=512')
    
    # --- CHANGE THIS SECTION ---
    # Generate a unique user data directory for each session to prevent conflicts
    user_data_dir = f"/tmp/chrome-user-data-{uuid.uuid4()}"
    chrome_options.add_argument(f'--user-data-dir={user_data_dir}')
    
    # The --single-process flag can be problematic in concurrent environments; it's best to remove it.
    # The line below is commented out in your original code, which is correct.
    # # chrome_options.add_argument('--single-process')
    # -----------------------------
    
    # Set Chrome binary path for containerized environments
    chrome_options.binary_location = os.environ.get("CHROME_BIN", "/usr/bin/chromium")
    
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.notifications": 2,
        "profile.default_content_settings.popups": 0,
        "profile.managed_default_content_settings.images": 2
    })
    
    driver = None
    
    try:
        if progress_callback:
            progress_callback("Initializing browser...")
        
        # Simplified driver initialization for containers
        try:
            # For containerized environments, use system chromedriver
            chromedriver_path = os.environ.get("CHROMEDRIVER_PATH", "/usr/bin/chromedriver")
            if os.path.exists(chromedriver_path):
                service = Service(chromedriver_path)
                driver = webdriver.Chrome(service=service, options=chrome_options)
                print(f"DEBUG: Using system chromedriver: {chromedriver_path}")
            else:
                # Fallback to ChromeDriverManager
                # service = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
                driver = webdriver.Chrome(service=service, options=chrome_options)
                print(f"DEBUG: Using ChromeDriverManager")
                
        except Exception as e:
            print(f"DEBUG: ChromeDriver initialization failed: {e}")
            # Final fallback - let selenium find chromedriver
            driver = webdriver.Chrome(options=chrome_options)
        
        # Set timeouts
        driver.set_page_load_timeout(30)
        driver.implicitly_wait(10)
        
        if progress_callback:
            progress_callback("Browser initialized successfully...")
            
        # Test browser functionality with retry mechanism
        max_retries = 3
        for attempt in range(max_retries):
            try:
                driver.get("about:blank")
                print(f"DEBUG: Browser test successful on attempt {attempt + 1}")
                break
            except Exception as e:
                print(f"DEBUG: Browser test failed on attempt {attempt + 1}: {e}")
                if attempt == max_retries - 1:
                    raise Exception(f"Browser initialization failed after {max_retries} attempts: {e}")
                time.sleep(2)
            
        # Navigate to login page with retry
        if progress_callback:
            progress_callback("Connecting to portal...")
        
        for attempt in range(3):
            try:
                driver.get(LOGIN_URL)
                break
            except Exception as e:
                print(f"DEBUG: Failed to load login page on attempt {attempt + 1}: {e}")
                if attempt == 2:
                    raise Exception(f"Could not load portal page: {e}")
                time.sleep(3)
        
        # Wait for login form with better error handling
        try:
            username_field = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
        except TimeoutException:
            # Try alternative selectors
            try:
                username_field = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.NAME, "username"))
                )
            except TimeoutException:
                raise Exception("Could not find username field. Portal might be down or structure changed.")
        
        if progress_callback:
            progress_callback("Filling login form...")
        
        # Fill login form with error handling
        try:
            username_field.clear()
            username_field.send_keys(username)
            
            day_field = driver.find_element(By.ID, "dd")
            day_field.clear()
            day_field.send_keys(birth_day)
            
            month_dropdown = Select(driver.find_element(By.ID, "mm"))
            month_dropdown.select_by_value(birth_month)
            
            year_field = driver.find_element(By.ID, "yyyy")
            year_field.clear()
            year_field.send_keys(birth_year)
            
        except Exception as e:
            raise Exception(f"Failed to fill login form: {e}")
        
        time.sleep(1)  # Brief pause before clicking login

        # Enhanced login button detection and clicking
        login_success = False
        login_selectors = [
            (By.XPATH, "//input[@type='submit']"),
            (By.XPATH, "//button[contains(text(), 'Login') or contains(text(), 'Sign In') or contains(@class, 'login')]"),
            (By.XPATH, "//input[@value='Login' or @value='Sign In']"),
            (By.CSS_SELECTOR, "button[type='submit']"),
            (By.CSS_SELECTOR, "input[type='submit']")
        ]
        
        for i, selector in enumerate(login_selectors):
            if login_success:
                break
            try:
                if progress_callback:
                    progress_callback(f"Attempting login... (method {i+1})")
                
                login_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable(selector)
                )
                
                # Scroll to button and click
                driver.execute_script("arguments[0].scrollIntoView(true);", login_button)
                time.sleep(0.5)
                
                try:
                    login_button.click()
                except WebDriverException:
                    # JavaScript click as fallback
                    driver.execute_script("arguments[0].click();", login_button)
                
                login_success = True
                print(f"DEBUG: Successfully clicked login button using selector {i+1}")
                
            except TimeoutException:
                print(f"DEBUG: Login selector {i+1} not found")
                continue
            except Exception as e:
                print(f"DEBUG: Login selector {i+1} failed: {e}")
                continue
        
        if not login_success:
            raise Exception("Could not find or click any login button.")

        # Wait for navigation with better detection
        if progress_callback:
            progress_callback("Logging in...")
        
        try:
            # Wait for either URL change or dashboard elements
            WebDriverWait(driver, 20).until(
                lambda driver: (
                    driver.current_url != LOGIN_URL or
                    len(driver.find_elements(By.CSS_SELECTOR, "div.uk-card, .dashboard, #dashboard")) > 0
                )
            )
        except TimeoutException:
            # Check for login errors
            error_indicators = [
                "Invalid Username",
                "Incorrect",
                "Authentication failed",
                "Login failed",
                "Wrong credentials"
            ]
            
            page_text = driver.page_source.lower()
            for error in error_indicators:
                if error.lower() in page_text:
                    raise Exception(f"Login failed: {error}")
            
            raise Exception("Login process timed out. Portal might be slow or credentials incorrect.")
        
        dashboard_url = driver.current_url
        print(f"DEBUG: Dashboard URL: {dashboard_url}")
        
        if progress_callback:
            progress_callback("Finding subjects...")

        # Enhanced subject container detection
        subject_container_selectors = [
            "div.uk-card.uk-card-body.cn-pad-20.cn-fee-head",
            "div.uk-card",
            ".marks-container",
            ".subject-container",
            "div[class*='card']"
        ]
        
        subject_list_container = None
        for selector in subject_container_selectors:
            try:
                subject_list_container = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                print(f"DEBUG: Found subject container using: {selector}")
                break
            except TimeoutException:
                continue
        
        if not subject_list_container:
            raise Exception("Could not find subject list container. Portal structure might have changed.")

        # Find subjects table
        try:
            subjects_table = subject_list_container.find_element(By.TAG_NAME, "table")
        except:
            # Look for table anywhere on page
            tables = driver.find_elements(By.TAG_NAME, "table")
            if not tables:
                raise Exception("No tables found on the page.")
            subjects_table = tables[0]  # Use first table as fallback

        # Get subject rows with better error handling
        subject_rows = []
        try:
            tbody = subjects_table.find_element(By.TAG_NAME, "tbody")
            all_trs = tbody.find_elements(By.TAG_NAME, "tr")
        except:
            all_trs = subjects_table.find_elements(By.TAG_NAME, "tr")
        
        # Filter valid subject rows
        for row in all_trs:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) >= 2:  # Must have at least 2 columns
                subject_rows.append(row)

        if not subject_rows:
            raise Exception("No valid subject rows found. Check if marks are available for the selected semester.")

        total_subjects = len(subject_rows)
        print(f"DEBUG: Found {total_subjects} subjects")
        
        # Process each subject with enhanced error recovery
        for i, subject_row in enumerate(subject_rows):
            try:
                if progress_callback:
                    progress_callback(f"Processing subject {i+1} of {total_subjects}...")
                
                # Get subject details
                cells = subject_row.find_elements(By.TAG_NAME, "td")
                course_code = cells[0].text.strip()
                raw_subject_name = cells[1].text.strip()
                
                print(f"DEBUG: Processing {raw_subject_name} ({course_code})")
                
                subject_key = map_subject_name(course_code, raw_subject_name, semester, branch)
                
                if not subject_key:
                    print(f"DEBUG: Skipping unknown subject: {raw_subject_name}")
                    continue

                # Find and click CIE button with multiple strategies
                cie_selectors = [
                    ".//a[./button[contains(@class, 'cn-cieclr') and text()='CIE']]",
                    ".//button[contains(@class, 'cn-cieclr') and text()='CIE']",
                    ".//a[contains(text(), 'CIE')]",
                    ".//button[contains(text(), 'CIE')]",
                    ".//a[.//*[text()='CIE']]",
                    ".//a[contains(@href, 'cie') or contains(@href, 'CIE')]"
                ]
                
                cie_element = None
                for selector in cie_selectors:
                    try:
                        cie_element = subject_row.find_element(By.XPATH, selector)
                        if cie_element.is_enabled() and cie_element.is_displayed():
                            break
                    except:
                        continue
                
                if not cie_element:
                    print(f"DEBUG: No CIE button found for {subject_key}")
                    student_marks[subject_key] = 0.0
                    continue
                
                # Click CIE button with retry
                click_success = False
                for attempt in range(3):
                    try:
                        driver.execute_script("arguments[0].scrollIntoView(true);", cie_element)
                        time.sleep(0.5)
                        
                        try:
                            cie_element.click()
                        except WebDriverException:
                            driver.execute_script("arguments[0].click();", cie_element)
                        
                        click_success = True
                        break
                        
                    except Exception as e:
                        print(f"DEBUG: CIE click attempt {attempt + 1} failed: {e}")
                        if attempt < 2:
                            time.sleep(1)

                if not click_success:
                    print(f"DEBUG: Could not click CIE for {subject_key}")
                    student_marks[subject_key] = 0.0
                    continue

                # Wait for marks page with timeout
                marks_loaded = False
                wait_strategies = [
                    (By.XPATH, "//table//th[contains(text(), 'Marks') or contains(text(), 'Score')]"),
                    (By.XPATH, "//table[contains(@class, 'marks') or contains(@class, 'result')]"),
                    (By.XPATH, "//table")
                ]
                
                for strategy in wait_strategies:
                    try:
                        WebDriverWait(driver, 10).until(EC.presence_of_element_located(strategy))
                        marks_loaded = True
                        break
                    except TimeoutException:
                        continue
                
                if not marks_loaded:
                    print(f"DEBUG: Marks page did not load for {subject_key}")
                    student_marks[subject_key] = 0.0
                else:
                    # Extract marks with improved error handling
                    raw_marks_strings = extract_marks_from_page_debug(driver)
                    
                    if not raw_marks_strings:
                        student_marks[subject_key] = 0.0
                    else:
                        component_marks = [parse_mark_string(s) for s in raw_marks_strings]
                        calculated_mark = calculate_subject_mark(subject_key, component_marks, semester, branch)
                        student_marks[subject_key] = calculated_mark

                # Return to dashboard with retry
                return_success = False
                for attempt in range(3):
                    try:
                        driver.back()
                        WebDriverWait(driver, 15).until(
                            lambda d: dashboard_url in d.current_url or
                            len(d.find_elements(By.CSS_SELECTOR, "div.uk-card, .dashboard")) > 0
                        )
                        return_success = True
                        break
                    except:
                        if attempt < 2:
                            print(f"DEBUG: Return attempt {attempt + 1} failed, trying direct navigation")
                            driver.get(dashboard_url)
                            time.sleep(2)

                if not return_success:
                    print(f"DEBUG: Could not return to dashboard after {subject_key}")
                    break  # Stop processing if we can't navigate back

            except Exception as e:
                print(f"DEBUG: Error processing subject {i+1}: {e}")
                student_marks[subject_key if 'subject_key' in locals() else f"subject_{i+1}"] = 0.0
                
                # Try to return to dashboard
                try:
                    driver.back()
                    time.sleep(2)
                except:
                    pass
                
        if progress_callback:
            progress_callback("Marks extraction completed!")

    except Exception as e:
        print(f"DEBUG: Main exception: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Better error messages
        error_msg = str(e)
        if "Could not load portal page" in error_msg or "timed out" in error_msg.lower():
            error_msg = "Portal is not accessible. Please try again later."
        elif "Could not find username field" in error_msg:
            error_msg = "Portal login page has changed. Please contact support."
        elif "Login failed" in error_msg or "credentials" in error_msg.lower():
            error_msg = "Invalid credentials. Please check your username and birth date."
        elif "No valid subject rows found" in error_msg:
            error_msg = "No marks found for the selected semester. Data might not be available yet."
        elif "Browser initialization failed" in error_msg:
            error_msg = "System error. Please try again."
            
        if progress_callback:
            progress_callback(error_msg)
        raise Exception(error_msg)
        
    finally:
        # Enhanced cleanup
        if driver:
            try:
                if progress_callback:
                    progress_callback("Cleaning up...")
                
                # Try to logout
                try:
                    logout_selectors = [
                        "//a[contains(text(), 'Logout') or contains(text(), 'Log Out')]",
                        "//button[contains(text(), 'Logout')]",
                        "//a[contains(@href, 'logout')]"
                    ]
                    
                    for selector in logout_selectors:
                        try:
                            logout_element = driver.find_element(By.XPATH, selector)
                            logout_element.click()
                            time.sleep(1)
                            break
                        except:
                            continue
                            
                except Exception as e:
                    print(f"DEBUG: Logout failed: {e}")
                    
            except:
                pass
            finally:
                try:
                    driver.quit()
                    print(f"DEBUG: Browser closed successfully")
                except:
                    print(f"DEBUG: Error closing browser")

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
            r'C:\Program Files\Google\Chrome\Application\chrome.exe',
            r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
            os.path.expanduser('~') + r'\AppData\Local\Google\Chrome\Application\chrome.exe'
        ]
        
        for path in paths:
            if os.path.exists(path):
                try:
                    # Precompute the escaped path
                    fixed_path = path.replace("\\", "\\\\")
                    cmd = f'wmic datafile where name="{fixed_path}" get Version /value'
                    
                    result = subprocess.check_output(cmd, shell=True)
                    version = result.decode().strip().split('=')[-1].strip()
                    if version:
                        return version
                except Exception:
                    continue
                
        # Alternative method using registry
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Google\Chrome\BLBeacon')
            version, _ = winreg.QueryValueEx(key, 'version')
            return version
        except Exception:
            pass
            
    except Exception as e:
        print(f"Error getting Chrome version: {str(e)}")
    return None


# Global variable to store progress
progress_data = {}


def update_progress(session_id, message):
    progress_data[session_id] = {'status': 'processing', 'message': message}

@app.route('/')
def home():
    return jsonify({
        "message": "Backend is running ✅",
        "status": "healthy",
        "available_endpoints": [
            "/health",
            "/get_cgpa",
            "/calculate_manual",
            "/progress"
        ]
    }), 200

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
    
# Add this route for basic testing
@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'Backend is running ✅',
        'chrome_available': os.path.exists(os.environ.get("CHROME_BIN", "/usr/bin/chromium")),
        'chromedriver_available': os.path.exists(os.environ.get("CHROMEDRIVER_PATH", "/usr/bin/chromedriver")),
        'port': os.environ.get("PORT", "not set")
    }), 200


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

# Update your main block at the end of the file
if __name__ == '__main__':
    # Get port from environment (Railway provides this)
    port = int(os.environ.get('PORT', 8000))
    # Make sure to bind to all interfaces (0.0.0.0)
    app.run(host='0.0.0.0', port=port, debug=False)
else:
    # This is important for gunicorn
    # Make sure the app is accessible when imported
    application = app