#!/bin/bash
uv run python rev0/fig4.py --noshow --model lr
uv run python rev0/fig4.py --noshow --model ridge
uv run python rev0/fig4.py --noshow --model lasso
uv run python rev0/fig4.py --noshow --model lgbm

uv run python rev0/fig4_shap.py --noshow --model lr
uv run python rev0/fig4_shap.py --noshow --model ridge
uv run python rev0/fig4_shap.py --noshow --model lasso
uv run python rev0/fig4_shap.py --noshow --model lgbm

uv run python rev0/fig4_ro.py --noshow
