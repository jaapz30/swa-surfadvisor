#!/usr/bin/env python3
import json, sys, time, urllib.request, urllib.parse, datetime, math

LAT, LON = 52.623, 5.783  # Schokkerhaven
TZ = "Europe/Amsterdam"
FORECAST_DAYS = 7
MODELS = [
    ("NOAA GFS", "https://api.open-meteo.com/v1/gfs"),
    ("DWD ICON", "https://api.open-meteo.com/v1/dwd-icon"),
    ("ECMWF IFS", "https://api.open-meteo.com/v1/ecmwf"),
    ("Météo-France", "https://api.open-meteo.com/v1/meteofrance"),
]
INCLUDE_KNMI = True
KNMI_HOURS = 60

def fetch(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))

def build_url(base):
    p = urllib.parse.urlparse(base)
    q = {
        "latitude": LAT,
        "longitude": LON,
        "hourly": "wind_speed_10m,wind_gusts_10m,wind_direction_10m",
        "wind_speed_unit": "kn",
        "timezone": TZ,
        "forecast_days": str(FORECAST_DAYS)
    }
    u = p._replace(query=urllib.parse.urlencode(q))
    return urllib.parse.urlunparse(u)

def build_knmi_url():
    base = "https://api.open-meteo.com/v1/forecast"
    p = urllib.parse.urlparse(base)
    q = {
        "latitude": LAT, "longitude": LON,
        "hourly": "wind_speed_10m,wind_gusts_10m,wind_direction_10m",
        "wind_speed_unit": "kn", "timezone": TZ,
        "models": "knmi_seamless", "forecast_days": "4"
    }
    u = p._replace(query=urllib.parse.urlencode(q))
    return urllib.parse.urlunparse(u)

def normalize(j, model):
    t = j.get("hourly",{}).get("time",[])
    spd = j.get("hourly",{}).get("wind_speed_10m",[])
    gst = j.get("hourly",{}).get("wind_gusts_10m",[])
    dire= j.get("hourly",{}).get("wind_direction_10m",[])
    out=[]
    for i in range(min(len(t), len(spd))):
        out.append((t[i], float(spd[i]), float(gst[i] if i<len(gst) else spd[i]), float(dire[i] if i<len(dire) else 0.0), model))
    return out

def mean_dir(degs):
    if not degs: return None
    x=y=0.0
    for d in degs:
        r = math.radians(d)
        x += math.cos(r); y += math.sin(r)
    ang = math.degrees(math.atan2(y,x))
    if ang<0: ang += 360.0
    return ang

def stddev(nums):
    if len(nums)<=1: return 0.0
    m = sum(nums)/len(nums)
    v = sum((n-m)**2 for n in nums)/(len(nums)-1)
    return v**0.5

def main():
    rows=[]; used=set()
    # base models
    for name, base in MODELS:
        try:
            j = fetch(build_url(base))
            rows += normalize(j, name); used.add(name)
        except Exception as e:
            print(f"[WARN] {name}: {e}", file=sys.stderr)
    # KNMI short-range
    if INCLUDE_KNMI:
        try:
            j = fetch(build_knmi_url())
            now = datetime.datetime.now(datetime.timezone.utc)
            for (t, spd, gst, dire, _) in normalize(j, "KNMI Harmonie (NL)"):
                tt = datetime.datetime.fromisoformat(t.replace("Z","+00:00"))
                if (tt - now).total_seconds()/3600.0 <= KNMI_HOURS:
                    rows.append((t, spd, gst, dire, "KNMI Harmonie (NL)"))
                    used.add("KNMI Harmonie (NL)")
        except Exception as e:
            print(f"[WARN] KNMI: {e}", file=sys.stderr)

    # merge per time
    per = {}
    for t, spd, gst, dire, name in rows:
        per.setdefault(t, []).append((spd, gst, dire, name))
    merged=[]
    for t in sorted(per.keys()):
        arr = per[t]
        spds = [a[0] for a in arr]; gsts=[a[1] for a in arr]; dirs=[a[2] for a in arr]
        spdAvg = sum(spds)/len(spds)
        gstAvg = sum(gsts)/len(gsts) if gsts else spdAvg
        dirAvg = mean_dir(dirs) if dirs else 0.0
        stdev  = stddev(spds)
        merged.append({"t": t, "spdAvg": round(spdAvg,2), "gstAvg": round(gstAvg,2), "dirAvg": round(dirAvg,2), "stdev": round(stdev,3)})
    out = {"__models": sorted(used), "data": merged}
    with open("fallback.json","w",encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False)

if __name__=="__main__":
    main()
