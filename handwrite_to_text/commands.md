1) Create Virtual Environment

python -m venv .venv

2) Enable virtual environment

.\venv\Scripts\activate

3) Install PaddleOCR:

(supporting docs) https://www.paddleocr.ai/main/en/quick_start.html#1-install-paddlepaddle

pip install paddlepaddle
pip install "paddleocr>=2.0.1"

4) Install CCache:

Ccache is a compiler cache. It speeds up recompilation by caching previous compilations and detecting when the same compilation is being done again.

https://github.com/ccache/ccache

Need to add the path only. Better to do this work, for speeding up compilation.

5) Run the test_code.py