# 🏗️ IaC & Infrastructure Automation: Exhaustive Interview Question Bank (Top 30 Questions)

> **Target Level**: Senior / Staff SRE & Platform Engineer (6.5+ YoE)  
> **Evaluation Focus**: Terragrunt DRY architecture, state file locking and concurrency, zero-downtime refactoring, automated drift remediation, and Policy-as-Code (OPA Conftest).

---

### Q1: What is the exact purpose of Terragrunt over vanilla Terraform, and how does it implement DRY configurations at scale?
> **Deep Answer**:
> - **Vanilla Terraform Pain Points**:
>   1. Backend configuration (`backend "s3"`) cannot interpolate variables; S3 bucket names and keys must be copy-pasted across every environment directory.
>   2. Provider configurations (`provider "aws"`) must be duplicated in every folder.
>   3. Passing outputs between distinct state files requires brittle `data "terraform_remote_state"` blocks.
> - **Terragrunt DRY Solutions**:
>   1. **`remote_state` block**: Root `terragrunt.hcl` defines the S3/DynamoDB backend once, and dynamically generates `backend.tf` in child folders with auto-computed paths (`path_relative_to_include()`).
>   2. **`generate` block**: Automatically generates the `provider "aws"` block with the correct environment tags and assumed IAM role.
>   3. **`dependency` block**: Declares explicit DAG dependencies between state files (e.g. `dependency.vpc.outputs.vpc_id`), automatically managing execution order during `terragrunt run-all apply` without coupling state files together.

---

### Q2: What happens under the hood during Terraform state locking, and how do you recover from a corrupted lock in Amazon DynamoDB?
> **Deep Answer**:
> - **State Locking Mechanics**:
>   - When `terraform plan` or `terraform apply` runs with an Amazon S3 backend, Terraform writes an item to the designated **Amazon DynamoDB locking table** (`LockID = "<bucket>/<path>/terraform.tfstate-md5"`).
>   - If another engineer or CI pipeline attempts to execute concurrently, DynamoDB conditional writes fail with `Error acquiring the state lock: ConditionalCheckFailedException`.
>   - Once the operation completes and the new state is uploaded to S3, the lock item is deleted from DynamoDB.
> - **Recovering from Stale Locks**:
>   - If a CI runner was forcefully killed (`SIGKILL`) or crashed mid-apply, the DynamoDB lock remains active.
>   - **Step 1**: Verify no active process is running against the infrastructure.
>   - **Step 2**: Run `terraform force-unlock <Lock-Info-ID>`.
>   - **Step 3**: Alternatively, delete the specific `LockID` item directly from the DynamoDB table via AWS CLI / Console.

---

### Q3: How do you refactor monolithic Terraform code (moving resources between modules) with zero downtime and zero infrastructure recreation?
> **Deep Answer**:
> - **The Problem**: In older Terraform versions, renaming a resource or moving it into a child module caused Terraform to plan a **Destroy and Create**, deleting live databases or load balancers.
> - **Modern Declarative Refactoring with `moved` Blocks**:
>   - Terraform 1.1+ supports declarative `moved` blocks in code:
>     ```hcl
>     # In your updated module code:
>     moved {
>       from = aws_instance.web_server
>       to   = module.compute.aws_instance.web_server[0]
>     }
>     ```
>   - When `terraform plan` runs, it detects the `moved` block and executes an internal state address update **without touching the live cloud resource**.
> - **Imperative Alternative (`terraform state mv`)**:
>   ```bash
>   terraform state mv aws_instance.web_server module.compute.aws_instance.web_server[0]
>   ```

---

### Q4: How do you design an automated Drift Detection and Remediation pipeline for 500+ Terraform modules?
> **Deep Answer**:
> 1. **Scheduled Drift Cron Job**:
>    - A GitHub Actions / Atlantis workflow runs daily at 6:00 AM UTC:
>      ```bash
>      terragrunt run-all plan -detailed-exitcode -no-color
>      ```
>    - `terraform plan -detailed-exitcode` returns:
>      - `0`: Succeeded with empty diff (No drift).
>      - `1`: Execution error / provider crash.
>      - `2`: **Succeeded with non-empty diff (DRIFT DETECTED)**.
> 2. **Alerting & Escalation**:
>    - If exit code `2` is returned, the pipeline formats the JSON diff, posts a summary to the `#infra-drift-alerts` Slack channel, and tags the module owners.
> 3. **Automated vs Manual Remediation Policy**:
>    - **Low-Risk Tags/Security Groups**: Auto-apply to reconcile drift back to Git truth.
>    - **Stateful Compute/Databases**: Require human review to avoid overwriting emergency hotfixes before changes are backported to Git.

