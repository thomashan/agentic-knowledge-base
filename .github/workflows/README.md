# GitHub Actions Workflows

This directory contains the CI/CD workflows for the `agentic-knowledge-base` project.

## Workflows

- `test-unit.yml`: Runs on every push for both `ubuntu-latest` and `macos-latest`. It executes linting, formatting checks, and unit tests (tests not marked as `integration`).
- `test-integration.yml`: Runs on every push for `ubuntu-latest`. It executes the integration tests (tests marked as `integration`), which require Docker services.

## Key Configuration: Conda Package Resolution

During the setup of the CI, a persistent `PackagesNotFoundError` was encountered when trying to install the `uv` package via Conda.

### Initial Investigation and Caching Attempts

Initial attempts to fix this involved adding caching for Conda packages (`actions/cache`). This was pursued because package resolution was observed to take a significant amount of time:

- **Without cache:** Package resolution took approximately 19 seconds (e.g. from [this CI run](https://github.com/thomashan/agentic-knowledge-base/actions/runs/19328413029/job/55285191104), 2025-11-13 10:27:58 to
  2025-11-13 10:28:17).

- **With cache hit:** Reloading from cache reduced this to approximately 3 seconds.

It did not reduce the total conda setup time because even with the cache enabled, conda still needs to download the index.

### Root Cause and Solution

The root cause was identified in the `setup-miniconda` action's configuration:

```yaml
use-only-tar-bz2: true
```

This setting forces Conda to only use the older `.tar.bz2` package format and ignore the newer, more efficient `.conda` format. The `uv` package, for the specific `macos-latest` architecture, was likely only available in
the modern `.conda` format from the `conda-forge` channel. By restricting Conda to the old format, we were preventing it from finding the package.

The solution was to change this setting to `false`:

```yaml
use-only-tar-bz2: false
```

This allows Conda to use the full range of packages available on `conda-forge`, resolving the `PackagesNotFoundError` and ensuring a reliable build across all platforms.
