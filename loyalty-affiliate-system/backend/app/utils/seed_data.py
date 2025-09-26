"""
Database seeding script for development and testing.

This script populates the database with sample data including:
- Users (admin, customers, affiliates)
- Customer information and kids
- Loyalty transactions and points
- Rewards catalog
- Affiliate data and commissions
- WhatsApp message templates
- Birthday promotions
"""

from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
import random
import json

from ..models import (
    User, UserRole, UserStatus,
    Customer, CustomerTier, CustomerStatus,
    CustomerKid,
    LoyaltyTransaction, TransactionType, TransactionSource,
    Reward, RewardStatus,
    RewardRedemption,
    TierBenefit,
    Affiliate, AffiliateStatus,
    CustomerReferral,
    AffiliateCommission, CommissionStatus,
    NotificationTemplate, TemplateCategory, MessageType,
    BirthdayPromotion, PromotionStatus,
    BirthdaySchedule
)
from ..core.security import get_password_hash


def seed_users(db: Session):
    """Create sample users with different roles."""
    print("Seeding users...")

    users_data = [
        {
            "name": "System Administrator",
            "email": "admin@loyaltyapp.com",
            "phone": "+1234567890",
            "password": "admin123",
            "role": UserRole.ADMIN,
            "status": UserStatus.ACTIVE
        },
        {
            "name": "John Smith",
            "email": "john.smith@email.com",
            "phone": "+1234567891",
            "password": "password123",
            "role": UserRole.CUSTOMER,
            "status": UserStatus.ACTIVE
        },
        {
            "name": "Sarah Johnson",
            "email": "sarah.j@email.com",
            "phone": "+1234567892",
            "password": "password123",
            "role": UserRole.CUSTOMER,
            "status": UserStatus.ACTIVE
        },
        {
            "name": "Mike Wilson",
            "email": "mike.wilson@email.com",
            "phone": "+1234567893",
            "password": "password123",
            "role": UserRole.CUSTOMER,
            "status": UserStatus.ACTIVE
        },
        {
            "name": "Emily Davis",
            "email": "emily.davis@email.com",
            "phone": "+1234567894",
            "password": "password123",
            "role": UserRole.CUSTOMER,
            "status": UserStatus.ACTIVE
        },
        {
            "name": "David Brown",
            "email": "david.brown@email.com",
            "phone": "+1234567895",
            "password": "password123",
            "role": UserRole.CUSTOMER,
            "status": UserStatus.ACTIVE
        },
        {
            "name": "Lisa Anderson",
            "email": "lisa.anderson@email.com",
            "phone": "+1234567896",
            "password": "password123",
            "role": UserRole.CUSTOMER,
            "status": UserStatus.ACTIVE
        },
        {
            "name": "Tom Garcia",
            "email": "tom.garcia@email.com",
            "phone": "+1234567897",
            "password": "password123",
            "role": UserRole.CUSTOMER,
            "status": UserStatus.ACTIVE
        },
        {
            "name": "Jennifer Martinez",
            "email": "jennifer.m@email.com",
            "phone": "+1234567898",
            "password": "password123",
            "role": UserRole.CUSTOMER,
            "status": UserStatus.ACTIVE
        },
        {
            "name": "Chris Taylor",
            "email": "chris.taylor@email.com",
            "phone": "+1234567899",
            "password": "password123",
            "role": UserRole.CUSTOMER,
            "status": UserStatus.ACTIVE
        },
        {
            "name": "Amanda White",
            "email": "amanda.white@email.com",
            "phone": "+1234567800",
            "password": "password123",
            "role": UserRole.AFFILIATE,
            "status": UserStatus.ACTIVE
        },
        {
            "name": "Robert Lee",
            "email": "robert.lee@email.com",
            "phone": "+1234567801",
            "password": "password123",
            "role": UserRole.AFFILIATE,
            "status": UserStatus.ACTIVE
        },
        {
            "name": "Michelle Harris",
            "email": "michelle.harris@email.com",
            "phone": "+1234567802",
            "password": "password123",
            "role": UserRole.AFFILIATE,
            "status": UserStatus.ACTIVE
        }
    ]

    for user_data in users_data:
        user = User(
            name=user_data["name"],
            email=user_data["email"],
            phone=user_data["phone"],
            password_hash=get_password_hash(user_data["password"]),
            role=user_data["role"],
            status=user_data["status"],
            email_verified=True,
            phone_verified=True,
            created_at=datetime.utcnow()
        )
        db.add(user)

    db.commit()
    print(f"Created {len(users_data)} users")


