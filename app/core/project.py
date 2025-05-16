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
