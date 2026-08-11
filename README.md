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
| `storage` | Manage storage resources (KV namespaces, SQL databases) |
| `types` | Generate TypeScript types for your bindings |
| `new-func` | Create a new function |
| `ship` | Deploy function to edge |
| `delete-func` | Delete a function |
| `reset-func` | Reset a failed function back to `created` so it can be re-shipped |
| `revisions` | List a function's deploy history |
| `rollback` | Instantly revert a function to a previous revision |
| `inspect` | Show a function's full details |
| `actors` | Manage StatefulActor types |
| `config` | View and change CLI preferences |

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

# Start from code you already have (advanced)
telnyx-edge new-func --from-dir=./my-existing-app --name=my-webhook
telnyx-edge ship --from-dir=my-webhook

# List your functions
telnyx-edge list

# Delete a function (asks for confirmation)
telnyx-edge delete-func hello-world

# ...or skip the prompt, for scripts and CI
telnyx-edge delete-func hello-world --yes
```

Destructive commands name what they are about to destroy and wait for you to type `yes` — the mistake worth catching is a wrong id, which a plain "are you sure?" would miss. Without a terminal they fail with an error naming `--yes` rather than prompting, so a pipeline never hangs on input that will not arrive.

Stop being asked entirely with `TELNYX_EDGE_SKIP_CONFIRMATIONS=1` for a shell or CI job, or `telnyx-edge config set skip_confirmations true` permanently.

### **Revisions & Rollback**

Every successful `ship` creates an immutable revision. Inspect a function's deploy history and instantly revert to a previous revision — no rebuild or re-upload required.

```bash
# List a function's recent revisions (newest first)
telnyx-edge revisions list my-func

# Roll back to a previous revision (instant traffic switch)
telnyx-edge rollback my-func <revision-id>
```

`revisions list` shows each revision's id (a short image SHA), the ship author, timestamp, deploy status, and which revision is currently active. `rollback` switches the active revision to an existing one within seconds; a revision that never reached a healthy deploy cannot be a rollback target.

### **Why a Ship Failed**

When a `ship` fails, `ship status` tells you *why* — classified by where it failed — so you don't have to read the raw build log.

```bash
# One actionable line: the failure reason (or ✅ if the last ship succeeded)
telnyx-edge ship status my-func

# Add the build-log snippet for a build failure
telnyx-edge ship status my-func --logs
```

The reason comes straight from the platform. A **build** failure shows the compiler/build error (and the log snippet under `--logs`); a **deploy**, **platform**, or **security review** failure shows a short explanation on its own line. `ship status` is read-only and accepts a function name or id.

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

### **SQL Databases**

SQL databases give your functions a real SQLite database at the edge. Create a database, apply a schema, and bind it to a function — the function reaches it through `env.<BINDING>` with a familiar prepare/bind/query API.

**Database management:**
```bash
# List all SQL databases
telnyx-edge storage sqldb list

# Create a new database
telnyx-edge storage sqldb create --name my-app-db

# Get details of a specific database
telnyx-edge storage sqldb get <database-id>

# Delete a database
telnyx-edge storage sqldb delete <database-id>
```

A database is ready to use as soon as it reports `provision_ok` — there is no server to size and nothing to deploy per database.

**Running SQL:**
```bash
# Run a statement directly against the database
telnyx-edge storage sqldb execute <database-id> --remote \
  --command "CREATE TABLE links (id INTEGER PRIMARY KEY, url TEXT NOT NULL)"

# Run a .sql file (schema, seed data, an import)
telnyx-edge storage sqldb execute <database-id> --remote --file ./schema.sql

# Machine-readable results
telnyx-edge storage sqldb execute <database-id> --remote \
  --command "SELECT * FROM links" --json
```

`execute` runs SQL out-of-band, so you can bootstrap a schema before writing a single line of function code.

**Migrations:**
```bash
# Create a numbered migration file
telnyx-edge storage sqldb migrations create <database-id> add_links_table

# See what is applied and what is pending
telnyx-edge storage sqldb migrations list <database-id> --remote

# Apply everything pending, in order
telnyx-edge storage sqldb migrations apply <database-id> --remote
```

Migration files live in `migrations/<database>/` with an auto-incrementing numeric prefix. Applied migrations are recorded inside the database itself, so `apply` is safe to re-run — it only applies what is still pending.

**Binding a database to a function** — add the block to your function's manifest (`func.toml`, or `telnyx.toml` if your project uses one):
```toml
[storage.sqldb.DB]
id = "<database-id>"
```

Every function bound to the same id shares one database.

Then use the database from your function:

```ts
import { env } from "@telnyx/edge-runtime";

// One statement, no results.
await env.DB.exec(
  "CREATE TABLE IF NOT EXISTS links (id INTEGER PRIMARY KEY, url TEXT NOT NULL)",
);

// Bind values instead of concatenating them into the SQL.
await env.DB.prepare("INSERT INTO links (url) VALUES (?)").bind(url).run();