---

### Q5: How do you implement Policy-as-Code using Open Policy Agent (OPA) / Conftest to block expensive or insecure Terraform plans in CI?
> **Deep Answer**:
> 1. **Generate Plan JSON**:
>    ```bash
>    terraform plan -out=tfplan.binary
>    terraform show -json tfplan.binary > tfplan.json
>    ```
> 2. **Author Rego Policies (e.g. Disallow Unencrypted EBS Volumes)**:
>    ```rego
>    package terraform.ebs
>    
>    deny[msg] {
>        resource := input.resource_changes[_]
>        resource.type == "aws_ebs_volume"
>        resource.change.actions[_] == "create"
>        not resource.change.after.encrypted
>        msg := sprintf("EBS Volume '%v' must have 'encrypted = true'!", [resource.address])
>    }
>    ```
> 3. **CI Gate Evaluation**:
>    ```bash
>    conftest test tfplan.json --policy policies/
>    ```
>    - If any `deny` rule triggers, Conftest returns exit code 1, **blocking the PR from being merged or applied via Atlantis**.

---

### Q6: What is the Terraform Graph Engine and how does it compute DAG dependencies and concurrency?
> **Deep Answer**:
> - Terraform constructs a **Directed Acyclic Graph (DAG)** of all resources:
>   - Nodes: Resources, modules, providers, variables, outputs.
>   - Edges: Implicit dependencies (references like `vpc_id = aws_vpc.main.id`) and explicit dependencies (`depends_on = [aws_iam_role_policy.attach]`).
> - **Topological Sort & Parallelism**:
>   - Terraform walks independent branches of the DAG concurrently (default `-parallelism=10`).
>   - If cyclic dependencies exist ($A \rightarrow B \rightarrow A$), the graph validator returns `Cycle in graph` before any cloud API is called.

---

### Q7: How do you manage Sensitive Values and Secrets in Terraform state files securely?
> **Deep Answer**:
> - **The State File Vulnerability**: The `terraform.tfstate` file stores sensitive attributes (passwords, private keys) in **plaintext JSON** even if marked `sensitive = true` in HCL code!
> - **Defenses**:
>   1. **Encrypted Storage**: S3 backend bucket must have Server-Side Encryption with a customer-managed AWS KMS key (SSE-KMS) and strict bucket policies.
>   2. **Ephemeral Dynamic Credentials**: Use Vault / AWS Secrets Manager with dynamic credential generation rather than hardcoding static database passwords into Terraform resources.
>   3. **State Access Auditing**: Restrict access to the S3 state bucket strictly to the CI/CD deployment role; human engineers should have zero read access to production state files.

---

### Q8: What are Terraform `import` blocks (Terraform 1.5+) and how do they replace legacy `terraform import` commands?
> **Deep Answer**:
> - **Legacy `terraform import`**:
>   - Imperative command: `terraform import aws_s3_bucket.data my-bucket-name`.
>   - Modifies the state file immediately, but leaves the HCL code blank, requiring manual, error-prone authoring of matching configuration blocks.
> - **Modern Declarative `import` Blocks**:
>   - Author in code:
>     ```hcl
>     import {
>       to = aws_s3_bucket.customer_data
>       id = "my-customer-bucket-prod"
>     }
>     ```
>   - Generates matching HCL automatically: `terraform plan -generate-config-out=generated.tf`.
>   - Reviewed and audited as part of standard Git pull request reviews before application.

---

### Q9: Compare Atlantis vs Spacelift vs Terraform Cloud for GitOps IaC automation.
> **Deep Answer**:
> - **Atlantis**:
>   - Open-source, self-hosted Kubernetes deployment.
>   - Comment-driven PR workflow (`atlantis plan`, `atlantis apply`).
>   - Simple, developer-friendly, zero external SaaS dependencies.
> - **Spacelift**:
>   - Sophisticated policy-as-code engine (native OPA Rego evaluation at pre-plan, post-plan, and pre-apply).
>   - Multi-IaC support (Terraform, OpenTofu, Pulumi, CloudFormation, Ansible).
>   - Native drift detection and automated state tracking.
> - **Terraform Cloud**:
>   - HashiCorp managed SaaS. Strong VCS integration and Sentinel policy engine.
>   - High cost based on managed resource counts (RUM billing).

