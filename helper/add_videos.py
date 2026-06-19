import sys
import os
import argparse # Import argparse
import random   # Keep random import
# Add the parent directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)  # Insert at beginning to prioritize local imports

from datetime import datetime, timedelta, timezone

# Import app and db from the local main module
import importlib.util
spec = importlib.util.spec_from_file_location("main", os.path.join(project_root, "main.py"))
main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main)
app = main.app
db = main.db

from models import YouTubeVideo, User
import random

# List of popular/viral YouTube videos with their IDs and links
VIRAL_VIDEOS_INITIAL = [
    {
        "youtube_id": "dQw4w9WgXcQ",
        "link": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "description": "Rick Astley - Never Gonna Give You Up (Rickroll)",
    },
    {
        "youtube_id": "oHg5SJYRHA0",
        "link": "https://www.youtube.com/watch?v=oHg5SJYRHA0",
        "description": "Bad Apple!! - Touhou Animation",
    },
    {
        "youtube_id": "9bZkp7q19f0",
        "link": "https://www.youtube.com/watch?v=9bZkp7q19f0",
        "description": "PSY - Gangnam Style",
    },
    {
        "youtube_id": "kffacxfA7G4",
        "link": "https://www.youtube.com/watch?v=kffacxfA7G4",
        "description": "Justin Bieber - Baby",
    },
    {
        "youtube_id": "JGwWNGJdvx8",
        "link": "https://www.youtube.com/watch?v=JGwWNGJdvx8",
        "description": "Ed Sheeran - Shape of You",
    },
    {
        "youtube_id": "OPf0YbXqDm0",
        "link": "https://www.youtube.com/watch?v=OPf0YbXqDm0",
        "description": "Mark Ronson ft. Bruno Mars - Uptown Funk",
    },
    {
        "youtube_id": "hT_nvWreIhg",
        "link": "https://www.youtube.com/watch?v=hT_nvWreIhg",
        "description": "One Direction - What Makes You Beautiful",
    },
    {
        "youtube_id": "fJ9rUzIMcZQ",
        "link": "https://www.youtube.com/watch?v=fJ9rUzIMcZQ",
        "description": "Queen - Bohemian Rhapsody",
    },
    {
        "youtube_id": "y6120QOlsfU",
        "link": "https://www.youtube.com/watch?v=y6120QOlsfU",
        "description": "Dramatic Chipmunk",
    },
    {
        "youtube_id": "kJQP7kiw5Fk",
        "link": "https://www.youtube.com/watch?v=kJQP7kiw5Fk",
        "description": "Luis Fonsi - Despacito ft. Daddy Yankee",
    },
    {
        "youtube_id": "C0DPdy98e4c",
        "link": "https://www.youtube.com/watch?v=C0DPdy98e4c",
        "description": "Wiz Khalifa - See You Again ft. Charlie Puth",
    },
    {
        "youtube_id": "RgKAFK5djSk",
        "link": "https://www.youtube.com/watch?v=RgKAFK5djSk",
        "description": "Waka Waka (This Time for Africa) - Shakira",
    },
    {
        "youtube_id": "ktvTqknDobU",
        "link": "https://www.youtube.com/watch?v=ktvTqknDobU",
        "description": "Charlie bit my finger - again !",
    },
    {
        "youtube_id": "jNQXAC9IVRw",
        "link": "https://www.youtube.com/watch?v=jNQXAC9IVRw",
        "description": "Me at the zoo (First YouTube Video)",
    },
    {
        "youtube_id": "YqeW9_5kURI",
        "link": "https://www.youtube.com/watch?v=YqeW9_5kURI",
        "description": "Evolution of Dance",
    },
    {
        "youtube_id": "eBGIQ7ZuuiU",
        "link": "https://www.youtube.com/watch?v=eBGIQ7ZuuiU",
        "description": "Adele - Hello",
    },
    {
        "youtube_id": "09m0B8RRiEE",
        "link": "https://www.youtube.com/watch?v=09m0B8RRiEE",
        "description": "Maroon 5 - Sugar",
    },
    {
        "youtube_id": "nfWlot6h_JM",
        "link": "https://www.youtube.com/watch?v=nfWlot6h_JM",
        "description": "Taylor Swift - Blank Space",
    },
    {
        "youtube_id": "uelHwf8o7_U",
        "link": "https://www.youtube.com/watch?v=uelHwf8o7_U",
        "description": "Crash Course World History - The Agricultural Revolution",
    },
    {
        "youtube_id": "zSgiXGELjbc",
        "link": "https://www.youtube.com/watch?v=zSgiXGELjbc",
        "description": "Kurzgesagt – In a Nutshell - The Fermi Paradox",
    },
    {
        "youtube_id": "Zi_XLOBDo_Y",
        "link": "https://www.youtube.com/watch?v=Zi_XLOBDo_Y",
        "description": "Nyan Cat [original]",
    },
    {
        "youtube_id": "ZZ5LpwO-An4",
        "link": "https://www.youtube.com/watch?v=ZZ5LpwO-An4",
        "description": "Keyboard Cat (Original)",
    },
    {
        "youtube_id": "kfVsfOSbJY0",
        "link": "https://www.youtube.com/watch?v=kfVsfOSbJY0",
        "description": "Harlem Shake (original army edition)",
    },
    {
        "youtube_id": "btPJPFnesV4",
        "link": "https://www.youtube.com/watch?v=btPJPFnesV4",
        "description": "Chocolate Rain Original Song by Tay Zonday",
    },
    {
        "youtube_id": "KmtzQCSh6xk",
        "link": "https://www.youtube.com/watch?v=KmtzQCSh6xk",
        "description": "Rebecca Black - Friday",
    },
    {
        "youtube_id": "OQSNhk5ICTI",
        "link": "https://www.youtube.com/watch?v=OQSNhk5ICTI",
        "description": "Star Wars Kid",
    },
    {
        "youtube_id": "b8HO6hba9ZE",
        "link": "https://www.youtube.com/watch?v=b8HO6hba9ZE",
        "description": "Numa Numa",
    },
    {
        "youtube_id": "sdyC1BrQd6g",
        "link": "https://www.youtube.com/watch?v=sdyC1BrQd6g",
        "description": "Shoes the Full Version",
    },
    {
        "youtube_id": "tntOCGkgt98",
        "link": "https://www.youtube.com/watch?v=tntOCGkgt98",
        "description": "Ultimate Dog Tease",
    },
    {
        "youtube_id": "jofNR_WkoCE",
        "link": "https://www.youtube.com/watch?v=jofNR_WkoCE",
        "description": "The Duck Song",
    },
    {
        "youtube_id": "QH2-TGUlwu4",
        "link": "https://www.youtube.com/watch?v=QH2-TGUlwu4",
        "description": "Nyan Cat",
    },
    {
        "youtube_id": "EwTZ2xpQwpA",
        "link": "https://www.youtube.com/watch?v=EwTZ2xpQwpA",
        "description": "Baby Shark Dance",
    },
    {
        "youtube_id": "HPJKxAhLhdk",
        "link": "https://www.youtube.com/watch?v=HPJKxAhLhdk",
        "description": "Old Town Road - Lil Nas X ft. Billy Ray Cyrus",
    },
    {
        "youtube_id": "gdZLi9oWNZg",
        "link": "https://www.youtube.com/watch?v=gdZLi9oWNZg",
        "description": "Smash Mouth - All Star",
    },
    {
        "youtube_id": "lWA2pjMjpBs",
        "link": "https://www.youtube.com/watch?v=lWA2pjMjpBs",
        "description": "Toto - Africa",
    },
    {
        "youtube_id": "3tmd-ClpJxA",
        "link": "https://www.youtube.com/watch?v=3tmd-ClpJxA",
        "description": "Darude - Sandstorm",
    },
    {
        "youtube_id": "6ZfuNTqbHE8",
        "link": "https://www.youtube.com/watch?v=6ZfuNTqbHE8",
        "description": "Take On Me - a-ha",
    },
    {
        "youtube_id": "V-_O7nl0Ii0",
        "link": "https://www.youtube.com/watch?v=V-_O7nl0Ii0",
        "description": "Potter Puppet Pals: The Mysterious Ticking Noise",
    },
    {
        "youtube_id": "gkTb9GP9lVI",
        "link": "https://www.youtube.com/watch?v=gkTb9GP9lVI",
        "description": "David After Dentist",
    },
    {
        "youtube_id": "z6EchXyieos",
        "link": "https://www.youtube.com/watch?v=z6EchXyieos",
        "description": "Leave Britney Alone!",
    },
    {
        "youtube_id": "oavMtUWDBTM",
        "link": "https://www.youtube.com/watch?v=oavMtUWDBTM",
        "description": "Talking Twin Babies",
    },
    {
        "youtube_id": "1uwOL4rB-go",
        "link": "https://www.youtube.com/watch?v=1uwOL4rB-go",
        "description": "Sneezing Baby Panda",
    },
    {
        "youtube_id": "dMH0bHeiRNg",
        "link": "https://www.youtube.com/watch?v=dMH0bHeiRNg",
        "description": "Kony 2012",
    },
    {
        "youtube_id": "Mh4f9AYRCZY",
        "link": "https://www.youtube.com/watch?v=Mh4f9AYRCZY",
        "description": "Double Rainbow Song",
    },
    {
        "youtube_id": "O1KW3ZkLtuo",
        "link": "https://www.youtube.com/watch?v=O1KW3ZkLtuo",
        "description": "Bed Intruder Song",
    },
    {
        "youtube_id": "X21mJh6j9i4",
        "link": "https://www.youtube.com/watch?v=X21mJh6j9i4",
        "description": "What Does The Fox Say? - Ylvis",
    },
    {
        "youtube_id": "u9VMfdG873E",
        "link": "https://www.youtube.com/watch?v=u9VMfdG873E",
        "description": "Pen Pineapple Apple Pen",
    },
    {
        "youtube_id": "Uj1ykZWtPYI",
        "link": "https://www.youtube.com/watch?v=Uj1ykZWtPYI",
        "description": "Man's Not Hot - Big Shaq",
    },
    {
        "youtube_id": "6Mgqbai3fKo",
        "link": "https://www.youtube.com/watch?v=6Mgqbai3fKo",
        "description": "This is America - Childish Gambino",
    },
    {
        "youtube_id": "PT2_F-1esPk",
        "link": "https://www.youtube.com/watch?v=PT2_F-1esPk",
        "description": "Bohemian Rhapsody Trailer",
    },
    {
        "youtube_id": "L_LUpnjgPso",
        "link": "https://www.youtube.com/watch?v=L_LUpnjgPso",
        "description": "How Animals Eat Their Food",
    },
    {
        "youtube_id": "wZZ7oFKsKzY",
        "link": "https://www.youtube.com/watch?v=wZZ7oFKsKzY",
        "description": "History of the entire world, i guess",
    },
    {
        "youtube_id": "ERTT_sv8sV0",
        "link": "https://www.youtube.com/watch?v=ERTT_sv8sV0",
        "description": "Bill Wurtz - just did a bad thing",
    },
    {
        "youtube_id": "DLzxrzFCyOs",
        "link": "https://www.youtube.com/watch?v=DLzxrzFCyOs",
        "description": "Lazy Sunday - SNL Digital Short",
    },
    {
        "youtube_id": "4Am7oKBD3PU",
        "link": "https://www.youtube.com/watch?v=4Am7oKBD3PU",
        "description": "Dick in a Box - SNL Digital Short",
    },
    {
        "youtube_id": "SAxpAs1Iaec",
        "link": "https://www.youtube.com/watch?v=SAxpAs1Iaec",
        "description": "I'm On A Boat - The Lonely Island ft. T-Pain",
    },
    {
        "youtube_id": "8UFIYGkROII",
        "link": "https://www.youtube.com/watch?v=8UFIYGkROII",
        "description": "OK Go - Here It Goes Again",
    },
    {
        "youtube_id": "qybUFnY7Y8w",
        "link": "https://www.youtube.com/watch?v=qybUFnY7Y8w",
        "description": "OK Go - This Too Shall Pass - Rube Goldberg Machine",
    },
    {
        "youtube_id": "mWRsgZuwf_8",
        "link": "https://www.youtube.com/watch?v=mWRsgZuwf_8",
        "description": "OK Go - The Writing's On the Wall",
    },
    {
        "youtube_id": "kOkQ4T5WO9E",
        "link": "https://www.youtube.com/watch?v=kOkQ4T5WO9E",
        "description": "Canon Rock - JerryC",
    },
    {
        "youtube_id": "d9NF2edxy-M",
        "link": "https://www.youtube.com/watch?v=d9NF2edxy-M",
        "description": "Guitar - Funtwo (Canon Rock cover)",
    },
    {
        "youtube_id": "Q5im0Ssyyy8",
        "link": "https://www.youtube.com/watch?v=Q5im0Ssyyy8",
        "description": "Where the Hell is Matt? (2008)",
    },
    {
        "youtube_id": "0Bmhjf0rKe8",
        "link": "https://www.youtube.com/watch?v=0Bmhjf0rKe8",
        "description": "Surprised Kitty",
    },
    {
        "youtube_id": "Lk59imFr6yI",
        "link": "https://www.youtube.com/watch?v=Lk59imFr6yI",
        "description": "Leeroy Jenkins",
    },
    {
        "youtube_id": "MMh8V0n43ik",
        "link": "https://www.youtube.com/watch?v=MMh8V0n43ik",
        "description": "Techno Viking",
    },
    {
        "youtube_id": "sTSA_sWGM44",
        "link": "https://www.youtube.com/watch?v=sTSA_sWGM44",
        "description": "Trololo (Mr. Trololo)",
    },
    {
        "youtube_id": "s8MDNFaGfT4",
        "link": "https://www.youtube.com/watch?v=s8MDNFaGfT4",
        "description": "Peanut Butter Jelly Time",
    },
    {
        "youtube_id": "M3iOROuTuMA",
        "link": "https://www.youtube.com/watch?v=M3iOROuTuMA",
        "description": "Salad Fingers 1: Spoons",
    },
    {
        "youtube_id": "CsGYh8AacgY",
        "link": "https://www.youtube.com/watch?v=CsGYh8AacgY",
        "description": "Charlie the Unicorn",
    },
    {
        "youtube_id": "N1GJbYp3gS8",
        "link": "https://www.youtube.com/watch?v=N1GJbYp3gS8",
        "description": "Grape Lady Falls!",
    },
    {
        "youtube_id": "BEtIoGQxqQs",
        "link": "https://www.youtube.com/watch?v=BEtIoGQxqQs",
        "description": "Afro Ninja",
    },
    {
        "youtube_id": "W45DRy7M1no",
        "link": "https://www.youtube.com/watch?v=W45DRy7M1no",
        "description": "Boom goes the dynamite",
    },
    {
        "youtube_id": "adCUgxS1Lsw",
        "link": "https://www.youtube.com/watch?v=adCUgxS1Lsw",
        "description": "Christian the Lion Reunion",
    },
    {
        "youtube_id": "qg1ckCkm8YI",
        "link": "https://www.youtube.com/watch?v=qg1ckCkm8YI",
        "description": "Will It Blend? - iPhone",
    },
    {
        "youtube_id": "ZN5PoW7_Mns",
        "link": "https://www.youtube.com/watch?v=ZN5PoW7_Mns",
        "description": "The Annoying Orange",
    },
    {
        "youtube_id": "7_cMaPE2lwE",
        "link": "https://www.youtube.com/watch?v=7_cMaPE2lwE",
        "description": "Fred Goes Grocery Shopping",
    },
    {
        "youtube_id": "6bVa6jn4rpE",
        "link": "https://www.youtube.com/watch?v=6bVa6jn4rpE",
        "description": "Don't Tase Me Bro!",
    },
    {
        "youtube_id": "lj3iNxZ8Dww",
        "link": "https://www.youtube.com/watch?v=lj3iNxZ8Dww",
        "description": "Miss Teen USA 2007 - South Carolina",
    },
    {
        "youtube_id": "wKsoXHYICqU",
        "link": "https://www.youtube.com/watch?v=wKsoXHYICqU",
        "description": "Obama Girl - I Got a Crush... on Obama",
    },
    {
        "youtube_id": "RxPZh4AnWyk",
        "link": "https://www.youtube.com/watch?v=RxPZh4AnWyk",
        "description": "Susan Boyle - I Dreamed A Dream - Britain's Got Talent 2009",
    },
    {
        "youtube_id": "4-94JhLEiN0",
        "link": "https://www.youtube.com/watch?v=4-94JhLEiN0",
        "description": "JK Wedding Entrance Dance",
    },
    {
        "youtube_id": "fsgWUq0fdKk",
        "link": "https://www.youtube.com/watch?v=fsgWUq0fdKk",
        "description": "Literal Bohemian Rhapsody",
    },
    {
        "youtube_id": "4wGR4-SeuJ0",
        "link": "https://www.youtube.com/watch?v=4wGR4-SeuJ0",
        "description": "Chad Vader: Day Shift Manager",
    },
    {
        "youtube_id": "4r7wHMg5Yjg",
        "link": "https://www.youtube.com/watch?v=4r7wHMg5Yjg",
        "description": "The Crazy Nastyass Honey Badger",
    },
    {
        "youtube_id": "K2cYWfq--Nw",
        "link": "https://www.youtube.com/watch?v=K2cYWfq--Nw",
        "description": "Daft Hands - Harder, Better, Faster, Stronger",
    },
    {
        "youtube_id": "PSpA6v0M0_k",
        "link": "https://www.youtube.com/watch?v=PSpA6v0M0_k",
        "description": "Daft Body - Harder, Better, Faster, Stronger",
    },
    {
        "youtube_id": "kxopViU98Xo",
        "link": "https://www.youtube.com/watch?v=kxopViU98Xo",
        "description": "Epic Sax Guy (10 hours)",
    },
    {
        "youtube_id": "eh7lp9umG2I",
        "link": "https://www.youtube.com/watch?v=eh7lp9umG2I",
        "description": "Dancing Baby (Oogachaka Baby)",
    },
    {
        "youtube_id": "Z4Y4keqTV6w",
        "link": "https://www.youtube.com/watch?v=Z4Y4keqTV6w",
        "description": "All Your Base Are Belong To Us",
    },
    {
        "youtube_id": "KaqC5FnvAEc",
        "link": "https://www.youtube.com/watch?v=KaqC5FnvAEc",
        "description": "End of the World (Flash animation)",
    },
    {
        "youtube_id": "J---aiyznGQ",
        "link": "https://www.youtube.com/watch?v=J---aiyznGQ",
        "description": "The Llama Song",
    },
    {
        "youtube_id": "60og9gwKh1o",
        "link": "https://www.youtube.com/watch?v=60og9gwKh1o",
        "description": "Badger Badger Badger",
    },
    {
        "youtube_id": "HPPj6viIBmU",
        "link": "https://www.youtube.com/watch?v=HPPj6viIBmU",
        "description": "We Like the Moon - Spongmonkeys",
    },
    {
        "youtube_id": "EIyixC9NsLI",
        "link": "https://www.youtube.com/watch?v=EIyixC9NsLI",
        "description": "Dramatic Look (Prairie Dog)",
    },
    {
        "youtube_id": "zYKupOsaJmk",
        "link": "https://www.youtube.com/watch?v=zYKupOsaJmk",
        "description": "Antoine Dodson 'Bed Intruder' Original News Report",
    },
    {
        "youtube_id": "NsLKQTh-Bqo",
        "link": "https://www.youtube.com/watch?v=NsLKQTh-Bqo",
        "description": "Technoviking Original Street Parade",
    },
    {
        "youtube_id": "pFlcqWQVVuU",
        "link": "https://www.youtube.com/watch?v=pFlcqWQVVuU",
        "description": "Gangnam Style - PSY (Official Music Video)", # Adding the official one too
    },
]

