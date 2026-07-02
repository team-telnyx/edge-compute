# 🚀 Telnyx Edge Compute CLI

> Deploy serverless functions to the edge with simple commands.

---

## 🚀 Quick Start

```bash
# Install (Linux x64)
VERSION=$(curl -s https://api.github.com/repos/team-telnyx/edge-compute/releases/latest | grep '"tag_name"' | cut -d'"' -f4)
curl -sSL https://github.com/team-telnyx/edge-compute/releases/download/$VERSION/telnyx-edge-$VERSION-linux-amd64.tar.gz | tar -xzf -
sudo mv telnyx-edge-$VERSION-linux-amd64/telnyx-edge /usr/local/bin/telnyx-edge
chmod +x /usr/local/bin/telnyx-edge

# Authenticate
telnyx-edge auth login

# Check status
telnyx-edge status
```

---

## 🧑‍💻 Usage

```bash
telnyx-edge [global options] <command> [command options]
```

| Command | Description |
|---------|-------------|
| `help` | Show help and usage information |
| `status` | Check CLI status and configuration |
| `list` | List your functions |
| `secrets` | Manage secrets |
| `bindings` | Manage Telnyx API key bindings |
| `storage` | Manage storage resources (KV namespaces) |
| `new-func` | Create a new function |
| `ship` | Deploy function to edge |
| `delete-func` | Delete a function |
| `reset-func` | Reset a failed function back to `created` so it can be re-shipped |
| `revisions` | List a function's deploy history |
| `rollback` | Instantly revert a function to a previous revision |

**Flags**

| Flag | Description |
|------|-------------|
| `--verbose` / `-v` | Enable verbose logging (available on all commands) |
| `--version` | Print the CLI version and exit — root command only (`telnyx-edge --version`), works without auth or config |

```bash
# Check which version you're running (handy when reporting bugs)
telnyx-edge --version
```

### **Core Examples**

```bash
# Create a new function from template
telnyx-edge new-func --language=go --name=hello-world
cd hello-world

# Deploy to edge
telnyx-edge ship

# Copy from existing example (advanced)
telnyx-edge new-func --from-dir=examples/webhook-receiver --name=my-webhook
telnyx-edge ship --from-dir=my-webhook

# List your functions
telnyx-edge list

# Delete a function
telnyx-edge delete-func hello-world
```

### **Revisions & Rollback**

Every successful `ship` creates an immutable revision. Inspect a function's deploy history and instantly revert to a previous revision — no rebuild or re-upload required.

```bash
# List a function's recent revisions (newest first)
telnyx-edge revisions list my-func

# Roll back to a previous revision (instant traffic switch)
telnyx-edge rollback my-func <revision-id>
```

`revisions list` shows each revision's id (a short image SHA), the ship author, timestamp, deploy status, and which revision is currently active. `rollback` switches the active revision to an existing one within seconds; a revision that never reached a healthy deploy cannot be a rollback target.

### **Resetting a Failed Function**

If a function gets stuck in a failed state (`build_failed`, `deploy_failed`, or `delete_failed`), `reset-func` tears down its deployed resources and returns it to `created` — **without changing the function's id, name, or config** — so you can fix the issue and re-`ship` it.

```bash
# Reset a failed function, then re-deploy it
telnyx-edge reset-func broken-func
telnyx-edge ship --from-dir=broken-func
```

Reset only applies to a failed function. A healthy function (`deploy_ok`) cannot be reset — use `delete-func` instead — and a function with an operation already in progress must finish (or time out) first. Teardown runs asynchronously; the function returns to `created` shortly after the command succeeds.

### **Bindings (Telnyx API Integration)**

Bindings provide automatic Telnyx API key injection for your edge functions, enabling secure access to Telnyx APIs without hardcoding credentials.

```bash
# Create a binding for your organization
telnyx-edge bindings create

# View current binding
telnyx-edge bindings get

# Validate your binding works
telnyx-edge bindings validate

# View binding details
telnyx-edge bindings get

# Update binding (regenerates tokens)
telnyx-edge bindings update

# Delete binding
telnyx-edge bindings delete
```

