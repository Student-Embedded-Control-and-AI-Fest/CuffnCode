from collections import Counter

def analyze_file(filename):
    with open(filename, "r", encoding="utf-8") as f:
        text = f.read()

    words = text.lower().split()

    if len(words) == 0:
        most_common = "-"
    else:
        most_common = Counter(words).most_common(1)[0][0]

    return {
        "file": filename,
        "lines": len(text.splitlines()),
        "words": len(words),
        "characters": len(text),
        "most_common": most_common
    }