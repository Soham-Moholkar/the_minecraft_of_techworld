# Framework comparison

This resettable lab calls the actual product training process with a deterministic
operational dataset. Inspect both loss curves and shared-holdout confusion matrices
in `.lab-state/evidence.json`, then change owned code in your IDE.

Install CPU dependencies into the active Python 3.12 environment:

```powershell
python -m pip install torch==2.14.0+cpu --index-url https://download.pytorch.org/whl/cpu
python -m pip install -e './apps/api-python[data,dev,frameworks]'
python labs/deep-learning/framework-comparison/run.py verify
```

`start` writes evidence, `test` checks that evidence, `reset` removes only the
lab's evidence file, and `verify` performs all three with guaranteed cleanup.
After installation the lab requires no internet, credentials or GPU. Budget
approximately 2 GiB available RAM for both runtimes; compute is one thread and
80 full-batch epochs per neural model. Fit timing excludes runtime startup.

For the real product, set `ATLAS_NEURAL=true`, rebuild the API image and open
`/models`. Import a saved operational dataset, then choose the Frameworks suite.
Missing dependencies return a service-unavailable error without a partial record.
The original classical suite continues to work in the default smaller image.

Security: no code upload, external checkpoints or arbitrary hyperparameters.
The process boundary runs trusted ATLAS code; it does not sandbox hostile code.
See ADR 0007 for tenancy, resource bounds and failure semantics.
