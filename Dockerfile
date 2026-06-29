# gc-ghost
# Layer 3: App code
# Provider and model injected at runtime via GC_PROVIDER and GC_MODEL env vars
FROM ghost-runtime

COPY src/ ./src/
ENTRYPOINT ["python", "src/main.py"]
