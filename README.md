This is a project that hits Leetcode's internal graphql API to fetch Meta's 30-day questions and output them into a csv. It requires that you have a Leetcode Premium subscription and that you add your LEETCODE_SESSION cookie to the `.env` file.

It optionally lets you pass in a previous csv to merge with the newly fetched questions. This is useful if you want to carry over your own custom fields, say Notes, etc.

```
python leetcode_helper.py --prev-csv <path_to_previous_csv>
```

Note:
- Previous csv must have the `title_slug` field (used to match).
- Any previous questions that aren't in the fetched question set will be marked as outdated and moved to the bottom of the sheet.
