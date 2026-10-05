# Frontend, Design System and Utility Component Specification

> **Product identity override:** Interpret this file through `00_PRODUCT_IDENTITY.md`. ATLAS is the real application; the IDE is the primary place for source modification. Any older “lesson/playground” wording means engineering documentation, operational tooling, reference modules, or controlled test environments—not the central product model.


## Goal

The frontend should be one of the most impressive parts of ATLAS: a dense but usable technical workspace capable of rendering lessons, code, datasets, tests, infrastructure, system diagrams, AI conversations, security findings and observability.

It must not become a generic card-grid dashboard.

## Primary stack

Preferred:
- Next.js
- React
- TypeScript
- Tailwind CSS
- shadcn/ui
- shadcn Base UI path for new projects/components where appropriate
- Radix compatibility where an existing component or ecosystem need warrants it
- Lucide icon set or the icon library configured by shadcn
- TanStack Query
- TanStack Table
- React Hook Form
- schema validation
- Monaco Editor for deep code editing
- React Flow / XYFlow-style graph canvas for architectures/workflows
- charting library selected deliberately for each visualization class

Use current official docs when installing.

## shadcn baseline

As of the 2026 shadcn documentation, the official component catalog includes primitives and composites such as:

- Accordion
- Alert
- Alert Dialog
- Aspect Ratio
- Attachment
- Avatar
- Badge
- Breadcrumb
- Bubble
- Button
- Button Group
- Calendar
- Card
- Carousel
- Chart
- Checkbox
- Collapsible
- Combobox
- Command
- Context Menu
- Data Table
- Date Picker
- Dialog
- Direction
- Drawer
- Dropdown Menu
- Empty
- Field
- Hover Card
- Input
- Input Group
- Input OTP
- Item
- Kbd
- Label
- Marker
- Menubar
- Message
- Message Scroller
- Native Select
- Navigation Menu
- Pagination
- Popover
- Progress
- Questionnaire
- Radio Group
- Resizable
- Scroll Area
- Select
- Separator
- Sheet
- Sidebar
- Skeleton
- Slider
- Spinner
- Switch
- Table
- Tabs
- Textarea
- Toast
- Toggle
- Toggle Group
- Tooltip
- Typography

Use these as source-owned components, not as untouchable package abstractions.

## Required ATLAS component layers

### Layer 1 — primitives
Keep `/components/ui` close to shadcn primitives.

### Layer 2 — composed application components
Examples:
- AppShell
- AppSidebar
- DomainSidebar
- MobileNav
- TopNav
- WorkspaceHeader
- BreadcrumbBar
- ContextToolbar
- CommandPalette
- GlobalSearch
- SearchFilters
- QuickSwitcher
- UserMenu
- ThemeToggle
- DensityToggle
- SplitPane
- ResizableWorkspace
- InspectorPanel
- BottomPanel
- StatusBar
- ShortcutHelp
- NotificationCenter

### Layer 3 — learning components
Create:
- TopicHeader
- LearningObjectives
- PrerequisiteGraph
- ConceptCallout
- DefinitionCard
- FormulaBlock
- MathRenderer
- CodeExample
- EditableCodeExample
- ExpectedOutput
- StepRunner
- ExerciseCard
- ChallengePanel
- HintPanel
- SolutionReveal
- CommonMistake
- ProductionNote
- SecurityNote
- PerformanceNote
- FurtherReading
- TopicNavigator
- RelatedTopics
- ProgressCheckpoint
- KnowledgeCheck
- GlossaryPopover
- Citation/ReferenceList
- CompareConcepts
- TimelineExplainer

### Layer 4 — code and runtime utilities
Create:
- MonacoCodeEditor
- ReadOnlyCodeViewer
- DiffViewer
- MultiFileEditor
- FileTree
- TabsForFiles
- TerminalPanel
- CommandRunner
- ProcessList
- EnvironmentVariableViewer
- HTTPRequestBuilder
- HTTPResponseViewer
- WebSocketConsole
- SSEViewer
- GraphQLExplorer
- gRPCRequestPanel
- JSONViewer
- YAMLViewer
- TOMLViewer
- XMLViewer
- CSVViewer
- HexViewer
- StackTraceViewer
- LogViewer
- StructuredLogViewer
- LogFilterBar
- RuntimeStatus
- ResourceMeter
- CPUChart
- MemoryChart
- NetworkChart
- DiskIOChart
- EventLoopLagChart
- FlameGraphContainer
- TraceWaterfall
- SpanDetails
- MetricsExplorer

### Layer 5 — testing utilities
Create:
- TestRunButton
- TestSuiteTree
- TestCaseRow
- TestStatusBadge
- TestSummary
- CoverageGauge
- CoverageFileTree
- CoverageHeatmap
- SnapshotDiff
- AssertionDetails
- PropertyTestResult
- FuzzRunPanel
- MutationScoreCard
- ContractTestMatrix
- E2ETimeline
- LoadTestControls
- LatencyHistogram
- ThroughputChart
- ErrorRateChart
- VirtualUsersChart
- TestArtifactViewer

