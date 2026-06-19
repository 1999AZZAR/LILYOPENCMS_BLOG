import sys
import os
import argparse # Import argparse
import random   # Import random for shuffling
from faker import Faker # Import Faker
# Add the parent directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)  # Insert at beginning to prioritize local imports

from models import db, Category  # Import your database and Category model

# Import app from the local main module
import importlib.util
spec = importlib.util.spec_from_file_location("main", os.path.join(project_root, "main.py"))
main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main)
app = main.app

# Initialize Faker
fake = Faker()

# Define the DEFAULT categories to insert
default_categories = [ # <<< RENAME THIS VARIABLE
    "Teknologi",
    "Olahraga",
    "Keuangan",
    "Hiburan",
    "Kesehatan",
    "Sains",
    "Pendidikan",
    "Perjalanan",
    "Makanan",
    "Lifestyle",
    "Otomotif",
    "Politik",
    "Lingkungan",
    "Seni & Budaya",
    "Mode",
    "Bisnis",
    "Properti",
    "Opini",
    "Internasional",
    "Regional",
    "Games",
    "Fotografi",
    "Parenting",
    "Lainnya" 
]


def add_categories(num_total_desired=None):
    with app.app_context():
        print("📂 LilyOpenCMS Category Generator")
        print("=" * 50)
        
        num_defaults = len(default_categories)

        # Determine the final list of category names
        target_categories = set() # Use a set for efficient uniqueness checks

        if num_total_desired is None:
            # Default case: use all predefined categories
            target_categories.update(default_categories)
            print(f"Using all {num_defaults} predefined categories.")
        elif num_total_desired <= num_defaults:
            # User wants a subset of predefined categories
            target_categories.update(default_categories[:num_total_desired])
            print(f"Using the first {num_total_desired} predefined categories.")
        else:
            # User wants more categories than predefined: use all defaults + generate extras
            target_categories.update(default_categories)
            num_to_generate = num_total_desired - num_defaults
            print(f"Using all {num_defaults} predefined categories.")
            print(f"Attempting to generate {num_to_generate} additional unique categories using Faker...")

            generated_count = 0
            attempts = 0
            max_attempts = num_to_generate * 5 # Give up after a reasonable number of tries

            while generated_count < num_to_generate and attempts < max_attempts:
                new_cat_name = fake.word().capitalize()
                # Ensure it's not empty, not already default, and not already generated
                if new_cat_name and len(new_cat_name) > 2 and new_cat_name not in target_categories:
                    target_categories.add(new_cat_name)
                    generated_count += 1
                attempts += 1

            if generated_count < num_to_generate:
                 print(f"⚠️ Warning: Could only generate {generated_count} unique categories after {max_attempts} attempts (reached {len(target_categories)} total).")
            else:
                 print(f"   Successfully generated {generated_count} additional categories.")

        # Determine which categories to add
        categories_to_process = sorted(list(target_categories)) # Sort for consistent order
        print(f"Attempting to add {len(categories_to_process)} categories...")
        added_count = 0
        skipped_count = 0

        # Loop through the selected categories and add them
        for category_name in categories_to_process:
            # Check if the category already exists
            existing_category = Category.query.filter_by(name=category_name).first()
            if not existing_category:
                # Create a new Category object
                new_category = Category(name=category_name)
                db.session.add(new_category)
                print(f"  + Adding '{category_name}'")
                added_count += 1
            else:
                # print(f"  - Skipping '{category_name}' (already exists)") # Optional: uncomment for verbose output
                skipped_count += 1

        # Commit the changes to the database
        if added_count > 0:
            try:
                db.session.commit()
                print(f"\n✅ Successfully added {added_count} new categories.")
                if skipped_count > 0:
                    print(f"   Skipped {skipped_count} categories that already existed.")
            except Exception as e:
                 db.session.rollback()
                 print(f"\n❌ Error committing categories: {e}")
        elif skipped_count > 0 and added_count == 0:
             print(f"\n🤷 No new categories were added ({skipped_count} selected categories already exist).")
        else:
             print("\n🤷 No categories were processed or added.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add predefined and/or generated categories to the database.")
    parser.add_argument(
        "--num-cat",
        type=int,
        default=len(default_categories), # Default to adding all predefined ones
        help=f"Total number of categories desired. If > {len(default_categories)}, Faker will generate the rest. (default: {len(default_categories)})"
    )
    args = parser.parse_args()

    # Validate num_cat if provided
    if args.num_cat <= 0:
        print("❌ Error: --num-cat must be a positive integer.", file=sys.stderr)
        sys.exit(1)
    # No need for max validation anymore, as we can generate more

    add_categories(args.num_cat) # Pass the total number desired to the function
