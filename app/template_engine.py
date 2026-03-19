import re

TAG_PATTERN = re.compile(r"#([A-Z_]+)")

TAG_ALIASES = {
    "TITLE": "title",
    "YEAR": "year",
    "RATING": "rating",
    "VOTES": "votes",
    "DURATION": "runtime",
    "GENRE": "genres",
    "STORY_LINE": "plot",
    "IMG_POSTER": "poster",
    "LANGUAGE": "language",
    "DIRECTOR": "director",
    "WRITER": "writer",
    "CAST": "cast",
}


def render_template(template: str, data: dict) -> str:
    def replace(match):
        tag = match.group(1)
        key = TAG_ALIASES.get(tag)

        if not key:
            return match.group(0)

        value = data.get(key)
        if value is None:
            return ""

        return str(value)

    return TAG_PATTERN.sub(replace, template)
