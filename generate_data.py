"""
This is a data generator in python
Author: Khai Kieu
"""
import argparse
import csv
import os
import random
import string
from datetime import datetime, time, timedelta


CITIES = [
    ("Atlanta", "GA", "30303", "404", 30), ("Detroit", "MI", "48226", "313", 3),
    ("Chicago", "IL", "60601", "312", 6), ("New York", "NY", "10001", "212", 7),
    ("Los Angeles", "CA", "90012", "213", 5), ("Houston", "TX", "77002", "713", 4),
    ("Phoenix", "AZ", "85004", "602", 3), ("Philadelphia", "PA", "19103", "215", 3),
    ("San Antonio", "TX", "78205", "210", 2), ("San Diego", "CA", "92101", "619", 2),
    ("Dallas", "TX", "75201", "214", 4), ("Seattle", "WA", "98101", "206", 3),
    ("Denver", "CO", "80202", "303", 3), ("Boston", "MA", "02108", "617", 3),
    ("Nashville", "TN", "37203", "615", 3), ("Louisville", "KY", "40202", "502", 2),
    ("Memphis", "TN", "38103", "901", 2), ("Charlotte", "NC", "28202", "704", 3),
    ("Miami", "FL", "33131", "305", 3), ("Minneapolis", "MN", "55401", "612", 2),
    ("Portland", "OR", "97204", "503", 2), ("Salt Lake City", "UT", "84101", "801", 2),
    ("Kansas City", "MO", "64106", "816", 2), ("Columbus", "OH", "43215", "614", 2),
    ("Indianapolis", "IN", "46204", "317", 2), ("Las Vegas", "NV", "89101", "702", 2),
    ("Baltimore", "MD", "21202", "410", 2), ("Pittsburgh", "PA", "15222", "412", 2),
    ("St. Louis", "MO", "63101", "314", 2), ("Orlando", "FL", "32801", "407", 2),
]

# city, region, postal code, country
INTL = [
    ("Toronto", "ON", "M5H 2N2", "CA"), ("Vancouver", "BC", "V6B 1A1", "CA"),
    ("London", "ENG", "EC1A 1BB", "GB"), ("Mexico City", "CDMX", "06000", "MX"),
    ("Berlin", "BE", "10115", "DE"), ("Tokyo", "13", "100-0001", "JP"),
]

# Common US street names; earlier entries are drawn more often (Zipf-like)
STREETS = [
    "Peachtree St", "Main St", "Broadway", "Market St", "Oak Ave", "Washington St",
    "Park Ave", "Maple Ave", "Elm St", "Lake St", "Pine St", "Cedar St",
    "Highland Ave", "Church St", "Jefferson Ave", "Madison St", "Lincoln Ave",
    "Sunset Blvd", "Michigan Ave", "5th Ave",
]

# carrier, facility name, city, state, code
# city level only 
HUBS = [
    ("UPS", "UPS Worldport", "Louisville", "KY", "SDF"),
    ("UPS", "UPS Chicago Area Consolidation Hub", "Hodgkins", "IL", "CHI"),
    ("UPS", "UPS Philadelphia Hub", "Philadelphia", "PA", "PHL"),
    ("UPS", "UPS Ontario Hub", "Ontario", "CA", "ONT"),
    ("UPS", "UPS Dallas Hub", "Dallas", "TX", "DAL"),
    ("UPS", "UPS Columbia Hub", "Columbia", "SC", "CAE"),
    ("UPS", "UPS Atlanta Hub", "Atlanta", "GA", "ATL"),
    ("USPS", "USPS Atlanta Network Distribution Center", "Atlanta", "GA", "ATL"),
    ("USPS", "USPS Chicago Network Distribution Center", "Chicago", "IL", "CHI"),
    ("USPS", "USPS Dallas Network Distribution Center", "Dallas", "TX", "DAL"),
    ("USPS", "USPS Denver Network Distribution Center", "Denver", "CO", "DEN"),
    ("USPS", "USPS Los Angeles Network Distribution Center", "Los Angeles", "CA", "LAX"),
    ("USPS", "USPS New Jersey Network Distribution Center", "Jersey City", "NJ", "NJC"),
]
CENTRAL_HUB = {"UPS": "UPS Worldport", "USPS": "USPS Chicago Network Distribution Center"}
TRUCKS_PER_HUB = 2
PLANES_PER_CARRIER = 3

