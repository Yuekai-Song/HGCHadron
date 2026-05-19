#!/bin/bash
# ============================================================
# Description:
#   Run CLUE data processing jobs in background using nohup.
#   Each job runs in the parent directory (../):
#     1. python3 harvest.py --dir CLUE/<dir>
#     2. python3 makePlots.py --dir CLUE/<dir>
#   Log files are written in the current directory.
#   The jobs continue running even if the terminal is closed.
# ============================================================

# List of directories to process
# "original_Sci" "photon_PU_Sci" "photon_noPU_Sci" "dsci_0.01" "dsci_0.05" "dsci_0.1" "dsci_0.2" "original_Si" "photon_PU_Si" "photon_noPU_Si" "dsi_1.0"
# dirs=("dsci_0.01" "dsci_0.05" "dsci_0.1" "dsci_0.2" "original_Si" "dsi_1.0" "dsi_1.5" "dsi_2.0" "dsi_2.5")
dirs=("original_FH" "dfh_1.0" "dfh_1.5" "dfh_2.0" "dfh_2.5")
# dirs=("photon_PU_Sci" "photon_noPU_Sci" "original_Sci" "dsci_0.01" "dsci_0.05" "dsci_0.1" "dsci_0.2")
# dirs=("NoUse2x2/photon_PU_Sci" "NoUse2x2/photon_noPU_Sci" "NoUse2x2/original_Sci" "NoUse2x2/dsci_0.01" "NoUse2x2/dsci_0.05" "NoUse2x2/dsci_0.1" "NoUse2x2/dsci_0.2")
# dirs=("photon_PU_Si" "photon_noPU_Si" "original_Si" "dsi_1.0" "dsi_1.5" "dsi_2.0" "dsi_2.5")
# Current directory where the script is executed (logs go here)
CURRENT_DIR="$(pwd)"
mkdir -p $CURRENT_DIR/logs
# Parent directory where the scripts are located (programs will run here)
PARENT_DIR="$(cd "$(dirname "$0")"/.. && pwd)"

# Submit background jobs for each directory
for dir in "${dirs[@]}"; do
    mkdir -p $(dirname "$CURRENT_DIR/logs/${dir}.log")
    LOGFILE="$CURRENT_DIR/logs/${dir}.log"
    echo "[INFO] Submitting job for dir: ${dir}"

    # Use nohup to detach process from terminal
    nohup bash -c "
        cd \"$PARENT_DIR\" || exit
        echo \"=== Starting job for ${dir} at \$(date) ===\" > \"$LOGFILE\"
        python3 harvest.py --dir \"CLUE/${dir}\" >> \"$LOGFILE\" 2>&1
        cd \"$CURRENT_DIR/${dir}\" || exit
        echo \"cd \$(pwd) for cmsRun\" >> \"$LOGFILE\"
        cmsRun step4.py >> \"$LOGFILE\" 2>&1
        cd \"$PARENT_DIR\" || exit
        echo \"=== Finished job for ${dir} at \$(date) ===\" >> \"$LOGFILE\"
    " > /dev/null 2>&1 &
done
        # python3 makePlots.py --dir \"CLUE/${dir}\" >> \"$LOGFILE\" 2>&1
echo "All jobs have been submitted with nohup."
echo "Logs are available in: $CURRENT_DIR/"