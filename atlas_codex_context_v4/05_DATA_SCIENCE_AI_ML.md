# Data Science, AI/ML and AI Engineering Specification

> **Product identity override:** Interpret this file through `00_PRODUCT_IDENTITY.md`. ATLAS is the real application; the IDE is the primary place for source modification. Any older “lesson/playground” wording means engineering documentation, operational tooling, reference modules, or controlled test environments—not the central product model.


This is a first-class pillar of ATLAS and should be one of the largest areas.

# 1. Mathematical foundations

Create interactive explanations/labs for:
- vectors,
- matrices,
- matrix multiplication,
- norms,
- dot products,
- eigen concepts,
- probability,
- random variables,
- distributions,
- expectation/variance,
- conditional probability,
- Bayes,
- sampling,
- hypothesis testing,
- confidence intervals,
- correlation/covariance,
- calculus intuition,
- derivatives,
- gradients,
- chain rule,
- optimization,
- gradient descent,
- regularization,
- numerical stability.

Tie math to code and model behavior.

# 2. Numerical/data libraries

## NumPy
Cover:
- ndarrays,
- dtypes,
- shapes,
- indexing,
- slicing,
- broadcasting,
- vectorization,
- ufuncs,
- aggregation,
- random,
- linear algebra,
- memory layout,
- views vs copies,
- performance.

## pandas
Cover:
- Series/DataFrame,
- selection,
- filtering,
- grouping,
- aggregation,
- merges/joins,
- reshaping,
- missing data,
- strings,
- dates,
- categorical data,
- IO,
- windowing,
- time series,
- performance.

## Polars
Teach:
- expressions,
- eager/lazy,
- query optimization,
- streaming concepts,
- comparison with pandas.

## SciPy
Representative practical modules:
- optimization,
- stats,
- signal,
- spatial,
- integration/interpolation,
- sparse.

## DuckDB
Use as an analytical bridge between SQL, files and dataframes.

Also include relevant:
- PyArrow
- Dask concepts/labs
- distributed dataframes where meaningful.

# 3. EDA

EDA should have rich visual and code-driven labs:

- schema inspection,
- data types,
- descriptive statistics,
- missingness,
- duplicates,
- outliers,
- univariate distributions,
- bivariate/multivariate analysis,
- correlation,
- categorical analysis,
- temporal analysis,
- leakage detection,
- data quality,
- class imbalance,
- target analysis,
- sampling,
- transformation,
- feature generation.

Visualizations:
- histogram,
- KDE concept,
- box,
- violin,
- scatter,
- line,
- area,
- bar,
- heatmap,
- correlation matrix,
- pair relationships,
- residual plots,
- QQ concepts,
- geospatial where suitable.

Libraries:
- Matplotlib
- Plotly
- Altair
- additional well-maintained visualization libraries when they add educational value.

# 4. Dataset scaling ladder

Each major data lesson should support one or more scales:

- tiny: 100–1,000 rows
- small: 10k
- medium: 100k
- large: 1M
- very large: 10M+
- distributed mode: generated or external object-store data

Teach memory and execution tradeoffs.

# 5. Classical machine learning

Implement core algorithms in two styles where educationally valuable:

1. from-scratch / NumPy-oriented implementation,
2. production-style library implementation.

Topics:
- linear regression,
- polynomial regression,
- logistic regression,
- k-NN,
- Naive Bayes,
- decision trees,
- random forests,
- gradient boosting,
- XGBoost,
- LightGBM,
- CatBoost,
- SVM,
- clustering,
- k-means,
- hierarchical clustering,
- DBSCAN,
- PCA,
- dimensionality reduction concepts,
- anomaly detection,
- ensembles,
- calibration.

Workflows:
- train/validation/test,
- cross-validation,
- preprocessing,
- pipelines,
- feature selection,
- hyperparameter tuning,
- metrics,
- leakage,
- bias/variance,
- class imbalance,
- model interpretation.

# 6. Deep learning

Primary deep-learning teaching stack should include PyTorch.
Also cover TensorFlow/Keras and JAX concepts/selected examples.

Topics:
- tensors,
- autodiff,
- layers,
- activation functions,
- loss functions,
- optimizers,
- initialization,
- normalization,
- regularization,
- training loop,
- validation,
- checkpointing,
- mixed precision,
- GPU use,
- distributed training concepts,
- CNNs,
- RNNs,
- LSTMs/GRUs,
- attention,
- transformers.

