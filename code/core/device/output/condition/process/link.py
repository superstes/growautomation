# operator processing for links

from core.utils.debug import debugger

LINK_ORDER_ID_1 = 1
LINK_ORDER_ID_2 = 2


def get_link_result(result_dict: dict, link) -> bool:
    if len(result_dict) != 2 or LINK_ORDER_ID_1 not in result_dict or LINK_ORDER_ID_2 not in result_dict:
        # log error or whatever
        debugger("device-output-condition-proc-link | get_link_result | link \"%s\" (id \"%s\") more or less than "
                 "2 results '%s" % (link.name, link.object_id, result_dict))
        raise ValueError("Got more/less than two results \"%s\" for link with id \"%s\"" % (result_dict, link.object_id))

    op = link.condition_operator

    debugger("device-output-condition-proc-link | get_link_result | processing link \"%s\", operator \"%s\", "
             "result dict \"%s\"" % (link.name, op, result_dict))

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
        debugger("device-output-condition-proc-link | get_link_result | link \"%s\" (id \"%s\") has an "
                 "unsupported operator '%s" % (link.name, link.object_id, op))
        raise KeyError("Link \"%s\" (id \"%s\") has an unsupported operator \"%s\""
                       % (link.name, link.object_id, link.condition_operator))

    return result


def _link_operator_not(result_dict: dict) -> bool:
    result = False

    if result_dict[LINK_ORDER_ID_1] is True and result_dict[LINK_ORDER_ID_2] is False:
        result = True

    return result


def _link_operator_and(result_dict: dict) -> bool:
    result = False

    if result_dict[LINK_ORDER_ID_1] is True and result_dict[LINK_ORDER_ID_2] is True:
        result = True

    return result


def _link_operator_or(result_dict: dict) -> bool:
    result = False

    if result_dict[LINK_ORDER_ID_1] is True or result_dict[LINK_ORDER_ID_2] is True:
        result = True

    return result


def _link_operator_xor(result_dict: dict) -> bool:
    return result_dict[LINK_ORDER_ID_1] != result_dict[LINK_ORDER_ID_2]