---

### Q10: How do you design dynamic Terraform modules using `for_each`, `dynamic` blocks, and `lookup` functions?
> **Deep Answer**:
> - **`for_each` on Maps (Avoid `count` on lists)**:
>   - `count` indexes resources by integer (`[0]`, `[1]`). Removing an item from the middle of the list causes Terraform to destroy and recreate all subsequent resources!
>   - `for_each` keys resources by unique string keys (`each.key`), ensuring safe additions and deletions.
> - **`dynamic` Blocks (Repeated Nested Arguments)**:
>   ```hcl
>   dynamic "ingress" {
>     for_each = var.ingress_rules
>     content {
>       description = ingress.value.description
>       from_port   = ingress.value.port
>       to_port     = ingress.value.port
>       protocol    = "tcp"
>       cidr_blocks = ingress.value.cidrs
>     }
>   }
>   ```

---

### Q11: What is the Terraform Provider SDK (Framework) and how does a custom provider interact with cloud APIs?
> **Deep Answer**:
> - **Terraform Plugin Protocol (gRPC)**: Terraform Core communicates with providers over a local gRPC socket.
> - **CRUD Operations**: Every resource schema implements four core Go functions:
>   1. `Create()`: Calls external REST API $\rightarrow$ Sets state ID.
>   2. `Read()`: Queries REST API $\rightarrow$ Updates in-memory state.
>   3. `Update()`: Detects changed attributes $\rightarrow$ Issues PATCH/PUT API calls.
>   4. `Delete()`: Calls DELETE API $\rightarrow$ Removes resource from state.

---

### Q12: How do you handle circular dependencies between Terraform resources?
> **Deep Answer**:
> - **Example**: Security Group A allows ingress from Security Group B, and Security Group B allows ingress from Security Group A.
> - **Solution**: Extract the circular attribute into a standalone child resource:
>   - Create `aws_security_group.sg_a` and `aws_security_group.sg_b` with zero inline ingress rules.
>   - Create separate `aws_security_group_rule` resources referencing both SGs after creation, cleanly breaking the DAG cycle.

---

### Q13: What is OpenTofu, why was it created, and what are the architectural differences from Terraform?
> **Deep Answer**:
> - **Origin**: Created by the Linux Foundation as a fully open-source (MPL-2.0) fork of Terraform following HashiCorp's license change to BSL (Business Source License).
> - **Innovations in OpenTofu**:
>   - **Native State Encryption**: Encrypts `terraform.tfstate` at rest client-side using AWS KMS, GCP KMS, or AES-GCM before writing to the remote backend.
>   - **Early Variable Evaluation**: Allows variables in backend configurations and module providers.
>   - **Drop-in Compatibility**: 100% syntactically compatible with standard Terraform HCL.

---

### Q14: How do you structure a multi-region disaster recovery deployment in Terragrunt?
> **Deep Answer**:
> - Reusable module in `_envcommon/aurora-cluster.hcl`.
> - Regional folders:
>   - `prod/us-east-1/aurora/terragrunt.hcl`: Defines primary database.
>   - `prod/eu-west-1/aurora/terragrunt.hcl`: Declares dependency on `us-east-1` and provisions Aurora Global Secondary replica.
> - `terragrunt run-all apply` automatically evaluates the dependency graph and provisions the primary cluster first.

---

### Q15: How do you test Terraform modules automatically using `terratest` in Go?
> **Deep Answer**:
> 1. **Terratest Lifecycle**:
>    - `terraform.InitAndApply(t, terraformOptions)`: Spawns real temporary cloud infrastructure.
> 2. **Validation**:
>    - Makes HTTP requests to the provisioned load balancer URL or queries AWS SDK to verify encryption and tags.
> 3. **Guaranteed Teardown**:
>    - `defer terraform.Destroy(t, terraformOptions)`: Guarantees complete cleanup of temporary AWS resources even if unit test assertions fail.

---

### Q16: What is the purpose of the `lifecycle` block (`prevent_destroy`, `create_before_destroy`, `ignore_changes`)?
> **Deep Answer**:
> - **`prevent_destroy = true`**: Rejects any `terraform destroy` or replacement plan (essential guardrail for production databases).
> - **`create_before_destroy = true`**: Spawns the new replacement resource before tearing down the old resource (zero-downtime DNS/cert replacements).
> - **`ignore_changes = [tags, desired_count]`**: Ignores external changes made by autoscalers or external taggers without reverting them during next apply.

