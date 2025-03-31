def filter_commands(commands, term="", tag_filter="Alle"):
    """
    Filtert die übergebenen Befehle anhand eines Suchbegriffs und optional eines Tags.

    :param commands: Liste von Befehlen (jeweils dict mit keys: command, beschreibung, optionen, tags)
    :param term: Suchbegriff (string, optional)
    :param tag_filter: Aktuell ausgewählter Tag oder "Alle"
    :return: Gefilterte Liste
    """
    term = term.lower().strip()
    filtered = []

    for cmd in commands:
        matches_search = (
            term in cmd.get("command", "").lower()
            or term in cmd.get("beschreibung", "").lower()
            or any(term in key.lower() or term in val.lower() for key, val in cmd.get("optionen", {}).items())
            or any(term in tag.lower() for tag in cmd.get("tags", []))
        )

        matches_tag = tag_filter == "Alle" or tag_filter in cmd.get("tags", [])

        if matches_search and matches_tag:
            filtered.append(cmd)

    return filtered
