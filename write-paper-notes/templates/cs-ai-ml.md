# [Full Title]

## 1. Introduction
[Context and motivation for the paper. What problem does it solve? Why is it important?]

**Contributions:**
- Contribution 1
- Contribution 2
- Contribution 3

## 2. Related Work
[Brief overview of prior work landscape]

| Approach | Core Idea | Limitation vs. This Work |
|----------|-----------|--------------------------|
| Prior A  | ...       | ...                      |
| Prior B  | ...       | ...                      |

## 3. Method

### 3.1 Problem Formulation
[Formal definition of inputs, outputs, and objective]

$$ \text{mathematical formulation} $$

### 3.2 Model Architecture
![Descriptive alt text describing the architecture](images/filename.png)
*Use the original paper figure. Only generate a Mermaid diagram if the paper has no architecture figure.*

### 3.3 Training Objective
[Loss function, optimization algorithm, hyperparameters]

$$ \mathcal{L} = \mathcal{L}_{\text{task}} + \lambda \mathcal{L}_{\text{reg}} $$

### 3.4 Implementation Details

| Parameter | Value |
|-----------|-------|
| Backbone  | ...   |
| Optimizer | ...   |
| LR        | ...   |
| Batch size| ...   |

**Pseudocode:**
```python
def training_step(batch):
    x, y = batch
    y_pred = model(x)
    loss = criterion(y_pred, y)
    loss.backward()
    optimizer.step()
```

## 4. Experiments

### 4.1 Setup
[Datasets used, evaluation metrics, baselines compared]

| Dataset | #Samples | #Classes | Metric |
|---------|----------|----------|--------|
| A       | 50K      | 10       | Acc.   |

### 4.2 Main Results

| Method | Dataset A | Dataset B |
|--------|-----------|-----------|
| Baseline 1 | 85.2 | 72.1 |
| Baseline 2 | 87.6 | 74.8 |
| **Ours** | **91.3** | **78.5** |

### 4.3 Ablation Studies

| Variant | Component | Metric A |
|---------|-----------|----------|
| Full model | — | 91.3 |
| − Module A | Module A removed | 88.1 |

### 4.4 Qualitative Analysis
[Interpret visual results]

![Descriptive alt text](images/filename.png)

## 5. Conclusion
[Key findings, limitations, and future work]
