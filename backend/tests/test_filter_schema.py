"""
these tests are intended to verify that the changes made to filter yamls will yield the 
desired results. Note that these tests DO NOT make any checks against functions in 
filter_utils. If you make changes there, the correct tests are found in test_filter_utils.

tests for override filters have not yet been implemented
"""

import pytest
from pathlib import Path
from typing import List
from constants import APPLIED_FILTER_PATH
from test_constants import DESIRED_PASS_APPLIED_EMAIL_FILTER_SUBJECT_FROM_PAIRS, \
    DESIRED_FAIL_APPLIED_EMAIL_FILTER_SUBJECT_FROM_PAIRS, SAMPLE_FILTER_PATH, \
    DESIRED_PASS_MANUAL_PARSE_SUBJECT_FROM_PAIRS, \
    DESIRED_FAIL_MANUAL_PARSE_SUBJECT_FROM_PAIRS, SAMPLE_OVERRIDE_FILTER_PATH
from utils.filter_utils import load_filter_config, apply_base_filter, apply_override_filter, FilterConfigType

FITLER_CONFIG_DIR = Path(__file__).parent.parent / "email_query_filters"

def get_base_filter_config_paths() -> List[Path]:
    rer_val = [SAMPLE_FILTER_PATH] + [x for x in FITLER_CONFIG_DIR.iterdir() \
        if ("override" not in str(x)) and ("manual" not in str(x))]
    return rer_val

def get_override_filter_config_paths() -> List[Path]:
    ret_val = [SAMPLE_OVERRIDE_FILTER_PATH] + [x for x in FITLER_CONFIG_DIR.iterdir() \
        if ("override" in str(x)) or ("manual" in str(x))]
    return ret_val

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

@pytest.mark.parametrize("filter_config", [load_filter_config(x) for x in get_override_filter_config_paths()])
def test_override_filter_yaml_schema(filter_config):
    """
    right now this just checks that there are no null "include_terms" fields
    """
    for block in filter_config:
        for sub_block in block:
            for key, value in sub_block.items():
                if key == "include_terms":
                    assert value is not None, "include_terms must not be NULL in an override or manual filter config."


@pytest.mark.parametrize("test_constant,filter_config,filter_type", 
                         [(DESIRED_PASS_APPLIED_EMAIL_FILTER_SUBJECT_FROM_PAIRS, APPLIED_FILTER_PATH, "base"),
                          (DESIRED_PASS_MANUAL_PARSE_SUBJECT_FROM_PAIRS, SAMPLE_OVERRIDE_FILTER_PATH, "override")])
def test_apply_email_filter_desired_pass(test_constant, filter_config, filter_type):
    """
    Tests if the desired subject, from pairs in test_constants will pass the filter

    Note that this isn't a TRUE unit test in that it does NOT test the functions 
    in utils/filter_utils. Instead, it tries to calculate whether an item will be included
    in a gmail search based on the contents of the yaml file.
    """
    filter_config = load_filter_config(filter_config)

    result_list = []
    for subject_text, from_text in test_constant:
        if filter_type == "base":
            result = apply_base_filter(subject_text, from_text, filter_config)
            result_list.append(result)
        elif filter_type == "override":
            result = apply_override_filter(subject_text, from_text, filter_config)
            result_list.append(result)

    assert all(result_list), \
        f"These subject, from pairs failed to pass: {[x for x, y in list(zip(test_constant, result_list)) if not y]}"
    
@pytest.mark.parametrize("test_constant,filter_config,filter_type", 
                         [(DESIRED_FAIL_APPLIED_EMAIL_FILTER_SUBJECT_FROM_PAIRS, APPLIED_FILTER_PATH, "base"),
                          (DESIRED_FAIL_MANUAL_PARSE_SUBJECT_FROM_PAIRS, SAMPLE_OVERRIDE_FILTER_PATH, "override")])
def test_apply_email_filter_desired_fail(test_constant, filter_config, filter_type):
    """
    Tests if the desired subject, from pairs in test_constants will pass the filter

    Note that this isn't a TRUE unit test in that it does NOT test the functions 
    in utils/filter_utils. Instead, it tries to calculate whether an item will be included
    in a gmail search based on the contents of the yaml file.
    """
    filter_config = load_filter_config(filter_config)

    result_list = []
    for subject_text, from_text in test_constant:
        if filter_type == "base":
            result = apply_base_filter(subject_text, from_text, filter_config)
            result_list.append(result)
        if filter_type == "override":
            result = apply_override_filter(subject_text, from_text, filter_config)
            result_list.append(result)

        if result:
            print(f"(subject: {subject_text}, from: {from_text} passed, which is undesired")

    assert not(any(result_list)), \
        f"These subject, from pairs failed to fail: {[x for x, y in list(zip(test_constant, result_list)) if y]}"