def seed_tier_benefits(db: Session):
    """Create tier benefits for different customer tiers."""
    print("Seeding tier benefits...")

    benefits_data = [
        # Bronze tier benefits
        {"tier": CustomerTier.BRONZE, "benefit_type": "points_multiplier", "benefit_value": "1.0", "description": "1x points on all purchases"},
        {"tier": CustomerTier.BRONZE, "benefit_type": "birthday_bonus", "benefit_value": "50", "description": "50 bonus points on birthday"},

        # Silver tier benefits
        {"tier": CustomerTier.SILVER, "benefit_type": "points_multiplier", "benefit_value": "1.25", "description": "1.25x points on all purchases"},
        {"tier": CustomerTier.SILVER, "benefit_type": "birthday_bonus", "benefit_value": "100", "description": "100 bonus points on birthday"},
        {"tier": CustomerTier.SILVER, "benefit_type": "free_shipping", "benefit_value": "true", "description": "Free shipping on orders"},

        # Gold tier benefits
        {"tier": CustomerTier.GOLD, "benefit_type": "points_multiplier", "benefit_value": "1.5", "description": "1.5x points on all purchases"},
        {"tier": CustomerTier.GOLD, "benefit_type": "birthday_bonus", "benefit_value": "200", "description": "200 bonus points on birthday"},
        {"tier": CustomerTier.GOLD, "benefit_type": "free_shipping", "benefit_value": "true", "description": "Free shipping on orders"},
        {"tier": CustomerTier.GOLD, "benefit_type": "priority_support", "benefit_value": "true", "description": "Priority customer support"},

        # Platinum tier benefits
        {"tier": CustomerTier.PLATINUM, "benefit_type": "points_multiplier", "benefit_value": "2.0", "description": "2x points on all purchases"},
        {"tier": CustomerTier.PLATINUM, "benefit_type": "birthday_bonus", "benefit_value": "500", "description": "500 bonus points on birthday"},
        {"tier": CustomerTier.PLATINUM, "benefit_type": "free_shipping", "benefit_value": "true", "description": "Free shipping on orders"},
        {"tier": CustomerTier.PLATINUM, "benefit_type": "priority_support", "benefit_value": "true", "description": "Priority customer support"},
        {"tier": CustomerTier.PLATINUM, "benefit_type": "exclusive_offers", "benefit_value": "true", "description": "Access to exclusive offers"},
    ]

    for benefit_data in benefits_data:
        benefit = TierBenefit(
            tier=benefit_data["tier"],
            benefit_type=benefit_data["benefit_type"],
            benefit_value=benefit_data["benefit_value"],
            description=benefit_data["description"],
            is_active=True,
            created_at=datetime.utcnow()
        )
        db.add(benefit)

    db.commit()
    print(f"Created {len(benefits_data)} tier benefits")


def seed_customers(db: Session):
    """Create sample customers with different tiers and activity levels."""
    print("Seeding customers...")

    # Get users with customer role
    customer_users = db.query(User).filter(User.role == UserRole.CUSTOMER).all()

    customers_data = []
    for i, user in enumerate(customer_users):
        # Random tier assignment with some logic
        if i < 2:  # First 2 customers are platinum
            tier = CustomerTier.PLATINUM
            points = random.randint(1000, 2000)
        elif i < 5:  # Next 3 are gold
            tier = CustomerTier.GOLD
            points = random.randint(500, 999)
        elif i < 8:  # Next 3 are silver
            tier = CustomerTier.SILVER
            points = random.randint(200, 499)
        else:  # Rest are bronze
            tier = CustomerTier.BRONZE
            points = random.randint(0, 199)

        customer = Customer(
            user_id=user.id,
            tier=tier,
            total_points=points,
            lifetime_points=points + random.randint(100, 500),
            current_streak=random.randint(0, 30),
            longest_streak=random.randint(30, 365),
            status=CustomerStatus.ACTIVE,
            joined_date=datetime.utcnow() - timedelta(days=random.randint(30, 365)),
            last_activity=datetime.utcnow() - timedelta(days=random.randint(0, 7))
        )
        customers_data.append(customer)

    for customer in customers_data:
        db.add(customer)

    db.commit()
    print(f"Created {len(customers_data)} customers")