### Layer 6 — data utilities
Create:
- DatasetBrowser
- DatasetCard
- DatasetMetadata
- SchemaTable
- DataGrid
- VirtualizedDataGrid
- ColumnInspector
- RowInspector
- MissingValuesPanel
- DuplicateAnalyzer
- OutlierExplorer
- DistributionChart
- CorrelationMatrix
- PairPlotContainer
- BoxPlot
- Histogram
- ScatterPlot
- TimeSeriesChart
- CategoricalFrequencyChart
- DataProfiler
- FilterBuilder
- QueryBuilder
- SQLConsole
- DuckDBConsole
- DataTransformationPipeline
- BeforeAfterDataDiff
- DataQualityScore
- DataQualityRuleBuilder
- SamplingControls
- DataSizeSelector
- ExportControls

### Layer 7 — ML utilities
Create:
- ExperimentTracker
- ExperimentRunCard
- HyperparameterTable
- HyperparameterSearchViewer
- TrainingCurve
- LossChart
- MetricChart
- ConfusionMatrix
- ROCChart
- PRCurve
- FeatureImportanceChart
- SHAPViewerAdapter
- PredictionExplorer
- ErrorAnalysisTable
- ModelComparison
- ModelCard
- ModelRegistryTable
- DatasetSplitViewer
- PipelineDiagram
- FeaturePipeline
- InferencePlayground
- BatchInferencePanel
- ModelLatencyChart
- ModelSizeCard
- CheckpointBrowser
- EmbeddingProjectorContainer

### Layer 8 — AI/LLM utilities
Use current shadcn chat primitives and, where valuable, AI-focused open components.

Create:
- AIChatWorkspace
- MessageThread
- StreamingMessage
- ReasoningStatus
- ToolCallCard
- ToolResultCard
- ToolApprovalDialog
- AgentStatus
- AgentTimeline
- AgentGraph
- PromptEditor
- PromptVersionHistory
- SystemPromptPanel
- TokenCounter
- TokenUsageChart
- ContextWindowMeter
- ModelSelector
- ProviderSelector
- TemperatureControls
- StructuredOutputViewer
- JSONSchemaEditor
- RAGPlayground
- RetrievalResults
- ChunkViewer
- ChunkingControls
- EmbeddingSimilarityViewer
- RerankingResults
- CitationViewer
- GroundednessPanel
- EvalSuitePanel
- EvalScoreCard
- HallucinationReview
- PromptInjectionAlert
- AgentPermissionMatrix
- HumanApprovalQueue
- MemoryInspector
- ConversationStateInspector
- MCPServerList
- MCPToolBrowser
- MCPResourceBrowser
- ToolSchemaViewer
- MultiAgentBoard

### Layer 9 — database utilities
Create:
- DatabaseExplorer
- ConnectionStatus
- SchemaExplorer
- TableExplorer
- ERDiagram
- QueryEditor
- QueryResultGrid
- QueryHistory
- ExplainPlanViewer
- ExplainAnalyzeTree
- IndexInspector
- IndexUsageCard
- LockViewer
- TransactionTimeline
- IsolationLevelSimulator
- MVCCVisualizer
- ConnectionPoolViewer
- ReplicationTopology
- ReplicaLagChart
- PartitionViewer
- ShardMap
- SlowQueryTable
- CacheHitChart
- WALViewer
- DatabaseMetricsPanel

### Layer 10 — streaming/data-engineering utilities
Create:
- TopicExplorer
- PartitionMap
- ProducerConsole
- ConsumerConsole
- ConsumerGroupViewer
- ConsumerLagChart
- MessageInspector
- SchemaRegistryViewer
- EventTimeline
- EventReplayPanel
- DeadLetterQueueViewer
- PipelineCanvas
- DAGViewer
- JobRunTimeline
- BackpressureViewer
- CheckpointViewer
- WatermarkVisualizer
- WindowingVisualizer
- BatchVsStreamComparison
- LineageGraph
- DataCatalogExplorer

### Layer 11 — DevOps/cloud utilities
Create:
- ServiceTopology
- ContainerList
- ContainerDetails
- DockerImageExplorer
- DockerLayerViewer
- KubernetesClusterOverview
- NamespaceSelector
- PodTable
- PodDetails
- DeploymentViewer
- ReplicaSetViewer
- ServiceViewer
- IngressViewer
- ConfigMapViewer
- SecretMetadataViewer
- HPAViewer
- ResourceRequestsLimits
- KubeEventTimeline
- HelmReleaseViewer
- TerraformPlanViewer
- TerraformStateExplorer
- IaCResourceGraph
- CICDPipeline
- PipelineRunDetails
- BuildLog
- ArtifactBrowser
- DeploymentTimeline
- RolloutViewer
- RollbackControls
- CloudResourceExplorer
- CostEstimateCard
- RegionMap
- AvailabilityZoneDiagram