---

### Q17: How do you prevent Terraform Plan files from being tampered with between CI plan and apply stages?
> **Deep Answer**:
> - Save plan as binary artifact: `terraform plan -out=tfplan.binary`.
> - Compute cryptographic SHA256 checksum in CI: `sha256sum tfplan.binary > tfplan.sha256`.
> - In apply stage: Verify checksum before running `terraform apply tfplan.binary` to prevent man-in-the-middle plan modifications.

---

### Q18: What is the difference between `local-exec` vs `remote-exec` provisioners, and why are they considered an anti-pattern?
> **Deep Answer**:
> - **`local-exec`**: Runs shell commands locally on the machine executing Terraform.
> - **`remote-exec`**: SSHs into the created VM to run shell scripts.
> - **Why it is an Anti-Pattern**:
>   - Breaks idempotency and declarative state tracking.
>   - Requires open SSH ports and hardcoded credentials.
>   - Replaced by Cloud-Init, Packer pre-baked AMIs, Kubernetes manifests, or Ansible.

---

### Q19: How do you manage multi-account AWS provider aliases dynamically in Terraform?
> **Deep Answer**:
> ```hcl
> provider "aws" {
>   alias  = "us_east_1"
>   region = "us-east-1"
> }
> 
> provider "aws" {
>   alias  = "eu_west_1"
>   region = "eu-west-1"
> }
> 
> module "dns_record" {
>   source    = "./modules/route53"
>   providers = { aws = aws.us_east_1 }
> }
> ```

---

### Q20: How do you implement automated Cost Estimation for Terraform PRs using Infracost?
> **Deep Answer**:
> 1. Run Infracost in GitHub Actions against the generated plan JSON:
>    ```bash
>    infracost breakdown --path=tfplan.json --format=json --out-file=infracost.json
>    ```
> 2. Infracost queries cloud pricing APIs and posts a formatted diff comment on the GitHub PR:
>    > 💰 **Monthly Cost Impact**: +$420.50/month (+12%)
> 3. Enforce budget policy: If estimated monthly cost increase $> \$1,000$, require mandatory approval from FinOps Team Lead before merge.

---

### Q21: How do you configure LocalStack in Terraform for offline integration testing without paying AWS cloud bills?
> **Deep Answer**:
> - Override AWS service endpoints in the `provider "aws"` block:
>   ```hcl
>   provider "aws" {
>     access_key = "test"
>     secret_key = "test"
>     region     = "us-east-1"
>     s3_use_path_style = true
>     endpoints {
>       s3       = "http://localhost:4566"
>       dynamodb = "http://localhost:4566"
>       sqs      = "http://localhost:4566"
>     }
>   }
>   ```
> - Enables running fast local integration test suites in CI without real cloud credentials.

---

### Q22: What causes "Partial Apply" states in Terraform and how do you resolve orphaned cloud resources?
> **Deep Answer**:
> - **Cause**: During `terraform apply`, Terraform creates Resource A, but encounters a network timeout or IAM error while creating Resource B. The process exits with an error.
> - **State Integrity**: Terraform automatically writes Resource A to the remote state file before exiting.
> - **Resolution**:
>   - Re-run `terraform apply`: Terraform reads state, sees Resource A already exists, and resumes by creating only Resource B.
>   - If Resource A was partially created in AWS but failed to save in state: Run `terraform import` to reconcile state before re-applying.

---

### Q23: What are Terraform `check` blocks (Terraform 1.5+) and how do they differ from `precondition` / `postcondition` blocks?
> **Deep Answer**:
> - **`precondition` / `postcondition`**:
>   - Hard assertions. If an assertion fails, **Terraform immediately halts execution with an error**.
> - **`check` blocks**:
>   - **Non-blocking continuous validation assertions**:
>     ```hcl
>     check "alb_health" {
>       data "http" "alb_response" {
>         url = "https://${aws_lb.main.dns_name}/health"
>       }
>       assert {
>         condition     = data.http.alb_response.status_code == 200
>         error_message = "ALB returned non-200 health check status!"
>       }
>     }
>     ```
>   - Emits warnings in plan/apply without failing the build, providing continuous health feedback.

---

### Q24: Explain Terragrunt multiple includes: `include "root"` vs `include "env"`.
> **Deep Answer**:
> - In complex enterprise setups:
>   - `include "root"`: Inherits the global S3 remote state and AWS provider generation from root `terragrunt.hcl`.
>   - `include "env"`: Inherits environment-level variables (`env = "prod"`, `vpc_cidr = "10.0.0.0/16"`) from parent `env.hcl`.
> - Allows deep DRY inheritance hierarchies across `root -> org -> environment -> region -> component`.

