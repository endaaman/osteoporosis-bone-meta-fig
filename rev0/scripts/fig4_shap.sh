#!/bin/bash
uv run python rev0/fig4_shap.py --noshow --model lr
uv run python rev0/fig4_shap.py --noshow --model ridge
uv run python rev0/fig4_shap.py --noshow --model lasso
uv run python rev0/fig4_shap.py --noshow --model lgbm
