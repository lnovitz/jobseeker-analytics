"""
these tests are intended to verify that the changes made to filter yamls will yield the 
desired results. Note that these tests DO NOT make any checks against functions in 
filter_utils. If you make changes there, the correct tests are found in test_filter_utils.

tests for override filters have not yet been implemented
"""

import pytest
from pathlib import Path
import yaml
from typing import List, Dict, Union
import re
from constants import APPLIED_FILTER_PATH #, APPLIED_FILTER_OVERRIDES_PATH
from test_constants import DESIRED_PASS_APPLIED_EMAIL_FILTER_SUBJECT_FROM_PAIRS, \
    DESIRED_FAIL_APPLIED_EMAIL_FILTER_SUBJECT_FROM_PAIRS, SAMPLE_FILTER_PATH

FilterConfigType = List[Dict[str, Union[str, int, bool, list, dict]]]

FITLER_CONFIG_DIR = Path(__file__).parent.parent / "email_query_filters"

def get_base_filter_config_paths() -> List[Path]:
    return [SAMPLE_FILTER_PATH] + [x for x in FITLER_CONFIG_DIR.iterdir() if "override" not in str(x)]

def get_override_filter_config_paths() -> List[Path]:
    return [x for x in FITLER_CONFIG_DIR.iterdir() if "override" in str(x)]

def load_filter_config(filter_path: str) -> FilterConfigType:
    with open(filter_path, 'r') as fid:
        filter_config = yaml.safe_load(fid)
        return filter_config     

def validate_schema_block_order(filter_config: FilterConfigType) -> bool:
    """
    Validates that 'exclude' blocks appear after 'include' blocks in the schema.
    """

    include_seen = False
    for block in filter_config:
        how = block.get("how")
        if how == "include":
            include_seen = True
        elif how == "exclude" and not include_seen:
            return False  # Exclude block before any include block
        
    return True

@pytest.mark.parametrize("filter_config", [load_filter_config(x) for x in get_base_filter_config_paths()])
def test_base_filter_yaml_schema(filter_config):
    logic_list = [block["logic"] for block in filter_config if block["logic"]]
    how_list = [block["how"] for block in filter_config]
    exclude_terms =  sum([block["terms"] for block in filter_config if block["how"] == "exclude"], [])

    assert all( [(x == "any" and y=="include") or (x == "all" and y == "exclude") for x, y in zip(logic_list, how_list)]), \
      "logic=any is not allowed for how=exclude"
    assert all (["*" not in x for x in exclude_terms]), "wildcard is not allowed in exclude blocks"
    assert validate_schema_block_order(filter_config), "Exclude block found before an include block"

def apply_base_filter(subject_text, from_text, filter_config) -> bool:
    """Applies the YAML filter to the given text."""

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

def apply_override_filter(text, field, filter_config) -> bool:
    """Applies the YAML filter to the given text."""

    pass

@pytest.mark.parametrize("test_constant,filter_config", 
                         [(DESIRED_PASS_APPLIED_EMAIL_FILTER_SUBJECT_FROM_PAIRS, APPLIED_FILTER_PATH)])
def test_apply_email_filter_desired_pass(test_constant, filter_config):
    """
    Tests if the desired subject, from pairs in test_constants will pass the filter

    Note that this isn't a TRUE unit test in that it does NOT test the functions 
    in utils/filter_utils. Instead, it tries to calculate whether an item will be included
    in a gmail search based on the contents of the yaml file.
    """
    filter_config = load_filter_config(APPLIED_FILTER_PATH)

    result_list = []
    for subject_text, from_text in test_constant:
        result = apply_base_filter(subject_text, from_text, filter_config)
        result_list.append(result)

    assert all(result_list), \
        f"These subject, from pairs failed to pass: {[x for x, y in list(zip(test_constant, result_list)) if not y]}"
    

@pytest.mark.parametrize("test_constant,filter_config", 
                         [(DESIRED_FAIL_APPLIED_EMAIL_FILTER_SUBJECT_FROM_PAIRS, APPLIED_FILTER_PATH)])
def test_apply_email_filter_desired_fail(test_constant, filter_config):
    """
    Tests if the desired subject, from pairs in test_constants will pass the filter

    Note that this isn't a TRUE unit test in that it does NOT test the functions 
    in utils/filter_utils. Instead, it tries to calculate whether an item will be included
    in a gmail search based on the contents of the yaml file.
    """
    filter_config = load_filter_config(APPLIED_FILTER_PATH)

    result_list = []
    for subject_text, from_text in test_constant:
        result = apply_base_filter(subject_text, from_text, filter_config)
        result_list.append(result)

        if result:
            print(f"(subject: {subject_text}, from: {from_text} passed, which is undesired")

    assert not(any(result_list)), \
        f"These subject, from pairs failed to fail: {[x for x, y in list(zip(test_constant, result_list)) if y]}"
