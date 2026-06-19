import sys
import os
from datetime import datetime, timedelta, timezone
import random
import requests
import time
import subprocess
import signal
import atexit
import mimetypes
import re
from io import BytesIO

# Add the parent directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)  # Insert at beginning to prioritize local imports

# Import app and db from the local main module
import importlib.util
spec = importlib.util.spec_from_file_location("main", os.path.join(project_root, "main.py"))
main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main)
app = main.app
db = main.db

from models import User

# Try to import PIL for image generation
try:
    from PIL import Image as PILImage, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

from faker import Faker

# Initialize Faker
fake = Faker()

# --- Configuration ---
BASE_URL = "http://127.0.0.1:5000"
LOGIN_URL = f"{BASE_URL}/login"
API_URL = f"{BASE_URL}/api/images"

# Credentials
LOGIN_USERNAME = os.environ.get("FLASK_LOGIN_USER", "suadmin")
LOGIN_PASSWORD = os.environ.get("FLASK_LOGIN_PASS", "suladang")

# Relative path to the uploads folder from the project root
SOURCE_IMAGES_FOLDER_RELATIVE = "helper/source_images"
# Define allowed image extensions (lowercase)
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}

# Colors for placeholder generation
PLACEHOLDER_COLORS = [
    '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', 
    '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9',
    '#F8C471', '#82E0AA', '#F1948A', '#85C1E9', '#F4D03F'
]

# Global variable to track server process
server_process = None

def cleanup_server():
    """Cleanup function to stop the server process."""
    global server_process
    if server_process:
        try:
            server_process.terminate()
            server_process.wait(timeout=5)
            print("🛑 Stopped Flask server")
        except subprocess.TimeoutExpired:
            server_process.kill()
            print("🛑 Force killed Flask server")
        except Exception as e:
            print(f"⚠️ Error stopping server: {e}")

# Register cleanup function
atexit.register(cleanup_server)

def start_flask_server():
    """Start the Flask server if it's not already running."""
    global server_process
    
    # First check if server is already running
    try:
        response = requests.get(f"{BASE_URL}/", timeout=2)
        if response.status_code == 200:
            print("✅ Flask server is already running")
            return True
    except requests.exceptions.RequestException:
        pass
    
    print("🚀 Starting Flask server...")
    try:
        # Start the server in a subprocess
        server_process = subprocess.Popen(
            [sys.executable, "main.py"],
            cwd=project_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid if hasattr(os, 'setsid') else None
        )
        
        # Wait for server to start
        max_retries = 30
        for i in range(max_retries):
            try:
                response = requests.get(f"{BASE_URL}/", timeout=2)
                if response.status_code == 200:
                    print("✅ Flask server started successfully")
                    return True
            except requests.exceptions.RequestException:
                pass
            
            time.sleep(1)
            if i % 5 == 0:
                print(f"⏳ Waiting for server to start... ({i+1}/{max_retries})")
        
        print("❌ Failed to start Flask server")
        return False
        
    except Exception as e:
        print(f"❌ Error starting Flask server: {e}")
        return False

def create_placeholder_image(width=800, height=600, text="Placeholder", color=None):
    """Create a placeholder image programmatically."""
    if not PIL_AVAILABLE:
        return None
        
    if color is None:
        color = random.choice(PLACEHOLDER_COLORS)
    
    # Create image with solid color background
    img = PILImage.new('RGB', (width, height), color)
    draw = ImageDraw.Draw(img)
    
    # Try to use a better font, fallback to default
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
    except (OSError, IOError):
        try:
            font = ImageFont.load_default()
        except:
            font = None
    
    # Add text to center
    if font:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        draw.text((x, y), text, fill='white', font=font)
    
    return img

