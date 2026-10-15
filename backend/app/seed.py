import datetime
import json
from typing import Optional
from sqlalchemy.orm import Session

from app.core.database import SessionLocal, Base, engine
from app.models.models import (
    Customer,
    Account,
    Transaction,
    LoanApplication,
    FraudAlert,
    CompliancePolicy,
    AuditEvent,
    ExecutionTrace,
)


def seed_database(db: Optional[Session] = None, force_recreate: bool = False):
    """Seed SQLite database with realistic fictional banking demo records."""
    target_engine = db.get_bind() if db is not None else engine
    if force_recreate:
        Base.metadata.drop_all(bind=target_engine)
    Base.metadata.create_all(bind=target_engine)

    session = db if db is not None else SessionLocal()
    try:
        # Check if already seeded
        if session.query(Customer).count() >= 8 and not force_recreate:
            return {"status": "already_seeded", "message": "Database already contains seed data."}

        # Clear existing records if force recreation
        if force_recreate:
            session.query(AuditEvent).delete()
            session.query(FraudAlert).delete()
            session.query(Transaction).delete()
            session.query(LoanApplication).delete()
            session.query(Account).delete()
            session.query(Customer).delete()
            session.query(CompliancePolicy).delete()
            session.commit()

        # 1. Seed Compliance Policies
        policies = [
            CompliancePolicy(
                id="POL-6001",
                code="AML-CFT-01",
                name="Anti-Money Laundering & Terrorist Financing",
                description="Flags cash transfers and wires exceeding ₹200,000 and offshore jurisdictions.",
                max_unverified_limit=25000.0,
                aml_flag_threshold=200000.0,
                rules_json=json.dumps({
                    "single_transaction_threshold": 200000.0,
                    "daily_aggregate_threshold": 500000.0,
                    "high_risk_jurisdictions": ["Dubai", "Cayman", "Zurich", "Unknown IP"],
                    "high_risk_categories": ["Crypto Transfer", "Overseas Forex Desk", "Offshore Casino"]
                }),
                is_active=True
            ),
            CompliancePolicy(
                id="POL-6002",
                code="KYC-VERIF-02",
                name="Customer Due Diligence & KYC Mandate",
                description="Restricts credit lending and high-value transfers for non-verified customers.",
                max_unverified_limit=25000.0,
                aml_flag_threshold=50000.0,
                rules_json=json.dumps({
                    "allowed_statuses": ["VERIFIED"],
                    "document_types": ["Aadhaar", "PAN", "Passport"],
                    "re-kyc_interval_years": 2
                }),
                is_active=True
            ),
            CompliancePolicy(
                id="POL-6003",
                code="CREDIT-DTI-03",
                name="Prudential Lending & DTI Ceiling",
                description="Caps permissible Debt-to-Income ratio at 40% with minimum credit score 650.",
                max_unverified_limit=0.0,
                aml_flag_threshold=1000000.0,
                rules_json=json.dumps({
                    "max_dti_ratio": 40.0,
                    "min_credit_score": 650,
                    "benchmark_rate": 10.5
                }),
                is_active=True
            ),
            CompliancePolicy(
                id="POL-6004",
                code="FRAUD-VELOCITY-04",
                name="Card & Real-Time Payment Velocity Defense",
                description="Detects anomalous burst transactions and repeated identical debit spikes.",
                max_unverified_limit=10000.0,
                aml_flag_threshold=150000.0,
                rules_json=json.dumps({
                    "max_rapid_transactions_per_hour": 5,
                    "identical_amount_window_minutes": 15
                }),
                is_active=True
            )
        ]
        session.add_all(policies)

        # 2. Seed 8 Fictional Customers
        customers = [
            Customer(
                id="CUST-1001",
                full_name="Rajesh Sharma",
                email="rajesh.sharma@example.in",
                phone="+91-98200-11223",
                city="Mumbai",
                kyc_status="VERIFIED",
                credit_score=745,
                monthly_income=95000.0,
                created_at=datetime.datetime(2023, 1, 15, 10, 0, 0)
            ),
            Customer(
                id="CUST-1002",
                full_name="Priya Patel",
                email="priya.patel@example.in",
                phone="+91-98450-44556",
                city="Bangalore",
                kyc_status="VERIFIED",
                credit_score=780,
                monthly_income=145000.0,
                created_at=datetime.datetime(2023, 2, 20, 11, 30, 0)
            ),
            Customer(
                id="CUST-1003",
                full_name="Amit Verma",
                email="amit.verma@example.in",
                phone="+91-98110-77889",
                city="Delhi",
                kyc_status="VERIFIED",
                credit_score=690,
                monthly_income=72000.0,
                created_at=datetime.datetime(2023, 4, 10, 9, 15, 0)
            ),
            Customer(
                id="CUST-1004",
                full_name="Sneha Kulkarni",
                email="sneha.kulkarni@example.in",
                phone="+91-98220-33445",
                city="Pune",
                kyc_status="VERIFIED",
                credit_score=765,
                monthly_income=110000.0,
                created_at=datetime.datetime(2023, 5, 18, 14, 0, 0)
            ),
            Customer(
                id="CUST-1005",
                full_name="Vikram Malhotra",
                email="vikram.malhotra@example.in",
                phone="+91-98710-99001",
                city="Mumbai",
                kyc_status="VERIFIED",
                credit_score=630,
                monthly_income=65000.0,
                created_at=datetime.datetime(2023, 7, 22, 16, 45, 0)
            ),
            Customer(
                id="CUST-1006",
                full_name="Dr. Ananya Iyer",
                email="ananya.iyer@example.in",
                phone="+91-94440-55667",
                city="Chennai",
                kyc_status="VERIFIED",
                credit_score=810,
                monthly_income=185000.0,
                created_at=datetime.datetime(2023, 8, 5, 12, 10, 0)
            ),
            Customer(
                id="CUST-1007",
                full_name="Rohan Mehra",
                email="rohan.mehra@example.in",
                phone="+91-97000-88990",
                city="Hyderabad",
                kyc_status="PENDING",  # Incomplete KYC
                credit_score=590,
                monthly_income=45000.0,
                created_at=datetime.datetime(2023, 10, 1, 15, 20, 0)
            ),
            Customer(
                id="CUST-1008",
                full_name="Deepa Nair",
                email="deepa.nair@example.in",
                phone="+91-94950-12345",
                city="Kochi",
                kyc_status="VERIFIED",
                credit_score=715,
                monthly_income=88000.0,
                created_at=datetime.datetime(2023, 11, 12, 10, 30, 0)
            )
        ]
        session.add_all(customers)
        session.flush()

        # 3. Seed 11 Bank Accounts
        accounts = [
            Account(
                id="ACCT-2001",
                customer_id="CUST-1001",
                account_number="SBIN004819201",
                account_type="Savings",
                balance=185420.50,
                currency="INR",
                status="ACTIVE",
                created_at=datetime.datetime(2023, 1, 15, 10, 30, 0)
            ),
            Account(
                id="ACCT-2002",
                customer_id="CUST-1001",
                account_number="SBIN004819202",
                account_type="Salary",
                balance=42300.00,
                currency="INR",
                status="ACTIVE",
                created_at=datetime.datetime(2023, 2, 1, 10, 0, 0)
            ),
            Account(
                id="ACCT-2003",
                customer_id="CUST-1002",
                account_number="HDFC001928341",
                account_type="Premium Savings",
                balance=412850.75,
                currency="INR",
                status="ACTIVE",
                created_at=datetime.datetime(2023, 2, 20, 12, 0, 0)
            ),
            Account(
                id="ACCT-2004",
                customer_id="CUST-1003",
                account_number="ICIC009182734",
                account_type="Current",
                balance=98400.00,
                currency="INR",
                status="ACTIVE",
                created_at=datetime.datetime(2023, 4, 10, 10, 0, 0)
            ),
            Account(
                id="ACCT-2005",
                customer_id="CUST-1004",
                account_number="AXIS007162534",
                account_type="Savings",
                balance=234500.00,
                currency="INR",
                status="ACTIVE",
                created_at=datetime.datetime(2023, 5, 18, 14, 30, 0)
            ),
            Account(
                id="ACCT-2006",
                customer_id="CUST-1005",
                account_number="KOTK003847261",
                account_type="Savings",
                balance=31200.25,
                currency="INR",
                status="ACTIVE",
                created_at=datetime.datetime(2023, 7, 22, 17, 0, 0)
            ),
            Account(
                id="ACCT-2007",
                customer_id="CUST-1006",
                account_number="SBIN005619283",
                account_type="Premium Savings",
                balance=890000.00,
                currency="INR",
                status="ACTIVE",
                created_at=datetime.datetime(2023, 8, 5, 12, 30, 0)
            ),
            Account(
                id="ACCT-2008",
                customer_id="CUST-1007",
                account_number="PUNB008271625",
                account_type="Savings",
                balance=15300.00,
                currency="INR",
                status="ACTIVE",
                created_at=datetime.datetime(2023, 10, 1, 15, 30, 0)
            ),
            Account(
                id="ACCT-2009",
                customer_id="CUST-1008",
                account_number="FEDB001827364",
                account_type="Savings",
                balance=164200.80,
                currency="INR",
                status="ACTIVE",
                created_at=datetime.datetime(2023, 11, 12, 11, 0, 0)
            ),
            Account(
                id="ACCT-2010",
                customer_id="CUST-1008",
                account_number="FEDB001827365",
                account_type="Current",
                balance=78900.00,
                currency="INR",
                status="ACTIVE",
                created_at=datetime.datetime(2023, 12, 1, 10, 0, 0)
            ),
            Account(
                id="ACCT-2011",
                customer_id="CUST-1002",
                account_number="HDFC001928342",
                account_type="Fixed Deposit Escrow",
                balance=500000.00,
                currency="INR",
                status="ACTIVE",
                created_at=datetime.datetime(2023, 3, 1, 10, 0, 0)
            )
        ]
        session.add_all(accounts)
        session.flush()

        # 4. Seed 45 Realistic Transactions (Including Suspicious Scenarios for Use Cases)
        now = datetime.datetime.utcnow()
        txns = [
            # --- CUST-1001 Transactions (Use Case 1, 2, 3, 5) ---
            # TXN-3001: Suspicious high-value offshore wire (Crucial for Use Case 3!)
            Transaction(
                id="TXN-3001",
                account_id="ACCT-2001",
                customer_id="CUST-1001",
                amount=275000.00,
                txn_type="DEBIT",
                category="Overseas Forex Desk",
                merchant="Apex Global FX Clearing",
                location="Dubai",
                timestamp=now - datetime.timedelta(days=1, hours=4),
                status="FLAGGED",
                is_flagged=True,
                flag_reason="High-risk offshore Forex wire exceeding ₹200,000 threshold from anomalous IP location (Dubai)"
            ),
            Transaction(
                id="TXN-3002",
                account_id="ACCT-2001",
                customer_id="CUST-1001",
                amount=95000.00,
                txn_type="CREDIT",
                category="Salary",
                merchant="Tata Consultancy Services Ltd",
                location="Mumbai",
                timestamp=now - datetime.timedelta(days=3),
                status="COMPLETED",
                is_flagged=False
            ),
            Transaction(
                id="TXN-3003",
                account_id="ACCT-2001",
                customer_id="CUST-1001",
                amount=12450.00,
                txn_type="DEBIT",
                category="Electronics",
                merchant="Croma Electronics Bandra",
                location="Mumbai",
                timestamp=now - datetime.timedelta(days=4, hours=2),
                status="COMPLETED",
                is_flagged=False
            ),
            Transaction(
                id="TXN-3004",
                account_id="ACCT-2001",
                customer_id="CUST-1001",
                amount=4850.00,
                txn_type="DEBIT",
                category="Grocery",
                merchant="Nature's Basket Khar",
                location="Mumbai",
                timestamp=now - datetime.timedelta(days=5),
                status="COMPLETED",
                is_flagged=False
            ),
            Transaction(
                id="TXN-3005",
                account_id="ACCT-2001",
                customer_id="CUST-1001",
                amount=2200.00,
                txn_type="DEBIT",
                category="Dining",
                merchant="Social Café BKC",
                location="Mumbai",
                timestamp=now - datetime.timedelta(days=6, hours=5),
                status="COMPLETED",
                is_flagged=False
            ),
            Transaction(
                id="TXN-3006",
                account_id="ACCT-2001",
                customer_id="CUST-1001",
                amount=3500.00,
                txn_type="DEBIT",
                category="Utilities",
                merchant="Adani Electricity Mumbai",
                location="Mumbai",
                timestamp=now - datetime.timedelta(days=7),
                status="COMPLETED",
                is_flagged=False
            ),
            Transaction(
                id="TXN-3007",
                account_id="ACCT-2001",
                customer_id="CUST-1001",
                amount=18500.00,
                txn_type="DEBIT",
                category="Travel",
                merchant="Air India Online Booking",
                location="Mumbai",
                timestamp=now - datetime.timedelta(days=9),
                status="COMPLETED",
                is_flagged=False
            ),
            Transaction(
                id="TXN-3008",
                account_id="ACCT-2001",
                customer_id="CUST-1001",
                amount=6200.00,
                txn_type="DEBIT",
                category="Healthcare",
                merchant="Apollo Pharmacy Worli",
                location="Mumbai",
                timestamp=now - datetime.timedelta(days=11),
                status="COMPLETED",
                is_flagged=False
            ),
            Transaction(
                id="TXN-3009",
                account_id="ACCT-2001",
                customer_id="CUST-1001",
                amount=1500.00,
                txn_type="DEBIT",
                category="Entertainment",
                merchant="PVR Cinemas Phoenix Mall",
                location="Mumbai",
                timestamp=now - datetime.timedelta(days=12),
                status="COMPLETED",
                is_flagged=False
            ),
            Transaction(
                id="TXN-3010",
                account_id="ACCT-2001",
                customer_id="CUST-1001",
                amount=10000.00,
                txn_type="DEBIT",
                category="ATM Withdrawal",
                merchant="SBI ATM Nariman Point",
                location="Mumbai",
                timestamp=now - datetime.timedelta(days=14),
                status="COMPLETED",
                is_flagged=False
            ),
            Transaction(
                id="TXN-3011",
                account_id="ACCT-2002",
                customer_id="CUST-1001",
                amount=15000.00,
                txn_type="DEBIT",
                category="Investment",
                merchant="Zerodha Broking Ltd",
                location="Mumbai",
                timestamp=now - datetime.timedelta(days=16),
                status="COMPLETED",
                is_flagged=False
            ),

            # --- CUST-1002 Transactions (Use Case 4 - Loan candidate) ---
            Transaction(
                id="TXN-3012",
                account_id="ACCT-2003",
                customer_id="CUST-1002",
                amount=145000.00,
                txn_type="CREDIT",
                category="Salary",
                merchant="Infosys Global Technology",
                location="Bangalore",
                timestamp=now - datetime.timedelta(days=2),
                status="COMPLETED",
                is_flagged=False
            ),
            Transaction(
                id="TXN-3013",
                account_id="ACCT-2003",
                customer_id="CUST-1002",
                amount=8500.00,
                txn_type="DEBIT",
                category="Grocery",
                merchant="Lulu Hypermarket",
                location="Bangalore",
                timestamp=now - datetime.timedelta(days=5),
                status="COMPLETED",
                is_flagged=False
            ),
            Transaction(
                id="TXN-3014",
                account_id="ACCT-2003",
                customer_id="CUST-1002",
                amount=4200.00,
                txn_type="DEBIT",
                category="Dining",
                merchant="Toit Brewpub Indiranagar",
                location="Bangalore",
                timestamp=now - datetime.timedelta(days=7),
                status="COMPLETED",
                is_flagged=False
            ),
            Transaction(
                id="TXN-3015",
                account_id="ACCT-2003",
                customer_id="CUST-1002",
                amount=25000.00,
                txn_type="DEBIT",
                category="Investment",
                merchant="HDFC Mutual Fund SIP",
                location="Bangalore",
                timestamp=now - datetime.timedelta(days=10),
                status="COMPLETED",
                is_flagged=False
            ),
            Transaction(
                id="TXN-3016",
                account_id="ACCT-2003",
                customer_id="CUST-1002",
                amount=12000.00,
                txn_type="DEBIT",
                category="Utilities",
                merchant="BESCOM Electric Power",
                location="Bangalore",
                timestamp=now - datetime.timedelta(days=15),
                status="COMPLETED",
                is_flagged=False
            ),

            # --- CUST-1005 Suspicious Transactions (Fraud Monitoring) ---
            Transaction(
                id="TXN-3017",
                account_id="ACCT-2006",
                customer_id="CUST-1005",
                amount=180000.00,
                txn_type="DEBIT",
                category="Crypto Transfer",
                merchant="Binance Peer-to-Peer Desk",
                location="Zurich",
                timestamp=now - datetime.timedelta(hours=10),
                status="FLAGGED",
                is_flagged=True,
                flag_reason="High risk cryptocurrency P2P transfer originating from anomalous foreign IP (Zurich)"
            ),
            Transaction(
                id="TXN-3018",
                account_id="ACCT-2006",
                customer_id="CUST-1005",
                amount=49999.00,
                txn_type="DEBIT",
                category="Crypto Transfer",
                merchant="WazirX Escrow Gateway",
                location="Mumbai",
                timestamp=now - datetime.timedelta(hours=6),
                status="FLAGGED",
                is_flagged=True,
                flag_reason="Structuring attempt detected: transaction kept just below ₹50,000 threshold"
            ),
            Transaction(
                id="TXN-3019",
                account_id="ACCT-2006",
                customer_id="CUST-1005",
                amount=49999.00,
                txn_type="DEBIT",
                category="Crypto Transfer",
                merchant="WazirX Escrow Gateway",
                location="Mumbai",
                timestamp=now - datetime.timedelta(hours=5, minutes=45),
                status="FLAGGED",
                is_flagged=True,
                flag_reason="Velocity anomaly: identical debit within 15 minutes of prior transaction"
            ),
            Transaction(
                id="TXN-3020",
                account_id="ACCT-2006",
                customer_id="CUST-1005",
                amount=65000.00,
                txn_type="CREDIT",
                category="Salary",
                merchant="Malhotra Retail Solutions",
                location="Mumbai",
                timestamp=now - datetime.timedelta(days=25),
                status="COMPLETED",
                is_flagged=False
            ),

            # --- CUST-1003 Transactions (Delhi Business) ---
            Transaction(
                id="TXN-3021",
                account_id="ACCT-2004",
                customer_id="CUST-1003",
                amount=72000.00,
                txn_type="CREDIT",
                category="Client Payment",
                merchant="Verma Enterprise Billing",
                location="Delhi",
                timestamp=now - datetime.timedelta(days=2),
                status="COMPLETED",
                is_flagged=False
            ),
            Transaction(
                id="TXN-3022",
                account_id="ACCT-2004",
                customer_id="CUST-1003",
                amount=14500.00,
                txn_type="DEBIT",
                category="Supplies",
                merchant="Delhi Stationery Wholesalers",
                location="Delhi",
                timestamp=now - datetime.timedelta(days=4),
                status="COMPLETED",
                is_flagged=False
            ),
            Transaction(
                id="TXN-3023",
                account_id="ACCT-2004",
                customer_id="CUST-1003",
                amount=220000.00,
                txn_type="DEBIT",
                category="Commercial Wire",
                merchant="Shenzhen Electronics Dist",
                location="Hong Kong",
                timestamp=now - datetime.timedelta(days=7),
                status="FLAGGED",
                is_flagged=True,
                flag_reason="Commercial cross-border payment exceeds AML single transaction limit without prior FX declaration"
            ),
            Transaction(
                id="TXN-3024",
                account_id="ACCT-2004",
                customer_id="CUST-1003",
                amount=6800.00,
                txn_type="DEBIT",
                category="Dining",
                merchant="Bukhara ITC Maurya",
                location="Delhi",
                timestamp=now - datetime.timedelta(days=9),
                status="COMPLETED",
                is_flagged=False
            ),

            # --- CUST-1004 Transactions (Pune Doctor) ---
            Transaction(
                id="TXN-3025",
                account_id="ACCT-2005",
                customer_id="CUST-1004",
                amount=110000.00,
                txn_type="CREDIT",
                category="Salary",
                merchant="Ruby Hall Clinic",
                location="Pune",
                timestamp=now - datetime.timedelta(days=1),
                status="COMPLETED",
                is_flagged=False
            ),
            Transaction(
                id="TXN-3026",
                account_id="ACCT-2005",
                customer_id="CUST-1004",
                amount=18400.00,
                txn_type="DEBIT",
                category="Medical Equipment",
                merchant="Medtronic India Pvt Ltd",
                location="Pune",
                timestamp=now - datetime.timedelta(days=3),
                status="COMPLETED",
                is_flagged=False
            ),
            Transaction(
                id="TXN-3027",
                account_id="ACCT-2005",
                customer_id="CUST-1004",
                amount=5400.00,
                txn_type="DEBIT",
                category="Grocery",
                merchant="Dorabjee's Supermarket Camp",
                location="Pune",
                timestamp=now - datetime.timedelta(days=8),
                status="COMPLETED",
                is_flagged=False
            ),

            # --- CUST-1006 Transactions (Chennai Professor) ---
            Transaction(
                id="TXN-3028",
                account_id="ACCT-2007",
                customer_id="CUST-1006",
                amount=185000.00,
                txn_type="CREDIT",
                category="Salary",
                merchant="IIT Madras Research Council",
                location="Chennai",
                timestamp=now - datetime.timedelta(days=2),
                status="COMPLETED",
                is_flagged=False
            ),
            Transaction(
                id="TXN-3029",
                account_id="ACCT-2007",
                customer_id="CUST-1006",
                amount=35000.00,
                txn_type="DEBIT",
                category="Education",
                merchant="Oxford Academic Press",
                location="Chennai",
                timestamp=now - datetime.timedelta(days=6),
                status="COMPLETED",
                is_flagged=False
            ),
            Transaction(
                id="TXN-3030",
                account_id="ACCT-2007",
                customer_id="CUST-1006",
                amount=4100.00,
                txn_type="DEBIT",
                category="Dining",
                merchant="Saravana Bhavan Mylapore",
                location="Chennai",
                timestamp=now - datetime.timedelta(days=12),
                status="COMPLETED",
                is_flagged=False
            ),

            # --- CUST-1007 Transactions (Hyderabad) ---
            Transaction(
                id="TXN-3031",
                account_id="ACCT-2008",
                customer_id="CUST-1007",
                amount=45000.00,
                txn_type="CREDIT",
                category="Salary",
                merchant="Hyderabad Media Works",
                location="Hyderabad",
                timestamp=now - datetime.timedelta(days=3),
                status="COMPLETED",
                is_flagged=False
            ),
            Transaction(
                id="TXN-3032",
                account_id="ACCT-2008",
                customer_id="CUST-1007",
                amount=28500.00,
                txn_type="DEBIT",
                category="Electronics",
                merchant="Reliance Digital Banjara",
                location="Hyderabad",
                timestamp=now - datetime.timedelta(days=8),
                status="FLAGGED",
                is_flagged=True,
                flag_reason="Transaction amount ₹28,500 exceeds ₹25,000 threshold for unverified KYC accounts (POL-6002)"
            ),

            # --- CUST-1008 Transactions (Kochi) ---
            Transaction(
                id="TXN-3033",
                account_id="ACCT-2009",
                customer_id="CUST-1008",
                amount=88000.00,
                txn_type="CREDIT",
                category="Salary",
                merchant="Kerala Spice Exports Ltd",
                location="Kochi",
                timestamp=now - datetime.timedelta(days=4),
                status="COMPLETED",
                is_flagged=False
            ),
            Transaction(
                id="TXN-3034",
                account_id="ACCT-2009",
                customer_id="CUST-1008",
                amount=14200.00,
                txn_type="DEBIT",
                category="Travel",
                merchant="Kerala Tourism Development",
                location="Kochi",
                timestamp=now - datetime.timedelta(days=10),
                status="COMPLETED",
                is_flagged=False
            ),
            Transaction(
                id="TXN-3035",
                account_id="ACCT-2010",
                customer_id="CUST-1008",
                amount=32000.00,
                txn_type="CREDIT",
                category="Invoice Settlement",
                merchant="Malabar Traders",
                location="Kochi",
                timestamp=now - datetime.timedelta(days=14),
                status="COMPLETED",
                is_flagged=False
            ),

            # Additional realistic transactions to reach >= 40 total
            Transaction(
                id="TXN-3036",
                account_id="ACCT-2001",
                customer_id="CUST-1001",
                amount=750.00,
                txn_type="DEBIT",
                category="Dining",
                merchant="Starbucks Bandra",
                location="Mumbai",
                timestamp=now - datetime.timedelta(days=18),
                status="COMPLETED",
                is_flagged=False
            ),
            Transaction(
                id="TXN-3037",
                account_id="ACCT-2001",
                customer_id="CUST-1001",
                amount=1200.00,
                txn_type="DEBIT",
                category="Transportation",
                merchant="Uber India Systems",
                location="Mumbai",
                timestamp=now - datetime.timedelta(days=20),
                status="COMPLETED",
                is_flagged=False
            ),
            Transaction(
                id="TXN-3038",
                account_id="ACCT-2003",
                customer_id="CUST-1002",
                amount=15000.00,
                txn_type="DEBIT",
                category="Shopping",
                merchant="Zara Phoenix Marketcity",
                location="Bangalore",
                timestamp=now - datetime.timedelta(days=18),
                status="COMPLETED",
                is_flagged=False
            ),
            Transaction(
                id="TXN-3039",
                account_id="ACCT-2003",
                customer_id="CUST-1002",
                amount=3200.00,
                txn_type="DEBIT",
                category="Healthcare",
                merchant="Fortis Hospital Pharmacy",
                location="Bangalore",
                timestamp=now - datetime.timedelta(days=22),
                status="COMPLETED",
                is_flagged=False
            ),
            Transaction(
                id="TXN-3040",
                account_id="ACCT-2005",
                customer_id="CUST-1004",
                amount=7500.00,
                txn_type="DEBIT",
                category="Dining",
                merchant="Malaka Spice Koregaon Park",
                location="Pune",
                timestamp=now - datetime.timedelta(days=15),
                status="COMPLETED",
                is_flagged=False
            ),
            Transaction(
                id="TXN-3041",
                account_id="ACCT-2007",
                customer_id="CUST-1006",
                amount=50000.00,
                txn_type="CREDIT",
                category="Consulting",
                merchant="Tata Motors R&D Consultancy",
                location="Chennai",
                timestamp=now - datetime.timedelta(days=20),
                status="COMPLETED",
                is_flagged=False
            ),
            Transaction(
                id="TXN-3042",
                account_id="ACCT-2009",
                customer_id="CUST-1008",
                amount=3800.00,
                txn_type="DEBIT",
                category="Fuel",
                merchant="Indian Oil Corporation Kochi",
                location="Kochi",
                timestamp=now - datetime.timedelta(days=19),
                status="COMPLETED",
                is_flagged=False
            ),
            Transaction(
                id="TXN-3043",
                account_id="ACCT-2001",
                customer_id="CUST-1001",
                amount=3200.00,
                txn_type="DEBIT",
                category="Subscriptions",
                merchant="Netflix & Spotify India",
                location="Mumbai",
                timestamp=now - datetime.timedelta(days=22),
                status="COMPLETED",
                is_flagged=False
            ),
            Transaction(
                id="TXN-3044",
                account_id="ACCT-2003",
                customer_id="CUST-1002",
                amount=6000.00,
                txn_type="DEBIT",
                category="Fitness",
                merchant="Cult.fit Koramangala",
                location="Bangalore",
                timestamp=now - datetime.timedelta(days=26),
                status="COMPLETED",
                is_flagged=False
            ),
            Transaction(
                id="TXN-3045",
                account_id="ACCT-2005",
                customer_id="CUST-1004",
                amount=14000.00,
                txn_type="DEBIT",
                category="Electronics",
                merchant="Apple Store Mumbai Online",
                location="Pune",
                timestamp=now - datetime.timedelta(days=28),
                status="COMPLETED",
                is_flagged=False
            )
        ]
        session.add_all(txns)
        session.flush()

        # 5. Seed 5 Realistic Fraud Alerts
        alerts = [
            FraudAlert(
                id="FA-5001",
                transaction_id="TXN-3001",
                customer_id="CUST-1001",
                risk_score=88,
                severity="CRITICAL",
                rule_triggered="Unusual high-value offshore wire to Dubai (₹275,000) exceeding AML ceiling with anomalous IP.",
                status="NEW",
                review_notes="Automated block triggered. Awaiting customer contact confirmation.",
                created_at=now - datetime.timedelta(days=1, hours=3)
            ),
            FraudAlert(
                id="FA-5002",
                transaction_id="TXN-3017",
                customer_id="CUST-1005",
                risk_score=92,
                severity="CRITICAL",
                rule_triggered="High-risk peer-to-peer cryptocurrency transfer to Binance from Switzerland endpoint (Zurich).",
                status="INVESTIGATING",
                review_notes="Compliance team investigating source of funds and wallet address reputation.",
                created_at=now - datetime.timedelta(hours=9)
            ),
            FraudAlert(
                id="FA-5003",
                transaction_id="TXN-3019",
                customer_id="CUST-1005",
                risk_score=78,
                severity="HIGH",
                rule_triggered="Velocity alert: multiple identical debit attempts (₹49,999) under 15 minutes structuring limit.",
                status="NEW",
                review_notes="Card temporarily frozen pending SMS OTP verification.",
                created_at=now - datetime.timedelta(hours=5, minutes=30)
            ),
            FraudAlert(
                id="FA-5004",
                transaction_id="TXN-3023",
                customer_id="CUST-1003",
                risk_score=70,
                severity="HIGH",
                rule_triggered="Commercial wire (₹220,000) to Hong Kong without prior international trade documentation.",
                status="INVESTIGATING",
                review_notes="Form 15CA/CB documentation requested from customer.",
                created_at=now - datetime.timedelta(days=6)
            ),
            FraudAlert(
                id="FA-5005",
                transaction_id="TXN-3032",
                customer_id="CUST-1007",
                risk_score=65,
                severity="MEDIUM",
                rule_triggered="Single transaction ₹28,500 exceeds ₹25,000 statutory limit for unverified KYC account.",
                status="NEW",
                review_notes="Account flagged for re-KYC before releasing transfer holds.",
                created_at=now - datetime.timedelta(days=7)
            )
        ]
        session.add_all(alerts)

        # 6. Seed 5 Realistic Loan Applications
        loans = [
            LoanApplication(
                id="LOAN-4001",
                customer_id="CUST-1002",  # Priya Patel - Prime candidate for Use Case 4
                requested_amount=300000.0,
                tenure_months=36,
                purpose="Home Renovation & Solar Rooftop",
                monthly_income=145000.0,
                existing_obligations=15000.0,
                status="APPROVED",
                interest_rate=9.5,
                estimated_emi=9611.23,
                dti_ratio=17.0,
                notes="Excellent credit score (780) and low existing obligations. Highly affordable.",
                created_at=now - datetime.timedelta(days=12)
            ),
            LoanApplication(
                id="LOAN-4002",
                customer_id="CUST-1001",  # Rajesh Sharma
                requested_amount=500000.0,
                tenure_months=48,
                purpose="Electric Vehicle Purchase (EV)",
                monthly_income=95000.0,
                existing_obligations=12000.0,
                status="UNDER_REVIEW",
                interest_rate=10.5,
                estimated_emi=12814.15,
                dti_ratio=26.1,
                notes="Underwriting assessment in progress. DTI within acceptable parameters.",
                created_at=now - datetime.timedelta(days=5)
            ),
            LoanApplication(
                id="LOAN-4003",
                customer_id="CUST-1006",  # Dr. Ananya Iyer
                requested_amount=1200000.0,
                tenure_months=60,
                purpose="Academic Laboratory Expansion",
                monthly_income=185000.0,
                existing_obligations=22000.0,
                status="APPROVED",
                interest_rate=9.25,
                estimated_emi=25068.74,
                dti_ratio=25.4,
                notes="Super-prime credit tier (810). Institutional guarantor verified.",
                created_at=now - datetime.timedelta(days=20)
            ),
            LoanApplication(
                id="LOAN-4004",
                customer_id="CUST-1005",  # Vikram Malhotra
                requested_amount=400000.0,
                tenure_months=24,
                purpose="Working Capital Loan",
                monthly_income=65000.0,
                existing_obligations=24000.0,
                status="REJECTED",
                interest_rate=14.5,
                estimated_emi=19293.45,
                dti_ratio=66.6,
                notes="Rejected: DTI (66.6%) heavily exceeds 40% cap; credit score 630 is below prime underwriting bar.",
                created_at=now - datetime.timedelta(days=8)
            ),
            LoanApplication(
                id="LOAN-4005",
                customer_id="CUST-1007",  # Rohan Mehra
                requested_amount=150000.0,
                tenure_months=12,
                purpose="Personal Medical Emergency",
                monthly_income=45000.0,
                existing_obligations=8000.0,
                status="REJECTED",
                interest_rate=14.5,
                estimated_emi=13506.12,
                dti_ratio=47.8,
                notes="Rejected: Incomplete KYC status (PENDING) and DTI exceeds 40%.",
                created_at=now - datetime.timedelta(days=15)
            )
        ]
        session.add_all(loans)

        # 7. Seed initial Audit Events
        audit_events = [
            AuditEvent(
                id="AUD-7001",
                timestamp=now - datetime.timedelta(days=1, hours=3, minutes=58),
                actor="RiskFraudAgent",
                event_type="FRAUD_ALERT_GENERATED",
                request_id="SYS-INIT-01",
                details_json=json.dumps({
                    "transaction_id": "TXN-3001",
                    "customer_id": "CUST-1001",
                    "rule": "AML-CFT-01",
                    "risk_score": 88,
                    "action": "BLOCK_AND_VERIFY"
                })
            ),
            AuditEvent(
                id="AUD-7002",
                timestamp=now - datetime.timedelta(days=12),
                actor="CreditLoanAgent",
                event_type="LOAN_EVALUATION",
                request_id="SYS-INIT-02",
                details_json=json.dumps({
                    "application_id": "LOAN-4001",
                    "customer_id": "CUST-1002",
                    "amount": 300000.0,
                    "result": "APPROVED",
                    "dti": 17.0
                })
            ),
            AuditEvent(
                id="AUD-7003",
                timestamp=now - datetime.timedelta(hours=9),
                actor="ComplianceAgent",
                event_type="AML_SURVEILLANCE_FLAG",
                request_id="SYS-INIT-03",
                details_json=json.dumps({
                    "transaction_id": "TXN-3017",
                    "customer_id": "CUST-1005",
                    "trigger": "Offshore Crypto Wire",
                    "status": "ESCALATED"
                })
            )
        ]
        session.add_all(audit_events)

        session.commit()
        return {
            "status": "success",
            "message": "Seeded database with 8 customers, 11 accounts, 45 transactions, 5 loan applications, 5 fraud alerts, 4 policies."
        }
    except Exception as e:
        session.rollback()
        raise e
    finally:
        if db is None:
            session.close()


if __name__ == "__main__":
    result = seed_database(force_recreate=True)
    print(result)
