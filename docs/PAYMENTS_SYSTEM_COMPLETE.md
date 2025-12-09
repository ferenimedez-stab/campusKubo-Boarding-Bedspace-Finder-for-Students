# Payments Management - Complete System Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│              ADMIN PAYMENTS VIEW                         │
│  (admin_payments_view.py)                               │
│  - Statistics Dashboard                                 │
│  - Status Filter                                        │
│  - Payment Table with Refund Actions                    │
│  - Refund Processing Modal                              │
│  - Payment Details Modal                                │
└────────────────┬────────────────────────────────────────┘
                 │ Uses
                 ↓
┌─────────────────────────────────────────────────────────┐
│           ADMIN SERVICE LAYER                            │
│  (admin_service.py)                                     │
│  - get_all_payments_admin()                             │
│  - process_refund()                                     │
│  - update_payment_status()                              │
│  - get_payment_statistics()                             │
└────────────────┬────────────────────────────────────────┘
                 │ Uses
                 ↓
┌─────────────────────────────────────────────────────────┐
│          DATABASE LAYER                                  │
│  (db.py)                                                │
│  - get_all_payments_admin()                             │
│  - process_payment_refund()                             │
│  - update_payment_status()                              │
│  - get_payment_statistics()                             │
│                                                         │
│          PAYMENT DATA MODEL                             │
│  (models/payment.py)                                    │
│  - Payment dataclass                                    │
│  - from_db_row()                                        │
│  - to_dict()                                            │
└────────────────┬────────────────────────────────────────┘
                 │ Persists to
                 ↓
┌─────────────────────────────────────────────────────────┐
│        SQLITE DATABASE (campuskubo.db)                  │
│                                                         │
│  payments TABLE                                         │
│  ├─ id, user_id, listing_id                           │
│  ├─ amount, status, payment_method                      │
│  ├─ created_at, updated_at                             │
│  ├─ refunded_amount, refund_reason                      │
│  └─ notes                                               │
│                                                         │
│  FOREIGN KEYS:                                          │
│  ├─ user_id → users(id)                               │
│  └─ listing_id → listings(id)                          │
└─────────────────────────────────────────────────────────┘
```

---

## Data Flow Diagrams

### Viewing Payments
```
Admin Views Payments Page
    ↓
AdminPaymentsView.build()
    ↓
_render_table()
    ↓
AdminService.get_all_payments_admin(status_filter)
    ↓
DB.get_all_payments_admin(status_filter)
    ↓
Query: SELECT FROM payments
       LEFT JOIN users
       LEFT JOIN listings
       WHERE status = ? (if filtered)
    ↓
Return List[Dict] with full payment info
    ↓
Render DataTable with 8 items per page
    ↓
Display to Admin
```

### Processing Refund
```
Admin Clicks "Refund" Button
    ↓
_open_refund_dialog(payment_id)
    ↓
Modal Opens with form fields
    ↓
Admin Fills:
├─ Refund Amount (₱)
├─ Refund Reason (text)
└─ Clicks "Process Refund"
    ↓
_submit_refund()
    ↓
Validate:
├─ Amount is numeric and > 0
├─ Reason is not empty
└─ Amount ≤ remaining balance
    ↓
AdminService.process_refund()
    ↓
DB.process_payment_refund()
    ↓
UPDATE payments SET:
├─ refunded_amount = refunded_amount + amount
├─ refund_reason = reason
├─ status = 'refunded' (if fully refunded)
├─ updated_at = now()
└─ WHERE id = payment_id
    ↓
RefreshService.notify_refresh()
    ↓
All registered admin views refresh
    ↓
AdminPaymentsView._on_global_refresh()
    ↓
_render_table()
_render_statistics()
    ↓
Updated table with refund reflected
Updated statistics showing new refund total
```

### Viewing Statistics
```
Statistics Panel Expands
    ↓
_render_statistics()
    ↓
AdminService.get_payment_statistics()
    ↓
DB.get_payment_statistics()
    ↓
Run multiple queries:
├─ Total revenue, refunds, net revenue
├─ Count of transactions
├─ Average, min, max amounts
├─ Breakdown by payment method
└─ Breakdown by status
    ↓
