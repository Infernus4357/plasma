import re


DEFAULT_PREFIX = "?"


MANAGER_ROLES = (1228955660058890352, 1228955733840625744)
MODERATOR_ROLES = (*MANAGER_ROLES, 1228951310544539779, 1228951428945543198)
TRIAL_MODERATOR_ROLES = (*MODERATOR_ROLES, 1228951762367680592)

COMMUNITY_SERVER_ID = 1227136991624429618
EXCLUSIVE_SERVER_ID = 1227979104486162544


TIME_REGEX = re.compile(
    r"""^\s*
        (?:(?P<years>\d+)\s*y(?:ears?)?)?\s*        # e.g. 2y,  2 years
        (?:(?P<months>\d+)\s*mo(?:nths?)?)?\s*      # e.g. 2mo, 2 months
        (?:(?P<weeks>\d+)\s*w(?:eeks?)?)?\s*        # e.g. 10w, 10 weeks
        (?:(?P<days>\d+)\s*d(?:ays?)?)?\s*          # e.g. 14d, 14 days
        (?:(?P<hours>\d+)\s*h(?:ours?)?)?\s*        # e.g. 12h, 12 hours
        (?:(?P<minutes>\d+)\s*m(?:inutes?)?)?\s*    # e.g. 10m, 10 minutes
        (?:(?P<seconds>\d+)\s*s(?:econds?)?)?\s*    # e.g. 15s, 15 seconds
        $
    """
)

TIME_UNITS = [
    ("year", "y"),
    ("month", "mo"),
    ("day", "d"),
    ("hour", "h"),
    ("minute", "m"),
    ("second", "s"),
]


EXCLUDED_PAGINATOR_BUTTONS = [
    "\N{BLACK LEFT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}\ufe0f",
    "\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}\ufe0f",
    "\N{BLACK SQUARE FOR STOP}\ufe0f",
]


AUDIT_LOG_RETRY_DELAY = 2.5
