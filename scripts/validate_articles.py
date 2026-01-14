import json
from datetime import datetime

def validate_articles():
    try:
        with open("static/data/articles.json", "r") as f:
            data = json.load(f)

        print(f"Loaded {len(data)} articles.")
        slugs = set()
        
        for i, article in enumerate(data):
            # Check required fields
            required = ["slug", "title", "date", "week", "year", "excerpt", "content", "featured_player_id"]
            missing = [key for key in required if key not in article]
            if missing:
                print(f"Article {i} ({article.get('slug', 'unknown')}) missing keys: {missing}")
            
            # Check slug uniqueness
            slug = article.get("slug")
            if slug:
                if slug in slugs:
                    print(f"Duplicate slug found: {slug}")
                slugs.add(slug)
            
            # Validate date format
            date_str = article.get("date")
            if date_str:
                try:
                    datetime.strptime(date_str, "%Y-%m-%d")
                except ValueError:
                    print(f"Invalid date format for {slug}: {date_str}")
            
            # Check for non-empty content
            if not article.get("content"):
                print(f"Warning: Empty content for {slug}")

        print("Validation check complete.")

    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    validate_articles()
