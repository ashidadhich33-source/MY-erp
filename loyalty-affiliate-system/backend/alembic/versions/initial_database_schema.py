"""Initial database schema

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role', sa.Enum('admin', 'customer', 'affiliate', name='userrole'), nullable=False),
        sa.Column('status', sa.Enum('active', 'inactive', 'suspended', name='userstatus'), nullable=False),
        sa.Column('email_verified', sa.Boolean(), nullable=False),
        sa.Column('phone_verified', sa.Boolean(), nullable=False),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_phone'), 'users', ['phone'], unique=True)

    # Create customers table
    op.create_table('customers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('tier', sa.Enum('bronze', 'silver', 'gold', 'platinum', name='customertier'), nullable=False),
        sa.Column('total_points', sa.Integer(), nullable=False),
        sa.Column('lifetime_points', sa.Integer(), nullable=False),
        sa.Column('current_streak', sa.Integer(), nullable=False),
        sa.Column('longest_streak', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('active', 'inactive', 'suspended', name='customerstatus'), nullable=False),
        sa.Column('joined_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('last_activity', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_customers_id'), 'customers', ['id'], unique=False)

    # Create customer_kids table
    op.create_table('customer_kids',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('date_of_birth', sa.DateTime(timezone=True), nullable=False),
        sa.Column('gender', sa.String(length=10), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_customer_kids_id'), 'customer_kids', ['id'], unique=False)

    # Create customer_tier_history table
    op.create_table('customer_tier_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('previous_tier', sa.Enum('bronze', 'silver', 'gold', 'platinum', name='customertier'), nullable=True),
        sa.Column('new_tier', sa.Enum('bronze', 'silver', 'gold', 'platinum', name='customertier'), nullable=False),
        sa.Column('points_at_upgrade', sa.Integer(), nullable=False),
        sa.Column('reason', sa.String(length=255), nullable=True),
        sa.Column('changed_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['changed_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_customer_tier_history_id'), 'customer_tier_history', ['id'], unique=False)

    # Create loyalty_transactions table
    op.create_table('loyalty_transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('points', sa.Integer(), nullable=False),
        sa.Column('transaction_type', sa.Enum('earned', 'redeemed', 'expired', 'adjustment', 'transfer', name='transactiontype'), nullable=False),
        sa.Column('source', sa.Enum('purchase', 'referral', 'birthday', 'promotion', 'manual', 'system', name='transactionsource'), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=False),
        sa.Column('reference_id', sa.String(length=100), nullable=True),
        sa.Column('metadata', sa.Text(), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_loyalty_transactions_id'), 'loyalty_transactions', ['id'], unique=False)
    op.create_index('ix_loyalty_transactions_source', 'loyalty_transactions', ['source'], unique=False)
    op.create_index('ix_loyalty_transactions_transaction_type', 'loyalty_transactions', ['transaction_type'], unique=False)
    op.create_index('ix_loyalty_transactions_user_customer', 'loyalty_transactions', ['user_id', 'customer_id'], unique=False)

    # Create rewards table
    op.create_table('rewards',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('points_required', sa.Integer(), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('image_url', sa.String(length=500), nullable=True),
        sa.Column('status', sa.Enum('active', 'inactive', 'out_of_stock', 'discontinued', name='rewardstatus'), nullable=False),
        sa.Column('stock_quantity', sa.Integer(), nullable=False),
        sa.Column('max_per_customer', sa.Integer(), nullable=False),
        sa.Column('valid_from', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('valid_until', sa.DateTime(timezone=True), nullable=True),
        sa.Column('terms_conditions', sa.Text(), nullable=True),
        sa.Column('is_featured', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_rewards_id'), 'rewards', ['id'], unique=False)

    # Create reward_redemptions table
    op.create_table('reward_redemptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('transaction_id', sa.Integer(), nullable=False),
        sa.Column('reward_id', sa.Integer(), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('redemption_code', sa.String(length=100), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('fulfilled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('fulfilled_by', sa.Integer(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
        sa.ForeignKeyConstraint(['fulfilled_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['reward_id'], ['rewards.id'], ),
        sa.ForeignKeyConstraint(['transaction_id'], ['loyalty_transactions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_reward_redemptions_id'), 'reward_redemptions', ['id'], unique=False)

    # Create tier_benefits table
    op.create_table('tier_benefits',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tier', sa.Enum('bronze', 'silver', 'gold', 'platinum', name='customertier'), nullable=False),
        sa.Column('benefit_type', sa.String(length=100), nullable=False),
        sa.Column('benefit_value', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('valid_from', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('valid_until', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tier_benefits_id'), 'tier_benefits', ['id'], unique=False)
    op.create_index('ix_tier_benefits_benefit_type', 'tier_benefits', ['benefit_type'], unique=False)
    op.create_index('ix_tier_benefits_tier', 'tier_benefits', ['tier'], unique=False)

    # Create affiliates table
    op.create_table('affiliates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('affiliate_code', sa.String(length=50), nullable=False),
        sa.Column('referral_link', sa.String(length=500), nullable=False),
        sa.Column('status', sa.Enum('pending', 'approved', 'rejected', 'suspended', 'active', 'inactive', name='affiliatestatus'), nullable=False),
        sa.Column('commission_rate', sa.DECIMAL(precision=5, scale=2), nullable=False),
        sa.Column('total_earnings', sa.DECIMAL(precision=15, scale=2), nullable=False),
        sa.Column('total_paid', sa.DECIMAL(precision=15, scale=2), nullable=False),
        sa.Column('unpaid_balance', sa.DECIMAL(precision=15, scale=2), nullable=False),
        sa.Column('payment_method', sa.String(length=50), nullable=True),
        sa.Column('payment_details', sa.Text(), nullable=True),
        sa.Column('website_url', sa.String(length=500), nullable=True),
        sa.Column('marketing_channels', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('approved_by', sa.Integer(), nullable=True),
        sa.Column('joined_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('last_activity', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['approved_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_affiliates_affiliate_code'), 'affiliates', ['affiliate_code'], unique=True)
    op.create_index(op.f('ix_affiliates_id'), 'affiliates', ['id'], unique=False)

    # Create customer_referrals table
    op.create_table('customer_referrals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('affiliate_id', sa.Integer(), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('referral_code_used', sa.String(length=50), nullable=False),
        sa.Column('referral_source', sa.String(length=100), nullable=True),
        sa.Column('conversion_value', sa.DECIMAL(precision=15, scale=2), nullable=False),
        sa.Column('commission_amount', sa.DECIMAL(precision=15, scale=2), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('metadata', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['affiliate_id'], ['affiliates.id'], ),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_customer_referrals_id'), 'customer_referrals', ['id'], unique=False)
    op.create_index('ix_customer_referrals_affiliate_customer', 'customer_referrals', ['affiliate_id', 'customer_id'], unique=False)
    op.create_index('ix_customer_referrals_referral_code', 'customer_referrals', ['referral_code_used'], unique=False)

    # Create affiliate_commissions table
    op.create_table('affiliate_commissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('affiliate_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('referral_id', sa.Integer(), nullable=True),
        sa.Column('commission_amount', sa.DECIMAL(precision=15, scale=2), nullable=False),
        sa.Column('commission_rate', sa.DECIMAL(precision=5, scale=2), nullable=False),
        sa.Column('status', sa.Enum('pending', 'approved', 'paid', 'cancelled', name='commissionstatus'), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=False),
        sa.Column('approved_by', sa.Integer(), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('paid_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('payment_reference', sa.String(length=100), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['affiliate_id'], ['affiliates.id'], ),
        sa.ForeignKeyConstraint(['approved_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['referral_id'], ['customer_referrals.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_affiliate_commissions_id'), 'affiliate_commissions', ['id'], unique=False)

    # Create payout_requests table
    op.create_table('payout_requests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('affiliate_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.DECIMAL(precision=15, scale=2), nullable=False),
        sa.Column('payment_method', sa.String(length=50), nullable=False),
        sa.Column('payment_details', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('transaction_id', sa.String(length=100), nullable=True),
        sa.Column('processed_by', sa.Integer(), nullable=True),
        sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['affiliate_id'], ['affiliates.id'], ),
        sa.ForeignKeyConstraint(['processed_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_payout_requests_id'), 'payout_requests', ['id'], unique=False)

    # Create notification_templates table
    op.create_table('notification_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('category', sa.Enum('bill', 'birthday', 'promotion', 'welcome', 'loyalty', 'affiliate', name='templatecategory'), nullable=False),
        sa.Column('message_type', sa.Enum('text', 'image', 'document', 'audio', 'video', 'template', name='messagetype'), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('variables', sa.Text(), nullable=True),
        sa.Column('media_url', sa.String(length=500), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_default', sa.Boolean(), nullable=False),
        sa.Column('usage_count', sa.Integer(), nullable=False),
        sa.Column('last_used', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notification_templates_category'), 'notification_templates', ['category'], unique=False)
    op.create_index(op.f('ix_notification_templates_id'), 'notification_templates', ['id'], unique=False)
    op.create_index('ix_notification_templates_is_active', 'notification_templates', ['is_active'], unique=False)

    # Create whatsapp_messages table
    op.create_table('whatsapp_messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=True),
        sa.Column('message_type', sa.Enum('text', 'image', 'document', 'audio', 'video', 'template', name='messagetype'), nullable=False),
        sa.Column('direction', sa.Enum('outbound', 'inbound', name='messagedirection'), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('media_url', sa.String(length=500), nullable=True),
        sa.Column('template_id', sa.Integer(), nullable=True),
        sa.Column('whatsapp_message_id', sa.String(length=100), nullable=True),
        sa.Column('recipient_phone', sa.String(length=20), nullable=False),
        sa.Column('status', sa.Enum('sent', 'delivered', 'read', 'failed', 'pending', name='messagestatus'), nullable=False),
        sa.Column('status_timestamp', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('metadata', sa.Text(), nullable=True),
        sa.Column('is_automated', sa.Boolean(), nullable=False),
        sa.Column('scheduled_for', sa.DateTime(timezone=True), nullable=True),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('delivered_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
        sa.ForeignKeyConstraint(['template_id'], ['notification_templates.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_whatsapp_messages_id'), 'whatsapp_messages', ['id'], unique=False)
    op.create_index('ix_whatsapp_messages_message_type', 'whatsapp_messages', ['message_type'], unique=False)
    op.create_index('ix_whatsapp_messages_recipient_phone', 'whatsapp_messages', ['recipient_phone'], unique=False)
    op.create_index('ix_whatsapp_messages_status', 'whatsapp_messages', ['status'], unique=False)
    op.create_index('ix_whatsapp_messages_user_customer', 'whatsapp_messages', ['user_id', 'customer_id'], unique=False)
    op.create_index('ix_whatsapp_messages_whatsapp_message_id', 'whatsapp_messages', ['whatsapp_message_id'], unique=False)

    # Create whatsapp_webhooks table
    op.create_table('whatsapp_webhooks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('webhook_id', sa.String(length=100), nullable=False),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('payload', sa.Text(), nullable=False),
        sa.Column('processed', sa.Boolean(), nullable=False),
        sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_whatsapp_webhooks_event_type'), 'whatsapp_webhooks', ['event_type'], unique=False)
    op.create_index(op.f('ix_whatsapp_webhooks_id'), 'whatsapp_webhooks', ['id'], unique=False)
    op.create_index('ix_whatsapp_webhooks_processed', 'whatsapp_webhooks', ['processed'], unique=False)

    # Create birthday_promotions table
    op.create_table('birthday_promotions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=True),
        sa.Column('kid_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('promotion_type', sa.String(length=50), nullable=False),
        sa.Column('birthday_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('scheduled_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('sent_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.Enum('scheduled', 'sent', 'delivered', 'read', 'failed', 'cancelled', name='promotionstatus'), nullable=False),
        sa.Column('promotion_code', sa.String(length=100), nullable=True),
        sa.Column('discount_amount', sa.String(length=50), nullable=True),
        sa.Column('message_content', sa.Text(), nullable=True),
        sa.Column('template_id', sa.Integer(), nullable=True),
        sa.Column('whatsapp_message_id', sa.Integer(), nullable=True),
        sa.Column('is_recurring', sa.Boolean(), nullable=False),
        sa.Column('metadata', sa.Text(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
        sa.ForeignKeyConstraint(['kid_id'], ['customer_kids.id'], ),
        sa.ForeignKeyConstraint(['template_id'], ['notification_templates.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['whatsapp_message_id'], ['whatsapp_messages.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_birthday_promotions_birthday_date'), 'birthday_promotions', ['birthday_date'], unique=False)
    op.create_index(op.f('ix_birthday_promotions_id'), 'birthday_promotions', ['id'], unique=False)
    op.create_index('ix_birthday_promotions_scheduled_date', 'birthday_promotions', ['scheduled_date'], unique=False)
    op.create_index('ix_birthday_promotions_status', 'birthday_promotions', ['status'], unique=False)

    # Create birthday_schedules table
    op.create_table('birthday_schedules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('promotion_type', sa.String(length=50), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('advance_notice_days', sa.Integer(), nullable=False),
        sa.Column('template_id', sa.Integer(), nullable=False),
        sa.Column('discount_amount', sa.String(length=50), nullable=False),
        sa.Column('max_promotions_per_day', sa.Integer(), nullable=False),
        sa.Column('last_processed', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['template_id'], ['notification_templates.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_birthday_schedules_id'), 'birthday_schedules', ['id'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('birthday_schedules')
    op.drop_table('birthday_promotions')
    op.drop_table('whatsapp_webhooks')
    op.drop_table('whatsapp_messages')
    op.drop_table('notification_templates')
    op.drop_table('payout_requests')
    op.drop_table('affiliate_commissions')
    op.drop_table('customer_referrals')
    op.drop_table('affiliates')
    op.drop_table('tier_benefits')
    op.drop_table('reward_redemptions')
    op.drop_table('rewards')
    op.drop_table('loyalty_transactions')
    op.drop_table('customer_tier_history')
    op.drop_table('customer_kids')
    op.drop_table('customers')
    op.drop_table('users')