def generate_placeholder_images(count=20):
    """Generate placeholder images in the source directory."""
    source_dir_absolute = os.path.join(project_root, SOURCE_IMAGES_FOLDER_RELATIVE)
    
    # Create source directory if it doesn't exist
    os.makedirs(source_dir_absolute, exist_ok=True)
    
    print(f"Generating {count} placeholder images in {source_dir_absolute}...")
    
    image_topics = [
        "Business", "Technology", "Education", "Health", "Travel", "Food", 
        "Sports", "Finance", "Entertainment", "Science", "Art", "Nature",
        "Politics", "Culture", "Environment", "Innovation", "UMKM", "Startup",
        "Investment", "Digital", "Social", "Economy", "News", "Info"
    ]
    
    for i in range(count):
        if PIL_AVAILABLE:
            # Generate different sized images
            sizes = [(800, 600), (1200, 800), (600, 400), (1000, 600)]
            width, height = random.choice(sizes)
            
            topic = random.choice(image_topics)
            color = random.choice(PLACEHOLDER_COLORS)
            
            img = create_placeholder_image(width, height, f"{topic} {i+1:02d}", color)
            
            if img:
                filename = f"placeholder_{i+1:02d}.jpg"
                filepath = os.path.join(source_dir_absolute, filename)
                img.save(filepath, 'JPEG', quality=85)
                print(f"  ✅ Created {filename}")
            else:
                print(f"  ❌ Failed to create image {i+1}")
        else:
            # Create a simple text file as placeholder when PIL is not available
            filename = f"placeholder_{i+1:02d}.txt"
            filepath = os.path.join(source_dir_absolute, filename)
            with open(filepath, 'w') as f:
                f.write(f"Placeholder image {i+1} - Install PIL/Pillow to generate actual images")
            print(f"  📝 Created text placeholder {filename} (PIL not available)")

def login_and_get_session():
    """Logs into the Flask app and returns a session object with cookies."""
    session = requests.Session()
    
    # Retry logic for login
    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f"Attempting login as {LOGIN_USERNAME} (attempt {attempt + 1}/{max_retries})...")
            
            # Fetch login page to get CSRF token
            login_page_resp = session.get(LOGIN_URL, timeout=10)
            login_page_resp.raise_for_status()
            
            # Try multiple ways to get CSRF token
            csrf_token = None
            
            # Method 1: Look for meta tag
            meta_match = re.search(r'<meta[^>]+name=["\']csrf-token["\'][^>]+content=["\']([^"\']+)["\']', login_page_resp.text, re.IGNORECASE)
            if meta_match:
                csrf_token = meta_match.group(1)
                print(f"   Found CSRF token in meta tag: {csrf_token[:10]}...")
            
            # Method 2: Look for input field
            if not csrf_token:
                input_match = re.search(r'<input[^>]+name=["\']csrf_token["\'][^>]+value=["\']([^"\']+)["\']', login_page_resp.text, re.IGNORECASE)
                if input_match:
                    csrf_token = input_match.group(1)
                    print(f"   Found CSRF token in input field: {csrf_token[:10]}...")
            
            # Method 3: Look for any csrf token in the page
            if not csrf_token:
                csrf_match = re.search(r'csrf_token["\']?\s*:\s*["\']([^"\']+)["\']', login_page_resp.text, re.IGNORECASE)
                if csrf_match:
                    csrf_token = csrf_match.group(1)
                    print(f"   Found CSRF token in script: {csrf_token[:10]}...")

            login_data = {
                "username": LOGIN_USERNAME,
                "password": LOGIN_PASSWORD,
                "remember": "y"
            }
            if csrf_token:
                login_data["csrf_token"] = csrf_token

            login_resp = session.post(LOGIN_URL, data=login_data, allow_redirects=True, timeout=10)
            login_resp.raise_for_status()

            # Check if login was successful
            if login_resp.url == LOGIN_URL or "Invalid username or password" in login_resp.text:
                print("❌ Login failed. Please check credentials and CSRF handling.")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                return None

            print("✅ Login successful.")
            return session
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Login attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            return None
    
    return None

