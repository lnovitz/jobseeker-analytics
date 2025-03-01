import yaml
import re
from typing import List, Dict, Union

FilterConfigType = List[Dict[str, Union[str, int, bool, list, dict]]]

def load_filter_config(filter_path: str) -> FilterConfigType:
    with open(filter_path, 'r') as fid:
        filter_config = yaml.safe_load(fid)
        return filter_config     

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
    """
    creates a gmail filter string from a yaml config
    """
    data = load_filter_config(filter_path)

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
    
    data = load_filter_config(filter_path)
        
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

def apply_base_filter(subject_text, from_text, filter_config) -> bool:
    """
    applies a base filter specified in a yaml config and returns a
    boolean indicating whether a (subject, from) pair passes the filter. 
    """

    ret_val = False # Default to failing if no filter logic is defined.

    for block in filter_config:
        if block["field"] == "subject":
            # check if the text is in the any, include block for that field
            if block["logic"] == "any" and block["how"] == "include":
                # simple compare
                if not ret_val:
                    ret_val = any([x.lower() in subject_text.lower() for x in block["terms"] if "*" not in x])

                # use regext for wildcard compare
                if not ret_val:
                    ret_val = any([re.findall(x.replace(" * ", ".*").lower(), subject_text.lower()) for x in block["terms"] if "*" in x])

            # check if the text is in the all, exclude block for that field.
            # all, exclude logic will override any matching includes
            if ret_val:
                if block["logic"] == "all" and block["how"] == "exclude":
                    ret_val = all([x.lower() not in subject_text.lower() for x in block["terms"]])

        if block["field"] == "from":
            # check if the text is in the any, include block for that field
            if block["logic"] == "any" and block["how"] == "include":
                # simple compare
                if not ret_val:
                    ret_val = any([x.lower() in from_text.lower() for x in block["terms"] if "*" not in x])

                # use regext for wildcard compare
                if not ret_val:
                    ret_val = any([re.findall(x.replace(" * ", ".*").lower(), from_text.lower()) for x in block["terms"] if "*" in x])

            # check if the text is in the all, exclude block for that field.
            # all, exclude logic will override any matching includes
            if ret_val:
                if block["logic"] == "all" and block["how"] == "exclude":
                    ret_val = all([x.lower() not in from_text.lower() for x in block["terms"]])

    return ret_val 

def apply_override_filter_item(text, field, filter_config) -> bool:
    """
    applies an override filter specified in a yaml config and returns a
    boolean indicating whether a (text, field) pair passes the filter. 
    """
    ret_val = False # Default to failing if no filter logic is defined.
    for block in filter_config:
        for sub_block in block:
            if sub_block["field"] == field:
                if sub_block["include_terms"] is not None:
                    for include_text in sub_block["include_terms"]:
                        if include_text.lower() in text.lower():
                            ret_val = True
                
                if sub_block["exclude_terms"] is not None:
                    for exclude_text in sub_block["exclude_terms"]:
                        if exclude_text.lower() in text.lower():
                            ret_val = False
                            #if we find a matching include, break out and return false
                            return ret_val
                        
    return ret_val

def apply_override_filter(subject_text, from_text, filter_config):
    """
    apply and logic to subject and from terms
    """
    result = apply_override_filter_item(subject_text, "subject", filter_config)
    result = result and apply_override_filter_item(from_text, "from", filter_config)

    return result