def seed_customer_kids(db: Session):
    """Create sample kids for customers."""
    print("Seeding customer kids...")

    customers = db.query(Customer).all()
    kids_names = ["Emma", "Noah", "Olivia", "Liam", "Ava", "William", "Sophia", "James", "Isabella", "Oliver"]

    for customer in customers:
        # 60% chance of having kids
        if random.random() < 0.6:
            num_kids = random.randint(1, 3)
            for i in range(num_kids):
                kid_name = f"{random.choice(kids_names)} {customer.user.name.split()[-1]}"
                birth_date = datetime.utcnow() - timedelta(days=random.randint(365, 365*15))  # 1-15 years old

                kid = CustomerKid(
                    customer_id=customer.id,
                    name=kid_name,
                    date_of_birth=birth_date,
                    gender=random.choice(["male", "female", "other"]),
                    notes=f"Born on {birth_date.strftime('%B %d, %Y')}",
                    is_active=True
                )
                db.add(kid)

    db.commit()
    print("Created customer kids")


def seed_rewards(db: Session):
    """Create sample rewards catalog."""
    print("Seeding rewards...")

    rewards_data = [
        {
            "name": "Free Coffee",
            "description": "Enjoy a complimentary coffee of your choice",
            "points_required": 100,
            "category": "beverage",
            "stock_quantity": -1,  # Unlimited
            "max_per_customer": 5,
            "is_featured": True
        },
        {
            "name": "10% Discount",
            "description": "Get 10% off your next purchase",
            "points_required": 200,
            "category": "discount",
            "stock_quantity": -1,
            "max_per_customer": 10,
            "is_featured": True
        },
        {
            "name": "Free Sandwich",
            "description": "Redeem for a delicious sandwich",
            "points_required": 150,
            "category": "food",
            "stock_quantity": 100,
            "max_per_customer": 3,
            "is_featured": False
        },
        {
            "name": "Birthday Gift",
            "description": "Special birthday surprise gift",
            "points_required": 300,
            "category": "gift",
            "stock_quantity": 50,
            "max_per_customer": 1,
            "is_featured": True
        },
        {
            "name": "Priority Service",
            "description": "Skip the line with priority service",
            "points_required": 75,
            "category": "service",
            "stock_quantity": -1,
            "max_per_customer": 20,
            "is_featured": False
        },
        {
            "name": "Mystery Box",
            "description": "Surprise gift box with random items",
            "points_required": 500,
            "category": "gift",
            "stock_quantity": 25,
            "max_per_customer": 2,
            "is_featured": True
        },
        {
            "name": "Free Dessert",
            "description": "Complimentary dessert with any meal",
            "points_required": 120,
            "category": "food",
            "stock_quantity": -1,
            "max_per_customer": 10,
            "is_featured": False
        },
        {
            "name": "VIP Event Access",
            "description": "Exclusive access to VIP events",
            "points_required": 1000,
            "category": "event",
            "stock_quantity": 10,
            "max_per_customer": 1,
            "is_featured": True
        }
    ]

    for reward_data in rewards_data:
        reward = Reward(
            name=reward_data["name"],
            description=reward_data["description"],
            points_required=reward_data["points_required"],
            category=reward_data["category"],
            stock_quantity=reward_data["stock_quantity"],
            max_per_customer=reward_data["max_per_customer"],
            is_featured=reward_data["is_featured"],
            status=RewardStatus.ACTIVE,
            created_at=datetime.utcnow()
        )
        db.add(reward)

    db.commit()
    print(f"Created {len(rewards_data)} rewards")


