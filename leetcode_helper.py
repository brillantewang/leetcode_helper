import requests
import json
import csv
from typing import List, Dict
import os
from dotenv import load_dotenv

load_dotenv()

def get_leetcode_meta_questions() -> List[Dict]:
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

def write_to_csv(questions: List[Dict]):
    with open("leetcode_meta_thirty_days.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["url"])
        for question in questions:
            writer.writerow([
                f"https://leetcode.com/problems/{question['titleSlug']}"
            ])

def main():
    try:
        print("Getting questions...")
        questions = get_leetcode_meta_questions()
        print("Writing to csv...")
        write_to_csv(questions)
        print("Successfully wrote questions to csv")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
