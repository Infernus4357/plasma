import asyncio
import datetime

from dateutil.relativedelta import relativedelta

from .constants import AUDIT_LOG_RETRY_DELAY, TIME_UNITS


# fmt: off

async def fetch_recent_audit_log_entry(guild, *, target=None, action=None, retry=0):
    while retry >= 0:
        async for entry in guild.audit_logs(limit=1, action=action):
            delta = datetime.datetime.now(datetime.timezone.utc) - entry.created_at
            if delta < datetime.timedelta(seconds=10) and (target is None or entry.target == target):
                return entry
            
        await asyncio.sleep(AUDIT_LOG_RETRY_DELAY)
        retry -= 1

    return None

# fmt: on


class Plural:
    def __init__(self, value):
        self.value = value

    def __format__(self, format_spec):
        singular, _, plural = format_spec.partition("|")

        if not plural:
            plural = f"{singular}s"

        suffix = plural if abs(self.value) != 1 else singular
        return f"{self.value} {suffix}"


def human_join(seq, *, delimiter=", ", final="and"):
    if not seq:
        return ""

    if len(seq) == 1:
        return str(seq[0])

    return f"{delimiter.join(map(str, seq[:-1]))} {final} {seq[-1]}"


def human_timedelta(end, *, reference=None, accuracy=3, brief=False, suffix=True):
    now = reference or datetime.datetime.now(datetime.timezone.utc)

    if isinstance(end, datetime.timedelta):
        end = now + end

    now = now.replace(tzinfo=now.tzinfo or datetime.timezone.utc, microsecond=0)
    end = end.replace(tzinfo=end.tzinfo or datetime.timezone.utc, microsecond=0)

    if end > now:
        delta = relativedelta(end, now)
        affix = ""
    else:
        delta = relativedelta(now, end)
        affix = " ago" if suffix else ""

    result = []
    for unit, brief_unit in TIME_UNITS:
        value = getattr(delta, unit + "s")
        if value <= 0:
            continue

        if unit == "day":
            weeks = delta.weeks
            if weeks:
                value -= weeks * 7
                result.append(f"{weeks}w" if brief else format(Plural(weeks), "week"))

        if value > 0:
            result.append(
                f"{value}{brief_unit}" if brief else format(Plural(value), unit)
            )

    if accuracy:
        result = result[:accuracy]

    if not result:
        return "now"

    return " ".join(result) + affix if brief else human_join(result) + affix
