This is a project that hits Leetcode's internal graphql API to fetch Meta's 30-day questions and output them into a csv. It requires that you have a Leetcode Premium subscription and that you add your LEETCODE_SESSION cookie to the `.env` file.

It optionally lets you pass in a previous csv to merge with the fetched questions.

```
python leetcode_helper.py --prev-csv <path_to_previous_csv>
```

Make sure the previous csv has the `title_slug` (used to match) and `url` columns. Any questions that aren't in the fetched question set will be marked as outdated and moved to the bottom of the sheet.