# carrier, service name, speed, typical days,  {package_type: (base, per_lb)
SERVICES = [
    ("UPS", "UPS Next Day Air", "OVERNIGHT", 1,
     {"ENVELOPE": (28.00, 0.0), "SMALL_BOX": (45.00, 3.50), "LARGE_BOX": (85.00, 4.50)}),
    ("UPS", "UPS 2nd Day Air", "TWO_DAY", 2,
     {"ENVELOPE": (18.00, 0.0), "SMALL_BOX": (28.00, 2.20), "LARGE_BOX": (55.00, 3.00)}),
    ("UPS", "UPS Ground", "STANDARD", 5,
     {"ENVELOPE": (9.00, 0.0), "SMALL_BOX": (12.00, 1.10), "LARGE_BOX": (22.00, 1.50)}),
    ("USPS", "USPS Priority Mail Express", "OVERNIGHT", 1,
     {"ENVELOPE": (30.00, 0.0), "SMALL_BOX": (40.00, 3.00), "LARGE_BOX": (75.00, 3.80)}),
    ("USPS", "USPS Priority Mail", "TWO_DAY", 2,
     {"ENVELOPE": (9.50, 0.0), "SMALL_BOX": (14.00, 1.40), "LARGE_BOX": (28.00, 1.90)}),
    ("USPS", "USPS Ground Advantage", "STANDARD", 5,
     {"ENVELOPE": (5.50, 0.0), "SMALL_BOX": (9.00, 0.90), "LARGE_BOX": (18.00, 1.20)}),
]
HAZMAT_SURCHARGE = 15.00
INTL_SURCHARGE = 25.00

HAZMAT_ITEMS = [  # real UN numbers / classes
    ("UN3481", "9", "Lithium ion batteries contained in equipment"),
    ("UN3480", "9", "Lithium ion batteries"),
    ("UN1950", "2.1", "Aerosols, flammable"),
    ("UN1266", "3", "Perfumery products"),
    ("UN1263", "3", "Paint"),
]
CUSTOMS_CONTENTS = [
    ("Clothing", 40, 400), ("Consumer electronics", 150, 1800), ("Books", 20, 200),
    ("Commercial documents", 0, 5), ("Auto parts", 60, 900), ("Medical supplies", 50, 700),
    ("Handmade gifts", 25, 250),
]

FIRST = ["James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael", "Linda",
         "David", "Elizabeth", "William", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
         "Thomas", "Sarah", "Daniel", "Karen", "Marcus", "Aaliyah", "Wei", "Priya",
         "Carlos", "Sofia", "Andre", "Keisha", "Tran", "Maria"]
LAST = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
        "Rodriguez", "Martinez", "Hernandez", "Lopez", "Wilson", "Anderson", "Thomas",
        "Taylor", "Moore", "Jackson", "Martin", "Lee", "Nguyen", "Patel", "Kim", "Harris",
        "Clark", "Lewis", "Robinson", "Walker", "Young", "Allen"]
BIZ_A = ["Peach State", "Summit", "Blue Ridge", "Capitol", "Pioneer", "Evergreen", "Liberty",
         "Keystone", "Harbor", "Lone Star", "Great Lakes", "Cardinal", "Granite", "Redwood",
         "Magnolia", "Atlas", "Northstar", "Silverline", "Bayou", "Riverbend"]
BIZ_B = ["Supply Co", "Apparel", "Electronics", "Outfitters", "Medical Supply", "Books",
         "Auto Parts", "Hardware", "Gifts", "Wholesale", "Cosmetics", "Tools", "Furniture",
         "Pharmacy", "Imports"]