// .all() returns every row; .first() returns one value or row.
const { results } = await env.DB.prepare("SELECT id, url FROM links ORDER BY id").all();
const count = await env.DB.prepare("SELECT COUNT(*) AS n FROM links").first<number>("n");
```

Bindings are read from the `env` object exported by `@telnyx/edge-runtime`, so `import` it as shown above. `env.DB` requires `@telnyx/edge-runtime` **0.9.0 or newer**.

Run [`telnyx-edge types`](#typed-bindings) to give `env.DB` its real type.

### **Typed Bindings**

Every binding you declare is reachable in TypeScript as `env.<BINDING>`. `telnyx-edge types` reads your manifest and writes a `telnyx-env.d.ts` at the project root giving each one its real type:

```bash
telnyx-edge types
```

```text
✓ Generated binding types for 2 binding(s) at telnyx-env.d.ts
    env.DB → SqlDatabase
    env.CACHE → KvNamespace
```

With that file in place, `env.DB` autocompletes with the full query API and a misspelled or undeclared binding fails to compile instead of surfacing as `undefined` at runtime.

```ts
import { env } from "@telnyx/edge-runtime";

const { results } = await env.DB.prepare("SELECT id FROM links").all();
await env.CACHE.put("last-run", new Date().toISOString());

env.TYPOED_NAME;  // compile error — not a declared binding
```

Re-run it whenever you add, rename, or remove a binding. It reads only your local manifest — no network, no authentication — so it is safe to run in a build script or a pre-commit hook.

Binding types require a recent `@telnyx/edge-runtime`; `types` checks the installed version and tells you which one a given binding needs.

### **StatefulActors**

A StatefulActor is a named, addressable object that owns its state. Each instance is identified by a name you choose, and the platform guarantees there is **one** live instance per name — so calls to the same name are serialized and never race. It is the right tool when a piece of state has a natural identity: one room, one session, one tenant, one document.

Actors are TypeScript-only and declared in a `telnyx.toml` manifest:

```toml
name = "chat"
main = "src/index.ts"
compatibility_date = "2026-05-01"

[[actors]]
binding = "ROOM"     # how your code reaches it
type    = "ChatRoom" # the exported class name
```

Scaffold a project with the actor wiring already in place:

```bash
telnyx-edge new-func --actor --name chat
```

Your module exports both the actor class and the HTTP handler:

```ts
import { ChatRoom } from "./chat-room.js";
export { ChatRoom };            // registers the class with the runtime

export default {
  async fetch(req: Request, env: Env): Promise<Response> {
    // Address an instance by name — same name, same instance, every time.
    const room = env.ROOM.idFromName("general");
    const messages = await room.history();
    return Response.json({ messages });
  },
};
```

Extend `StatefulActor` to get `this.ctx`. `ctx.storage` is that instance's private state — a key/value API, plus `ctx.storage.sql` for a full SQLite database belonging to that one instance. `sql.exec(...)` takes the statement and its bind parameters and returns a cursor; call `.toArray()` for the rows:

```ts
import { StatefulActor } from "@telnyx/edge-runtime";

type Message = { id: number; body: string };

export class ChatRoom extends StatefulActor {
  async post(body: string) {
    this.ctx.storage.sql.exec(
      "CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, body TEXT)",
    );
    this.ctx.storage.sql.exec("INSERT INTO messages (body) VALUES (?)", body);
  }

  async history(): Promise<Message[]> {
    return this.ctx.storage.sql
      .exec<Message>("SELECT id, body FROM messages ORDER BY id")
      .toArray();
  }
}
```

Writes are acknowledged only once they are durable, and an instance rehydrates its database when it next activates — so state survives the pod being replaced.

**Managing deployed actor types:**
```bash
# List the actor types in your account
telnyx-edge actors list

# Inspect one type
telnyx-edge actors inspect ChatRoom

# Delete a type and its instances
telnyx-edge actors delete ChatRoom
```

`telnyx-edge inspect <function>` shows every binding a function declares — actors, SQL databases, KV namespaces and secrets — alongside its other details. Each row gives the `env.<NAME>` handle, the kind of binding, what it targets, and its status.

**`ctx.storage.sql` is not the same thing as a SQL database.** Both give you SQLite, and the difference is ownership:

| | `ctx.storage.sql` | `storage sqldb` |
|---|---|---|
| belongs to | one actor instance | your account |
| created by | existing — activate an instance | `telnyx-edge storage sqldb create` |
| reached with | `ctx.storage.sql` inside the class | `env.DB` from any bound function |
| shared between functions | no | yes |
| CLI access | none | `execute`, `migrations` |

Use `ctx.storage.sql` when the data belongs to one entity and nothing else should touch it. Use a SQL database when several functions query the same data.

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

- [📚 Complete Documentation](https://developers.telnyx.com/docs/edge-compute) - Full guide for getting started and advanced usage

---

## 🆘 Support

- Issues: [GitHub Issues](https://github.com/team-telnyx/edge-compute/issues)