Pip install on macOs for lib compatibility with lambda execution environment
```
pip install \               
    --target=./python/lib/python3.9/site-packages \
    --python 3.9 \
    --upgrade \
    openai

pip install \                    
    --platform manylinux2014_x86_64 \
    --target=./python/lib/python3.9/site-packages \
    --implementation cp \
    --python 3.9 \
    --only-binary=:all: --upgrade \
    stability-sdk

pip install \                    
    --platform manylinux2014_x86_64 \
    --target=./python/lib/python3.9/site-packages \
    --implementation cp \
    --python 3.9 \
    --only-binary=:all: --upgrade \
    pandas
```