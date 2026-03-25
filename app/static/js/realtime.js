(function () {
  'use strict';

  var STORAGE_KEY = 'smartstore.low_stock_notifications';
  var MAX_ITEMS_PER_STORE = 50;

  function parseJson(raw, fallback) {
    try {
      return JSON.parse(raw);
    } catch (e) {
      return fallback;
    }
  }

  function readStoreMap() {
    var raw = window.localStorage.getItem(STORAGE_KEY);
    var parsed = parseJson(raw || '{}', {});
    if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) return {};
    return parsed;
  }

  function writeStoreMap(data) {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(data || {}));
  }

  function normalizeLowStockEvent(payload) {
    var safe = payload || {};
    var stock = Number(safe.stockCount);
    var threshold = Number(safe.threshold);
    return {
      id: [safe.inventoryItemId || '', safe.timestamp || Date.now()].join(':'),
      inventoryItemId: safe.inventoryItemId || null,
      stockCount: Number.isFinite(stock) ? stock : null,
      threshold: Number.isFinite(threshold) ? threshold : null,
      storeId: safe.storeId || null,
      storeName: safe.storeName || null,
      productId: safe.productId || null,
      productName: safe.productName || null,
      shelfId: safe.shelfId || null,
      timestamp: safe.timestamp || new Date().toISOString()
    };
  }

  function persistLowStock(payload) {
    var event = normalizeLowStockEvent(payload);
    if (!event.storeId) return event;

    var storeMap = readStoreMap();
    var list = Array.isArray(storeMap[event.storeId]) ? storeMap[event.storeId] : [];
    list.unshift(event);
    if (list.length > MAX_ITEMS_PER_STORE) {
      list = list.slice(0, MAX_ITEMS_PER_STORE);
    }
    storeMap[event.storeId] = list;
    writeStoreMap(storeMap);
    return event;
  }

  function getLowStockForStore(storeId) {
    if (!storeId) return [];
    var storeMap = readStoreMap();
    var list = storeMap[storeId];
    return Array.isArray(list) ? list : [];
  }

  function emitClientEvent(name, detail) {
    window.dispatchEvent(new CustomEvent(name, { detail: detail || {} }));
  }

  if (typeof window.io !== 'function') {
    console.warn('[realtime] Socket.IO client is not available');
    return;
  }

  var socket = window.io({
    transports: ['websocket', 'polling'],
    reconnection: true
  });

  socket.on('connect', function () {
    emitClientEvent('smartstore:socket-connected', { sid: socket.id });
  });

  socket.on('disconnect', function (reason) {
    emitClientEvent('smartstore:socket-disconnected', { reason: reason });
  });

  socket.on('product_price_change', function (payload) {
    emitClientEvent('smartstore:product-price-change', payload || {});
  });

  socket.on('low_stock', function (payload) {
    var event = persistLowStock(payload || {});
    emitClientEvent('smartstore:low-stock', event);
  });

  window.smartStoreRealtime = {
    socket: socket,
    getLowStockForStore: getLowStockForStore
  };
}());
