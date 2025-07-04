import requests
import csv
import os
from dotenv import load_dotenv
from datetime import datetime
import argparse
from enum import Enum

load_dotenv()

class FavoriteSlug(Enum):
    """Enum for LeetCode favorite list slugs"""
    FACEBOOK_THIRTY_DAYS = "facebook-thirty-days"
    UBER_THREE_MONTHS = "uber-three-months"

def get_leetcode_questions(favorite_slug: str = FavoriteSlug.FACEBOOK_THIRTY_DAYS.value) -> list[dict]:
    url = "https://leetcode.com/graphql"

    # Based this on the actual network request that leetcode makes in browser
    query = """
    query favoriteQuestionList(
        $favoriteSlug: String!,
        $sortBy: QuestionSortByInput,
        $version: String = "v2"
    ) {
        favoriteQuestionList(
            favoriteSlug: $favoriteSlug,
            sortBy: $sortBy
            version: $version
        ) {
            questions {
                title
                titleSlug
                difficulty
            }
        }
    }
    """

    variables = {
        "favoriteSlug": f"{favorite_slug}",
        "sortBy": {
            "sortField": "CUSTOM", # This is what leetcode actually uses by default. Can also use FREQUENCY
            "sortOrder": "ASCENDING"
        }
    }

    headers = {
        "Cookie": f"LEETCODE_SESSION={os.getenv('LEETCODE_SESSION')}",  # After logging into leetcode, get this from your browser and add to .env
        "Content-Type": "application/json",
    }

    response = requests.post(
        url,
        json={
            "query": query,
            "variables": variables
        },
        headers=headers
    )

    response.raise_for_status()

    data = response.json()
    return data["data"]["favoriteQuestionList"]["questions"]

def read_previous_csv(file_path: str) -> tuple[list[dict], list[str]]:
    if not os.path.exists(file_path):
        return [], []

    with open(file_path, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader), reader.fieldnames

def write_to_csv(favorite_slug: str, questions: list[dict], prev_questions: list[dict] = [], prev_fieldnames: list[str] = []):
    print(f"Writing {len(questions)} questions to csv...")

    timestamp = datetime.now().strftime("%m%d%Y")
    filename = f"leetcode_{favorite_slug}_{timestamp}.csv"

    fieldnames = ["title_slug", "url", "is_outdated"]
    fieldnames.extend(f for f in prev_fieldnames if f not in fieldnames)
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        # Write current questions
        prev_lookup = {q["title_slug"]: q for q in prev_questions}
        for q in questions:
            url = f"https://leetcode.com/problems/{q['titleSlug']}"
            row = {
                "title_slug": q["titleSlug"],
                "url": url,
                "is_outdated": ""
            }

            if q["titleSlug"] in prev_lookup:
                prev_q = prev_lookup[q["titleSlug"]]
                for field in fieldnames:
                    if field not in row:
                        row[field] = prev_q[field]
            writer.writerow(row)

        # Write outdated questions from previous csv
        curr_slugs = {q["titleSlug"] for q in questions}
        for prev_q in prev_questions:
            if prev_q["title_slug"] not in curr_slugs:
                row = dict(prev_q)
                row["is_outdated"] = "T"
                writer.writerow(row)

        print(f"Successfully wrote questions to {filename}")

def main():
    parser = argparse.ArgumentParser(description='Fetch LeetCode questions and optionally merge with previous CSV')
    parser.add_argument('--prev-csv', type=str, help='Path to previous CSV file to merge with')
    parser.add_argument('--favorite-slug', type=str,
                       default=FavoriteSlug.FACEBOOK_THIRTY_DAYS.value,
                       help=f'Favorite slug to fetch questions from. Example options: {", ".join([slug.value for slug in FavoriteSlug])}. You can also use any custom slug.')
    args = parser.parse_args()

    try:
        print("Getting questions...")
        questions = get_leetcode_questions(args.favorite_slug)

        prev_questions, prev_fieldnames = [], []
        if args.prev_csv:
            print(f"Reading previous CSV from {args.prev_csv}...")
            prev_questions, prev_fieldnames = read_previous_csv(args.prev_csv)

        write_to_csv(args.favorite_slug, questions, prev_questions, prev_fieldnames)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