Return Dict with all statistics
    ↓
Build stat cards with:
├─ Total Revenue: ₱X,XXX.XX (GREEN)
├─ Total Refunds: ₱X,XXX.XX (ORANGE)
├─ Net Revenue: ₱X,XXX.XX (BLUE)
├─ Transactions: NNN (PURPLE)
└─ Avg Transaction: ₱X,XXX.XX (INDIGO)
    ↓
Display to Admin
```

---

## Database Schema

### Payments Table
```sql
CREATE TABLE payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,                          -- Who paid
    listing_id INTEGER,                       -- Which listing
    amount REAL,                              -- Payment amount
    status TEXT DEFAULT 'completed',          -- Payment status
    payment_method TEXT DEFAULT 'unknown',    -- How paid
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    refunded_amount REAL DEFAULT 0,           -- Total refunded
    refund_reason TEXT,                       -- Why refunded
    notes TEXT,                               -- Admin notes
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY(listing_id) REFERENCES listings(id) ON DELETE SET NULL
);
```

### Sample Data
```sql
-- Completed payment
INSERT INTO payments VALUES
(1, 101, 5, 15000.00, 'completed', 'cash', '2024-01-15', '2024-01-15', 0, NULL, NULL);

-- Fully refunded payment
INSERT INTO payments VALUES
(2, 102, 6, 12000.00, 'refunded', 'card', '2024-01-10', '2024-01-20', 12000.00, 'Duplicate booking', 'Refund processed 2024-01-20');

-- Partially refunded payment
INSERT INTO payments VALUES
(3, 103, 7, 20000.00, 'completed', 'online_banking', '2024-01-05', '2024-01-18', 5000.00, 'Partial refund for lease termination', NULL);
```

---

## Key Algorithms

### Refund Processing Algorithm
```python
def process_payment_refund(payment_id, refund_amount, reason):
    # 1. Fetch current payment
    payment = GET payment WHERE id = payment_id

    # 2. Calculate balances
    original = payment.amount
    already_refunded = payment.refunded_amount
    remaining = original - already_refunded

    # 3. Validate refund amount
    IF refund_amount > remaining:
        RETURN (False, "Refund exceeds remaining balance")
    IF refund_amount <= 0:
        RETURN (False, "Refund amount must be > 0")

    # 4. Calculate new status
    new_refunded_total = already_refunded + refund_amount
    IF new_refunded_total >= original:
        new_status = 'refunded'
    ELSE:
        new_status = 'completed'  # Partial refund

    # 5. Update database
    UPDATE payments SET
        refunded_amount = new_refunded_total,
        refund_reason = reason,
        status = new_status,
        updated_at = NOW()
    WHERE id = payment_id

    # 6. Return success
    RETURN (True, "Refund of ₱X,XXX.XX processed successfully")
```

### Statistics Calculation Algorithm
```python
def get_payment_statistics():
    stats = {}

    # 1. Revenue calculations
    stats['total_revenue'] = SUM(amount) WHERE status IN ('completed', 'refunded')
    stats['total_refunds'] = SUM(refunded_amount) WHERE status IN ('completed', 'refunded')
    stats['net_revenue'] = stats['total_revenue'] - stats['total_refunds']

    # 2. Transaction metrics
    stats['total_transactions'] = COUNT(*) WHERE status IN ('completed', 'refunded')
    stats['avg_transaction'] = AVG(amount) WHERE status IN ('completed', 'refunded')
    stats['min_transaction'] = MIN(amount) WHERE status IN ('completed', 'refunded')
    stats['max_transaction'] = MAX(amount) WHERE status IN ('completed', 'refunded')

    # 3. Payment method breakdown
    FOR EACH method IN (SELECT DISTINCT payment_method):
        stats['payment_methods'][method] = {
            'count': COUNT(*) WHERE payment_method = method,
            'total': SUM(amount) WHERE payment_method = method
        }

    # 4. Status breakdown
    FOR EACH status IN (SELECT DISTINCT status):
        stats['statuses'][status] = {
            'count': COUNT(*) WHERE status = status,
            'total': SUM(amount) WHERE status = status
        }

    RETURN stats
