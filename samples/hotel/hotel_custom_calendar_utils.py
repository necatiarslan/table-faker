# hotel_custom_calendar_utils.py
# custom code to generate room_month and hotel_month tables based on reservation data
# These tables provide monthly aggregates of room occupancy and revenue
# They are not directly generated but derived from existing reservation and room data
# to simulate a hotel booking system's monthly performance metrics.

# This function is imported and used in hotel.yaml under the python_import key
from datetime import date, datetime
from calendar import monthrange

_CACHE = {}

def _month_floor(d: date) -> date:
    return date(d.year, d.month, 1)

def _month_add(d: date, k: int) -> date:
    y = d.year + (d.month - 1 + k) // 12
    m = (d.month - 1 + k) % 12 + 1
    return date(y, m, 1)

def _months_between(a: date, b: date) -> int:
    return (b.year - a.year) * 12 + (b.month - a.month)

def _parse(dstr: str) -> date:
    return datetime.strptime(dstr, "%Y-%m-%d").date()

def _build_room_month_index(res_rows, room_rows):
    if not res_rows:
        return []

    start = _month_floor(min(_parse(r["check_in"]) for r in res_rows))
    end   = _month_floor(max(_parse(r["check_out"]) for r in res_rows))
    nmonths = _months_between(start, end) + 1

    # index per room with revenue fields
    per_room = {}
    for r in res_rows:
        ci = _parse(r["check_in"])
        co = _parse(r["check_out"])
        subtotal = float(r.get("subtotal", 0.0))
        total_amount = float(r.get("total_amount", 0.0))
        stay_len = int(r.get("stay_length") or (co - ci).days or 1)
        rid = r["room_id"]
        per_room.setdefault(rid, []).append((ci, co, subtotal, total_amount, stay_len))

    room_to_hotel = {r["room_id"]: r["hotel_id"] for r in room_rows}

    out = []
    for room in room_rows:
        rid = room["room_id"]
        hid = room_to_hotel[rid]
        for k in range(nmonths):
            m = _month_add(start, k)
            m_start, m_end = m, _month_add(m, 1)  # [m_start, m_end)
            days = monthrange(m.year, m.month)[1]

            cnt = 0
            occupied_days = 0
            room_rev = 0.0       # subtotal
            total_rev = 0.0      # total_amount

            for ci, co, sub, tot, stay_len in per_room.get(rid, []):
                if ci < m_end and co > m_start:
                    cnt += 1
                    overlap_start = max(ci, m_start)
                    overlap_end = min(co, m_end)
                    nights = (overlap_end - overlap_start).days
                    if nights > 0:
                        occupied_days += nights
                        frac = nights / max(stay_len, 1)
                        room_rev += sub * frac
                        total_rev += tot * frac

            out.append({
                "hotel_id": hid,
                "room_id": rid,
                "month": f"{m.year:04d}-{m.month:02d}",
                "number_of_reservations": cnt,
                "occupied_days": occupied_days,
                "number_of_available_days": days,
                "room_revenue": round(room_rev, 2),
                "total_revenue": round(total_rev, 2),
            })
    return out

def _ensure(get_table):
    if "room_month" in _CACHE:
        return
    res = get_table("reservation")
    rooms = get_table("room")
    room_month = _build_room_month_index(res, rooms)
    _CACHE["room_month"] = room_month

    agg = {}
    for r in room_month:
        key = (r["hotel_id"], r["month"])
        a = agg.setdefault(key, {
            "hotel_id": r["hotel_id"],
            "month": r["month"],
            "number_of_reservations": 0,
            "occupied_days": 0,
            "room_ids": set(),
            "days": r["number_of_available_days"],
            "room_revenue": 0.0,
            "total_revenue": 0.0,
        })
        a["number_of_reservations"] += r["number_of_reservations"]
        a["occupied_days"] += r["occupied_days"]
        a["room_ids"].add(r["room_id"])
        a["room_revenue"] += r["room_revenue"]
        a["total_revenue"] += r["total_revenue"]

    hotel_month = []
    for (hid, month), v in agg.items():
        total_available = v["days"] * len(v["room_ids"]) if v["room_ids"] else 0
        hotel_month.append({
            "hotel_id": hid,
            "month": month,
            "number_of_reservations": v["number_of_reservations"],
            "occupied_days": v["occupied_days"],
            "number_of_available_days": total_available,
            "occupancy_rate": round(v["occupied_days"] / total_available * 100, 1) if total_available > 0 else 0.0,
            "room_revenue": round(v["room_revenue"], 2),
            "total_revenue": round(v["total_revenue"], 2),
        })
    _CACHE["hotel_month"] = sorted(hotel_month, key=lambda x: (x["hotel_id"], x["month"]))

def room_month_len(get_table):
    _ensure(get_table)
    return len(_CACHE.get("room_month", []))

def room_month_row(get_table, idx):
    _ensure(get_table)
    cache = _CACHE.get("room_month", [])
    if idx < 0 or idx >= len(cache):
        raise IndexError(f"room_month_row: index {idx} out of range (cache has {len(cache)} entries)")
    return cache[idx]

def hotel_month_len(get_table):
    _ensure(get_table)
    return len(_CACHE.get("hotel_month", []))

def hotel_month_row(get_table, idx):
    _ensure(get_table)
    cache = _CACHE.get("hotel_month", [])
    if idx < 0 or idx >= len(cache):
        raise IndexError(f"hotel_month_row: index {idx} out of range (cache has {len(cache)} entries)")
    return cache[idx]