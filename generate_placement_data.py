from pathlib import Path
Path("data").mkdir(exist_ok=True)

import random
import numpy as np
import pandas as pd

random.seed(42)
np.random.seed(42)

BRANCHES = {"CSE": 30, "ISE": 20, "ECE": 18, "AIML": 12, "EEE": 8, "ME": 7, "CV": 5}
BRANCH_CODES = list(BRANCHES.keys())
BRANCH_WEIGHTS = np.array([BRANCHES[b] for b in BRANCH_CODES], dtype=float)
BRANCH_WEIGHTS /= BRANCH_WEIGHTS.sum()
BRANCH_CGPA_SHIFT = {"CSE": 0.15, "ISE": 0.10, "AIML": 0.10, "ECE": 0.0,
 "EEE": -0.05, "ME": -0.05, "CV": -0.05}
GRAD_YEARS = [2024, 2025, 2026]
STUDENTS_PER_YEAR = 200
FIRST_NAMES = [
 "Aarav","Vivaan","Aditya","Vihaan","Arjun","Sai","Reyansh","Krishna","Ishaan","Rohan",
 "Karthik","Nikhil","Siddharth","Varun","Akash","Rahul","Manoj","Suresh","Ganesh","Ajay",
 "Ananya","Diya","Ishita","Kavya","Meera","Priya","Riya","Sneha","Tanvi","Trisha",
 "Aishwarya","Divya","Lakshmi","Pooja","Ramya","Sanjana","Shreya","Swathi","Varsha","Nandini",
 "Mohammed","Fatima","Zara","Arnav","Advait","Devansh","Harsha","Kiran","Naveen","Prajwal",
 "Chirag","Deepak","Girish","Harish","Jagdish","Lokesh","Mahesh","Naresh","Pavan","Raghav",
 "Anjali","Bhavya","Chaitra","Deepika","Gayatri","Harini","Kavita","Madhuri","Nisha","Ojasvi",
]
LAST_NAMES = [
 "Sharma","Gupta","Reddy","Rao","Iyer","Iyengar","Nair","Menon","Pillai","Shetty",
 "Kumar","Kulkarni","Deshpande","Joshi","Patil","Naik","Hegde","Bhat","Kamath","Gowda",
 "Murthy","Prasad","Verma","Singh","Yadav","Mishra","Pandey","Agarwal","Jain","Chowdhury",
 "Krishnan","Subramaniam","Raghavan","Venkatesh","Balakrishnan","Ramesh","Suresh",
 "Mahadev","Achar","Bhandari",
]

def make_name(used):
 for _ in range(20):
 name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
 if used[name] < 2:
 used[name] += 1
 return name
 used[name] += 1
 return name

def sample_cgpa(branch):
 raw = np.random.beta(2.6, 2.0)
 cgpa = 5.0 + raw * 5.0 + BRANCH_CGPA_SHIFT.get(branch, 0.0) + np.random.normal(0, 0.15)
 return float(np.clip(round(cgpa, 2), 5.0, 9.8))

# --- STUDENTS ---
students_rows = []
used_names = __import__("collections").defaultdict(int)
sid_counter = 1
for grad_year in GRAD_YEARS:
 branches = np.random.choice(BRANCH_CODES, size=STUDENTS_PER_YEAR, p=BRANCH_WEIGHTS)
 for branch in branches:
 students_rows.append({
 "student_id": f"STU{sid_counter:05d}",
 "name": make_name(used_names),
 "branch": branch,
 "batch_year": int(grad_year),
 "cgpa": sample_cgpa(branch),
 "backlogs": 0 if random.random() < 0.82 else random.choice([1, 1, 2, 3]),
 "gender": random.choice(["M", "F"]),
 })
 sid_counter += 1

# --- COMPANIES ---
COMPANIES_RAW = [
 ("Microsoft India","Product",1),("Amazon","Product",1),("Google","Product",1),
 ("Adobe","Product",1),("Goldman Sachs","Finance",1),("JP Morgan Chase","Finance",1),
 ("Walmart Global Tech","Product",1),("Cisco Systems","Product",1),
 ("Qualcomm","Semiconductor",1),("Intuit","Product",1),("Salesforce","Product",1),
 ("Uber","Product",1),("Flipkart","Product",2),("Swiggy","Product",2),
 ("Myntra","Product",2),("Razorpay","Fintech",2),("Zoho Corporation","Product",2),
 ("Freshworks","Product",2),("PhonePe","Fintech",2),("SAP Labs India","Product",2),
 ("VMware","Product",2),("Intel","Semiconductor",2),("Texas Instruments","Semiconductor",2),
 ("Bosch Global Software","Core Engineering",2),("Siemens","Core Engineering",2),
 ("Deloitte","Consulting",2),("EY","Consulting",2),("Accenture Digital","Consulting",2),
 ("ThoughtWorks","IT Services",2),("Morgan Stanley","Finance",2),
 ("Tata Consultancy Services","IT Services",3),("Infosys","IT Services",3),
 ("Wipro","IT Services",3),("Cognizant","IT Services",3),("Capgemini","IT Services",3),
 ("HCLTech","IT Services",3),("Tech Mahindra","IT Services",3),
 ("Mindtree","IT Services",3),("L&T Technology Services","Core Engineering",3),
 ("Tata Motors","Core Engineering",3),("Ashok Leyland","Core Engineering",3),
 ("Bharat Electronics Limited","Core Engineering",3),("Toyota Kirloskar","Core Engineering",3),
 ("Mercedes-Benz R&D India","Core Engineering",2),("UST Global","IT Services",3),
 ("Persistent Systems","IT Services",3),("LTIMindtree","IT Services",3),
 ("Hexaware Technologies","IT Services",3),
]
TIER_CGPA_CUTOFF = {1: 8.0, 2: 7.0, 3: 6.0}
TIER_CTC_RANGE = {1: (18, 45), 2: (9, 16), 3: (3.5, 7.5)}

