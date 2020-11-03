# operator processing for links

from core.utils.debug import debugger


def get_link_result(result_dict: dict, link) -> bool:
    if len(result_dict) != 2:
        # log error or whatever
        debugger("device-output-condition-proc-link | _get_link_result | link '%s' more or less than 2 results '%s"
                 % (link.object_id, result_dict))
        raise ValueError("Got more than two results '%s' for link with id '%s'" % (result_dict, link.object_id))

    op = link.operator

    if op == 'and':
        result = _link_operator_and(result_dict=result_dict)
    elif op == 'nand':
        result = not _link_operator_and(result_dict=result_dict)
    elif op == 'or':
        result = _link_operator_or(result_dict=result_dict)
    elif op == 'nor':
        result = not _link_operator_or(result_dict=result_dict)
    elif op == 'not':
        result = _link_operator_not(result_dict=result_dict)
    elif op == 'xor':
        result = _link_operator_xor(result_dict=result_dict)
    elif op == 'xnor':
        result = not _link_operator_xor(result_dict=result_dict)
    else:
        # log error or whatever
        debugger("device-output-condition-proc-link | _get_link_result | link '%s' has an unsupported operator '%s"
                 % (link.object_id, op))
        raise KeyError("Link with id '%s' has an unsupported operator '%s'" % (link.object_id, link.operator))

    return result


def _link_operator_not(result_dict: dict) -> bool:
    result = False

    if result_dict[1] is True and result_dict[2] is False:
        result = True

    return result


def _link_operator_and(result_dict: dict) -> bool:
    result = False

    if result_dict[1] is True and result_dict[2] is True:
        result = True

    return result


def _link_operator_or(result_dict: dict) -> bool:
    result = False

    if result_dict[1] is True or result_dict[2] is True:
        result = True

    return result


def _link_operator_xor(result_dict: dict) -> bool:
    return result_dict[1] != result_dict[2]
