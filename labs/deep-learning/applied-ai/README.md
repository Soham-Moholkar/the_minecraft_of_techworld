# Applied AI compatibility suite

This lab executes ATLAS-owned CNN, GRU, Transformer encoder and matrix-factorization
training on deterministic synthetic fixtures. The fixtures expose known signals and
fixed baselines so a dependency upgrade or code change has a measurable regression
contract. They are not substitutes for public benchmark datasets or production
model validation.

Run `python labs/deep-learning/applied-ai/run.py verify`. The lab writes only
`.lab-state/evidence.json` and always removes it after verification. It needs the
optional CPU PyTorch runtime, one CPU thread, no GPU, no credentials and no network.

The chronological forecast fits only pre-cutoff observations. Recommendation
negatives exclude each user's held-out positive. The vision and text fixtures split
before fitting. No checkpoint is loaded or retained.
