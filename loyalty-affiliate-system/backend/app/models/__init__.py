# Import all models to ensure they are registered with SQLAlchemy
from .user import User, UserRole, UserStatus
from .customer import Customer, CustomerKid, CustomerTierHistory, CustomerTier, CustomerStatus
from .loyalty import (
    LoyaltyTransaction,
    Reward,
    RewardRedemption,
    TierBenefit,
    TransactionType,
    TransactionSource,
    RewardStatus
)
from .affiliate import (
    Affiliate,
    CustomerReferral,
    AffiliateCommission,
    PayoutRequest,
    AffiliateStatus,
    CommissionStatus
)
from .whatsapp import (
    WhatsAppMessage,
    NotificationTemplate,
    WhatsAppWebhook,
    MessageType,
    MessageDirection,
    MessageStatus,
    TemplateCategory
)
from .birthday import BirthdayPromotion, BirthdaySchedule, PromotionStatus

# Make all models available at package level
__all__ = [
    # User models
    "User", "UserRole", "UserStatus",

    # Customer models
    "Customer", "CustomerKid", "CustomerTierHistory", "CustomerTier", "CustomerStatus",

    # Loyalty models
    "LoyaltyTransaction", "Reward", "RewardRedemption", "TierBenefit",
    "TransactionType", "TransactionSource", "RewardStatus",

    # Affiliate models
    "Affiliate", "CustomerReferral", "AffiliateCommission", "PayoutRequest",
    "AffiliateStatus", "CommissionStatus",

    # WhatsApp models
    "WhatsAppMessage", "NotificationTemplate", "WhatsAppWebhook",
    "MessageType", "MessageDirection", "MessageStatus", "TemplateCategory",

    # Birthday models
    "BirthdayPromotion", "BirthdaySchedule", "PromotionStatus"
]