# Telnyx Edge CLI

Deploy serverless functions to Telnyx's edge infrastructure.

## Installation

Download the latest release for your platform from [Releases](https://github.com/team-telnyx/edge-compute/releases).

### macOS / Linux

```bash
# Download and extract (replace URL with your platform)
tar -xzf telnyx-edge-*.tar.gz
sudo mv telnyx-edge-*/telnyx-edge /usr/local/bin/
```

### One-liner Install

```bash
# macOS Apple Silicon
curl -sSL $(curl -s https://api.github.com/repos/team-telnyx/edge-compute/releases/latest | grep "browser_download_url.*macos-arm64.tar.gz" | cut -d '"' -f 4) | tar -xz && sudo mv telnyx-edge-*/telnyx-edge /usr/local/bin/

# macOS Intel
curl -sSL $(curl -s https://api.github.com/repos/team-telnyx/edge-compute/releases/latest | grep "browser_download_url.*macos-amd64.tar.gz" | cut -d '"' -f 4) | tar -xz && sudo mv telnyx-edge-*/telnyx-edge /usr/local/bin/

# Linux x86_64
curl -sSL $(curl -s https://api.github.com/repos/team-telnyx/edge-compute/releases/latest | grep "browser_download_url.*linux-amd64.tar.gz" | cut -d '"' -f 4) | tar -xz && sudo mv telnyx-edge-*/telnyx-edge /usr/local/bin/

# Linux ARM64
curl -sSL $(curl -s https://api.github.com/repos/team-telnyx/edge-compute/releases/latest | grep "browser_download_url.*linux-arm64.tar.gz" | cut -d '"' -f 4) | tar -xz && sudo mv telnyx-edge-*/telnyx-edge /usr/local/bin/
```

### Windows

Download the `.zip` from [Releases](https://github.com/team-telnyx/edge-compute/releases), extract, and add to your PATH.

## Quick Start

```bash
# Authenticate with your Telnyx account
telnyx-edge auth login

# Create a new function
telnyx-edge new-func --language=go --name=my-function
cd my-function

# Deploy to edge
telnyx-edge ship

# List your functions
telnyx-edge list
```

## Commands

| Command | Description |
|---------|-------------|
| `auth login` | Authenticate with Telnyx (opens browser) |
| `auth logout` | Clear authentication |
| `auth status` | Show authentication status |
| `status` | Check CLI configuration and connectivity |
| `new-func` | Create a new function from template |
| `ship` | Deploy function to edge infrastructure |
| `list` | List all deployed functions |
| `delete-func` | Delete a function |
| `secrets` | Manage secrets for your functions |
| `bindings` | Manage Telnyx API key bindings |

## Supported Languages

Create functions in your preferred language:

```bash
telnyx-edge new-func --language=javascript --name=my-func
telnyx-edge new-func --language=typescript --name=my-func
telnyx-edge new-func --language=python --name=my-func
telnyx-edge new-func --language=go --name=my-func
telnyx-edge new-func --language=quarkus --name=my-func
```

| Language | Template | Runtime |
|----------|----------|---------|
| JavaScript | `javascript` | Node.js 18+ |
| TypeScript | `typescript` | Node.js 18+ |
| Python | `python` | Python 3.11+ |
| Go | `go` | Go 1.25+ |
| Java | `quarkus` | Java 17+ (Quarkus) |

## Function Development

### Project Structure

Each function contains:

```
my-function/
├── func.toml          # Function configuration
├── handler.go         # Your function code (varies by language)
└── go.mod             # Dependencies (varies by language)
```

### Configuration (func.toml)

```toml
[edge_compute]
func_id = "func-abc123"
func_name = "my-function"

[env_vars]
MY_VAR = "value"
```

### Deploying

```bash
# From within the function directory
telnyx-edge ship

# Or specify the directory
telnyx-edge ship --from-dir=./my-function
```

## Secrets Management

Store sensitive values that your functions can access at runtime:

```bash
# Add a secret
telnyx-edge secrets add DATABASE_URL "postgres://..."

# List secrets
telnyx-edge secrets list

# Delete a secret
telnyx-edge secrets delete DATABASE_URL
```

## Telnyx API Bindings

Enable your functions to call Telnyx APIs without hardcoding credentials:

```bash
# Create a binding with your Telnyx API key
telnyx-edge bindings create <your-telnyx-api-key>

# Validate the binding works
telnyx-edge bindings validate

# View binding info
telnyx-edge bindings get
```

Your functions will automatically receive `TELNYX_API_KEY` and `TELNYX_BASE_URL` environment variables.

## Configuration

The CLI stores configuration in `~/.telnyx-edge/config.toml`. This is managed automatically - just run `telnyx-edge auth login` to get started.

## Help

```bash
# General help
telnyx-edge --help

# Command-specific help
telnyx-edge new-func --help
telnyx-edge ship --help
```

## Support

- [Telnyx Developer Docs](https://developers.telnyx.com)
- [GitHub Issues](https://github.com/team-telnyx/edge-compute/issues)
