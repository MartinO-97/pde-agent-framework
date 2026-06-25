def write_failure_output(planning_or_proving: str) -> str:

    r""" Function to create output for a failed planning or
    proving process.
    
    Parameters
    ----------
    planning_or_proving: str
        Did the workflow failed in the planning or proving stage.
    """

    error_message = \
    f""" \\documentclass[11pt, a4paper]{{article}} \n
        \n
        \\usepackage{{a4wide}} \n
        \\usepackage{{amsmath}} \n
        \\usepackage{{amssymb}} \n
        \\usepackage{{amsthm}} \n
        \\usepackage{{txfonts}} \n
        \\usepackage{{mathtools}} \n
        \\usepackage{{tikz}} \n
        \\usepackage{{mdwlist}} \n 

        \\begin{{document}} \n
            The workflow failed in the {planning_or_proving} stage. See .json files
            for furhter information.
        \\end{{document}} 
    """