companies_rows = []
for i, (name, sector, tier) in enumerate(COMPANIES_RAW, start=1):
 companies_rows.append({
 "company_id": f"CMP{i:03d}",
 "company_name": name,
 "sector": sector,
 "tier": tier,
 "base_cgpa_cutoff": TIER_CGPA_CUTOFF[tier],
 })
companies_df = pd.DataFrame(companies_rows)

# --- DRIVES ---
ROLE_TYPES_BY_SECTOR = {
 "Product": ["Software Development", "Software Development", "Data Science"],
 "IT Services": ["Software Development", "System Engineer", "Software Development"],
 "Finance": ["Analyst", "Software Development"],
 "Fintech": ["Software Development", "Analyst"],
 "Consulting": ["Analyst", "Consultant"],
 "Core Engineering": ["Core Engineering", "Core Engineering", "Software Development"],
 "Semiconductor": ["Core Engineering", "Software Development"],
}
DRIVE_MONTHS = [7, 8, 9, 10, 11, 12, 1, 2]

def eligible_branches_for(sector, role_type):
 if role_type == "Core Engineering":
 return random.choice([["ME", "CV"], ["ME", "EEE"], ["ME", "CV", "EEE"]])
 if role_type in ("Analyst", "Consultant"):
 return random.sample(BRANCH_CODES, k=random.randint(4, len(BRANCH_CODES)))
 if random.random() < 0.5:
 return BRANCH_CODES.copy()
 return list({"CSE", "ISE", "ECE", "AIML"} | set(random.sample(BRANCH_CODES, k=2)))

drives_rows = []
drive_counter = 1
for _, comp in companies_df.iterrows():
 n_years = random.choice([1, 2, 2, 3, 3, 3])
 years = random.sample(GRAD_YEARS, k=min(n_years, len(GRAD_YEARS)))
 for year in years:
 role_type = random.choice(ROLE_TYPES_BY_SECTOR[comp["sector"]])
 branches = eligible_branches_for(comp["sector"], role_type)
 cutoff = float(np.clip(round(comp["base_cgpa_cutoff"] + random.uniform(-0.3, 0.3), 2), 5.5, 9.0))
 lo, hi = TIER_CTC_RANGE[comp["tier"]]
 ctc = round(random.uniform(lo, hi), 1)
 if role_type == "Data Science":
 ctc = round(ctc * random.uniform(1.05, 1.25), 1)
 if role_type == "Core Engineering":
 ctc = round(ctc * random.uniform(0.8, 0.95), 1)
 drives_rows.append({
 "drive_id": f"DRV{drive_counter:04d}",
 "company_id": comp["company_id"],
 "year": int(year),
 "month": random.choice(DRIVE_MONTHS),
 "role_type": role_type,
 "eligible_branches": ",".join(sorted(branches)),
 "cgpa_cutoff": cutoff,
 "ctc_lpa": ctc,
 })
 drive_counter += 1
drives_df = pd.DataFrame(drives_rows)

# --- OFFERS ---
offers_rows = []
offer_counter = 1
offers_by_student = {r["student_id"]: 0 for _, r in pd.DataFrame(students_rows).iterrows()}
students_by_year = {y: [r for r in students_rows if r["batch_year"] == y] for y in GRAD_YEARS}

for _, drive in drives_df.iterrows():
 comp = companies_df[companies_df["company_id"] == drive["company_id"]].iloc[0]
 pool = students_by_year[drive["year"]]
 branches = drive["eligible_branches"].split(",")
 eligible = [s for s in pool
 if s["branch"] in branches
 and s["cgpa"] >= drive["cgpa_cutoff"]
 and s["backlogs"] == 0
 and offers_by_student[s["student_id"]] < 2]
 if not eligible:
 continue
 lo, hi = {1: (3, 10), 2: (5, 20), 3: (15, 60)}[comp["tier"]]
 n_hires = min(len(eligible), random.randint(lo, hi))
 if n_hires <= 0:
 continue
 weights = np.exp([(s["cgpa"] - drive["cgpa_cutoff"]) * 1.8 for s in eligible])
 weights = weights / weights.sum()
 chosen = np.random.choice(eligible, size=n_hires, replace=False, p=weights)
 for stu in chosen:
 pkg = round(drive["ctc_lpa"] * random.uniform(0.9, 1.12), 2)
 offers_rows.append({
 "offer_id": f"OFR{offer_counter:05d}",
 "student_id": stu["student_id"],
 "drive_id": drive["drive_id"],
 "offer_year": int(drive["year"]),
 "offer_month": int(drive["month"]),
 "package_lpa": pkg,
 "status": np.random.choice(["Accepted", "Declined", "Pending"], p=[0.78, 0.14, 0.08]),
 })
 offer_counter += 1
 offers_by_student[stu["student_id"]] += 1

offers_df = pd.DataFrame(offers_rows)

# --- WRITE TO DATABRICKS TABLES ---
spark.createDataFrame(students_df).write.mode("overwrite").saveAsTable("workspace.default.students")
spark.createDataFrame(companies_df).write.mode("overwrite").saveAsTable("workspace.default.companies")
spark.createDataFrame(drives_df).write.mode("overwrite").saveAsTable("workspace.default.drives")
spark.createDataFrame(offers_df).write.mode("overwrite").saveAsTable("workspace.default.offers")

print("Done!")
print(f"Students: {len(students_df)}")
print(f"Companies: {len(companies_df)}")
print(f"Drives: {len(drives_df)}")
print(f"Offers: {len(offers_df)}")