Once a binding is created, your functions automatically receive `TELNYX_API_KEY` and `TELNYX_BASE_URL` environment variables, allowing seamless use of the Telnyx SDK.

### **KV Storage (Key-Value Storage)**

KV storage provides persistent key-value storage for your edge functions. Create namespaces to store and retrieve data at the edge.

**Namespace management:**
```bash
# List all KV namespaces
telnyx-edge storage kv list

# Create a new KV namespace
telnyx-edge storage kv create --name my-data-store

# Get details of a specific namespace
telnyx-edge storage kv get <namespace-id>

# Delete a namespace
telnyx-edge storage kv delete <namespace-id>

# List with pagination
telnyx-edge storage kv list --page 2 --page-size 20
```

**Key operations:**
```bash
# List keys in a namespace (with optional prefix filter)
telnyx-edge storage kv key list <namespace-id>
telnyx-edge storage kv key list <namespace-id> --prefix config/

# Get a key's value (raw bytes printed to stdout)
telnyx-edge storage kv key get <namespace-id> <key>

# Put a text value
telnyx-edge storage kv key put <namespace-id> <key> "hello world"

# Put a binary value from a file (application/octet-stream)
telnyx-edge storage kv key put <namespace-id> <key> --path ./data.bin

# Put a value with a time-to-live (key auto-expires after the duration)
telnyx-edge storage kv key put <namespace-id> <key> "session token" --ttl 30m

# Delete a key (idempotent)
telnyx-edge storage kv key delete <namespace-id> <key>
```

Keys support hierarchical paths using `/` as a separator (e.g. `config/db/host`). Key list results include cursor-based pagination — when there are more results, use `--cursor <value>` to fetch the next page.

Use `--ttl` to give a key a time-to-live; it is set when the value is written and the key is automatically deleted after the duration elapses. The value is a Go duration string (e.g. `30s`, `5m`, `1h`, `24h`) and must be a whole number of seconds — at least `1s`, no sub-second precision. Keys written without `--ttl` persist until explicitly deleted.

Once a KV namespace is created, you can bind it to your functions and access it via the runtime API to store and retrieve data.

---

## 📦 Installation

Choose one of the following methods:

### **Binary Download (Recommended)**

```bash
# Linux x64 (example)
VERSION=$(curl -s https://api.github.com/repos/team-telnyx/edge-compute/releases/latest | grep '"tag_name"' | cut -d'"' -f4)
if [ -z "$VERSION" ]; then
  echo "Error: Could not fetch latest version. Please check your internet connection or specify a version manually."
  echo "Example: VERSION=v0.0.3"
  exit 1
fi
curl -sSL https://github.com/team-telnyx/edge-compute/releases/download/$VERSION/telnyx-edge-$VERSION-linux-amd64.tar.gz | tar -xzf -
sudo mv telnyx-edge-$VERSION-linux-amd64/telnyx-edge /usr/local/bin/telnyx-edge
chmod +x /usr/local/bin/telnyx-edge
```

**Other platforms:** Replace `linux-amd64` in the URL above with:
- `macos-amd64` (macOS Intel)
- `macos-arm64` (macOS Apple Silicon) 
- `linux-arm64` (Linux ARM64)
- `windows-amd64.zip` (Windows)

---

## ⚙️ Configuration

The CLI stores configuration in:

* `~/.telnyx-edge/config.toml`

Configuration is managed automatically by the CLI. Run `telnyx-edge auth login` to authenticate and configure.

Example `config.toml` (auto-generated):

```toml
api_endpoint = "https://api.telnyx.com"

[oauth]
client_id = "your-client-id"

[tokens]
access_token = "your-access-token"
refresh_token = "your-refresh-token"
```

---

## 🔔 Staying up to date

The CLI checks once a day for a newer release and prints an upgrade notice to stderr if you're behind. It never blocks your command. Disable with `TELNYX_NO_UPDATE_CHECK=1`.

---

## 📖 Documentation

- [📚 Complete Documentation](docs/overview.md) - Full guide for getting started and advanced usage

---

## 🆘 Support

- Issues: [GitHub Issues](https://github.com/team-telnyx/edge-compute-cli/issues)
- Discussions: [GitHub Discussions](https://github.com/team-telnyx/edge-compute-cli/discussions)