from django.db import models
from core_app.models import CreateMixin, UpdateMixin, SoftDeleteMixin
from decimal import Decimal


class Currency(CreateMixin, UpdateMixin, SoftDeleteMixin):
    symbol = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    is_fiat = models.BooleanField(default=False)
    decimals = models.PositiveSmallIntegerField(default=8)
    is_stable_coin = models.BooleanField(default=False)  # برای تشخیص استیبل کوین‌ها مثل USDT

    def __str__(self):
        return f"{self.name} ({self.symbol})"

    class Meta:
        db_table = 'currency'
        verbose_name_plural = 'currencies'


class Market(CreateMixin, UpdateMixin, SoftDeleteMixin):
    SPOT = 'spot'
    FUTURES = 'futures'
    MARKET_TYPES = [
        (SPOT, 'Spot'),
        (FUTURES, 'Futures'),
    ]

    base_currency = models.ForeignKey(Currency, on_delete=models.PROTECT, related_name='base_markets')
    quote_currency = models.ForeignKey(Currency, on_delete=models.PROTECT, related_name='quote_markets')
    market_type = models.CharField(max_length=10, choices=MARKET_TYPES, default=SPOT)
    is_active = models.BooleanField(default=True)
    price_precision = models.PositiveSmallIntegerField(default=2)
    amount_precision = models.PositiveSmallIntegerField(default=6)
    min_order_amount = models.DecimalField(max_digits=20, decimal_places=8)
    min_notional = models.DecimalField(max_digits=20, decimal_places=8, default=Decimal('10.0'))  # حداقل ارزش سفارش
    maker_fee = models.DecimalField(max_digits=5, decimal_places=4, default=Decimal('0.001'))  # 0.1%
    taker_fee = models.DecimalField(max_digits=5, decimal_places=4, default=Decimal('0.002'))  # 0.2%

    # فیلدهای مخصوص Futures
    max_leverage = models.PositiveSmallIntegerField(default=20, null=True, blank=True)  # فقط برای Futures
    funding_rate_interval = models.PositiveSmallIntegerField(default=8, null=True,
                                                             blank=True)  # ساعت بین funding rateها

    def __str__(self):
        return f"{self.base_currency.symbol}/{self.quote_currency.symbol} ({self.get_market_type_display()})"

    class Meta:
        db_table = 'market'
        unique_together = ('base_currency', 'quote_currency', 'market_type')


class Order(CreateMixin, UpdateMixin, SoftDeleteMixin):
    MARKET = 'market'
    LIMIT = 'limit'
    STOP_LIMIT = 'stop_limit'
    STOP_MARKET = 'stop_market'  # اضافه شده
    TAKE_PROFIT_LIMIT = 'take_profit_limit'  # اضافه شده
    TAKE_PROFIT_MARKET = 'take_profit_market'  # اضافه شده
    ORDER_TYPES = [
        (MARKET, 'Market'),
        (LIMIT, 'Limit'),
        (STOP_LIMIT, 'Stop Limit'),
        (STOP_MARKET, 'Stop Market'),
        (TAKE_PROFIT_LIMIT, 'Take Profit Limit'),
        (TAKE_PROFIT_MARKET, 'Take Profit Market'),
    ]

    BUY = 'buy'
    SELL = 'sell'
    SIDE_CHOICES = [
        (BUY, 'Buy'),
        (SELL, 'Sell'),
    ]

    OPEN = 'open'
    PARTIALLY_FILLED = 'partially_filled'  # اضافه شده
    FILLED = 'filled'
    CANCELLED = 'cancelled'
    REJECTED = 'rejected'  # اضافه شده
    EXPIRED = 'expired'  # اضافه شده
    STATUS_CHOICES = [
        (OPEN, 'Open'),
        (PARTIALLY_FILLED, 'Partially Filled'),
        (FILLED, 'Filled'),
        (CANCELLED, 'Cancelled'),
        (REJECTED, 'Rejected'),
        (EXPIRED, 'Expired'),
    ]

    user = models.ForeignKey("account_app.User", on_delete=models.PROTECT, related_name="user_orders")
    market = models.ForeignKey(Market, on_delete=models.PROTECT, related_name='orders')
    order_type = models.CharField(max_length=20, choices=ORDER_TYPES)
    side = models.CharField(max_length=4, choices=SIDE_CHOICES)
    amount = models.DecimalField(max_digits=30, decimal_places=8)
    price = models.DecimalField(max_digits=30, decimal_places=8, null=True, blank=True)
    stop_price = models.DecimalField(max_digits=30, decimal_places=8, null=True, blank=True)
    filled_amount = models.DecimalField(max_digits=30, decimal_places=8, default=0)
    avg_fill_price = models.DecimalField(max_digits=30, decimal_places=8, null=True, blank=True)  # اضافه شده
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=OPEN)
    time_in_force = models.CharField(max_length=10, default='GTC')  # Good Till Cancel, IOC, FOK
    reduce_only = models.BooleanField(default=False)  # فقط برای Futures
    close_position = models.BooleanField(default=False)  # فقط برای Futures
    client_order_id = models.CharField(max_length=50, null=True, blank=True, unique=True)
    fee = models.DecimalField(max_digits=30, decimal_places=8, default=0)  # کارمزد پرداختی
    fee_currency = models.ForeignKey(Currency, on_delete=models.PROTECT, null=True, blank=True)

    class Meta:
        db_table = "order"
        ordering = ['-created_at']


