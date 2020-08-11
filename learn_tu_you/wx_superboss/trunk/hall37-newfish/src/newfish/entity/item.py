#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Auther: houguangdong
# @Time: 2020/6/30






_inited = False


allActionType = {
    store.StoreTabType.STT_HOT: HotStoreBuyAction,
    store.StoreTabType.STT_CHEST: ChestStoreBuyAction,
    store.StoreTabType.STT_ITEM: ChestStoreBuyAction,
    store.StoreTabType.STT_COIN: CoinStoreBuyAction,
    store.StoreTabType.STT_DIAMOND: DiamondStoreBuyAction,
    store.StoreTabType.STT_PEARL: PearlStoreBuyAction,
    store.StoreTabType.STT_COUPON: CouponStoreBuyAction,
    store.StoreTabType.STT_GUNSKIN: GunSkinStoreBuyAction,
    store.StoreTabType.STT_BULLET: BulletStoreBuyAction,
    store.StoreTabType.STT_TIMELIMITED: TimeLimitedStoreBuyAction,
    store.StoreTabType.STT_EXCHANGE: ExchangeStoreBuyAction
}


def initialize():
    ftlog.debug("newfish item initialize begin")
    global _inited
    if not _inited:
        _inited = True
        from poker.entity.events.tyevent import ChargeNotifyEvent
        from hall.game import TGHall
        from hall.entity.hallitem import TYItemExchangeEvent, TYSaleItemEvent
        from newfish.game import TGFish
        from newfish.entity.event import NFChargeNotifyEvent
        TGHall.getEventBus().subscribe(TYItemExchangeEvent, _triggerExchangeEvent)
        TGHall.getEventBus().subscribe(TYSaleItemEvent, _triggerSaleItemEvent)
        TGHall.getEventBus().subscribe(ChargeNotifyEvent, _triggerChargeNotifyEvent)
        TGFish.getEventBus().subscribe(NFChargeNotifyEvent, _triggerChargeNotifyEvent)
    ftlog.debug("newfish item initialize end")