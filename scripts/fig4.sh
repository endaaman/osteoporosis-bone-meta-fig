#!/bin/bash
uv run python fig4.py --noshow --model lr
uv run python fig4.py --noshow --model ridge
uv run python fig4.py --noshow --model lasso
uv run python fig4.py --noshow --model lgbm
