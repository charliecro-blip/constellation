# GitHub Actions Setup

If workflow runs do not appear after commits, check whether Actions are enabled for the repository.

## Steps

1. Open the repository on GitHub.
2. Go to Settings.
3. In the left sidebar, open Actions, then General.
4. Under Actions permissions, choose Allow all actions and reusable workflows.
5. Under Workflow permissions, choose Read and write permissions if available.
6. Save.
7. Push any small commit or edit a file to trigger the workflow.

## Expected Result

A workflow named tests should appear under the Actions tab.

The workflow installs the Python package and runs:

```bash
pytest -q
```
