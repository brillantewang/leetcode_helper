import requests
import json
import csv
import os
from dotenv import load_dotenv
from datetime import datetime
import argparse

load_dotenv()

def get_leetcode_meta_questions() -> list[dict]:
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
        "favoriteSlug": "facebook-thirty-days",
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

def read_previous_csv(file_path: str) -> list[dict]:
    if not os.path.exists(file_path):
        return []

    with open(file_path, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

def write_to_csv(questions: list[dict], prev_questions: list[dict] = None):
    timestamp = datetime.now().strftime("%m%d%Y")
    filename = f"leetcode_meta_thirty_days_{timestamp}.csv"

    with open(filename, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["title_slug", "url", "is_outdated"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        # Write current questions
        for q in questions:
            url = f"https://leetcode.com/problems/{q['titleSlug']}"
            writer.writerow({
                "title_slug": q["titleSlug"],
                "url": url,
                "is_outdated": ""
            })

        # Write outdated questions from previous csv
        curr_slugs = set([q["titleSlug"] for q in questions])
        for prev_q in prev_questions:
            if prev_q["title_slug"] not in curr_slugs:
                writer.writerow({
                    "title_slug": prev_q["title_slug"],
                    "url": prev_q["url"],
                    "is_outdated": "T"
                })

def main():
    parser = argparse.ArgumentParser(description='Fetch LeetCode questions and optionally merge with previous CSV')
    parser.add_argument('--prev-csv', type=str, help='Path to previous CSV file to merge with')
    args = parser.parse_args()

    try:
        print("Getting questions...")
        questions = get_leetcode_meta_questions()

        prev_questions = []
        if args.prev_csv:
            print(f"Reading previous CSV from {args.prev_csv}...")
            prev_questions = read_previous_csv(args.prev_csv)
        
        print("Writing to csv...")
        write_to_csv(questions, prev_questions)
        print("Successfully wrote questions to csv")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
