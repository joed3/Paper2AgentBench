# Paper2AgentBench

## Description
This repo holds the benchmarking scripts and results for the AlphaGenome agent for [Paper2Agent](https://github.com/jmiao24/Paper2Agent#)

## Installation

### Prerequisites

- Python 3.11
- Claude Code: Install following instructions at anthropic.com/claude-code

### Local setup for benchmarking

1. Clone the repository:
```bash
git clone <repository-url>
cd Paper2AgentBench
```

2. Create and activate a conda environment:

With conda:
```bash
# Create a new conda environment
conda create -n paper2agent python=3.11

# Activate the environment
conda activate paper2agent
```

With base python:
```bash
python -m venv paper2agent  # be sure you have your python pointed at python3.11
source paper2agent/bin/activate
```

3. Install dependencies:

**Option A: Using pip (recommended)**
```bash
pip install --upgrade pip setuptools wheel build
```

**Option B: Using conda**
```bash
# Install core dependencies via conda
conda install pip setuptools wheel build
```

4. Build the package in editable mode for local development
```bash
pip install -e .
```

5. [Install Claude Code](https://www.anthropic.com/claude-code)

The following steps were inspired by [this FastMCP documentation](https://gofastmcp.com/integrations/claude-code).

To install Claude Code:
```bash
# First install Node.js, if not already present
brew install node
# Then install claude-code
npm install -g @anthropic-ai/claude-code
```

6. Register the MCP server with Claude Code

Note: We are registering the MCP server for AlphaGenome in this example.
```bash
# First time, need to install
fastmcp install claude-code ./AlphaGenome/src/alphagenome_mcp.py --project ./Paper2AgentBench
```

The following commands are helpful for debugging the MCP server instances
```bash
# Get a list of MCP servers
claude mcp list

# Remove an MCP server
claude mcp remove <server name>

# After installing, can run as follows
fastmcp run ./AlphaGenome/src/alphagenome_mcp.py:mcp
```

7. Finally, test the installation!

At this point, you've built the python package and the MCP server, registered it with Claude as a backend, and 
now you can run your first test queries like so:
```bash
# First load claude
claude
# Then run a test query using an example from our benchmark data
Score variant chr22:36201698:A>C using the recommended RNA_SEQ variant scorer. What is the quantile score for the RBFOX2 gene in neuronal stem cell?
```

### Running local benchmarking with AlphaGenome MCP
Once you've completed the above setup, you can run benchmarking locally as follows.

1. Generate benchmark questions and ground truth answers by running the labeling scripts. These are scripts that execute specific queries using human-curated code following the AlphaGenome repo:
```bash
# Tutorial-based benchmark
python AlphaGenome/benchmarking/scripts/ag_tutorial_labeler_cli.py

# Novel benchmark
python AlphaGenome/benchmarking/scripts/ag_novel_labeler_cli.py
```
These scripts will output CSV files with naming convention `AlphaGenome/benchmarking/data/ag_<tutorial|novel>_benchmark_<run date>.csv` with each question and ground truth answer, with empty fields to hold agent responses and human grading.

2. Generate agent responses for:
- The Paper2Agent-created AlphaGenome MCP - see `AlphaGenome/benchmarking/scripts/COLLECT_AGENT_RESPONSES_README.md` for details
- The Claude + Repo agent - see `AlphaGenome/benchmarking/scripts/CLAUDE_ONLY_RESPONSES_README.md` for details
- The Biomni agent - see see `AlphaGenome/benchmarking/scripts/COLLECT_BIOMNI_RESPONSES_README.md` for details

Running benchmarking for each of these agents will output a new CSV in the `AlphaGenome/benchmarking/data/` directory with the same name prefix `ag_<tutorial|novel>_benchmark_<run date>` and suffix `with_<agent name>_responses.csv`. These CSV files will now have the final agent responses as well as fields recording the run-time for each query and estimated total cost (USD), where available. 

3. Now that you have the benchmark questions with ground truth labels and agent responses, all you need to do now is manually review the agent responses against the ground truth labels. Add your grades (either correct or incorrect) in with the "grade" column for each benchmark set and and "grade comments". Save your graded benchmarks with the same filename with suffix `_human_graded.csv`.

4. You can summarize your benchmarking results with the following command:
```bash
python AlphaGenome/benchmarking/scripts/analyze_human_graded_data.py
```
This will generate a set of summary figures (PNG) in the `data/` directory, and it will print to STDOUT a set of summary metrics. 

## 📚 Citation
```
@misc{miao2025paper2agent,
      title={Paper2Agent: Reimagining Research Papers As Interactive and Reliable AI Agents}, 
      author={Jiacheng Miao and Joe R. Davis and Jonathan K. Pritchard and James Zou},
      year={2025},
      eprint={2509.06917},
      archivePrefix={arXiv},
      primaryClass={cs.AI},
      url={https://arxiv.org/abs/2509.06917}, 
}
```