# 7. NLP

- text preprocessing,
- tokenization,
- n-grams,
- classical features,
- embeddings,
- classification,
- NER,
- similarity,
- retrieval,
- transformers,
- sequence-to-sequence concepts,
- evaluation.

# 8. Computer vision

- image representation,
- OpenCV,
- preprocessing,
- augmentation,
- CNNs,
- classification,
- object detection concepts,
- segmentation concepts,
- embeddings,
- transfer learning,
- evaluation,
- inference.

# 9. Time series

- resampling,
- decomposition,
- trends/seasonality,
- lag features,
- rolling windows,
- forecasting metrics,
- classical models,
- ML models,
- deep-learning approaches,
- anomaly detection,
- backtesting.

# 10. Recommendation systems

- popularity baselines,
- collaborative filtering,
- matrix factorization,
- content-based,
- ranking,
- retrieval + ranking,
- implicit feedback,
- cold start,
- offline evaluation,
- serving concepts.

# 11. Reinforcement learning

Cover foundations without pretending RL is needed everywhere:
- state/action/reward,
- policies,
- value functions,
- exploration,
- bandits,
- Q-learning,
- policy-gradient concepts,
- simulation environments.

# 12. MLOps

- experiment tracking,
- MLflow,
- data/version tracking,
- model registry,
- reproducibility,
- feature pipelines,
- model packaging,
- online/batch inference,
- model serving,
- monitoring,
- drift,
- evaluation,
- rollback,
- canary model deployment,
- data quality,
- governance concepts.

# 13. LLM engineering

Teach:
- tokenizer behavior,
- context windows,
- prompting,
- system/user/tool roles,
- structured outputs,
- tool calling,
- embeddings,
- semantic similarity,
- chunking,
- vector indexing,
- hybrid search,
- reranking,
- RAG,
- citations/grounding,
- conversation memory,
- caching,
- streaming,
- latency,
- throughput,
- batching,
- quantization,
- local model serving,
- fine-tuning concepts,
- adapters/LoRA concepts,
- evaluation,
- cost modeling,
- observability.

Support provider abstraction:
- local models,
- open models,
- hosted providers.
Do not hard-code the product to one vendor.

# 14. Agentic AI

Teach progressively:

## Single-agent
- instructions,
- tools,
- state,
- memory,
- retries,
- limits,
- approvals.

## Workflow agents
- deterministic graph,
- conditional routing,
- parallel branches,
- retries,
- checkpoints,
- human-in-the-loop.

## Multi-agent
- planner,
- specialist agents,
- critic/reviewer,
- tool isolation,
- shared vs private state,
- coordination failure modes.

Framework coverage can include current well-maintained tools such as:
- LangChain concepts,
- LangGraph,
- AutoGen-style patterns,
- Crew-style orchestration patterns,
- direct SDK implementations.

Do not teach frameworks without also showing framework-free foundations.

# 15. MCP/tool protocol area

Create:
- MCP architecture explanation,
- server/client mental model,
- tools/resources/prompts where applicable,
- local mock MCP servers,
- schema inspection,
- permissions,
- retries,
- timeouts,
- tool failures,
- audit logs,
- agent-tool contracts,
- integration examples.

The frontend should include an MCP explorer.

# 16. AI evaluation

Create reusable evaluation infrastructure:
- exact-match where applicable,
- semantic similarity,
- LLM-as-judge concepts with caveats,
- groundedness,
- citation correctness,
- retrieval recall/precision,
- tool-use success,
- structured output validity,
- safety checks,
- latency,
- cost/token usage,
- regression suites.

# 17. AI security

Cross-reference the security spec:
- prompt injection,
- indirect prompt injection,
- data exfiltration risks,
- tool privilege,
- insecure output handling,
- RAG poisoning,
- untrusted content,
- multi-tenant isolation,
- secret leakage,
- approval boundaries,
- sandboxing,
- auditability.

# 18. AI lab examples

Examples:
- compare chunk sizes,
- compare embedding models,
- compare retrieval strategies,
- compare rerankers,
- evaluate RAG answer quality,
- break structured output,
- recover from tool timeout,
- revoke a tool permission,
- inspect context usage,
- run local model vs hosted model,
- quantization tradeoff lab,
- prompt regression suite,
- agent workflow replay.