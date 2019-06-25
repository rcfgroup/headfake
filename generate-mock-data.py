from random import randint,seed, random
from faker import Faker
from faker.providers import date_time, person

import pandas as pd

# random seed
import mdconfig

# generated ID start and end points

#min/max codes to generate per person (weighted according to days since birth)

# number of patients to generate data for

# probability that patient has no data

# date range for randomised date of birth

# date range for date extracted


# file names

# randomise random number generator
seed(mdconfig.SEED)

fake = Faker()
fake.seed(mdconfig.SEED)
fake.add_provider(date_time)
fake.add_provider(person)

# load common codes and obtain total code number
codes = pd.read_csv(mdconfig.CODE_FILE,sep="\t")
#codes.sort_values
#total_code_no=codes["count"].sum()

# create search list containing expanded number of codes (e.g. if ABCD frequency=4, it is included 4 times)
search_list = []
for idx, code in codes.iterrows():
    no_codes = int(code["count"]/100)
    read_code = code["read_code"]
    search_list.extend([read_code] * no_codes)

# generate patients file
patients = []
for i in range(1, mdconfig.NO_PATIENTS):
    gender = 1 if random() > 0.5 else 2

    patients.append({
            "id":randint(mdconfig.ID_START, mdconfig.ID_END),
            "full_name":fake.name_female() if gender==1 else fake.name_male(),
            "date_of_birth":fake.date_between_dates(mdconfig.START_DOB, mdconfig.END_DOB),
            "date_extracted":fake.date_between_dates(mdconfig.START_DATE_EXTRACTED, mdconfig.END_DATE_EXTRACTED),
            "gender":gender
        })

patient_df = pd.DataFrame(patients)

patient_df.to_csv(mdconfig.OUTPUT_PATIENT_FILE, sep="\t", index=False)

# generate clinical data file

clin_data = []

for patient in patients:

    delta_date = patient["date_extracted"] - patient["date_of_birth"]
    days_since_birth = delta_date.days

    # number of codes to include is randomised based on days since birth and a min/max value
    no_codes_to_include = int(days_since_birth / randint(mdconfig.MIN_GENERATED_CODES_PER_PERSON,
                                                         mdconfig.MAX_GENERATED_CODES_PER_PERSON))

    if random() > mdconfig.PROB_NO_DATA:
        continue

    for i in range(0,no_codes_to_include):

        rnd_code = search_list[randint(0, len(search_list) - 1)]

        clin_data.append({
            "patient_id":patient["id"],
            "date_recorded":fake.date_between_dates(patient["date_of_birth"],patient["date_extracted"]),
            "read_code":rnd_code
        })

clin_df = pd.DataFrame(clin_data)

clin_df.to_csv(mdconfig.OUTPUT_CLINICAL_FILE, sep="\t", index=False)

