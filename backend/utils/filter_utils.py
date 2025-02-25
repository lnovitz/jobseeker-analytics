import yaml

def parse_simple(
        term: str, 
        field: str,
        exclude: bool=False
        ) -> str:
    
    """
    Parses a simple combination of search field and search term into a gmail search string.
    If exclude is true, a "-" character is prepended to the field. 

    Args:
        term (str): list of terms to parse
        field (str): field to search
        exclude (bool): whether to exclude the terms
    """
    if field == "body":
        field_str = ""
    else:
        field_str = f"{field}:"

    if exclude:
        out_str = f"-{field_str}\"{term}\""
    else:
        out_str = f"{field_str}\"{term}\""

    return out_str

def parse_wildcard(
        term: str, 
        field: str,
        exclude: bool=False
        ) -> str:
    """
    The wildcard * is convenient to use in a yaml file, but it is 
    not supported by the Gmail API. This function will parse 
    any number of wildcards as ({field}: "{term1}" AND {field}: "{term2}" AND ...)

    If exclude is true, a "-" character is prepended to the field. 

    Args:
        term (str): list of terms to parse
        field (str): field to search
        exclude (bool): whether to exclude the terms
    """
    if field == "body":
        field_str = ""
    else:
        field_str = f"{field}:"

    if exclude:
        sub_terms = term.split(" * ")
        out_str =  "(" + " AND ".join([f"-{field_str}\"{x}\"" for x in sub_terms]) + ")"

    else:
        sub_terms = term.split(" * ")
        out_str = "(" + " AND ".join([f"{field_str}\"{x}\"" for x in sub_terms]) + ")"

    return out_str

def parse_base_filter_config(filter_path: str) -> str:
    with open(filter_path, 'r') as fid:
        data = yaml.safe_load(fid)

    filter_str = ""
    for block in data:
        sub_filter_str = ""
        if block["logic"] == "any":
            operator = " OR "
        elif block["logic"] == "all":
            operator = " AND "

        # parse each item based on schema logic    
        simple_filters = []
        wildcard_any_filters = []
        if block["how"] == "include":
            simple_filters += [parse_simple(x, block["field"], exclude=False) for x in block["terms"] if "*" not in x]
            wildcard_any_filters += [parse_wildcard(x, block["field"], exclude=False) for x in block["terms"] if "*" in x]
        if block["how"] == "exclude":
            simple_filters +=  [parse_simple(x, block["field"], exclude=True) for x in block["terms"]]
        
        # join with appropriate operator
        if simple_filters + wildcard_any_filters:                
            sub_filter_str = operator.join(simple_filters + wildcard_any_filters)

        # if this isn't the first item then we need to add an extra operator in from
        if sub_filter_str:
            if len(filter_str) > 0:
                sub_filter_str = operator + sub_filter_str
            filter_str += sub_filter_str

    filter_str = "(" + filter_str + ")"

    return filter_str

def parse_override_filter_config(filter_path: str):
    """ not implemented """
    with open(filter_path, 'r') as fid:
        data = yaml.safe_load(fid)
        
    filter_str_list = []
    for block in data:
        simple_filters = []
        for sub_block in block:
            include_terms = sub_block["include_terms"]
            exclude_terms = sub_block["exclude_terms"]

            # parse each item based on schema logic    
            if include_terms is not None:
                simple_filters += [parse_simple(x, sub_block["field"], exclude=False) for x in sub_block["include_terms"]]
            if exclude_terms is not None:
                simple_filters +=  [parse_simple(x, sub_block["field"], exclude=True) for x in sub_block["exclude_terms"]]

        # join with an AND operator
        if simple_filters:
            filter_str_list.append("(" + " AND ".join(simple_filters) + ")")

    filter_str = "(" + " OR ".join(filter_str_list) + ")"

    return filter_str