---

### Q25: Compare Pulumi vs Terraform / Terragrunt for enterprise platform engineering.
> **Deep Answer**:
> - **Terraform / Terragrunt (HCL - Declarative)**:
>   - Strict DSL. Easy for security teams to parse with static analysis (Rego/Checkov).
>   - Limitations: HCL lacks real loops, functions, and object-oriented abstractions.
> - **Pulumi (General-Purpose Languages - TypeScript/Go/Python)**:
>   - Full power of real programming languages: classes, loops, native unit test frameworks (Jest/Go testing), and IDE autocompletion.
>   - **Tradeoff**: Increased risk of engineers writing complex, non-deterministic imperative code (e.g. database lookups inside loops) that breaks IaC reproducibility.

---

### Q26: How do you manage Zero-Downtime Database Password Rotation in Terraform without state drift?
> **Deep Answer**:
> 1. **Do not store passwords in Terraform HCL**:
>    - Configure AWS RDS with `manage_master_user_password = true`.
> 2. **AWS Secrets Manager Integration**:
>    - AWS RDS automatically generates the master password, writes it to AWS Secrets Manager, and manages automated 30-day rotation using an internal AWS Lambda rotation function.
> 3. **Application Consumption**:
>    - Applications fetch the dynamic password at runtime via Vault / Secrets Store CSI Driver, eliminating all password state tracking in Terraform.

---

### Q27: How do you structure an enterprise Private Terraform Module Registry with semantic release automation?
> **Deep Answer**:
> - Dedicated Git repository per module (`terraform-aws-eks-cluster`).
> - **Release Automation (Semantic Release + Conventional Commits)**:
>   - Commits with `feat:` automatically trigger GitHub Actions to tag `v1.2.0`.
>   - Commits with `fix:` automatically tag `v1.2.1`.
>   - Commits with `BREAKING CHANGE:` bump major version `v2.0.0`.
> - Consumer repos lock modules to minor version ranges (`source = "...?ref=v1.2.0"`).

---

### Q28: Compare Crossplane Provider AWS vs Terraform AWS Controller on Kubernetes.
> **Deep Answer**:
> - **Terraform Controller (ACK / Terraform Operator)**:
>   - Executes `terraform plan` and `terraform apply` asynchronously inside a Kubernetes pod on Git change.
> - **Crossplane (Native Kubernetes Resource Model)**:
>   - Replaces Terraform engine entirely with native Kubernetes controllers calling AWS APIs via Go SDK directly.
>   - Continuously reconciles live infrastructure state every 60 seconds (active self-healing), automatically reverting any out-of-band AWS console modifications.

---

### Q29: How do you detect and remediate drift in Kubernetes resources managed by Terraform's `kubernetes_manifest` provider?
> **Deep Answer**:
> - **The Problem**: Kubernetes controllers dynamically inject default fields and metadata (e.g. `metadata.creationTimestamp`, `spec.clusterIP`) into live objects, causing Terraform to detect permanent spurious drift on every plan.
> - **Remediation**:
>   - Use `computed_fields` attribute in `kubernetes_manifest` to tell Terraform which fields are server-managed.
>   - Alternatively, use **ArgoCD GitOps for in-cluster Kubernetes resources** and reserve Terraform strictly for foundational cloud infrastructure (VPCs, EKS, RDS).

---

### Q30: How do you design multi-cloud Terraform modules abstracting AWS and GCP infrastructure behind a single interface?
> **Deep Answer**:
> 1. **Facade Pattern Module**:
>    - Define common inputs (`variable "cloud_provider" { type = string }`, `variable "cluster_name" { type = string }`).
> 2. **Conditional Child Module Invocation**:
>    ```hcl
>    module "aws_k8s" {
>      count  = var.cloud_provider == "aws" ? 1 : 0
>      source = "./modules/aws-eks"
>    }
>    module "gcp_k8s" {
>      count  = var.cloud_provider == "gcp" ? 1 : 0
>      source = "./modules/gcp-gke"
>    }
>    ```
> 3. **Normalized Outputs**: Expose unified output attributes (`output "kubeconfig" { value = var.cloud_provider == "aws" ? module.aws_k8s[0].kubeconfig : module.gcp_k8s[0].kubeconfig }`).
