#!/bin/bash
# Create a simple test dbt project for feature validation

set -e

TEST_DIR="/tmp/lattice_test_dbt"
rm -rf "$TEST_DIR"
mkdir -p "$TEST_DIR"

cd "$TEST_DIR"

# Initialize git
git init
git config user.name "Test User"
git config user.email "test@example.com"

# Create dbt_project.yml
cat > dbt_project.yml <<'EOF'
name: test_analytics
version: 1.0.0
profile: test_profile

model-paths: ["models"]
EOF

# Create models directory
mkdir -p models

# Create some sample models with good commit messages
cat > models/customers.sql <<'EOF'
-- Customer dimension table
SELECT
    customer_id,
    first_name,
    last_name,
    email,
    created_at
FROM raw.customers
WHERE deleted_at IS NULL  -- Exclude soft-deleted customers
EOF

git add dbt_project.yml models/customers.sql
git commit -m "Add customer dimension excluding soft deletes

Decision: Exclude soft-deleted customers from dimension table
Rationale: Soft deletes indicate customer opted out, should not appear in analytics
"

cat > models/revenue.sql <<'EOF'
-- Daily revenue excluding refunds
SELECT
    DATE(order_date) as date,
    SUM(amount) - COALESCE(SUM(refund_amount), 0) as net_revenue
FROM orders
GROUP BY 1
EOF

git add models/revenue.sql
git commit -m "Calculate revenue net of refunds

Decision: Revenue metric always excludes refunds
Rationale: Accounting team requires net revenue for financial reporting
"

cat > models/active_users.sql <<'EOF'
-- Active users (logged in within 30 days)
SELECT
    user_id,
    last_login_at
FROM users
WHERE last_login_at >= CURRENT_DATE - INTERVAL '30 days'
EOF

git add models/active_users.sql
git commit -m "Define active users as 30-day login window

Decision: Active user = logged in within 30 days
Rationale: Product team standard definition for engagement metrics
"

echo "✅ Test dbt project created at: $TEST_DIR"
echo "Now run: lattice init --path $TEST_DIR && lattice index --path $TEST_DIR"