# --- Generate placeholders to reach 150 ---
VIRAL_VIDEOS = VIRAL_VIDEOS_INITIAL[:] # Copy the initial list

placeholder_count = 200 - len(VIRAL_VIDEOS)

for i in range(placeholder_count):
    # Generate a plausible but fake YouTube ID (11 chars, base64-like)
    fake_id_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
    fake_id = "".join(random.choice(fake_id_chars) for _ in range(11))

    # Avoid collision with real IDs (unlikely but possible)
    while any(v['youtube_id'] == fake_id for v in VIRAL_VIDEOS):
         fake_id = "".join(random.choice(fake_id_chars) for _ in range(11))

    VIRAL_VIDEOS.append({
        "youtube_id": fake_id,
        "link": f"https://www.youtube.com/watch?v={fake_id}",
        "description": f"Placeholder Video {i+1} - Replace Me",
    })

def push_test_youtube_videos(num_to_add=None):
    with app.app_context():
        print("🎥 LilyOpenCMS YouTube Video Generator")
        print("=" * 50)
        
        # Ensure the database is initialized
        db.create_all()

        # Fetch all users from the database
        users = User.query.all()

        if not users:
            print("❌ Please ensure there is at least one user in the database.")
            print("   Run generate_user.py first!")
            return

        # Determine which videos to process based on num_to_add
        videos_to_process = VIRAL_VIDEOS
        if num_to_add is not None:
            if num_to_add > len(VIRAL_VIDEOS):
                print(f"⚠️ Warning: Requested {num_to_add} videos, but only {len(VIRAL_VIDEOS)} are defined. Adding all available.")
                num_to_add = len(VIRAL_VIDEOS) # Cap at max available
            elif num_to_add <= 0:
                 print("🤷 No videos requested to be added.")
                 return
            videos_to_process = VIRAL_VIDEOS[:num_to_add]

        # Add viral YouTube videos to the database
        added_count = 0
        skipped_count = 0
        print(f"Attempting to add {len(videos_to_process)} YouTube videos...")
        for i, video_data in enumerate(videos_to_process):
            # Randomly select a user
            user = random.choice(users)

            # Check if the video already exists
            if YouTubeVideo.query.filter_by(
                youtube_id=video_data["youtube_id"]
            ).first():
                # print(f"  - Skipping video {video_data['youtube_id']} (already exists)") # Optional verbose output
                skipped_count += 1
                continue

            # Create a YouTube video entry
            video = YouTubeVideo(
                youtube_id=video_data["youtube_id"],
                link=video_data["link"],
                title=video_data["description"],  # Fill video title from VIRAL_VIDEOS
                user_id=user.id,
                is_visible=True,
                created_at=datetime.now(timezone.utc)
                - timedelta(days=i),  # Spread out creation dates
                updated_at=datetime.now(timezone.utc),
            )

            print(f"  + Adding video: {video_data['description'][:50]}...") # Show progress
            db.session.add(video)
            added_count += 1

        # Commit the changes to the database
        if added_count > 0:
            try:
                db.session.commit()
                print(f"\n✅ Successfully added {added_count} new YouTube videos.")
                if skipped_count > 0:
                    print(f"   Skipped {skipped_count} videos that already existed.")
            except Exception as e:
                 db.session.rollback()
                 print(f"\n❌ Error committing videos: {e}")
        elif skipped_count > 0 and added_count == 0:
             print(f"\n🤷 No new videos were added ({skipped_count} selected videos already exist).")
        else:
             print("\n🤷 No videos were processed or added.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add predefined YouTube videos to the database.")
    parser.add_argument(
        "--num-vids",
        type=int,
        default=len(VIRAL_VIDEOS), # Default to adding all defined videos
        help=f"Number of videos to add from the predefined list (max: {len(VIRAL_VIDEOS)}). (default: {len(VIRAL_VIDEOS)})"
    )
    args = parser.parse_args()

    # No need for strict positive validation here, handled in the function

    push_test_youtube_videos(args.num_vids) # Pass the number to the function
