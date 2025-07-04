This is a project that hits Leetcode's internal graphql API to fetch questions (ie meta thirty days) and output them into a csv. It requires that you have a Leetcode Premium subscription and that you add your LEETCODE_SESSION cookie to the `.env` file. You can find this by inspecting the graphql call that Leetcode makes in your network tab.

It optionally lets you pass in a previous csv to merge with the newly fetched questions. This is useful if you want to carry over your own custom fields, say `is_mastered`, `notes`, etc. Then every time you want an updated list of questions, simply run the script with your last spreadsheet as the input, and your custom data will be preserved into the new sheet.

By default this fetches `facebook-thirty-days` questions. Otherwise you can pass in a favorite slug in the form of `company-time_period`. You can look at `favoriteSlug` in your url to see what Leetcode actually uses, ie https://leetcode.com/company/uber/?favoriteSlug=uber-three-months.

Example usage:
```
python leetcode_helper.py --prev-csv some_path.csv --favorite-slug uber-three-months
```

Note:
- Previous csv must have the `title_slug` field (used to match).
- Any previous questions that aren't in the fetched question set will be marked as outdated and moved to the bottom of the sheet.
