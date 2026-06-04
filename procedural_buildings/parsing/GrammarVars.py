import gin


@gin.configurable
def grammar_var_overrides(values=None):
    """Return dict of grammar variable overrides.

    Usage in .gin files:
        grammar_var_overrides.values = {"N": 5, "windowWidth": 3.0}
    """
    return values or {}


def get_grammar_var(name, fallback):
    """Return override for grammar variable `name`, or `fallback`."""
    overrides = grammar_var_overrides()
    if overrides and name in overrides:
        return overrides[name]
    return fallback