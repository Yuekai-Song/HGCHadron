# generate_jobs.py
# Generate jobs.txt for HTCondor multi-variable queue
# Each line format: ParticleId PU SampleId

# Define each group as (ParticleId, PU, SampleId start, SampleId end)
import os
import sys

num = 1
groups = [
    (211, 0, 0),
    (211, 0, 1),
]
pdgId = {22: 'photon', 211: 'pion', 11: 'electron'}
pu = ['noPU', 'PU']
sci = ['Si', 'Sci']
for grp in groups:
    os.system(f'mkdir -p {pdgId[grp[0]]}_{pu[grp[1]]}_{sci[grp[2]]}/jobs')
with open("jobs.txt", "w") as f:
    start = 1
    for particle, pu, sci in groups:
        for sample_id in range(start, start + num):
            f.write(f"{particle} {pu} {sci} {sample_id}\n")
            start += 1

total_jobs = start - 1
print(f"jobs.txt generated, total {total_jobs} lines")
