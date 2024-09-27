import re


def extract_id_from_link(link):
    # Regular expression pattern to extract the ID from the Google Sheets link
    pattern = r'/spreadsheets/d/([a-zA-Z0-9-_]+)'

    # Use re.search to find the pattern in the link
    match = re.search(pattern, link)

    # If a match is found, return the ID group, otherwise return None
    if match:
        return match.group(1)
    else:
        return None