```

---

## Payment Status Lifecycle

```
┌─────────────┐
│  PENDING    │ ← Payment initiated, awaiting completion
└──────┬──────┘
       │ (Payment received)
       ↓
┌─────────────┐
│ COMPLETED   │ ← Normal payment completed
└──────┬──────┘
       │ (Refund requested)
       ├──────────────────────────────┐
       │ (Full refund)                 │ (Partial refund)
       ↓                               ↓
┌─────────────────┐    (Still eligible for more refunds)
│   REFUNDED      │
└─────────────────┘

Alternative paths:

PENDING → FAILED ← Payment failed (declined card, etc.)
PENDING → COMPLETED ← Successful payment
FAILED → COMPLETED ← Payment retry successful
```

---

## Refund Examples

### Example 1: Full Refund
```
Original Payment: ₱15,000
Refunded Amount: ₱0
Admin Processes: ₱15,000 refund
Result:
- Status changes to "refunded"
- Refunded Amount becomes ₱15,000
- No more refunds possible
```

### Example 2: Partial Refund (Single)
```
Original Payment: ₱20,000
Refunded Amount: ₱0
Admin Processes: ₱5,000 refund (lease termination)
Result:
- Status remains "completed"
- Refunded Amount becomes ₱5,000
- Can still refund ₱15,000 more
```

### Example 3: Partial Refund (Multiple)
```
Original Payment: ₱20,000
Refunded Amount: ₱5,000 (from Example 2)
Admin Processes: ₱15,000 refund (full lease cancellation)
Result:
- Status changes to "refunded"
- Refunded Amount becomes ₱20,000
- Fully refunded, no more refunds possible
```

### Example 4: Over-Refund Attempt (FAILS)
```
Original Payment: ₱15,000
Refunded Amount: ₱10,000
Admin Attempts: ₱10,000 refund (remaining = ₱5,000)
Result:
- ERROR: "Refund amount (₱10,000) exceeds remaining balance (₱5,000)"
- No changes made
- User shown error message
```

---

## UI Component Breakdown

### Statistics Dashboard
```
┌─────────────────────────────────────────┐
│        PAYMENT STATISTICS               │
├─────────────────────────────────────────┤
│ ┌────────────┐  ┌────────────┐  ...    │
│ │ 💰 Total   │  │ ↩️  Total  │         │
│ │ Revenue    │  │ Refunds    │         │
│ │ ₱XXX,XXX   │  │ ₱XXX,XXX   │         │
│ └────────────┘  └────────────┘         │
│ ┌────────────┐  ┌────────────┐  ...    │
│ │ 📈 Net     │  │ 🧾 Trans   │         │
│ │ Revenue    │  │ Count      │         │
│ │ ₱XXX,XXX   │  │ NNN        │         │
│ └────────────┘  └────────────┘         │
└─────────────────────────────────────────┘
```

### Payment Table
```
┌──────┬────────┬─────────┬────────┬──────────┬──────────┬──────────┬────────┬──────────┐
│ ID   │ User   │ Listing │ Amount │ Refunded │ Status   │ Method   │ Date   │ Actions  │
├──────┼────────┼─────────┼────────┼──────────┼──────────┼──────────┼────────┼──────────┤
│PMT001│user@.. │Main St  │₱15,000 │₱0       │ ✓ Compl  │ Cash     │ Jan 15 │[Refund] ✓│
│PMT002│user@.. │2nd Ave  │₱12,000 │₱12,000 │ ↩ Refund │ Card     │ Jan 10 │[Details] │
│PMT003│user@.. │3rd Blvd │₱20,000 │₱5,000  │ ✓ Compl  │ Online   │ Jan 05 │[Refund] ✓│
└──────┴────────┴─────────┴────────┴──────────┴──────────┴──────────┴────────┴──────────┘
```

### Refund Dialog
```
┌─────────────────────────────────────┐
│   PROCESS REFUND                    │
├─────────────────────────────────────┤
│                                     │
│ Payment ID: PMT001                  │
│ ─────────────────────────────────── │
│                                     │
│ Refund Amount (₱)                   │
│ [15000           ]                  │
│                                     │
│ Reason                              │
│ [Customer requested full refund...] │
│ [                                 ] │
│ [                                 ] │
│                                     │
│              [Cancel] [Process Ref] │
└─────────────────────────────────────┘
```

---

## Error Handling

### Frontend Validation
```
User Action → Validate Input
    ↓
