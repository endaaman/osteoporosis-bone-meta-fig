#!/bin/bash
set -e
cd "$(dirname "$0")/.."

bash scripts/fig2.sh
bash scripts/fig3.sh
bash scripts/fig4.sh
bash scripts/fig4_ro.sh
bash scripts/fig4_shap.sh
bash scripts/fig5.sh
bash scripts/fig6.sh
