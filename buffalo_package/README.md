# Buffalo

Buffalo is a simple and easy-to-use workflow management library for managing various work tasks in projects. The library provides a Python API interface that can be easily integrated into your applications.

## Installation

```bash
pip install buffalo-workflow
```

## Usage

Buffalo provides a simple API for creating and managing workflows:

```python
from buffalo import Buffalo, Work

# Initialize Buffalo, specify the project root directory and template path
buffalo = Buffalo("/path/to/projects", "/path/to/template.yml")

# Create a project
project = buffalo.create_project("my_project", "My Project")

# Get a job
project_folder_name, work = buffalo.get_a_job("Task Name")

# Update job status
buffalo.update_work_status(project_folder_name, work, Work.IN_PROGRESS)

# Complete job
buffalo.update_work_status(project_folder_name, work, Work.DONE)
```

## Environment Variables

Buffalo will prioritize using the user-provided template file. It will only use the built-in example template when the user template doesn't exist:

```python
# Provide your own template file path
buffalo = Buffalo("/path/to/projects", "/path/to/your_own_template.yml")

# If your template doesn't exist, Buffalo will use the built-in template
```

## Custom Workflow Templates

A core feature of Buffalo is allowing users to define their own workflows. You can create your own template file in the following format:

```yaml
workflow:
  works:
    - name: "Your First Step"
      status: not_started
      output_file: "output1.md"
      comment: "Description for the first step"
    
    - name: "Your Second Step"
      status: not_started
      output_file: "output2.md"
      comment: "Description for the second step"
    
    # You can add more steps...
```

## Getting the Example Template File

If you need to reference the built-in example template, you can use:

```python
from buffalo import get_template_path

template_path = get_template_path()
print(f"Example template file path: {template_path}")
```

## Advanced Usage

Buffalo is designed for easy integration with your project workflow management:

- Create multiple projects with different workflows
- Track the status of each work item through the workflow lifecycle
- Automatically save project state after each status update
- Load existing projects when Buffalo is reinitialized 