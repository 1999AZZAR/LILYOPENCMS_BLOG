import sys
import os
import argparse

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

from models import Image


def set_all_image_visibility(visible_status: bool):
    """
    Sets the 'is_visible' status for all images in the database.

    Args:
        visible_status (bool): The desired visibility status (True for visible, False for hidden).
    """
    with app.app_context():
        print(f"Attempting to set visibility for all images to: {visible_status}")

        try:
            # Efficiently update all images at once using update()
            # This is generally faster than fetching all, iterating, and saving one by one
            num_updated = db.session.query(Image).update(
                {"is_visible": visible_status}, synchronize_session=False
            )

            # Commit the changes
            db.session.commit()

            if num_updated > 0:
                print("-" * 30)
                print(
                    f"✅ Successfully updated visibility for {num_updated} images to {visible_status}."
                )
                print("-" * 30)
            else:
                print("-" * 30)
                print("🤷 No images found or no visibility changes needed.")
                print("-" * 30)

        except Exception as e:
            db.session.rollback()
            print("-" * 30)
            print(f"❌ Error updating image visibility: {e.__class__.__name__} - {e}")
            print("   Database changes have been rolled back.")
            print("-" * 30)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Set visibility for all images.")
    parser.add_argument("visibility", choices=['true', 'false'],
                        help="Set visibility to 'true' or 'false'.")

    args = parser.parse_args()
    desired_visibility = args.visibility.lower() == 'true'
    set_all_image_visibility(desired_visibility)