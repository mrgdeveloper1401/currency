from django.contrib import admin
from django.utils.html import format_html
from .models import Currency, Market, Order, Trade, FuturesPosition, FundingRate, Liquidation


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'name', 'is_active', 'is_fiat', 'is_stable_coin', 'decimals')
    list_filter = ('is_active', 'is_fiat', 'is_stable_coin')
    search_fields = ('symbol', 'name')
    list_editable = ('is_active',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (None, {
            'fields': ('symbol', 'name', 'is_active')
        }),
        ('Currency Type', {
            'fields': ('is_fiat', 'is_stable_coin', 'decimals'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Market)
class MarketAdmin(admin.ModelAdmin):
    list_display = ('market_pair', 'market_type', 'is_active', 'price_precision', 'amount_precision')
    list_filter = ('market_type', 'is_active', 'base_currency', 'quote_currency')
    search_fields = ('base_currency__symbol', 'quote_currency__symbol')
    list_editable = ('is_active', 'price_precision', 'amount_precision')
    raw_id_fields = ('base_currency', 'quote_currency')

    def market_pair(self, obj):
        return f"{obj.base_currency.symbol}/{obj.quote_currency.symbol}"

    market_pair.short_description = 'Market Pair'

    fieldsets = (
        (None, {
            'fields': ('base_currency', 'quote_currency', 'market_type', 'is_active')
        }),
        ('Order Settings', {
            'fields': ('price_precision', 'amount_precision', 'min_order_amount', 'min_notional'),
            'classes': ('collapse',)
        }),
        ('Fee Structure', {
            'fields': ('maker_fee', 'taker_fee'),
            'classes': ('collapse',)
        }),
        ('Futures Settings', {
            'fields': ('max_leverage', 'funding_rate_interval'),
            'classes': ('collapse',)
        }),
    )


class TradeInline(admin.TabularInline):
    model = Trade
    extra = 0
    readonly_fields = ('price', 'amount', 'fee', 'fee_currency', 'is_maker')
    can_delete = False
    max_num = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'user', 'market', 'side', 'order_type', 'amount_price', 'status', 'created_at')
    list_filter = ('status', 'side', 'order_type', 'market__market_type')
    search_fields = (
    'user__username', 'market__base_currency__symbol', 'market__quote_currency__symbol', 'client_order_id')
    readonly_fields = ('created_at', 'updated_at', 'filled_amount', 'avg_fill_price', 'fee', 'fee_currency')
    raw_id_fields = ('user', 'market', 'fee_currency')
    inlines = [TradeInline]
    actions = ['cancel_orders', 'force_fill_orders']

    def order_id(self, obj):
        return str(obj.id)[:8]

    order_id.short_description = 'ID'

    def amount_price(self, obj):
        if obj.price:
            return f"{obj.amount} @ {obj.price}"
        return f"{obj.amount} (Market)"

    amount_price.short_description = 'Amount/Price'

    fieldsets = (
        (None, {
            'fields': ('user', 'market', 'order_type', 'side', 'status')
        }),
        ('Order Details', {
            'fields': ('amount', 'price', 'stop_price', 'filled_amount', 'avg_fill_price')
        }),
        ('Advanced', {
            'fields': ('time_in_force', 'reduce_only', 'close_position', 'client_order_id'),
            'classes': ('collapse',)
        }),
        ('Fees', {
            'fields': ('fee', 'fee_currency'),
            'classes': ('collapse',)
        }),
    )

    def cancel_orders(self, request, queryset):
        updated = queryset.filter(status=Order.OPEN).update(status=Order.CANCELLED)
        self.message_user(request, f'{updated} orders cancelled.')

    cancel_orders.short_description = "Cancel selected orders"

    def force_fill_orders(self, request, queryset):
        # این اکشن فقط برای اهداف تستی استفاده شود
        updated = 0
        for order in queryset.filter(status=Order.OPEN):
            order.filled_amount = order.amount
            order.avg_fill_price = order.price or order.market.get_current_price()
            order.status = Order.FILLED
            order.save()
            updated += 1
        self.message_user(request, f'{updated} orders force filled.')

    force_fill_orders.short_description = "Force fill orders (TEST ONLY)"


@admin.register(Trade)
class TradeAdmin(admin.ModelAdmin):
    list_display = ('trade_id', 'order', 'side', 'price_amount', 'fee_display', 'created_at')
    list_filter = ('order__market', 'is_maker')
    raw_id_fields = ('order', 'fee_currency')
    readonly_fields = ('created_at', 'updated_at')

    def trade_id(self, obj):
        return str(obj.id)[:8]

    trade_id.short_description = 'ID'

    def side(self, obj):
        return obj.order.side

    side.short_description = 'Side'

    def price_amount(self, obj):
        return f"{obj.price} x {obj.amount}"

    price_amount.short_description = 'Price/Amount'

    def fee_display(self, obj):
        return f"{obj.fee} {obj.fee_currency.symbol}"

    fee_display.short_description = 'Fee'


@admin.register(FuturesPosition)
class FuturesPositionAdmin(admin.ModelAdmin):
    list_display = ('position_id', 'user', 'market', 'side_leverage', 'entry_mark_price', 'pnl_display', 'status')
    list_filter = ('status', 'side', 'market')
    search_fields = ('user__username', 'market__base_currency__symbol')
    readonly_fields = ('created_at', 'updated_at', 'unrealized_pnl', 'realized_pnl', 'mark_price')
    raw_id_fields = ('user', 'market')
    actions = ['close_positions', 'force_liquidate']

    def position_id(self, obj):
        return str(obj.id)[:8]

    position_id.short_description = 'ID'

    def side_leverage(self, obj):
        return f"{obj.get_side_display()} {obj.leverage}x"

    side_leverage.short_description = 'Side/Leverage'

    def entry_mark_price(self, obj):
        return f"{obj.entry_price} / {obj.mark_price}"

    entry_mark_price.short_description = 'Entry/Mark'

    def pnl_display(self, obj):
        pnl = obj.unrealized_pnl + obj.realized_pnl
        color = 'green' if pnl >= 0 else 'red'
        return format_html(f'<span style="color: {color}">{pnl:.4f}</span>')

    pnl_display.short_description = 'Total PNL'

    fieldsets = (
        (None, {
            'fields': ('user', 'market', 'side', 'status', 'leverage')
        }),
        ('Position Details', {
            'fields': ('amount', 'entry_price', 'close_price', 'liquidation_price')
        }),
        ('Margin', {
            'fields': ('margin', 'initial_margin', 'maintenance_margin'),
            'classes': ('collapse',)
        }),
        ('PNL', {
            'fields': ('unrealized_pnl', 'realized_pnl', 'mark_price'),
            'classes': ('collapse',)
        }),
        ('Funding', {
            'fields': ('funding_rate', 'last_funding_time'),
            'classes': ('collapse',)
        }),
    )

    def close_positions(self, request, queryset):
        updated = queryset.filter(status=FuturesPosition.OPEN).update(status=FuturesPosition.CLOSED)
        self.message_user(request, f'{updated} positions closed.')

    close_positions.short_description = "Close selected positions"

    def force_liquidate(self, request, queryset):
        # این اکشن فقط برای اهداف تستی استفاده شود
        updated = 0
        for position in queryset.filter(status=FuturesPosition.OPEN):
            position.status = FuturesPosition.LIQUIDATED
            position.save()
            updated += 1
        self.message_user(request, f'{updated} positions liquidated (TEST ONLY).')

    force_liquidate.short_description = "Force liquidate (TEST ONLY)"


@admin.register(FundingRate)
class FundingRateAdmin(admin.ModelAdmin):
    list_display = ('market', 'rate_percent', 'next_funding_time', 'created_at')
    list_filter = ('market',)
    raw_id_fields = ('market',)

    def rate_percent(self, obj):
        return f"{float(obj.rate) * 100:.4f}%"

    rate_percent.short_description = 'Rate'


@admin.register(Liquidation)
class LiquidationAdmin(admin.ModelAdmin):
    list_display = ('position', 'price', 'amount', 'realized_pnl', 'created_at')
    raw_id_fields = ('position',)
    readonly_fields = ('created_at', 'updated_at')