def seed_affiliates(db: Session):
    """Create sample affiliates with different statuses."""
    print("Seeding affiliates...")

    affiliate_users = db.query(User).filter(User.role == UserRole.AFFILIATE).all()

    for user in affiliate_users:
        affiliate_code = f"AFF{random.randint(1000, 9999)}"
        affiliate = Affiliate(
            user_id=user.id,
            affiliate_code=affiliate_code,
            referral_link=f"https://loyaltyapp.com/ref/{affiliate_code}",
            status=random.choice([AffiliateStatus.ACTIVE, AffiliateStatus.APPROVED]),
            commission_rate=random.choice([5.0, 7.5, 10.0, 15.0]),
            total_earnings=random.randint(100, 1000),
            total_paid=random.randint(50, 800),
            unpaid_balance=random.randint(25, 200),
            payment_method=random.choice(["bank_transfer", "paypal", "check"]),
            website_url=f"https://example{random.randint(1, 100)}.com" if random.random() > 0.5 else None,
            marketing_channels=json.dumps(random.sample(["social_media", "blog", "email", "website", "youtube"], random.randint(1, 3))),
            joined_date=datetime.utcnow() - timedelta(days=random.randint(30, 365)),
            last_activity=datetime.utcnow() - timedelta(days=random.randint(0, 7))
        )
        db.add(affiliate)

    db.commit()
    print(f"Created {len(affiliate_users)} affiliates")


def seed_notification_templates(db: Session):
    """Create WhatsApp message templates."""
    print("Seeding notification templates...")

    admin_user = db.query(User).filter(User.role == UserRole.ADMIN).first()

    templates_data = [
        {
            "name": "Welcome Message",
            "category": TemplateCategory.WELCOME,
            "content": "Welcome to our loyalty program, {{name}}! 🎉 Thank you for joining us. You'll start earning points on your next purchase!",
            "variables": json.dumps(["name"]),
            "message_type": MessageType.TEXT
        },
        {
            "name": "Birthday Greeting",
            "category": TemplateCategory.BIRTHDAY,
            "content": "Happy Birthday, {{name}}! 🎂 We hope you have a wonderful day. As our valued customer, enjoy {{discount}} on your next purchase!",
            "variables": json.dumps(["name", "discount"]),
            "message_type": MessageType.TEXT
        },
        {
            "name": "Points Earned",
            "category": TemplateCategory.LOYALTY,
            "content": "Great news, {{name}}! You've earned {{points}} points for your recent purchase. Your current balance is {{total_points}} points!",
            "variables": json.dumps(["name", "points", "total_points"]),
            "message_type": MessageType.TEXT
        },
        {
            "name": "Tier Upgrade",
            "category": TemplateCategory.LOYALTY,
            "content": "Congratulations, {{name}}! 🎉 You've been upgraded to {{tier}} tier! Enjoy enhanced benefits including {{benefit_description}}.",
            "variables": json.dumps(["name", "tier", "benefit_description"]),
            "message_type": MessageType.TEXT
        },
        {
            "name": "Affiliate Welcome",
            "category": TemplateCategory.AFFILIATE,
            "content": "Welcome to our affiliate program, {{name}}! Your affiliate code is {{affiliate_code}}. Start earning commissions by sharing your referral link!",
            "variables": json.dumps(["name", "affiliate_code"]),
            "message_type": MessageType.TEXT
        },
        {
            "name": "Purchase Receipt",
            "category": TemplateCategory.BILL,
            "content": "Thank you for your purchase, {{name}}! Order #{{order_id}} has been confirmed. You've earned {{points}} loyalty points!",
            "variables": json.dumps(["name", "order_id", "points"]),
            "message_type": MessageType.TEXT
        }
    ]

    for template_data in templates_data:
        template = NotificationTemplate(
            name=template_data["name"],
            category=template_data["category"],
            message_type=template_data["message_type"],
            content=template_data["content"],
            variables=template_data["variables"],
            is_active=True,
            is_default=True,
            created_by=admin_user.id,
            created_at=datetime.utcnow()
        )
        db.add(template)

    db.commit()
    print(f"Created {len(templates_data)} notification templates")