CARD_BRANDS = ["Visa", "Mastercard", "Amex", "Discover"]



def wchoice(items, weights):
    return random.choices(items, weights=weights, k=1)[0]


def zipf(n, s=1.1):
    return [1.0 / ((i + 1) ** s) for i in range(n)]


def phone(area):
    return f"({area}) 555-{random.randint(100, 199):04d}"  # 555-01xx style: fictional


def ups_tracking():
    body = "".join(random.choices(string.ascii_uppercase + string.digits, k=16))
    return "1Z" + body


def usps_tracking():
    return "9400" + "".join(random.choices(string.digits, k=18))


def sql_lit(v):
    if v is None:
        return "NULL"
    if isinstance(v, datetime):
        return "'" + v.strftime("%Y-%m-%d %H:%M:%S") + "'"
    if isinstance(v, (int, float)):
        return repr(v)
    return "'" + str(v).replace("'", "''") + "'"


class Table:
    """In-memory table. If auto_id is set, add() prepends the identity value (starts at 1)."""

    def __init__(self, name, columns, auto_id=False):
        self.name, self.columns, self.auto_id, self.rows = name, columns, auto_id, []

    def add(self, *vals):
        new_id = len(self.rows) + 1
        self.rows.append(((new_id,) + vals) if self.auto_id else vals)
        return new_id


IDENTITY = {"location": "location_id", "customer": "customer_id", "recipient": "recipient_id",
            "service": "service_id", "payment_method": "payment_id", "package": "package_id",
            "tracking_event": "event_id", "delivery": "delivery_id"}

