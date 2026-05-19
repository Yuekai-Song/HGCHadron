import os
import glob
import argparse
import shutil
import re

# 1. Set command line arguments
parser = argparse.ArgumentParser(description='Generate modified step3.py and jobs.txt')
parser.add_argument('--job-dir', type=str, default='pion_PU', help='where the step2 files are')
# parser.add_argument('--dfh', type=float, default=1.3, help='deltac_si parameter at FH')
parser.add_argument('--dsi', type=float, default=1.3, help='deltac_si parameter')
parser.add_argument('--dsci', type=float, default=0.0315, help='deltac_sci parameter')
parser.add_argument('--outdir', '-o', type=str, required=True, help='Output directory name')
parser.add_argument('--step3', type=str, default='step3.py', help='Path to original step3.py')
parser.add_argument('--clean', action='store_true', default=False, help='clean jobs.txt')
parser.add_argument('--maxnum', type=int, default=100, help='max job nums')
args = parser.parse_args()

deltac_si = args.dsi
deltac_sci = args.dsci
# deltac_fh = args.dfh
outdir = args.outdir
step3_path = args.step3

default_dee = 1.3
# default_dfh = 1.3
default_dsci = 0.0315
default_dsi = 1.3

if 'Sci' in args.job_dir:
    maxEne = 3000.0
else:
    maxEne = 5000.0 
# 2. Create output directory if it does not exist
os.makedirs(outdir, exist_ok=True)
os.makedirs(os.path.join(outdir, 'jobs'), exist_ok=True)
os.makedirs(os.path.join(outdir, 'logs'), exist_ok=True)
# 3. Read original step3.py
with open(step3_path, 'r') as f:
    content = f.read()

# 4. Prepare edit lines
edit_lines = [
    # f'process.hgcalLayerClustersHFNose.plugin.deltac = cms.vdouble({deltac_si}, {deltac_si}, {deltac_si}, {deltac_sci})',
    # f'process.hgcalLayerClustersEE.plugin.deltac = cms.vdouble({deltac_si}, {deltac_si}, {deltac_si}, {deltac_sci})',
    f'process.hgcalValidator.histoProducerAlgoBlock.maxEne = cms.double({maxEne})'
]
if deltac_si != default_dsi or deltac_sci != default_dsci:
    edit_lines += [
        f'process.hgcalLayerClustersHSi.plugin.deltac = cms.vdouble({default_dee}, {deltac_si}, {deltac_si}, {default_dsci})',
        f'process.hgcalLayerClustersHSci.plugin.deltac = cms.vdouble({default_dee}, {default_dsi}, {default_dsi}, {deltac_sci})'
    ]
edit_str = '\n'.join(edit_lines) + '\n'

# 5. Replace #{EDITS} placeholder
if '#{EDITS}' in content:
    content = content.replace('#{EDITS}', '#{EDITS}\n' + edit_str)
else:
    print('Warning: #{EDITS} placeholder not found in original step3.py.')
# if deltac_si != 1.3 or deltac_sci != 0.0315 or deltac_fh != 1.3:
#     if '#{EDITS}' in content:
#         content = content.replace('#{EDITS}', '#{EDITS}\n' + edit_str)
#     else:
#         print('Warning: #{EDITS} placeholder not found in original step3.py.')
# elif 'photon' in args.job_dir:
#     if '#{EDITS}' in content:
#         content = content.replace('#{EDITS}', '#{EDITS}\n' + edit_lines[0])
#     else:
#         print('Warning: #{EDITS} placeholder not found in original step3.py.')

new_step3_path = os.path.join(outdir, 'step3.py')
with open(new_step3_path, 'w') as f:
    f.write(content)

print(f'Modified step3.py created at {new_step3_path}.')

# 7. Read step2_*.root files and write jobs.txt
jobs_dir = f'/grid_mnt/data_cms_upgrade/song/HGCAL/HGCHadron/{args.job_dir}/jobs'
root_files = sorted(glob.glob(os.path.join(jobs_dir, 'step2_*.root')))

jobs_file_path = './jobs.txt'
opt_w = 'w' if args.clean else 'a'

num = 1
with open(jobs_file_path, opt_w) as f:
    for file_path in root_files:
        filename = os.path.basename(file_path)
        # Check format: step2_[number].root
        match = re.match(r'step2_(\d+)\.root$', filename)
        if not match:
            continue
        x = match.group(1)
        histo_path = os.path.join(outdir, 'jobs', f"histo_{x}.root")
        if not os.path.exists(histo_path):
            f.write(f'{file_path} {outdir}\n')
            num += 1
        if num > args.maxnum:
            break

print(f'jobs.txt generated in {outdir}.')