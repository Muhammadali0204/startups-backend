from tortoise import Tortoise


def shorter(text, max_length=250):
    if len(text) <= max_length:
        return text
    words = text.split()
    shorted = ""
    for word in words:
        if len(shorted) + len(word) + 1 > max_length:
            break
        if shorted:
            shorted += " "
        shorted += word
    shorted += "..."
    return shorted


async def fuzzy_multiword_search(user_input: str):
    words = user_input.lower().split()

    conditions = " OR ".join([
        f"similarity(title, '{word}') > 0.1 OR similarity(subtitle, '{word}') > 0.1"
        for word in words
    ])

    order = " + ".join([
        f"similarity(title, '{word}') + similarity(subtitle, '{word}')"
        for word in words
    ])

    query = f"""
        SELECT * FROM projects
        WHERE {conditions}
        ORDER BY {order} DESC
        LIMIT 10
    """

    rows = await Tortoise.get_connection("default").execute_query_dict(query)
    return rows