### Layer 12 — observability/SRE utilities
Create:
- ServiceHealthGrid
- SLOCard
- SLIChart
- ErrorBudgetGauge
- BurnRateChart
- IncidentTimeline
- AlertList
- AlertDetails
- TraceExplorer
- MetricsDashboard
- LogSearch
- CorrelationView
- REDDashboard
- USEMethodDashboard
- GoldenSignalsPanel
- OnCallRunbookViewer
- PostmortemViewer
- DependencyMap

### Layer 13 — security utilities
Create:
- SecurityOverview
- FindingCard
- FindingTable
- SeverityBadge
- VulnerabilityDetails
- CVEReferencePanel
- DependencyRiskTable
- SecretScanResult
- SASTFindingViewer
- DASTFindingViewer
- ContainerScanViewer
- SBOMExplorer
- LicenseRiskTable
- ThreatModelCanvas
- STRIDEChecklist
- AttackSurfaceMap
- TrustBoundaryDiagram
- PermissionMatrix
- RBACExplorer
- ABACPolicyViewer
- AuthFlowDiagram
- JWTInspector
- OAuthFlowVisualizer
- SessionInspector
- CSPBuilder
- SecurityHeadersViewer
- AuditLogViewer
- DetectionRuleViewer
- SIEMEventTable
- IncidentResponseBoard
- EvidenceTimeline
- RemediationChecklist
- SecurityRegressionStatus

### Layer 14 — system-design utilities
Create:
- ArchitectureCanvas
- ArchitectureNode
- ServiceNode
- DatabaseNode
- QueueNode
- CacheNode
- CDNNode
- LoadBalancerNode
- RegionNode
- ExternalSystemNode
- ArchitectureEdge
- TrustBoundary
- DataFlowOverlay
- RequestFlowAnimator
- FailureOverlay
- CapacityCalculator
- QPSCalculator
- StorageCalculator
- BandwidthCalculator
- CacheCalculator
- PartitionCalculator
- AvailabilityCalculator
- ReplicationCalculator
- BottleneckInspector
- ArchitectureComparison
- TradeoffMatrix
- DecisionRecordPanel

### Layer 15 — generic utilities
Create reusable:
- MetricCard
- StatStrip
- EmptyState
- ErrorState
- LoadingState
- OfflineState
- PermissionDeniedState
- NoResults
- FilterChips
- SortMenu
- ColumnPicker
- SavedViewMenu
- ExportMenu
- ImportDialog
- ConfirmDangerousAction
- CopyButton
- ShareStateButton
- KeyboardShortcut
- RelativeTime
- AbsoluteTime
- Duration
- ByteSize
- Percentage
- CodeBadge
- TechnologyBadge
- StatusPill
- SeverityPill
- VersionBadge
- EnvironmentBadge
- CollapsibleSection
- FullscreenPanel
- StickyToolbar
- FloatingActions
- SideInspector
- DetailDrawer
- MasterDetail
- VirtualList
- InfiniteList
- SearchHighlight
- MarkdownRenderer
- MDXRenderer
- MermaidRenderer
- DiagramExport
- DownloadArtifact
- UploadDropzone
- FilePreview
- ErrorBoundary
- ClientOnly
- CopyableValue
- KeyValueTable
- DefinitionList
- ObjectInspector
- Timeline
- ActivityFeed
- Stepper
- Wizard
- DiffBadge

## Pages and layouts

Use multiple layout archetypes:

1. **Reading layout** — prose + sticky outline + code.
2. **Lab layout** — instructions + workspace + outputs.
3. **IDE layout** — file tree + editor + terminal + tests.
4. **Data layout** — schema + grid + profiling + charts.
5. **Observability layout** — dashboards + logs + traces.
6. **Architecture layout** — full canvas + inspector.
7. **Security layout** — findings + threat model + remediation.
8. **AI layout** — chat/workflow + context/tool/eval sidebars.
9. **Dashboard layout** — metrics and activity.
10. **Comparison layout** — synchronized variants + benchmark results.

## Visual direction

- technical, dense, polished, not childish,
- clear hierarchy,
- restrained motion,
- excellent dark mode,
- readable light mode,
- monospace only where technical,
- spacious reading pages,
- compact operational dashboards,
- consistent semantic colors for success/warning/error/info,
- do not rely on color alone,
- excellent empty/loading/error states.

## Online/community component usage

Codex may use reputable open-source UI components from online registries if they:
- solve a real interaction need,
- can be source-audited,
- have compatible licensing,
- do not balloon dependencies,
- meet accessibility expectations.

Adapt them into the ATLAS component layer. Do not create a visual collage of unrelated component styles.

## Storybook/component lab

Create a component development surface:
- states,
- variants,
- accessibility checks,
- interaction tests,
- responsive previews,
- dark/light,
- dense/comfortable,
- error/empty/loading examples.

## Frontend test baseline

Every important interactive utility needs:
- unit/component tests where useful,
- keyboard behavior tests,
- accessibility assertions,
- E2E coverage for critical flows.