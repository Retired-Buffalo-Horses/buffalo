# Buffalo

Buffalo is a powerful workflow management tool designed for quickly creating and managing project workflows. It provides a simple and flexible way to define, track, and manage tasks and workflows within projects.

## Key Features

- 🚀 Quick project creation and management
- 📋 YAML-based workflow definition
- 🔄 Work status tracking and management
- 📁 Project template support
- 🔍 Flexible work retrieval mechanism
- 💾 Automatic project state saving and loading
- 📊 Ordered workflow execution with index-based sorting

## Installation

```bash
pip install buffalo-workflow
```

## Quick Start

1. Create a workflow template file (e.g., `workflow_template.yml`):

```yaml
workflow:
  works:
    - name: "task_1"
      status: not_started
      comment: "First task"
      index: 1
    - name: "task_2"
      status: not_started
      comment: "Second task"
      index: 2
```

> Note: Each work in the workflow must have an `index` field, which is used to determine the execution order. Works will be automatically sorted by their index values, regardless of their order in the template file.

2. Use Buffalo to create and manage projects:

```python
from pathlib import Path
from buffalo import Buffalo

# Initialize Buffalo
base_dir = Path("./projects")
template_path = Path("./workflow_template.yml")
buffalo = Buffalo(base_dir, template_path)

# Create a new project
project = buffalo.create_project("my_project")

# Get a pending task
project, work = buffalo.get_a_job("task_1")

# Update task status
buffalo.update_work_status(project.folder_name, work, "in_progress")
```

## Project Structure

```
my_project/
├── buffalo.yml          # Project configuration file
└── workflow_description.yml  # Workflow description file
```

## Requirements

- Python >= 3.8
- PyYAML >= 5.1

## License

MIT License

## Contributing

Issues and Pull Requests are welcome!

## Links

- [Homepage](https://github.com/wengzhiwen/buffalo)
- [Issue Tracker](https://github.com/wengzhiwen/buffalo/issues)