class Trade(CreateMixin, UpdateMixin, SoftDeleteMixin):
    """مدل برای ثبت معاملات انجام شده (تسویه سفارشات)"""
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name='trades')
    price = models.DecimalField(max_digits=30, decimal_places=8)
    amount = models.DecimalField(max_digits=30, decimal_places=8)
    fee = models.DecimalField(max_digits=30, decimal_places=8)
    fee_currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    is_maker = models.BooleanField(default=False)  # آیا Maker بوده یا Taker

    class Meta:
        db_table = 'trade'


class FuturesPosition(CreateMixin, UpdateMixin, SoftDeleteMixin):
    OPEN = 'open'
    CLOSED = 'closed'
    LIQUIDATED = 'liquidated'
    STATUS_CHOICES = [
        (OPEN, 'Open'),
        (CLOSED, 'Closed'),
        (LIQUIDATED, 'Liquidated'),
    ]

    LONG = 'long'
    SHORT = 'short'
    SIDE_CHOICES = [
        (LONG, 'Long'),
        (SHORT, 'Short'),
    ]

    user = models.ForeignKey("account_app.User", on_delete=models.PROTECT, related_name="user_futures_positions")
    market = models.ForeignKey(Market, on_delete=models.PROTECT, related_name="market_futures")
    side = models.CharField(max_length=5, choices=SIDE_CHOICES)
    amount = models.DecimalField(max_digits=30, decimal_places=8)
    entry_price = models.DecimalField(max_digits=30, decimal_places=8)
    leverage = models.PositiveSmallIntegerField(default=1)
    liquidation_price = models.DecimalField(max_digits=30, decimal_places=8)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=OPEN)
    unrealized_pnl = models.DecimalField(max_digits=30, decimal_places=8, default=0)  # سود/زیان محقق نشده
    realized_pnl = models.DecimalField(max_digits=30, decimal_places=8, default=0)  # سود/زیان محقق شده
    margin = models.DecimalField(max_digits=30, decimal_places=8)  # مارجین استفاده شده
    initial_margin = models.DecimalField(max_digits=30, decimal_places=8)  # مارجین اولیه
    maintenance_margin = models.DecimalField(max_digits=30, decimal_places=8)  # مارجین نگهداری
    mark_price = models.DecimalField(max_digits=30, decimal_places=8)  # قیمت مارک برای محاسبه PNL
    close_price = models.DecimalField(max_digits=30, decimal_places=8, null=True, blank=True)  # قیمت بسته شدن
    funding_rate = models.DecimalField(max_digits=10, decimal_places=8, default=0)  # نرخ تامین مالی
    last_funding_time = models.DateTimeField(null=True, blank=True)  # زمان آخرین funding

    class Meta:
        db_table = 'futures_position'
        ordering = ('-created_at',)


class FundingRate(CreateMixin, UpdateMixin, SoftDeleteMixin):
    """مدل برای ثبت نرخ‌های تامین مالی (Funding Rate)"""
    market = models.ForeignKey(Market, on_delete=models.PROTECT, related_name='funding_rates')
    rate = models.DecimalField(max_digits=10, decimal_places=8)
    next_funding_time = models.DateTimeField()

    class Meta:
        db_table = 'funding_rate'
        ordering = ('-created_at',)


class Liquidation(CreateMixin, UpdateMixin, SoftDeleteMixin):
    """مدل برای ثبت معاملات Liquidation"""
    position = models.ForeignKey(FuturesPosition, on_delete=models.PROTECT, related_name='liquidations')
    price = models.DecimalField(max_digits=30, decimal_places=8)
    amount = models.DecimalField(max_digits=30, decimal_places=8)
    realized_pnl = models.DecimalField(max_digits=30, decimal_places=8)
    fee = models.DecimalField(max_digits=30, decimal_places=8)

    class Meta:
        db_table = 'liquidation'
