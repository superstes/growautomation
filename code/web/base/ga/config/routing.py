from ..subviews.condition import ListConditionView, ListConditionLinkView
from ..subviews.group import ListGroupView
from ..subviews.default import ListView, DetailView, CreateView, UpdateView, DeleteView

group_type_list = ['connection', 'input', 'output', 'area']
group_nested_type_list = ['area']

choose_dict = {
    'list': {
        'conditiongroup': ListConditionView,
        'conditionlinkobject': ListConditionLinkView,
        '*list': {
            1: {
                'option': [f"{ typ }group" for typ in group_type_list],
                'value': ListGroupView,
            },
        },
        '*': ListView,
    },
    'detailed': {
        '*list': {
            1: {
                'option': [f"{ typ }member" for typ in group_type_list],
                'value': 'sub',
            },
            2: {
                'option': [f"{ typ }nestedgroup" for typ in group_nested_type_list],
                'value': 'sub',
            },
        },
        '*': DetailView,
    },
    'create': {
        '*': CreateView,
    },
    'update': {
        '*': UpdateView,
    },
    'delete': {
        '*': DeleteView,
    },
}

choose_sub_dict = {
    'list': {
        '*': ListView,
    },
    'detailed': {
        '*': DetailView,
    },
    'create': {
        '*': CreateView,
    },
    'update': {
        '*': UpdateView,
    },
    'delete': {
        '*': DeleteView,
    },
}
