"""Bihar district CSR data.

CSR spend (Rs crore): MCA via Rajya Sabha Unstarred Q.1010, 9 Dec 2025 (data to 31 Mar 2025).
Population: Census of India 2011 (via Wikipedia, List of districts of Bihar).
None = no CSR recorded ("-") in the source table.
Aspirational = NITI Aayog Aspirational Districts Programme. Flood belt = Kosi-Seemanchal.
"""
YEARS = ["FY 2020-21", "FY 2021-22", "FY 2022-23", "FY 2023-24"]
STATE_TOTAL = [89.89, 178.97, 241.41, 260.53]
UNATTRIBUTED = [39.35, 29.22, 12.64, 16.41]
PSU = [7.51, 56.48, 110.29, 91.13]
NON_PSU = [82.38, 122.50, 131.12, 169.40]
BIHAR_POP = 104099452  # Census 2011

ASPIRATIONAL = {"Araria", "Aurangabad", "Banka", "Begusarai", "Gaya", "Jamui", "Katihar", "Khagaria",
                "Muzaffarpur", "Nawada", "Purnia", "Sheikhpura", "Sitamarhi"}
FLOOD_BELT = {"Araria", "Katihar", "Kishanganj", "Purnia", "Saharsa", "Supaul", "Madhepura"}

# name, population (2011), [FY21, FY22, FY23, FY24]
DISTRICTS = [
    ("Araria", 2811569, [0.01, 7.73, 7.13, 1.16]),
    ("Arwal", 699000, [None, None, None, None]),
    ("Aurangabad", 2540073, [1.48, 4.64, 12.04, 10.63]),
    ("Banka", 2034763, [0.03, 0.68, 7.50, 0.15]),
    ("Begusarai", 2970541, [3.53, 8.90, 18.11, 20.09]),
    ("Bhagalpur", 3037766, [0.88, 1.11, 9.01, 12.86]),
    ("Bhojpur", 2728407, [5.44, 2.06, 12.81, 19.31]),
    ("Buxar", 1706352, [0.84, 0.51, 1.23, 0.34]),
    ("Darbhanga", 3937385, [1.62, 5.40, 12.06, 10.69]),
    ("Gaya", 4391418, [1.68, 6.11, 5.78, 13.51]),
    ("Gopalganj", 2562012, [0.17, 0.61, 1.11, 1.25]),
    ("Jamui", 1760405, [0.36, 0.69, 8.93, 4.49]),
    ("Jehanabad", 1125313, [0.34, 0.29, 1.40, 8.49]),
    ("Kaimur", 1626384, [0.00, 0.34, 0.02, 0.10]),
    ("Katihar", 3071029, [0.23, 0.80, 0.09, 0.54]),
    ("Khagaria", 1666886, [0.00, 1.42, 3.53, 0.50]),
    ("Kishanganj", 1690400, [1.15, 2.99, 38.36, 0.70]),
    ("Lakhisarai", 1000912, [0.10, None, 0.24, 0.06]),
    ("Madhepura", 2001762, [0.50, 0.31, 0.09, 1.59]),
    ("Madhubani", 4487379, [0.15, 0.18, 0.68, 3.36]),
    ("Munger", 1367765, [0.26, 0.78, 3.84, 4.03]),
    ("Muzaffarpur", 4801062, [5.55, 9.83, 10.09, 52.00]),
    ("Nalanda", 2877653, [1.89, 3.03, 3.58, 4.56]),
    ("Nawada", 2219146, [None, 0.34, 1.67, 2.24]),
    ("Pashchim Champaran", 3935042, [0.65, 39.73, 1.36, 4.75]),
    ("Patna", 5838465, [16.86, 35.39, 27.17, 38.72]),
    ("Purbi Champaran", 5099371, [0.20, 0.77, 1.61, 2.83]),
    ("Purnia", 3264619, [0.14, 1.19, 12.10, 2.02]),
    ("Rohtas", 2959918, [0.27, None, 0.63, 0.58]),
    ("Saharsa", 1900661, [None, 0.29, 0.26, 0.32]),
    ("Samastipur", 4261566, [0.82, 6.15, 6.89, 7.33]),
    ("Saran", 3951862, [0.76, 3.75, 10.92, 3.57]),
    ("Sheikhpura", 634927, [None, 1.07, 2.31, 1.94]),  # source row lists 3 values; year totals confirm FY21 is the blank
    ("Sheohar", 656246, [0.00, 0.03, 0.00, 0.15]),
    ("Sitamarhi", 3423574, [1.77, 1.81, 3.51, 2.74]),
    ("Siwan", 3330464, [0.55, None, 0.76, 0.46]),
    ("Supaul", 2229076, [None, 0.00, 0.28, 2.59]),
    ("Vaishali", 3495021, [2.30, 0.82, 1.69, 3.48]),
]

def slug(name):
    return name.lower().replace(" ", "-")

def v(x):
    return x or 0.0

def rows():
    out = []
    for name, pop, s in DISTRICTS:
        tot = sum(v(x) for x in s)
        out.append(dict(name=name, slug=slug(name), pop=pop, series=s, fy24=v(s[3]), total=tot,
                        pc24=v(s[3]) * 1e7 / pop, pc4=tot * 1e7 / pop,
                        aspirational=name in ASPIRATIONAL, flood=name in FLOOD_BELT))
    for key, rk in (("fy24", "rank24"), ("pc24", "rankpc"), ("total", "ranktot")):
        for i, r in enumerate(sorted(out, key=lambda r: -r[key])):
            r[rk] = i + 1
    return out
