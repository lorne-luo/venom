from django.db import models
from django.utils.translation import ugettext_lazy as _


class Trade(models.Model):
    broker = models.CharField(_('broker'), max_length=12, blank=True)
    account_id = models.CharField(_('account_id'), max_length=12, blank=True)
    trade_id = models.CharField(_('trade_id'), max_length=12, blank=False)
    instrument = models.CharField(_('instrument'), max_length=12, blank=False)
    strategy_name = models.CharField(_('strategy_name'), max_length=12, blank=True)
    strategy_version = models.CharField(_('strategy_version'), max_length=12, blank=True)
    strategy_magic_number = models.IntegerField(_('strategy_magic_number'), blank=True, null=True)

    open_time = models.DateTimeField(_('open time'), auto_now_add=False, editable=True, blank=True, null=True)
    close_time = models.DateTimeField(_('close time'), auto_now_add=False, editable=True, blank=True, null=True)
    profitable_time = models.DecimalField(_('profitable time'), max_digits=8, decimal_places=2, blank=True, null=True)

    open_price = models.DecimalField(_('open_price'), max_digits=8, decimal_places=5, blank=True, null=True)
    close_price = models.DecimalField(_('close_price'), max_digits=8, decimal_places=5, blank=True, null=True)
    side = models.CharField(_('side'), max_length=12, blank=True, null=False)
    lots = models.DecimalField(_('lots'), max_digits=8, decimal_places=2, blank=True, null=True)
    pips = models.DecimalField(_('pips'), max_digits=8, decimal_places=2, blank=True, null=True)
    profit = models.DecimalField(_('profit'), max_digits=8, decimal_places=2, blank=True, null=True)

    max_profit = models.DecimalField(_('max_profit'), max_digits=8, decimal_places=2, blank=True, null=True)
    min_profit = models.DecimalField(_('min_profit'), max_digits=8, decimal_places=2, blank=True, null=True)
    drawdown = models.DecimalField(_('min_profit'), max_digits=8, decimal_places=5, blank=True, null=True)
    risk = models.DecimalField(_('risk'), max_digits=8, decimal_places=2, blank=True, null=True)
