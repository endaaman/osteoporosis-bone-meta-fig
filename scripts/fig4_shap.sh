#!/bin/bash
uv run python fig4_shap.py --noshow --model lr
uv run python fig4_shap.py --noshow --model ridge
uv run python fig4_shap.py --noshow --model lasso
uv run python fig4_shap.py --noshow --model lgbm
