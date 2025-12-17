from datetime import datetime, timezone

def iso_to_xorosoft(iso_ts: str) -> str:

    dt = datetime.fromisoformat(iso_ts.replace("Z", "+00:00"))
    return dt.strftime("%m/%d/%Y %I:%M:%S %p")

def xorosoft_to_iso(xoro_ts: str) -> str:

    dt = datetime.strptime(xoro_ts, "%m/%d/%Y %I:%M:%S %p")
    dt = dt.replace(tzinfo=timezone.utc)

    return dt.isoformat(timespec="milliseconds").replace("+00:00", "Z")


