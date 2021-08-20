from .template import builtins
import re
import random
from .caching import CachedObject


@builtins.register("colour_list", timeout=None)
def colour_list(request):
    return [
        'bg', 'pm', 'sh', 'sc',
        'r-bg', 'r-pm', 'r-sh', 'r-sc',
        'lt-bg', 'lt-pm', 'lt-sh', 'lt-sc',
        'dk-bg', 'dk-pm', 'dk-sh', 'dk-sc',
        'ig-blue', 'ig-pink', 'ig-purp', 'ig-oran'
    ]


builtins.register(
    "site_info",
    timeout=None,
)(
    {
        # "site_name": "Soar-Tech",
        # "currency": "$",
        "font_sizes": list(range(10)),
        # "border_radius": [
        #     "top-left", "bottom-left",
        #     "top-right", "bottom-right"
        # ],
    }
)


# @builtins.register("user_agent", timeout=60 * 60)
# def user_agent(request):
#     from django_user_agents.utils import get_user_agent
#     user_agent = get_user_agent(request)
#     default = {
#         "is_mobile": None,
#         "is_tablet": None,
#         "is_touch_capable": None,
#         "is_pc": None,
#         "is_bot": None
#     }
#     for obj in default:
#         try:
#             default[obj] = getattr(user_agent, obj)
#         except Exception:
#             continue
#     return default