def upload_image_via_api(session, filepath, filename, description):
    """Upload a single image via the API with retry logic."""
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            # Prepare form data
            form_data = {
                "name": os.path.splitext(filename)[0],
                "description": description,
            }

            # Prepare file data
            mime_type, _ = mimetypes.guess_type(filepath)
            if not mime_type:
                mime_type = 'application/octet-stream'

            with open(filepath, 'rb') as f:
                files_payload = {
                    'file': (filename, f, mime_type)
                }
                
                print(f"   ⬆️ Uploading {filename} via API (attempt {attempt + 1}/{max_retries})...")
                response = session.post(API_URL, data=form_data, files=files_payload, timeout=30)
                
                if response.status_code in [200, 201]:
                    print(f"   ✅ Successfully uploaded {filename}")
                    return True
                else:
                    error_msg = f"Status {response.status_code}"
                    try: 
                        error_data = response.json()
                        error_msg += f": {error_data.get('error', response.text)}"
                    except: 
                        error_msg += f": {response.text}"
                    print(f"   ❌ API upload failed for {filename}. {error_msg}")
                    
                    if attempt < max_retries - 1:
                        time.sleep(2)
                        continue
                    return False
                    
        except requests.exceptions.RequestException as e:
            print(f"   ❌ API request error for {filename}: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            return False
        except Exception as e:
            print(f"   ❌ Unexpected error for {filename}: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            return False
    
    return False

def add_images_via_api():
    """Add images via the API to ensure proper handling by the image parser."""
    print("🖼️ LilyOpenCMS Image Generator & API Uploader")
    print("=" * 50)
    
    # Start Flask server if needed
    if not start_flask_server():
        print("❌ Cannot proceed without Flask server")
        return
    
    # Get the absolute path to source directory
    source_dir_absolute = os.path.join(project_root, SOURCE_IMAGES_FOLDER_RELATIVE)
    
    # Check if directory exists, if not create it and generate placeholder images
    if not os.path.isdir(source_dir_absolute):
        print(f"📁 Source images directory not found at: {source_dir_absolute}")
        print("Creating directory and generating placeholder images...")
        os.makedirs(source_dir_absolute, exist_ok=True)
        generate_placeholder_images(20)
    else:
        # Check if directory is empty
        files_in_dir = [f for f in os.listdir(source_dir_absolute) 
                       if os.path.isfile(os.path.join(source_dir_absolute, f))]
        
        if not files_in_dir:
            print(f"📁 Source images directory is empty: {source_dir_absolute}")
            print("Generating placeholder images...")
            generate_placeholder_images(20)
    
    # Login to get session
    session = login_and_get_session()
    if not session:
        print("❌ Could not login. Skipping image upload.")
        return

    # Scan source directory for images
    print(f"\n🔍 Scanning for image files in: {source_dir_absolute}")
    added_count = 0
    skipped_count = 0
    error_count = 0

    files_in_dir = os.listdir(source_dir_absolute)
    print(f"   Found {len(files_in_dir)} total items.")

    # Sort files to process them in a consistent order
    files_in_dir.sort()

    for filename in files_in_dir:
        source_filepath = os.path.join(source_dir_absolute, filename)

        # Check if it's a file and has an allowed extension
        _, ext = os.path.splitext(filename)
        if (
            not os.path.isfile(source_filepath)
            or ext.lower() not in ALLOWED_EXTENSIONS
        ):
            skipped_count += 1
            continue

        # Generate a fake description
        description = fake.sentence(nb_words=random.randint(5, 15))

        # Upload via API
        if upload_image_via_api(session, source_filepath, filename, description):
            added_count += 1
        else:
            error_count += 1

    # Final summary
    print("-" * 50)
    if added_count > 0:
        print(f"✅ Successfully uploaded {added_count} images via API.")
    else:
        print("🤷 No new images were uploaded via API.")

    if skipped_count > 0:
        print(f"ℹ️ Skipped {skipped_count} files (not images).")
    if error_count > 0:
        print(f"⚠️ Encountered errors uploading {error_count} files.")
    print("-" * 50)

if __name__ == "__main__":
    try:
        add_images_via_api()
    finally:
        cleanup_server()