IF amount not numeric THEN
    Show: "Enter a valid refund amount"
    RETURN (no submission)

IF amount ≤ 0 THEN
    Show: "Refund amount must be greater than 0"
    RETURN (no submission)

IF reason is empty THEN
    Show: "Please provide a refund reason"
    RETURN (no submission)

IF all valid THEN
    Submit to backend
```

### Backend Validation
```
Backend Receives Request
    ↓
IF payment not found THEN
    RETURN (False, "Payment not found")

IF refund_amount > remaining_balance THEN
    RETURN (False, "Refund amount exceeds remaining balance")

IF status not in (completed, refunded) THEN
    RETURN (False, "Cannot refund this payment")

IF all valid THEN
    Process refund
    RETURN (True, "Refund processed successfully")
```

---

## Performance Considerations

### Query Optimization
- **Index on created_at**: For sorting (default order)
- **Index on status**: For filtering by status
- **Index on user_id**: For user-specific queries (if needed)

### Pagination Strategy
- **Page Size**: Fixed 8 items per page
- **Calculation**: total_pages = ceil(total_items / page_size)
- **Memory**: Only current page kept in memory

### Statistics Caching
- **Recalculated on each request** (ensures accuracy)
- **Consider caching** if performance becomes an issue
- **Current: Acceptable** for admin-level frequency

---

## Security Measures

### SQL Injection Prevention
- ✅ All queries use parameterized statements
- ✅ No string concatenation in SQL
- ✅ User input always passed as parameter

### Authentication
- ✅ All operations require admin authentication
- ✅ SessionState.is_admin() checked before rendering view
- ✅ Redirect to login if not authenticated

### Data Integrity
- ✅ Foreign key constraints maintained
- ✅ Transactions with rollback on error
- ✅ Audit trail (refund_reason + notes logged)

### Input Validation
- ✅ Amount must be numeric and positive
- ✅ Reason must be non-empty
- ✅ Status must be valid enum value
- ✅ Payment must exist before update

---

## Testing Strategy

### Unit Tests
```python
def test_process_refund_success():
    # Test successful refund
    assert process_refund(1, 5000, "Test") == (True, msg)

def test_process_refund_over_amount():
    # Test over-refund fails
    assert process_refund(1, 50000, "Test") == (False, msg)

def test_get_statistics():
    # Test statistics calculations
    stats = get_payment_statistics()
    assert stats['total_revenue'] > 0
    assert stats['net_revenue'] <= stats['total_revenue']

def test_update_payment_status():
    # Test status update
    assert update_payment_status(1, 'failed') == (True, msg)
```

### Integration Tests
```python
def test_refund_workflow():
    # 1. Create payment
    # 2. Verify initial status
    # 3. Process refund
    # 4. Verify status changed
    # 5. Verify amount updated
    # 6. Verify RefreshService notified

def test_statistics_after_refund():
    # 1. Get initial stats
    # 2. Process refund
    # 3. Get updated stats
    # 4. Verify refund total increased
    # 5. Verify net revenue decreased
```

---

## Glossary

| Term | Definition |
|------|-----------|
| **Payment** | A financial transaction from user to platform |
| **Refund** | Return of payment amount to user |
| **Partial Refund** | Refund of less than full payment amount |
| **Full Refund** | Refund of entire payment amount |
| **Status** | Current state of payment (completed, refunded, pending, failed) |
| **Payment Method** | How payment was made (cash, card, online_banking, check) |
| **Net Revenue** | Total revenue minus total refunds |
| **Audit Trail** | Record of refund reason and admin notes |

---

**Document Version:** 1.0
**Last Updated:** December 2024
**Status:** Complete Implementation Ready