# the generator
def generate(n_customers, n_recipients, n_packages, now):
    T = {n: Table(n, c, auto_id=(n in IDENTITY)) for n, c in {
        "location": ["location_id", "location_type", "name", "carrier", "street_number",
                     "street_name", "city", "state_province", "postal_code", "country"],
        "customer": ["customer_id", "name", "phone", "customer_type", "address_location_id"],
        "recipient": ["recipient_id", "name", "phone", "address_location_id"],
        "service": ["service_id", "carrier", "service_name", "speed", "typical_days"],
        "service_rate": ["service_id", "package_type", "base_price", "per_lb"],
        "payment_method": ["payment_id", "customer_id", "method_type", "account_number",
                           "card_brand", "card_last4"],
        "package": ["package_id", "tracking_number", "sender_id", "recipient_id", "service_id",
                    "payment_id", "package_type", "weight_lb", "declared_value", "ship_date",
                    "charge"],
        "tracking_event": ["event_id", "package_id", "location_id", "event_type", "event_time"],
        "delivery": ["delivery_id", "package_id", "vehicle_location_id", "promised_at",
                     "delivered_at", "signed_by"],
        "hazmat_detail": ["package_id", "un_number", "hazard_class", "proper_shipping_name"],
        "customs_declaration": ["package_id", "contents", "declared_value", "origin_country",
                                "destination_country"],
    }.items()}

    #  services & rates
    service_info = {}  # service_id -> (carrier, speed, days, rates)
    services_by_carrier = {"UPS": [], "USPS": []}
    for carrier, sname, speed, days, rates in SERVICES:
        sid = T["service"].add(carrier, sname, speed, days)
        for ptype, (base, per_lb) in rates.items():
            T["service_rate"].add(sid, ptype, base, per_lb)
        service_info[sid] = (carrier, speed, days, rates)
        services_by_carrier[carrier].append(sid)

    # warehouses (hubs), trucks, planes
    def add_loc(ltype, name=None, carrier=None, num=None, street=None, city=None,
                state=None, zipc=None, country="US"):
        lid = len(T["location"].rows) + 1
        T["location"].rows.append((lid, ltype, name, carrier, num, street, city, state,
                                   zipc, country))
        return lid

    hubs = {"UPS": [], "USPS": []}   # (loc_id, state, [truck ids])
    for carrier, fname, city, state, code in HUBS:
        hid = add_loc("WAREHOUSE", fname, carrier, city=city, state=state)
        trucks = [add_loc("TRUCK", f"{carrier}-{code}-T{i}", carrier, city=city, state=state)
                  for i in range(1, TRUCKS_PER_HUB + 1)]
        hubs[carrier].append((hid, state, fname, trucks))
    planes = {c: [add_loc("PLANE", f"{c}-AIR-{i:02d}", c) for i in range(1, PLANES_PER_CARRIER + 1)]
              for c in ("UPS", "USPS")}

    def hub_for(carrier, state):
        same = [h for h in hubs[carrier] if h[1] == state]
        if same:
            return random.choice(same)
        return next(h for h in hubs[carrier] if h[2] == CENTRAL_HUB[carrier])

    # address factory
    city_w = [c[4] for c in CITIES]
    street_w = zipf(len(STREETS))

    def new_us_address():
        city, state, zipc, area, _ = wchoice(CITIES, city_w)
        street = wchoice(STREETS, street_w)
        lid = add_loc("ADDRESS", num=str(random.randint(100, 9999)), street=street,
                      city=city, state=state, zipc=zipc)
        return lid, area, state

    def new_intl_address():
        city, region, postal, country = random.choice(INTL)
        lid = add_loc("ADDRESS", num=str(random.randint(1, 250)),
                      street=random.choice(["High St", "King St", "Queen St", "Station Rd"]),
                      city=city, state=region, zipc=postal, country=country)
        return lid, country

    # customers + payment methods
    n_contract = int(n_customers * 0.30)
    n_prepaid = int(n_customers * 0.15)
    types = (["CONTRACT"] * n_contract + ["PREPAID"] * n_prepaid +
             ["CREDIT_CARD"] * (n_customers - n_contract - n_prepaid))
    random.shuffle(types)
    cust_weight, cust_payment, cust_state = {}, {}, {}
    used_biz = set()
    for ctype in types:
        lid, area, state = new_us_address()
        if ctype == "CONTRACT":
            while True:
                nm = f"{random.choice(BIZ_A)} {random.choice(BIZ_B)}"
                if nm not in used_biz:
                    used_biz.add(nm)
                    break
        else:
            nm = f"{random.choice(FIRST)} {random.choice(LAST)}"
        cid = T["customer"].add(nm, phone(area), ctype, lid)
        if ctype == "CONTRACT":
            acct = "".join(random.choices(string.digits, k=9))
            pid = T["payment_method"].add(cid, "ACCOUNT", acct, None, None)
            cust_weight[cid] = random.uniform(8, 40)
        elif ctype == "CREDIT_CARD":
            pid = T["payment_method"].add(cid, "CREDIT_CARD", None,
                                          random.choice(CARD_BRANDS), f"{random.randint(0, 9999):04d}")
            cust_weight[cid] = random.uniform(0.5, 4)
        else:  # PREPAID sender, e.g. a product return label
            code = "PP-" + "".join(random.choices(string.digits, k=8))
            pid = T["payment_method"].add(cid, "PREPAID", code, None, None)
            cust_weight[cid] = random.uniform(0.3, 2)
        cust_payment[cid] = pid
    cust_ids = list(cust_weight)

    # recipients (about 4% international)
    recipients = []  # (recipient_id, state or None, country)
    for _ in range(n_recipients):
        nm = f"{random.choice(FIRST)} {random.choice(LAST)}"
        if random.random() < 0.04:
            lid, country = new_intl_address()
            rid = T["recipient"].add(nm, None, lid)
            recipients.append((rid, lid, None, country))
        else:
            lid, area, state = new_us_address()
            ph = phone(area)
            rid = T["recipient"].add(nm, ph, lid)
            recipients.append((rid, lid, state, "US"))
    cust_loc = {r[0]: r[4] for r in T["customer"].rows}
    loc_state = {r[0]: r[7] for r in T["location"].rows}

    # packages, events, deliveries, special handling
    ptype_choices = ["ENVELOPE", "SMALL_BOX", "LARGE_BOX"]
    ptype_w = [25, 45, 30]
    speed_w = {"OVERNIGHT": 20, "TWO_DAY": 25, "STANDARD": 55}
    used_tn = set()
    cust_w = [cust_weight[c] for c in cust_ids]

    for _ in range(n_packages):
        cid = wchoice(cust_ids, cust_w)
        rid, rloc, rstate, rcountry = random.choice(recipients)
        intl = rcountry != "US"
        carrier = random.choice(["UPS", "USPS"])
        sids = services_by_carrier[carrier]
        sid = wchoice(sids, [speed_w[service_info[s][1]] for s in sids])
        _, speed, days, rates = service_info[sid]
        ptype = wchoice(ptype_choices, ptype_w)
        weight = {"ENVELOPE": round(random.uniform(0.1, 1.0), 2),
                  "SMALL_BOX": round(random.uniform(1.0, 10.0), 2),
                  "LARGE_BOX": round(random.uniform(10.0, 50.0), 2)}[ptype]
        declared = round({"ENVELOPE": random.uniform(0, 100),
                          "SMALL_BOX": random.uniform(20, 500),
                          "LARGE_BOX": random.uniform(50, 2000)}[ptype], 2)
        hazmat = (not intl) and ptype != "ENVELOPE" and random.random() < 0.04
        base, per_lb = rates[ptype]
        charge = round(base + per_lb * weight + (HAZMAT_SURCHARGE if hazmat else 0)
                       + (INTL_SURCHARGE if intl else 0), 2)

        # ship time: random day in the past year, business hours
        d = (now - timedelta(days=int(random.random() * 365))).date()
        ship_dt = datetime.combine(d, time(random.randint(9, 17), random.randint(0, 59)))
        if ship_dt > now:
            ship_dt = now - timedelta(minutes=random.randint(30, 300))

        # promised time
        if speed == "OVERNIGHT":
            promised = datetime.combine(ship_dt.date() + timedelta(days=1), time(10, 30))
        elif speed == "TWO_DAY":
            promised = datetime.combine(ship_dt.date() + timedelta(days=2), time(17, 0))
        else:
            promised = datetime.combine(ship_dt.date() + timedelta(days=random.randint(3, 5)),
                                        time(20, 0))
        if intl:
            promised += timedelta(days=3)

        # actual delivery: ~12% late
        if random.random() < 0.12:
            delivered = promised + timedelta(hours=random.uniform(1, 36))
        else:
            delivered = promised - timedelta(hours=random.uniform(0, 8))
        delivered = max(delivered, ship_dt + timedelta(hours=12)).replace(microsecond=0, second=0)

        # tracking number
        while True:
            tn = ups_tracking() if carrier == "UPS" else usps_tracking()
            if tn not in used_tn:
                used_tn.add(tn)
                break

        pkg_id = T["package"].add(tn, cid, rid, sid, cust_payment[cid], ptype, weight,
                                  declared, ship_dt.date(), charge)

        # route
        origin_state = loc_state[cust_loc[cid]]
        origin_hub = hub_for(carrier, origin_state)
        if intl:
            plane = random.choice(planes[carrier])
            steps = [("PICKED_UP", cust_loc[cid]), ("SCANNED", origin_hub[0]),
                     ("LOADED", plane), ("DELIVERED", rloc)]
            fracs = [0, 0.08, 0.20, 1.0]
            dest_truck = None
        else:
            dest_hub = hub_for(carrier, rstate)
            dest_truck = random.choice(dest_hub[3])
            if speed != "STANDARD" and origin_hub[0] != dest_hub[0]:
                vehicle = random.choice(planes[carrier])
            else:
                vehicle = random.choice(origin_hub[3])
            steps = [("PICKED_UP", cust_loc[cid]), ("SCANNED", origin_hub[0]),
                     ("LOADED", vehicle), ("ARRIVED", dest_hub[0]),
                     ("LOADED", dest_truck), ("OUT_FOR_DELIVERY", dest_truck),
                     ("DELIVERED", rloc)]
            fracs = [0, 0.07, 0.18, 0.55, 0.78, 0.88, 1.0]

        total = (delivered - ship_dt).total_seconds()
        times = []
        for i, f in enumerate(fracs):
            jitter = 0 if i in (0, len(fracs) - 1) else random.uniform(-0.02, 0.02) * total
            t = (ship_dt + timedelta(seconds=f * total + jitter)).replace(second=0, microsecond=0)
            if times and t <= times[-1]:
                t = times[-1] + timedelta(minutes=1)
            times.append(t)
        times[-1] = max(times[-1], delivered)

        done = times[-1] <= now
        for (etype, lid), t in zip(steps, times):
            if t <= now:
                T["tracking_event"].add(pkg_id, lid, etype, t)

        if done:
            rec_name = next(r[1] for r in T["recipient"].rows if r[0] == rid)
            signer = random.choices([rec_name, "Front desk", "Receptionist", "Left at door"],
                                    weights=[70, 12, 10, 8])[0]
            T["delivery"].add(pkg_id, dest_truck, promised, times[-1], signer)

        if hazmat:
            un, cls, nm = random.choice(HAZMAT_ITEMS)
            T["hazmat_detail"].add(pkg_id, un, cls, nm)
        if intl:
            what, lo, hi = random.choice(CUSTOMS_CONTENTS)
            T["customs_declaration"].add(pkg_id, what, round(random.uniform(lo, hi), 2),
                                         "US", rcountry)
    return T



