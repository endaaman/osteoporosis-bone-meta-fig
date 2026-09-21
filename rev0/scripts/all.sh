#!/bin/bash
set -e
cd "$(dirname "$0")/../.."

bash rev0/scripts/fig2.sh
bash rev0/scripts/fig3.sh
bash rev0/scripts/fig4.sh
bash rev0/scripts/fig4_ro.sh
bash rev0/scripts/fig4_shap.sh
bash rev0/scripts/fig5.sh
bash rev0/scripts/fig6.sh