def seed_loyalty_transactions(db: Session):
    """Create sample loyalty transactions."""
    print("Seeding loyalty transactions...")

    customers = db.query(Customer).all()
    transaction_types = [TransactionType.EARNED, TransactionType.REDEEMED]
    sources = [TransactionSource.PURCHASE, TransactionSource.PROMOTION, TransactionSource.MANUAL]

    for customer in customers:
        # Create 5-15 random transactions per customer
        num_transactions = random.randint(5, 15)

        for i in range(num_transactions):
            # Determine if earned or redeemed (70% earned, 30% redeemed)
            if random.random() < 0.7 and customer.total_points > 50:
                trans_type = TransactionType.EARNED
                points = random.randint(10, 100)
                description = f"Earned points from {random.choice(['purchase', 'promotion', 'bonus'])}"
            else:
                trans_type = TransactionType.REDEEMED
                available_points = min(customer.total_points, random.randint(25, 150))
                points = -available_points  # Negative for redemptions
                description = f"Redeemed points for {random.choice(['reward', 'discount', 'gift'])}"

            transaction = LoyaltyTransaction(
                user_id=customer.user_id,
                customer_id=customer.id,
                points=points,
                transaction_type=trans_type,
                source=random.choice(sources),
                description=description,
                reference_id=f"TXN{random.randint(10000, 99999)}",
                metadata=json.dumps({"source": "seed_data"}),
                created_at=datetime.utcnow() - timedelta(days=random.randint(0, 180))
            )
            db.add(transaction)

    db.commit()
    print(f"Created loyalty transactions for {len(customers)} customers")


def seed_customer_referrals(db: Session):
    """Create sample customer referrals."""
    print("Seeding customer referrals...")

    affiliates = db.query(Affiliate).all()
    customers = db.query(Customer).all()

    for affiliate in affiliates:
        # Each affiliate gets 2-8 referrals
        num_referrals = random.randint(2, 8)

        for i in range(num_referrals):
            # Pick a random customer (ensure not referring themselves)
            available_customers = [c for c in customers if c.user_id != affiliate.user_id]
            if not available_customers:
                continue

            customer = random.choice(available_customers)
            conversion_value = random.randint(50, 500)
            commission_amount = conversion_value * (affiliate.commission_rate / 100)

            referral = CustomerReferral(
                affiliate_id=affiliate.id,
                customer_id=customer.id,
                referral_code_used=affiliate.affiliate_code,
                referral_source=random.choice(["social_media", "email", "website", "word_of_mouth"]),
                conversion_value=conversion_value,
                commission_amount=commission_amount,
                status="converted",
                metadata=json.dumps({"campaign": "seed_data"}),
                created_at=datetime.utcnow() - timedelta(days=random.randint(0, 90))
            )
            db.add(referral)

    db.commit()
    print(f"Created customer referrals for {len(affiliates)} affiliates")


def run_seed(db: Session):
    """Run all seeding functions."""
    print("Starting database seeding...")

    # Clear existing data (optional - be careful in production!)
    # db.query(BirthdayPromotion).delete()
    # db.query(CustomerReferral).delete()
    # db.query(AffiliateCommission).delete()
    # db.query(LoyaltyTransaction).delete()
    # db.query(RewardRedemption).delete()
    # db.query(Reward).delete()
    # db.query(TierBenefit).delete()
    # db.query(CustomerKid).delete()
    # db.query(Customer).delete()
    # db.query(Affiliate).delete()
    # db.query(NotificationTemplate).delete()
    # db.query(User).delete()
    # db.commit()

    # Seed data in order (respecting foreign key constraints)
    seed_tier_benefits(db)
    seed_users(db)
    seed_customers(db)
    seed_customer_kids(db)
    seed_rewards(db)
    seed_affiliates(db)
    seed_notification_templates(db)
    seed_loyalty_transactions(db)
    seed_customer_referrals(db)

    print("Database seeding completed successfully! 🎉")


if __name__ == "__main__":
    # This can be run as a standalone script
    from ..core.database import SessionLocal

    db = SessionLocal()
    try:
        run_seed(db)
    finally:
        db.close()