LOAD_ORDER = ["location", "customer", "recipient", "service", "service_rate", "payment_method",
              "package", "tracking_event", "delivery", "hazmat_detail", "customs_declaration"]


def write_outputs(T, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "seed.sql"), "w") as f:
        f.write("-- Generated by generate_data.py. Run schema.sql first.\nBEGIN;\n")
        for name in LOAD_ORDER:
            t = T[name]
            cols = ", ".join(t.columns)
            for i in range(0, len(t.rows), 500):
                chunk = t.rows[i:i + 500]
                vals = ",\n  ".join("(" + ", ".join(sql_lit(v) for v in r) + ")" for r in chunk)
                f.write(f"INSERT INTO {name} ({cols}) VALUES\n  {vals};\n")
        for name, col in IDENTITY.items():
            f.write(f"SELECT setval(pg_get_serial_sequence('{name}','{col}'), "
                    f"(SELECT MAX({col}) FROM {name}));\n")
        f.write("COMMIT;\n")
    for name in LOAD_ORDER:
        t = T[name]
        with open(os.path.join(out_dir, f"{name}.csv"), "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(t.columns)
            w.writerows(["" if v is None else v for v in r] for r in t.rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=4710)
    ap.add_argument("--customers", type=int, default=120)
    ap.add_argument("--recipients", type=int, default=400)
    ap.add_argument("--packages", type=int, default=2500)
    ap.add_argument("--out", default="data")
    ap.add_argument("--dsn", help="optional psycopg2 DSN: load seed.sql directly")
    args = ap.parse_args()

    random.seed(args.seed)
    now = datetime.now().replace(second=0, microsecond=0)
    T = generate(args.customers, args.recipients, args.packages, now)
    write_outputs(T, args.out)

    print(f"Generated at {now:%Y-%m-%d %H:%M}. Row counts:")
    for name in LOAD_ORDER:
        print(f"  {name:20s} {len(T[name].rows):>7d}")
    print(f"Wrote {args.out}/seed.sql and one CSV per table.")

    if args.dsn:
        import psycopg2  # pip install psycopg2-binary
        with psycopg2.connect(args.dsn) as conn, conn.cursor() as cur:
            cur.execute(open(os.path.join(args.out, "seed.sql")).read())
        print("Loaded into database.")


if __name__ == "__main__":
    main()
